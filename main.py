import json
import networkx as nx
from itertools import product
import random




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


from gensim.models import KeyedVectors

# Word2Vecモデルの読み込み（グローバルに1度）
w2v_model = KeyedVectors.load_word2vec_format("model.vec", binary=False)

# 関連語を5語だけ取得
def get_related_words_from_w2v(word, topn=5):
    try:
        results = w2v_model.most_similar(positive=[word], topn=topn)
        return {w: float(sim) for w, sim in results}
    except KeyError:
        return {}


# === 分割関数 ===
def segment_text_by_meaning_network(
    text: str,
    graph: nx.Graph,
    n_min: int = 1,
    n_max: int = 6,
    related_threshold: float = 0.45,
    similarity_threshold: float = 0.6
) -> list[str]:
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
    break_scores = []
    for i in range(max_len - 1):
        similarities = []
        for matrix in all_matrices:
            if i < len(matrix) - 1:
                a, b = matrix[i], matrix[i+1]
                if a and b:
                    inter = a & b
                    union = a | b
                    sim = len(inter) / len(union) if union else 0.0
                    similarities.append(sim)
        break_score = 1.0 - (sum(similarities) / len(similarities)) if similarities else 1.0
        break_scores.append(break_score)

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

def random_chain_evaluation(graph, start_terms, steps=20, related_threshold=0.35):
    result = {}

    for start in start_terms:
        if start not in graph:
            continue

        valid_ends = []

        try:
            neighbors1 = list(graph.neighbors(start))
        except:
            continue  # 無効な語

        for neighbor in neighbors1:
            current = neighbor
            for _ in range(steps):
                try:
                    next_neighbors = list(graph.neighbors(current))
                    if not next_neighbors:
                        break
                    current = random.choice(next_neighbors)
                except:
                    break

            # 最後の current が start につながっていれば重み評価
            if graph.has_edge(start, current):
                weight = graph[start][current].get("weight", 0)
                if weight >= related_threshold:
                    valid_ends.append((current, round(weight, 3)))
                if not graph.has_edge(start, current):
                    graph.add_edge(start, current, weight=weight)
                elif weight > graph[start][current]["weight"]:
                    graph[start][current]["weight"] = weight

        result[start] = valid_ends

    return result


def estimate_similarity_by_unicode(unknown_term, known_terms, topn=5):
    def char_distance(c1, c2):
        return abs(ord(c1) - ord(c2))

    def term_distance(t1, t2):
        min_len = min(len(t1), len(t2))
        distances = [char_distance(t1[i], t2[i]) for i in range(min_len)]
        return sum(distances) / len(distances)

    similarity_scores = []
    for known in known_terms:
        dist = term_distance(unknown_term, known)
        similarity = 1 / (1 + dist)  # 距離を類似度に変換
        similarity_scores.append((known, similarity))

    # 類似度の高い順に並べる
    similarity_scores.sort(key=lambda x: x[1], reverse=True)
    return similarity_scores[:topn]


# === 関連語展開（1段階） ===
def expand_terms(terms: list[str], graph: nx.Graph, related_threshold: float = 0.35) -> dict:
    result = {}
    for term in terms:
        related = {
            neighbor: graph[term][neighbor]['weight']
            for neighbor in graph.neighbors(term)
            if graph[term][neighbor]['weight'] > related_threshold
        } if term in graph else {}
        result[term] = related
    return result


