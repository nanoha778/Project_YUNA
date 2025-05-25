# -*- coding: utf-8 -*-
import os
import json
import random
import networkx as nx
from gensim.models import KeyedVectors
from itertools import product
import unicodedata

# === Word2Vec モデル読み込み ===
w2v_model = KeyedVectors.load_word2vec_format("model.vec", binary=False)

# === 意味ネットワーク読み込み ===
def load_meaning_network(json_path: str) -> nx.Graph:
    G = nx.Graph()
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        for src, neighbors in data.items():
            for tgt, weight in neighbors.items():
                try:
                    G.add_edge(src, tgt, weight=float(weight))
                except ValueError:
                    continue
    return G

# === テキスト分割 ===
def segment_text_by_meaning_network(text: str, graph: nx.Graph, n_min=1, n_max=8, related_threshold=0.7, similarity_threshold=0.45) -> list[str]:
    def get_filtered_related_terms(term: str) -> set:
        if term not in graph:
            return set()
        return {
            neighbor
            for neighbor in graph.neighbors(term)
            if graph[term][neighbor].get("weight", 1.0) > related_threshold
        }

    all_matrices = []
    for n in range(n_min, n_max + 1):
        ngrams = [text[i:i+n] for i in range(len(text) - n + 1)]
        matrix = [get_filtered_related_terms(term) for term in ngrams]
        all_matrices.append(matrix)

    max_len = max(len(m) for m in all_matrices)

    def safe_similarity(a, b):
        if not a or not b:
            return None
        inter = a & b
        union = a | b
        return len(inter) / len(union) if union else 0.0

    break_scores = []
    for i in range(max_len - 1):
        sims = []
        for matrix in all_matrices:
            if i < len(matrix) - 1:
                sim = safe_similarity(matrix[i], matrix[i+1])
                if sim is not None:
                    sims.append(sim)
        break_scores.append(1.0 - sum(sims)/len(sims) if sims else 0.0)

    def clean_text(text):
        return ''.join(c for c in text if unicodedata.category(c)[0] != 'C')

    log = print  # fallback
    log("==== Break scores ====")
    for i, s in enumerate(break_scores):
        log(f"{i}: {s:.3f}")

    result = []
    buffer = text[0]
    for i in range(1, len(text)):
        if i-1 < len(break_scores) and break_scores[i-1] >= similarity_threshold:
            result.append(buffer)
            buffer = text[i]
        else:
            buffer += text[i]
    result.append(buffer)
    return result

# === 類似語処理 ===
def estimate_similarity_by_unicode(unknown_term, known_terms, topn=5):
    def char_distance(c1, c2): return abs(ord(c1) - ord(c2))
    def term_distance(t1, t2):
        min_len = min(len(t1), len(t2))
        distances = [char_distance(t1[i], t2[i]) for i in range(min_len)]
        return sum(distances) / len(distances)

    similarity_scores = []
    for known in known_terms:
        dist = term_distance(unknown_term, known)
        similarity = 1 / (1 + dist)
        similarity_scores.append((known, similarity))

    similarity_scores.sort(key=lambda x: x[1], reverse=True)
    return similarity_scores[:topn]

# === モデル関数群 ===
def get_neighbors(term: str, G: nx.Graph) -> dict[str, float]:
    return {n: G[term][n].get("weight", 0.0) for n in G.neighbors(term)} if term in G else {}

def get_w2v_similar_terms(term: str, w2v_model, topn=5) -> dict[str, float]:
    try:
        results = w2v_model.most_similar(positive=[term], topn=topn)
        return {w: float(sim) for w, sim in results}
    except KeyError:
        return {}

def expand_single_term(term: str, G, w2v_model, threshold=0.35, topn=5) -> list[str]:
    neighbors = get_neighbors(term, G)
    w2v_terms = get_w2v_similar_terms(term, w2v_model, topn)
    combined = {**neighbors, **w2v_terms}
    scores = {w: score_term_relation(w, [term], G, w2v_model, threshold, topn) for w in combined if w != term}
    return filter_terms_by_score(scores, base_threshold=threshold)

