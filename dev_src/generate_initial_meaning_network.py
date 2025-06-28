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
model_path = './cc.ja.300.vec'
output_file = 'assoc_network.json'
related_words_n = 50
similarity_threshold = 0.3
sleep_min, sleep_max = 1.0, 2.0

print("fastTextモデルをロード中...")
model = KeyedVectors.load_word2vec_format(model_path, binary=False)
print("fastTextモデルのロードが完了しました。")

tagger = fugashi.Tagger()

assoc_data = {}
if os.path.exists(output_file):
    with open(output_file, 'r', encoding='utf-8') as f:
        assoc_data = json.load(f)
    print(f"既存のネットワークデータ（{len(assoc_data)}語）をロードしました。")
else:
    print("新規にネットワークデータを作成します。")

headers = {
    'User-Agent': 'Mozilla/5.0 (Project YUNA bot)'
}

def is_valid_definition(text):
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
    except Exception as e:
        print(f"[WARN] {word} ページ取得時に例外発生: {e}")
        return []

def extract_keywords(text):
    words = []
    for word in tagger(text):
        surface = word.surface
        if surface in model:
            words.append(surface)
    return list(set(words))

def get_random_related_words(word, n=related_words_n, threshold=similarity_threshold):
    """
    指定単語に対してコサイン類似度がしきい値以上の単語を全抽出し
    ランダムにn件ピックアップ。関連度はコサイン値そのまま。
    """
    try:
        t0 = time.time()
        similar = [
            (other, float(model.similarity(word, other)))
            for other in model.index_to_key if other != word
        ]
        filtered = [(w, score) for w, score in similar if score >= threshold]
        t1 = time.time()
        if not filtered:
            print(f"  [INFO] '{word}': 閾値{threshold}以上の関連語は見つかりませんでした。")
            return {}
        sampled = random.sample(filtered, min(n, len(filtered)))
        print(f"  [OK] '{word}' 関連語候補:{len(filtered)}件 → サンプル:{len(sampled)}件（計算{t1-t0:.2f}s）")
        return {w: round(score, 4) for w, score in sampled}
    except KeyError:
        print(f"  [WARN] '{word}' はモデルに未登録のためスキップ")
        return {}

# --- メイン処理 ---
try:
    page_count = 0
    while True:
        page_count += 1
        print(f"\n== {page_count}ページ目 ==")
        res = requests.get("https://ja.wiktionary.org/wiki/Special:Random", headers=headers, timeout=10)
        word = res.url.rsplit('/', 1)[-1]
        print(f"[PAGE] {word} 取得中...")

        defs = get_definitions(word)
        print(f"  定義文 {len(defs)}件抽出")
        if not defs:
            continue

        for d in defs:
            keywords = extract_keywords(d)
            print(f"    意味文から抽出された単語数: {len(keywords)}")
            for keyword in keywords:
                assoc = get_random_related_words(keyword)
                if assoc:
                    assoc_data[keyword] = assoc
                    print(f"    [SAVE] '{keyword}' の関連語ネットワークを追加（全体:{len(assoc_data)}語）")

        # 都度保存
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(assoc_data, f, ensure_ascii=False, indent=2)
        print(f"[SAVE] ネットワークデータを保存（{len(assoc_data)}語）")

        time.sleep(random.uniform(sleep_min, sleep_max))

except KeyboardInterrupt:
    print("\n[STOP] 強制終了が検知されました。最終保存を実行します。")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(assoc_data, f, ensure_ascii=False, indent=2)
    print(f"[DONE] 終了時点のネットワークデータ（{len(assoc_data)}語）を保存しました。")
