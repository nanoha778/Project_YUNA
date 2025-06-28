import os
import time
import random
import json
from gensim.models import KeyedVectors
import fugashi
import re

# dotenvで.envからAPIキーを読み込む
from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai

# --- 設定 ---
model_path = './cc.ja.300.vec'
output_file = 'assoc_network.json'
related_words_n = 50
similarity_threshold = 0.3
sleep_min, sleep_max = 1.0, 2.0

# .envからAPIキー読み込み
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise Exception("Gemini APIキーが設定されていません。プロジェクトディレクトリに .env ファイルを作成し GEMINI_API_KEY=... の形でAPIキーを記述してください。")

# --- Gemini初期化 ---
genai.configure(api_key=gemini_api_key)
gemini = genai.GenerativeModel("gemini-1.5-flash")

print("fastTextモデルをロード中...")
model = KeyedVectors.load_word2vec_format(model_path, binary=False)
print("fastTextモデルのロードが完了しました。")

tagger = fugashi.Tagger()

assoc_data = {}
if os.path.exists(output_file):
    with open(output_file, 'r', encoding='utf-8') as f:
        assoc_data = json.load(f)
    print(f"既存ネットワークデータ（{len(assoc_data)}語）をロードしました。")
else:
    print("新規にネットワークデータを作成します。")

def extract_keywords(text):
    words = []
    for word in tagger(text):
        surface = word.surface
        if surface in model:
            words.append(surface)
    return list(set(words))

def get_random_related_words(word, n=related_words_n, threshold=similarity_threshold):
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

try:
    text_count = 0
    while True:
        text_count += 1
        print(f"\n== Gemini生成 {text_count} 回目 ==")

        prompt = "日本語で日常的なシーンの長文を400字以上生成してください。"
        print("[Gemini] 長文生成中...")
        t0 = time.time()
        response = gemini.generate_content(prompt)
        t1 = time.time()
        generated_text = response.text.strip()
        print(f"[Gemini] 生成テキスト（{len(generated_text)}文字, {t1-t0:.2f}s）：\n{generated_text[:60]}...")

        keywords = extract_keywords(generated_text)
        print(f"  形態素解析で抽出された単語数: {len(keywords)}")

        for keyword in keywords:
            assoc = get_random_related_words(keyword)
            if assoc:
                assoc_data[keyword] = assoc
                print(f"    [SAVE] '{keyword}' の関連語ネットワークを追加（全体:{len(assoc_data)}語）")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(assoc_data, f, ensure_ascii=False, indent=2)
        print(f"[SAVE] ネットワークデータを保存（{len(assoc_data)}語）")

        time.sleep(random.uniform(sleep_min, sleep_max))

except KeyboardInterrupt:
    print("\n[STOP] 強制終了が検知されました。最終保存を実行します。")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(assoc_data, f, ensure_ascii=False, indent=2)
    print(f"[DONE] 終了時点のネットワークデータ（{len(assoc_data)}語）を保存しました。")
