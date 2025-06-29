import requests
from bs4 import BeautifulSoup
from gensim.models import KeyedVectors
import fugashi
import json
import os
import time
import random
import re

# --- 設定 ---
model_path = './cc.ja.300.vec'            # fastText日本語モデル
output_file = 'assoc_network.json'     # 保存ファイル
related_words_topn = 20
merge_factor = 1.05
sleep_min, sleep_max = 1.0, 2.0

similarity_threshold = 0.4                 # 類似度しきい値
vocab_limit = 2000                        # 類似語探索語彙の上限数

# --- JSON読み込みで失敗時リトライする関数 ---
def load_json_with_retry(filepath, retry_interval=1.0):
    while True:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            print(f"[WARN] {filepath} の読み込みに失敗しました。{retry_interval}秒後にリトライします。")
            time.sleep(retry_interval)

print("fastTextモデルをロード中...")
model = KeyedVectors.load_word2vec_format(model_path, binary=False)
print("fastTextモデルのロードが完了しました。")

tagger = fugashi.Tagger()

assoc_data = load_json_with_retry(output_file)

headers = {
    'User-Agent': 'Mozilla/5.0 (Project YUNA bot)'
}

def is_valid_definition(text):
    if len(text) < 1:
        return False
    if re.fullmatch(r'[\W\d_]+', text):
        return False
    return True

def get_definitions(word):
    url = f"https://ja.wiktionary.org/wiki/{word}"
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            return []
        soup = BeautifulSoup(res.text, 'html.parser')
        ol_tags = soup.select('ol > li')
        defs = [li.get_text() for li in ol_tags if li.get_text()]
        return [d for d in defs if is_valid_definition(d)]
    except Exception:
        return []

def extract_keywords(text):
    words = []
    for word in tagger(text):
        surface = word.surface
        if surface in model:
            words.append(surface)
    return list(set(words))

def get_related_words(word, topn=related_words_topn):
    try:
        limited_keys = model.index_to_key[:vocab_limit]
        similar = [
            (other, float(model.similarity(word, other)))
            for other in limited_keys if other != word
        ]
        filtered = [(w, score) for w, score in similar if score >= similarity_threshold]
        if not filtered:
            return {}
        sampled = random.sample(filtered, min(topn, len(filtered)))
        return {w: round(score, 4) for w, score in sampled}
    except KeyError:
        return {}

def merge_related_words(old, new):
    merged = old.copy()
    for k, v in new.items():
        # ただ単に値を新しいもので上書きするだけ
        merged[k] = v
    return merged


try:
    while True:
        res = requests.get("https://ja.wiktionary.org/wiki/Special:Random", headers=headers, timeout=10)
        word = res.url.rsplit('/', 1)[-1]

        defs = get_definitions(word)
        if not defs:
            continue

        for d in defs:
            for keyword in extract_keywords(d):
                assoc = get_related_words(keyword)
                if not assoc:
                    continue
                if keyword in assoc_data:
                    assoc_data[keyword] = merge_related_words(assoc_data[keyword], assoc)
                else:
                    assoc_data[keyword] = assoc

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(assoc_data, f, ensure_ascii=False, indent=2)

        time.sleep(random.uniform(sleep_min, sleep_max))

except KeyboardInterrupt:
    print("強制終了されました。最終結果を保存します。")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(assoc_data, f, ensure_ascii=False, indent=2)
