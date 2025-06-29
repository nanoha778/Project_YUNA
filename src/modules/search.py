# src/modules/search.py


class SearchModule:
    def __init__(self, meaning_network):
        self.meaning_network = meaning_network

    def adjacent_score(self, words):
        score = 0.0
        for i in range(len(words) - 1):
            w1, w2 = words[i], words[i + 1]
            score += self.meaning_network.get(w1, {}).get(w2, 0.0)
        return score

    def maximize_adjacent_similarity(self, words):
        if not words:
            return []

        unvisited = set(words)
        current = words[0]
        order = [current]
        unvisited.remove(current)

        while unvisited:
            next_word = max(unvisited, key=lambda w: self.meaning_network.get(current, {}).get(w, 0.0))
            order.append(next_word)
            unvisited.remove(next_word)
            current = next_word

        return order

    def cut_by_thresholds(self, words, lower_threshold, upper_threshold):
        if not words:
            return []

        for i in range(len(words) - 1):
            w1, w2 = words[i], words[i + 1]
            score = self.meaning_network.get(w1, {}).get(w2, 0.0)
            if score < lower_threshold or score > upper_threshold:
                return words[:i+1]

        return words
