# app.py - LINE Bot 記帳 (Railway + PostgreSQL 版)
import os, logging
from flask import Flask, request, abort
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from db import get_conn, init_db

load_dotenv()
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET","")
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN","")
PORT = int(os.getenv("PORT","5000"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("linebot-pg")

app = Flask(__name__)
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

def add_record(user_id, category, amount, note):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO records (user_id, category, amount, note) VALUES (%s,%s,%s,%s)",
                (user_id, category, amount, note))
    conn.commit()
    cur.close()
    conn.close()

def list_records(user_id, limit=10):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, category, amount, note, created_at FROM records WHERE user_id=%s ORDER BY id DESC LIMIT %s",
                (user_id, limit))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature","")
    body = request.get_data(as_text=True)
    logger.info("Received body: %s", body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id or "anonymous"
    text = event.message.text.strip()
    parts = text.split()
    reply = "請輸入 help 查看指令。"

    try:
        if not parts:
            reply = "請輸入指令（help 查看說明）"
        elif parts[0].lower() in ["記帳","add"]:
            if len(parts)<3:
                reply = "格式：記帳 類別 金額 [備註]"
            else:
                category = parts[1]
                amount = float(parts[2])
                note = " ".join(parts[3:]) if len(parts)>3 else ""
                add_record(user_id, category, amount, note)
                reply = f"✅ 已記帳：{category} {amount} {note}"
        elif parts[0].lower() in ["list","查詢"]:
            n = int(parts[1]) if len(parts)>1 else 10
            rows = list_records(user_id, n)
            if not rows:
                reply = "目前沒有紀錄。"
            else:
                lines = [f"{r[0]}. {r[1]} {r[2]} {r[3]} ({r[4]})" for r in rows]
                reply = "\n".join(lines)
        elif parts[0].lower() in ["help","說明"]:
            reply = ("指令：\n"
                     "記帳 類別 金額 [備註]\n"
                     "list [n]\n"
                     "help")
    except Exception as e:
        logger.exception("Error handling message")
        reply = f"⚠️ 發生錯誤：{e}"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=PORT)
