import json
from gensim.models import KeyedVectors

# --- 設定 ---
meaning_network_path = "meaning_network.json"
output_path = "meaning_network_updated.json"
w2v_model_path = "cc.ja.300.vec"   # fastText日本語Wikipediaモデル

# --- モデル読み込み ---
print("🟡 Word2Vecモデル（cc.ja.300.vec）を読み込み中……")
model = KeyedVectors.load_word2vec_format(w2v_model_path, binary=False)
print("✅ モデル読み込み完了！")

# --- ネットワーク読み込み ---
print(f"🟡 ネットワーク「{meaning_network_path}」を読み込み中……")
with open(meaning_network_path, "r", encoding="utf-8") as f:
    net = json.load(f)
print("✅ ネットワーク読み込み完了！")

total_pairs = 0
updated_pairs = 0
not_found_pairs = 0

# --- 関連度を上書きしていくよ！ ---
for word, rels in net.items():
    for rel_word in rels.keys():
        total_pairs += 1
        if word in model and rel_word in model:
            sim = float(model.similarity(word, rel_word))
            net[word][rel_word] = sim
            updated_pairs += 1
            # 1000件ごとに進捗表示
            if updated_pairs % 1000 == 0:
                print(f"  {updated_pairs}件目: {word} ↔ {rel_word} → 類似度 {sim:.4f}")
        else:
            net[word][rel_word] = None
            not_found_pairs += 1
            print(f"  ⚠️ 見つからない単語: {word} または {rel_word}")

print("✅ 類似度上書き処理終了！")
print(f"  ▶️ 類似度上書き済み: {updated_pairs}ペア")
print(f"  ⚠️ 単語未検出: {not_found_pairs}ペア（合計 {total_pairs}ペア中）")

# --- 保存 ---
print(f"🟡 保存中……({output_path})")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(net, f, ensure_ascii=False, indent=2)
print("✅ 完了！新しいネットワークを書き出したよ 🎉")
