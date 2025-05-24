import os
import time
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
import openai
from main import load_meaning_network, run_talk_command

# === .envファイル読み込み ===
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)

# === ログディレクトリとロガー設定 ===
os.makedirs("logs", exist_ok=True)
log_filename = datetime.now().strftime("logs/%Y%m%d.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_filename, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TalkLogger")

# ChatGPTに自然文を生成させる関数
import re

def generate_talk_sentences(n=20):
    logger.info(f"ChatGPTに {n} 個の文章を生成依頼")
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{
            "role": "user",
            "content": f"日本語で短い自然文を{n}個、すべて「/talk 文」という形式で生成してください。"
        }],
        temperature=0.7
    )
    full_text = response.choices[0].message.content
    logger.info("ChatGPTの応答全文:\n" + full_text)

    # 柔軟に/talk文だけ抽出（番号付きや空白にも対応）
    lines = full_text.strip().splitlines()
    talk_lines = []
    for line in lines:
        match = re.search(r"/talk\s+(.+)", line)
        if match:
            talk_lines.append(match.group(1).strip())

    logger.info(f"抽出された文章数: {len(talk_lines)}")
    return talk_lines

# 意味ネットワーク読み込み
G = load_meaning_network("meaning_network.json")

while True:
    try:
        sentences = generate_talk_sentences(20)
        for sentence in sentences:
            logger.info(f"実行: /talk {sentence}")
            run_talk_command(sentence, G, logger=logger)
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("手動停止されました。処理を終了します。")
        break
    except Exception as e:
        logger.exception(f"⚠ エラー発生: {e}")
        time.sleep(5)
