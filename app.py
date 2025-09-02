# app.py - LINE 記帳 Bot (SQLite 改良版)
import os, sqlite3, logging
from datetime import datetime, date
from flask import Flask, request, abort
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 載入環境變數
load_dotenv()
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET","")
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN","")
DB_PATH = os.getenv("DB_PATH","bookkeeping.db")
PORT = int(os.getenv("PORT","5000"))

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("linebook")

# Flask + LINE
app = Flask(__name__)
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# 初始化 DB
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            record_date TEXT,
            item TEXT,
            category TEXT,
            amount REAL,
            note TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_record(user_id, item, category, amount, note=""):
    today = date.today().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO records (user_id, record_date, item, category, amount, note, created_at) VALUES (?,?,?,?,?,?,?)',
              (user_id, today, item, category, amount, note, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def query_records(user_id, mode="recent", value=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    sql = "SELECT record_date, item, category, amount, note FROM records WHERE user_id=?"
    params = [user_id]

    today = date.today()
    if mode == "date":  # 指定日期 (MMDD)
        year = today.year
        query_date = f"{year}-{value[:2]}-{value[2:]}"  # 例如 "2025-09-02"
        sql += " AND record_date=?"
        params.append(query_date)
    elif mode == "today":
        sql += " AND record_date=?"
        params.append(today.strftime("%Y-%m-%d"))
    elif mode == "month":
        sql += " AND strftime('%Y-%m', record_date)=?"
        params.append(today.strftime("%Y-%m"))
    sql += " ORDER BY id DESC"

    if mode == "recent":
        sql += " LIMIT 10"

    c.execute(sql, tuple(params))
    rows = c.fetchall()
    conn.close()
    return rows

def export_csv(user_id):
    out_path = "records.csv"
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT record_date, item, category, amount, note FROM records WHERE user_id=? ORDER BY id", (user_id,))
    rows = c.fetchall()
    conn.close()
    import csv
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date","item","category","amount","note"])
        writer.writerows(rows)
    return out_path

# LINE webhook
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
    reply = "⚠️ 指令錯誤，請輸入正確格式。"

    try:
        parts = text.split()
        # 記帳：品項 種類 價格 [備註]
        if len(parts) >= 3 and parts[1].isdigit() == False:  
            item = parts[0]
            category = parts[1]
            amount = float(parts[2])
            note = " ".join(parts[3:]) if len(parts)>3 else ""
            add_record(user_id, item, category, amount, note)
            reply = f"✅ 已記帳：{item} {category} {amount} {note}"
        elif text in ["清單"]:
            rows = query_records(user_id, "recent")
            reply = "\n".join([f"{r[0]} {r[1]} {r[2]} {r[3]} {r[4]}" for r in rows]) or "沒有紀錄"
        elif text.isdigit() and len(text)==4:  # ex: 0902
            rows = query_records(user_id, "date", text)
            reply = "\n".join([f"{r[0]} {r[1]} {r[2]} {r[3]} {r[4]}" for r in rows]) or f"{text} 沒有紀錄"
        elif text in ["今日"]:
            rows = query_records(user_id, "today")
            reply = "\n".join([f"{r[0]} {r[1]} {r[2]} {r[3]} {r[4]}" for r in rows]) or "今天沒有紀錄"
        elif text in ["本月"]:
            rows = query_records(user_id, "month")
            reply = "\n".join([f"{r[0]} {r[1]} {r[2]} {r[3]} {r[4]}" for r in rows]) or "本月沒有紀錄"
        elif text in ["儲存"]:
            path = export_csv(user_id)
            reply = f"📊 已輸出最新紀錄到 {path}"
    except Exception as e:
        logger.exception("Error")
        reply = f"⚠️ 發生錯誤：{e}"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=PORT, debug=True)

