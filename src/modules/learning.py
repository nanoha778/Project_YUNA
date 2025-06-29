# src/modules/learning.py

from collections import Counter, deque

class LearningModule:
    def __init__(self, meaning_network, forward_cell):
        self.meaning_network = meaning_network
        self.forward_cell = forward_cell

    def propagate_and_learn(
        self,
        input_word,
        repeat=10,        # 伝播の反復回数
        num_iter=100,     # 1回の反復でのサンプリング回数
        depth=2,          # 伝播の深さ
        topn=5,           # 1回で取る関連語の最大数
        threshold=0.1,    # 閾値
        learning_rate=0.01 # 重み更新率
    ):
        """
        正順セルを使って伝播しつつ語の出現頻度をカウント、
        出現頻度に基づいて重みを更新する簡単な学習スクリプト
        """
        for r in range(repeat):
            counter = Counter()
            for _ in range(num_iter):
                queue = deque()
                queue.append((input_word, 0))
                visited = set()
                while queue:
                    word, d = queue.popleft()
                    if d >= depth:
                        continue
                    results = self.forward_cell.get_direct_connections(word, threshold=threshold)
                    results = sorted(results, key=lambda x: -x[1])[:topn]
                    for next_word, weight in results:
                        if (next_word, d + 1) not in visited:
                            counter[next_word] += 1
                            queue.append((next_word, d + 1))
                            visited.add((next_word, d + 1))
            # 出現頻度に応じて重みを学習率で加算
            total = sum(counter.values())
            conn_dict = self.meaning_network.get(input_word, {}).copy()
            for word, count in counter.items():
                freq = count / total if total else 0
                old_weight = conn_dict.get(word, 0.0)
                new_weight = min(1.0, old_weight + freq * learning_rate)
                conn_dict[word] = new_weight
            self.meaning_network[input_word] = conn_dict
