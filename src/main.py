import os
import json
from thinking_cell import ForwardCell, BackwardCell
from utils.io_utils import input_command
from modules.thinking import ThinkingModule

def load_meaning_network():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    network_path = os.path.join(base_dir, "knowledge", "meaning_network.json")
    with open(network_path, encoding="utf-8") as f:
        return json.load(f)

def main():
    meaning_network = load_meaning_network()
    forward_cell = ForwardCell(meaning_network)
    backward_cell = BackwardCell(meaning_network)
    thinker = ThinkingModule(meaning_network)

    while True:
        params = input_command()
        cmd = params["command"]

        if cmd == "/forward":
            input_word = params["input_word"]
            depth = params["depth"]
            threshold = params["threshold"]
            topn = params["topn"]

            layers = forward_cell.get_multi_layer_connections(input_word, depth=depth, threshold=threshold, topn=topn)

            print(f"\n/forward コマンド結果（{depth}層まで）:")
            for i, layer in enumerate(layers, 1):
                print(f"Layer {i}:")
                for w, weight in layer:
                    print(f"  {w} (重み={weight})")

        elif cmd == "/backward":
            input_words = params["input_words"]
            threshold = params["threshold"]

            results = backward_cell.backward(input_words, threshold=threshold)

            print(f"\n/backward コマンド評価結果（閾値={threshold}）:")
            for word, score in results:
                print(f"  {word}: {score:.3f}")

        elif cmd == "/learning":
            print("学習コマンドが選択されました。")
            print(params)
            # 実装したい学習処理をここに入れてね

        elif cmd == "/talk":
            message = params["message"]
            print(f"あなた: {message}")
            print("YUNA: ごめんね、今はまだおしゃべり機能未実装です！")

        elif cmd == "/think":
            input_word = params["input_word"]
            n = params["n"]
            threshold = params["threshold"]
            topn = params["topn"]
            backward_threshold = params["backward_threshold"]

            res = thinker.forward_then_sort_then_backward(
                input_word=input_word,
                n=n,
                threshold=threshold,
                topn=topn,
                backward_threshold=backward_threshold,
            )

            print(f"\n/think コマンド実行結果:")
            print("並べ替え語句リスト:")
            print(res["sorted_words"])
            print("\n逆順セル評価結果:")
            for w, s in res["backward_results"]:
                print(f"  {w}: {s:.3f}")

if __name__ == "__main__":
    main()
