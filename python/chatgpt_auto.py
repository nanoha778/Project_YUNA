# -*- coding: utf-8 -*-
import os
import time
import json
import logging
import re
import requests
from datetime import datetime
from dotenv import load_dotenv
import openai
import main

# === .envファイル読み込み ===
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

# === OpenAI クライアント設定 ===
client = openai.OpenAI(api_key=api_key) if api_key else None

# === ログディレクトリとロガー設定 ===
os.makedirs("logs", exist_ok=True)
log_filename = datetime.now().strftime("logs/%Y%m%d.log")

logger = logging.getLogger("TalkLogger")
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

file_handler = logging.FileHandler(log_filename, encoding="utf-8")
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)
logger.propagate = False

# === 安全なテキストフィルタ ===
import unicodedata
def clean_text(text):
    return ''.join(c for c in text if unicodedata.category(c)[0] != 'C')

# === Geminiフォールバック関数 ===
def generate_talk_sentences_with_gemini(n=50):
    logger.info(f"[Gemini] フォールバックして {n} 個の文を生成依頼")
    endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    prompt = {
        "contents": [{
            "role": "user",
            "parts": [{
                "text": f"日本語で短い自然文を{n}個、すべて「/talk 文」という形式で生成してください。"
            }]
        }]
    }

    try:
        response = requests.post(
            f"{endpoint}?key={gemini_api_key}",
            json=prompt,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        content = response.json()

        candidates = content.get('candidates', [])
        if not candidates:
            logger.warning("[Gemini] 応答が空でした")
            return []

        text = candidates[0]["content"]["parts"][0]["text"]
        logger.info("[Gemini] 応答全文:\n" + clean_text(text))

        lines = text.strip().splitlines()
        talk_lines = []
        for line in lines:
            match = re.search(r"/talk\s+(.+)", line)
            if match:
                talk_lines.append(match.group(1).strip())

        logger.info(f"[Gemini] 抽出された文数: {len(talk_lines)}")
        return talk_lines

    except Exception as e:
        logger.exception(f"[Gemini] フォールバック中に失敗: {e}")
        return []

# === OpenAI + Gemini統合関数 ===
def generate_talk_sentences(n=50, logger=logger):
    if not client:
        logger.warning("[OpenAI] APIキー未設定、Geminiにフォールバックします")
        return generate_talk_sentences_with_gemini(n)

    logger.info(f"[OpenAI] に {n} 個の文を生成依頼")
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": f"日本語で短い自然文を{n}個、すべて「/talk 文」という形式で生成してください。"
            }],
            temperature=0.7
        )
        full_text = response.choices[0].message.content
        logger.info("[OpenAI] 応答全文:\n" + clean_text(full_text))

        lines = full_text.strip().splitlines()
        talk_lines = []
        for line in lines:
            match = re.search(r"/talk\s+(.+)", line)
            if match:
                talk_lines.append(match.group(1).strip())

        logger.info(f"[OpenAI] 抽出された文数: {len(talk_lines)}")
        return talk_lines

    except Exception as e:
        logger.warning(f"[OpenAI] 失敗、Geminiにフォールバックします: {e}")
        return generate_talk_sentences_with_gemini(n)

# === 意味ネットワーク読み込み ===
G = main.load_meaning_network("meaning_network.json")

# === 実行ループ ===
def main_loop():
    while True:
        try:
            sentences = generate_talk_sentences(20)
            for sentence in sentences:
                logger.info(f"[Run] /talk {sentence}")
                main.run_talk_command(sentence, G, main.w2v_model, logger=logger)
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("手動停止されました。終了します。")
            break
        except Exception as e:
            logger.exception(f"[ERR] エラー発生: {e}")
            time.sleep(5)

# === CLI実行時のみループ開始 ===
if __name__ == "__main__":
    main_loop()
