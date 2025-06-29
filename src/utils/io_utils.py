# src/utils/io_utils.py

def input_with_default(prompt, default, cast_func=str):
    """
    入力を促し、空入力ならdefaultを返す。型変換はcast_funcで。
    """
    val = input(prompt).strip()
    if val == '':
        return default
    try:
        return cast_func(val)
    except Exception:
        print(f"無効な入力です。デフォルト値 {default} を使用します。")
        return default

def input_command():
    print("=== Project YUNA コマンド入力 ===")
    valid_commands = ["/forward", "/backward", "/learning", "/talk", "/think"]

    while True:
        cmd = input("コマンドを入力してください（/forward, /backward, /learning, /talk, /think）: ").strip().lower()
        if cmd in valid_commands:
            break
        print("無効なコマンドです。もう一度入力してください。")

    params = {"command": cmd}

    if cmd == "/forward":
        params["input_word"] = input_with_default("正順セルの入力語を指定してください（例：猫）: ", "猫")
        params["depth"] = input_with_default("探索深さを指定してください（例：3）: ", 3, int)
        params["threshold"] = input_with_default("閾値を指定してください（例：0.5）: ", 0.5, float)
        params["topn"] = input_with_default("取得件数上限を指定してください（例：5）: ", 5, int)

    elif cmd == "/backward":
        words_str = input("逆順セルに渡す語群をスペース区切りで入力してください: ").strip()
        params["input_words"] = words_str.split() if words_str else []
        params["threshold"] = input_with_default("閾値を指定してください（例：0.3）: ", 0.3, float)

    elif cmd == "/learning":
        params["input_word"] = input_with_default("学習対象の入力語を指定してください（例：猫）: ", "猫")
        params["repeat"] = input_with_default("学習繰り返し回数を指定してください（例：10）: ", 10, int)
        params["num_iter"] = input_with_default("1回のサンプリング回数を指定してください（例：100）: ", 100, int)
        params["depth"] = input_with_default("探索深さを指定してください（例：2）: ", 2, int)
        params["topn"] = input_with_default("取得件数上限を指定してください（例：5）: ", 5, int)
        params["threshold"] = input_with_default("閾値を指定してください（例：0.1）: ", 0.1, float)
        params["learning_rate"] = input_with_default("学習率を指定してください（例：0.01）: ", 0.01, float)

    elif cmd == "/talk":
        params["message"] = input("話しかけてください: ").strip()

    elif cmd == "/think":
        params["input_word"] = input_with_default("入力語を指定してください（例：猫）: ", "猫")
        params["n"] = input_with_default("思考繰り返し回数(n)を指定してください（例：3）: ", 3, int)
        params["threshold"] = input_with_default("正順セルの閾値を指定してください（例：0.5）: ", 0.5, float)
        params["topn"] = input_with_default("正順セル取得件数上限(topn)を指定してください（例：5）: ", 5, int)
        params["backward_threshold"] = input_with_default("逆順セルの閾値を指定してください（例：0.3）: ", 0.3, float)

    return params
