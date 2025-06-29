# src/modules/thinking.py

from thinking_cell import ForwardCell, BackwardCell
from modules.search import SearchModule

class ThinkingModule:
    def __init__(self, meaning_network):
        self.meaning_network = meaning_network
        self.forward_cell = ForwardCell(meaning_network)
        self.backward_cell = BackwardCell(meaning_network)
        self.searcher = SearchModule(meaning_network)

    def forward_think_n(self, input_word, n=3, threshold=0.5, topn=5):
        """
        正順セルに入力語を入れて関連語取得、
        返ってきた語群を一つずつ正順セルに入れて関連語取得を繰り返す（n回）
        
        :return: 最終的に得た関連語辞書 {語: [(関連語, 重み), ...], ...}
        """
        current_words = [input_word]
        accumulated_results = {}

        for _ in range(n):
            new_results = {}
            for word in current_words:
                related = self.forward_cell.get_direct_connections(word, threshold=threshold)
                if topn is not None:
                    related = sorted(related, key=lambda x: -x[1])[:topn]
                new_results[word] = related

            # 次回ループ用語群を集める
            current_words = []
            for rel_list in new_results.values():
                current_words.extend([w for w, _ in rel_list])

            # 結果を累積マージ
            accumulated_results.update(new_results)

            # もしもう関連語が得られなかったら終了
            if not current_words:
                break

        return accumulated_results

    def forward_then_sort_then_backward(self, input_word, n=5, threshold=0.45, topn=100, backward_threshold=0.7):
        """
        1. forward_think_nでn回繰り返し正順セルを回す
        2. 返ってきた語句群をまとめて並べ替え
        3. 並べ替え結果を逆順セルに渡して評価
        """
        # 1. forward_think_nを呼んで関連語辞書を取得
        forward_results = self.forward_think_n(input_word, n=n, threshold=threshold, topn=topn)

        # 2. forward_resultsの語をまとめる（キーと関連語の両方）
        words_set = set()
        for w, related_list in forward_results.items():
            words_set.add(w)
            for rw, _ in related_list:
                words_set.add(rw)
        words = list(words_set)

        # 3. searchモジュールで並べ替え
        sorted_words = self.searcher.maximize_adjacent_similarity(words)


        # 4. 逆順セルで評価
        backward_results = self.backward_cell.backward(sorted_words, threshold=backward_threshold)

        return {
            "sorted_words": sorted_words,
            "backward_results": backward_results,
        }