def expand_term_list(terms: list[str], G, w2v_model, threshold=0.35, topn=5) -> dict[str, list[str]]:
    expanded_terms = {}
    for term in terms:
        if w2v_model is not None and hasattr(w2v_model, "key_to_index") and term not in w2v_model.key_to_index:
            # Word2Vec に存在しない場合 → 空で登録 or スキップ
            expanded_terms[term] = []
            continue

        try:
            expanded_terms[term] = expand_single_term(term, G, w2v_model, threshold, topn)
        except Exception as e:
            # 想定外のエラー保護
            expanded_terms[term] = []
    return expanded_terms

def score_term_relation(term: str, reference_terms: list[str], G: nx.Graph, w2v_model, base_weight=0.5, topn=5) -> float:
    diffs = []
    for ref in reference_terms:
        if G.has_edge(term, ref):
            weight = G[term][ref].get("weight", 0.0)
        else:
            weight = get_w2v_similar_terms(term, w2v_model, topn).get(ref, 0.0)
        diff = abs(weight - base_weight)
        diffs.append(diff)
    return sum(diffs) / len(diffs) if diffs else float("inf")

def filter_terms_by_score(scores: dict[str, float], base_threshold=0.6, random_range=(0.95, 1.05)) -> list[str]:
    adjusted_threshold = base_threshold * random.uniform(*random_range)
    return [term for term, score in scores.items() if score <= adjusted_threshold]

def add_new_nodes_to_graph(term: str, related_terms: list[str], G: nx.Graph, base_weight=0.5):
    for rel in related_terms:
        if not G.has_edge(term, rel):
            G.add_edge(term, rel, weight=base_weight)

def save_meaning_network(G: nx.Graph, path="meaning_network.json"):
    data = {}
    for src, tgt, attrs in G.edges(data=True):
        data.setdefault(src, {})
        data[src][tgt] = round(attrs.get("weight", 0.0), 6)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# === 区間補正 ===
def is_hiragana(s: str) -> bool:
    return all('ぁ' <= c <= 'ん' for c in s)

def merge_hiragana_chunks(chunks: list[str]) -> list[str]:
    result = []
    buffer = ""
    for chunk in chunks:
        if is_hiragana(chunk):
            buffer += chunk
        else:
            if buffer:
                result.append(buffer)
                buffer = ""
            result.append(chunk)
    if buffer:
        result.append(buffer)
    return result

# === 実行エントリ ===
def run_talk_command(text: str, G: nx.Graph, w2v_model, logger=None):
    log = logger.info if logger else print
    log(f"[入力]: {text}")
    terms = segment_text_by_meaning_network(text, G)
    terms = merge_hiragana_chunks(terms)
    log(f"[分割語句]: {terms}")

    unknown_terms = [t for t in terms if t not in G]
    if unknown_terms:
        known_terms = list(G.nodes)
        for unknown in unknown_terms:
            for word, score in estimate_similarity_by_unicode(unknown, known_terms, topn=5):
                if not G.has_edge(unknown, word):
                    G.add_edge(unknown, word, weight=score)
                elif score > G[unknown][word]["weight"]:
                    G[unknown][word]["weight"] = score

    expanded = expand_term_list(terms, G, w2v_model)
    for term, related in expanded.items():
        add_new_nodes_to_graph(term, related, G)

    merged = list({w for rel in expanded.values() for w in rel})
    
    merged += ["言葉", "話", "言語", "私"]
    expanded2 = expand_term_list(merged, G, w2v_model)
    for term, related in expanded2.items():
        add_new_nodes_to_graph(term, related, G)

    all_terms = list({w for rel in expanded2.values() for w in rel})
    log(f"生成語句: {all_terms}")

    scores = {term: score_term_relation(term, ["言葉", "話", "言語", "私"], G, w2v_model) for term in all_terms}
    most_important = sorted(scores.items(), key=lambda x: x[1])[0][0] if scores else "不明"
    log(f"最重要語句: {most_important}")

    filename = text.strip().replace(" ", "_")[:32]
    os.makedirs(f"./memory/{most_important}", exist_ok=True)
    with open(f"./memory/{most_important}/{filename}.txt", "w", encoding="utf-8") as f:
        f.write(f"[関連語]: {' '.join(all_terms)}\n")

    save_meaning_network(G)
    log(f"[OK] 保存完了: {filename}.txt")

def get_graph_and_model():
    return load_meaning_network("meaning_network.json"), w2v_model
