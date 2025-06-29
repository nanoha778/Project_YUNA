# src/thinking_cell.py

class ForwardCell:
    def __init__(self, meaning_network):
        self.meaning_network = meaning_network

    def get_multi_layer_connections(self, input_word, depth=3, threshold=0.5, topn=None):
        """
        1. depth回関連語をたどる（これまでの多層取得）
        2. 出てきた語すべてに対し「入力語との関連度」を計算して閾値でフィルタ
        3. フィルタ後の語について関連語を取得して返す
        """
        layers = []
        visited = set([input_word])
        current_layer = [input_word]

        all_found_words = set()

        for d in range(depth):
            next_layer = []
            layer_result = []
            for word in current_layer:
                connections = self.meaning_network.get(word, {})
                conn_list = [(w, float(weight)) for w, weight in connections.items()]
                # フィルタはここではまだしない
                for w, weight in conn_list:
                    if w not in visited:
                        layer_result.append((w, weight))
                        next_layer.append(w)
                        visited.add(w)
                        all_found_words.add(w)
            layers.append(layer_result)
            current_layer = next_layer

        # 入力語との関連度でフィルタ
        filtered_words = []
        for w in all_found_words:
            relatedness = self.meaning_network.get(input_word, {}).get(w, 0.0)
            if relatedness >= threshold:
                filtered_words.append(w)

        # フィルタ後の語それぞれについて関連語を取得（topn制限あり）
        final_results = {}
        for w in filtered_words:
            connections = self.meaning_network.get(w, {})
            conn_list = [(cw, float(weight)) for cw, weight in connections.items()]
            if topn is not None:
                conn_list = sorted(conn_list, key=lambda x: -x[1])[:topn]
            final_results[w] = conn_list

        return final_results
    def get_direct_connections(self, word, threshold=None):
        connections = self.meaning_network.get(word, {})
        conn_list = [(w, float(weight)) for w, weight in connections.items()]
        if threshold is not None:
            conn_list = [c for c in conn_list if c[1] >= threshold]
        return conn_list


from collections import defaultdict

class BackwardCell:
    def __init__(self, meaning_network):
        self.meaning_network = meaning_network

    def backward(self, input_words, threshold=0.0):
        score_dict = defaultdict(float)
        count_dict = defaultdict(int)

        for word in input_words:
            connections = self.meaning_network.get(word, {})
            for related_word, weight in connections.items():
                score_dict[related_word] += float(weight)
                count_dict[related_word] += 1

        final_scores = {}
        for word in score_dict:
            avg_score = score_dict[word] / count_dict[word]
            if avg_score >= threshold:
                final_scores[word] = avg_score

        return sorted(final_scores.items(), key=lambda x: -x[1])
