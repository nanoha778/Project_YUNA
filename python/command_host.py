# -*- coding: utf-8 -*-
import importlib
import time
import os
import traceback
import logging
from gensim.models import KeyedVectors
import main  # main.py の処理を使う
import chatgpt_auto

import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


# === ロガー設定（安全・UTF-8対応） ===
logger = logging.getLogger("TalkLogger")
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

logger.propagate = False

logger.info("main.py を再読み込みします")

# === 初期モデル読み込み ===
G, w2v_model = main.get_graph_and_model()
last_main_mtime = 0.0

w2v_model_path = "model.vec"
w2v_model_mtime = 0.0

def reload_main_if_changed():
    global main, last_main_mtime, G, w2v_model
    try:
        current_mtime = os.path.getmtime("main.py")
        if current_mtime > last_main_mtime:
            logger.info("main.py に変更を検知、再読み込みを試みます...")
            try:
                main = importlib.reload(main)
                G, w2v_model = main.get_graph_and_model()
                last_main_mtime = current_mtime
                logger.info("main.py を正常に再読み込みしました。")
            except Exception:
                logger.warning("main.py に構文エラーがあります。修正されるまで待機中...")
                traceback.print_exc()
    except FileNotFoundError:
        logger.warning("main.py が見つかりません。")

def load_w2v_model_if_updated():
    global w2v_model, w2v_model_mtime
    try:
        current_mtime = os.path.getmtime(w2v_model_path)
        if w2v_model is None or current_mtime > w2v_model_mtime:
            logger.info(f"[W2V] モデルを再読み込み中: {w2v_model_path}")
            w2v_model = KeyedVectors.load_word2vec_format(w2v_model_path, binary=False)
            w2v_model_mtime = current_mtime
            logger.info("[W2V] モデルの再読み込み完了")
    except Exception as e:
        logger.warning(f"[W2V] モデルの読み込みに失敗しました: {e}")

# === メインループ ===
while True:
    reload_main_if_changed()
    logger.info("コマンド (/talk テキスト or /once or /exit):")
    try:
        cmd = sys.stdin.readline()
        if not cmd:
            break

        cmd = cmd.strip()
        if cmd.startswith("/talk "):
            text = cmd.split(" ", 1)[1]
            main.run_talk_command(text, G, w2v_model, logger=logger)

        elif cmd == "/exit":
            logger.info("終了します。")
            break

        elif cmd == "/once":
            reload_main_if_changed()
            sentences = chatgpt_auto.generate_talk_sentences(1, logger=logger)
            for sentence in sentences:
                logger.info(f"[AUTO] /talk {sentence}")
                load_w2v_model_if_updated()
                main.run_talk_command(sentence, G, w2v_model, logger=logger)

        time.sleep(0.3)

    except Exception as e:
        logger.error(f"[ERR] 入力処理中にエラー: {e}")