def run_talk_command(text: str, G: nx.Graph, logger=None):
    log = logger.info if logger else print  # ✅ 修正
    log(f"[入力]: {text}")
    terms = segment_text_by_meaning_network(text, G)
    log(f"[分割語句]: {terms}")

    unknown_terms = [term for term in terms if term not in G]
    if unknown_terms:
        log("[未知語が検出されました → Unicode類似度で類似語推定]")
        known_terms = list(G.nodes)
        for unknown in unknown_terms:
            similar = estimate_similarity_by_unicode(unknown, known_terms, topn=5)
            log(f"  {unknown} → {[f'{w}({round(s, 3)})' for w, s in similar]}")
            for word, score in similar:
                if not G.has_edge(unknown, word):
                    G.add_edge(unknown, word, weight=score)
                elif score > G[unknown][word]["weight"]:
                    G[unknown][word]["weight"] = score
    else:
        log("[未知語はありません]")

    related = expand_terms(terms, G)
    log("[関連語句（しきい値 > 0.35）]:")
    for term, rels in related.items():
        log(f"  {term}: {list(rels.keys())[:10]} ...")

    w2v_expanded_terms = set(terms)
    for term in terms:
        related_words = get_related_words_from_w2v(term, topn=5)
        w2v_expanded_terms.update(related_words.keys())

    log(f"Word2Vec補強後語句: {list(w2v_expanded_terms)}")
    chain_result1 = random_chain_evaluation(G, terms, steps=20, related_threshold=0.35)
    log("[第1フェーズ：意味連鎖（20ステップ → 起点語との関連度 >= 0.35）]:")
    first_level_words = set()
    for term, valid in chain_result1.items():
        if valid:
            log(f"  {term}: {[f'{w}({s})' for w, s in valid]}")
            first_level_words.update(w for w, _ in valid)
        else:
            log(f"  {term}: (なし)")

    second_chain_input = list(first_level_words | {"言葉", "言語"})
    chain_result2 = random_chain_evaluation(G, second_chain_input, steps=20, related_threshold=0.35)
    log("[第2フェーズ：意味連鎖（20ステップ → 起点語との関連度 >= 0.35）]:")
    for term, valid in chain_result2.items():
        if valid:
            log(f"  {term}: {[f'{w}({s})' for w, s in valid]}")
        else:
            log(f"  {term}: (なし)")

    log("[最終フェーズ：意味ネットワークで強く関連する語を抽出]")
    meaningful_words = set()
    for start_term, connections in chain_result2.items():
        for word, score in connections:
            if score >= 0.495:
                meaningful_words.add(word)
                if not G.has_edge(start_term, word):
                    G.add_edge(start_term, word, weight=score)
                elif G[start_term][word]["weight"] < score:
                    G[start_term][word]["weight"] = score

    if meaningful_words:
        log("意味ネットワーク上で強く関連する語（マージ後）:")
        log(list(meaningful_words))
    else:
        log("意味ネットワーク上で強く関連する語は見つかりませんでした。")

    # JSON保存
    save_data = {}
    for src, tgt, attrs in G.edges(data=True):
        save_data.setdefault(src, {})
        save_data[src][tgt] = round(attrs.get("weight", 0.0), 6)

    with open("meaning_network.json", "w", encoding="utf-8") as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)

    log("[✔] meaning_network.json に関連度を上書き保存しました。")


# === メイン待機ループ ===
if __name__ == "__main__":
    G = load_meaning_network("meaning_network.json")
    print("コマンドを入力してください：")
    print("  /talk テキスト")
    print("  /looptest テキスト 範囲 密度")
    print("  /exit")

    while True:
        try:
            cmd = input("> ").strip()

            if cmd == "/exit":
                print("終了します。")
                break

            elif cmd.startswith("/talk "):
                parts = cmd.split(maxsplit=1)
                if len(parts) < 2:
                    print("⚠️ /talk の後にテキストを入力してください。")
                    continue
                _, text = parts
                run_talk_command(text, G)



            elif cmd.startswith("/looptest "):
                parts = cmd.split(maxsplit=4)
                if len(parts) != 4:
                    print("形式: /looptest <テキスト> <範囲開始> <密度>")
                    continue
                _, text_input, base_str, step_str = parts
                base = float(base_str)
                step = float(step_str)
                values = [round(base + i * step, 3) for i in range(int((1.0 - base) / step) + 1)]

                for rel_th, sim_th in product(values, values):
                    result = segment_text_by_meaning_network(
                        text=text_input,
                        graph=G,
                        related_threshold=rel_th,
                        similarity_threshold=sim_th
                    )
                    print(f"[related={rel_th:.3f}, similarity={sim_th:.3f}] → {result}")
                print("ループテスト完了。")

        except Exception as e:
            print(f"エラー: {e}")
