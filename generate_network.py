from gensim.models import KeyedVectors
import json
from tqdm import tqdm

model = KeyedVectors.load_word2vec_format("model.vec", binary=False)

with open("vocabulary.txt", "r", encoding="utf-8") as f:
    words = [line.strip() for line in f if line.strip()]

def get_related_words(word, topn=200):
    try:
        results = model.most_similar(positive=[word], topn=topn)
        return {w: float(sim) for w, sim in results}
    except KeyError:
        return {}

meaning_network = {}
for word in tqdm(words, desc="Generating network"):
    meaning_network[word] = get_related_words(word)

with open("meaning_network.json", "w", encoding="utf-8") as f:
    json.dump(meaning_network, f, ensure_ascii=False, indent=2)

print("✅ meaning_network.json saved")
