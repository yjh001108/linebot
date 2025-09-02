# app.py - LINE 記帳 Bot (SQLite 改良＋DB migration＋CSV 覆蓋輸出)
import os, sqlite3, logging, csv, re
from datetime import datetime, date
from flask import Flask, request, abort
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# load env
load_dotenv()
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET","")
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN","")
DB_PATH = os.getenv("DB_PATH","bookkeeping.db")
PORT = int(os.getenv("PORT","5000"))

# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("linebook")

app = Flask(__name__)
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN) if CHANNEL_ACCESS_TOKEN else None
handler = WebhookHandler(CHANNEL_SECRET) if CHANNEL_SECRET else None

# -------------------------
# Database helpers & migration
# -------------------------
def table_exists(conn, name):
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
    return c.fetchone() is not None

def get_columns(conn, table):
    c = conn.cursor()
    c.execute(f"PRAGMA table_info({table})")
    return [row[1] for row in c.fetchall()]

def init_db():
    """Create table if not exists. Also perform migration for missing column(s)."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if not table_exists(conn, "records"):
        logger.info("Creating new 'records' table.")
        c.execute('''
            CREATE TABLE records (
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
    else:
        cols = get_columns(conn, "records")
        logger.info("Existing columns: %s", cols)
        # If record_date column missing, add it and populate from created_at if possible
        if "record_date" not in cols:
            logger.info("'record_date' column missing. Adding column and migrating values.")
            c.execute("ALTER TABLE records ADD COLUMN record_date TEXT")
            # If created_at exists, use its date portion, else use today's date
            if "created_at" in cols:
                c.execute("UPDATE records SET record_date = substr(created_at,1,10) WHERE record_date IS NULL OR record_date = ''")
            else:
                today = date.today().strftime("%Y-%m-%d")
                c.execute("UPDATE records SET record_date = ? WHERE record_date IS NULL OR record_date = ''", (today,))
            conn.commit()
        # If created_at missing, add it too
        if "created_at" not in cols:
            logger.info("'created_at' column missing. Adding column.")
            c.execute("ALTER TABLE records ADD COLUMN created_at TEXT")
            # fill with current timestamp
            now = datetime.utcnow().isoformat()
            c.execute("UPDATE records SET created_at = ? WHERE created_at IS NULL OR created_at = ''", (now,))
            conn.commit()
    conn.close()

def add_record(user_id, item, category, amount, note=""):
    today = date.today().strftime("%Y-%m-%d")
    now = datetime.utcnow().isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO records (user_id, record_date, item, category, amount, note, created_at) VALUES (?,?,?,?,?,?,?)',
              (user_id, today, item, category, amount, note, now))
    conn.commit()
    conn.close()

def query_records(user_id, mode="recent", value=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    base = "SELECT id, record_date, item, category, amount, note FROM records WHERE user_id=?"
    params = [user_id]
    today = date.today()
    if mode == "date":  # value is 'MMDD' string
        try:
            mm = int(value[:2])
            dd = int(value[2:])
            # basic validation
            if not (1 <= mm <= 12 and 1 <= dd <= 31):
                return []
            year = today.year
            qdate = f"{year}-{mm:02d}-{dd:02d}"
            base += " AND record_date=?"
            params.append(qdate)
        except:
            return []
    elif mode == "today":
        base += " AND record_date=?"
        params.append(today.strftime("%Y-%m-%d"))
    elif mode == "month":
        base += " AND strftime('%Y-%m', record_date)=?"
        params.append(today.strftime("%Y-%m"))
    # ordering
    base += " ORDER BY id DESC"
    if mode == "recent":
        base += " LIMIT 10"
    c.execute(base, tuple(params))
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
    # write (overwrite) CSV
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date","item","category","amount","note"])
        writer.writerows(rows)
    full = os.path.abspath(out_path)
    return full

# -------------------------
# Webhook & message handling
# -------------------------
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature","")
    body = request.get_data(as_text=True)
    logger.info("Received body: %s", body)
    try:
        if handler is None:
            logger.error("Webhook handler not set (CHANNEL_SECRET missing).")
            abort(500)
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.exception("Invalid signature")
        abort(400)
    except Exception as e:
        logger.exception("Unhandled error in handler")
        # return 200 or 500? LINE expects 200 for success; but if error, return 500
        abort(500)
    return "OK"

def is_mmdd(text):
    return bool(re.fullmatch(r"\d{4}", text))

@handler.add(MessageEvent, message=TextMessage) if handler else (lambda f: f)
def handle_message(event):
    user_id = event.source.user_id or "anonymous"
    text = event.message.text.strip()
    logger.info("Message from %s: %s", user_id, text)
    reply = "⚠️ 指令錯誤。輸入 help 查看說明。"

    try:
        # 常用命令（完全匹配）
        if text in ["help","說明","Help"]:
            reply = ("指令說明：\n"
                     "1) 記帳：品項 種類 價錢 [備註]\n   範例：午餐 食物 120 跟朋友\n"
                     "2) 清單 -> 最近 10 筆\n"
                     "3) MMDD (例：0902) -> 查該月該日所有紀錄\n"
                     "4) 今日 -> 查今天紀錄\n"
                     "5) 本月 -> 查本月紀錄\n"
                     "6) 儲存 -> 匯出為 records.csv（覆蓋）")
        elif text == "清單" or text.lower()=="list":
            rows = query_records(user_id, "recent")
            if rows:
                lines = [f"{r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5] or ''}" for r in rows]
                reply = "\n".join(lines)
            else:
                reply = "目前沒有紀錄。"
        elif text == "今日":
            rows = query_records(user_id, "today")
            if rows:
                lines = [f"{r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5] or ''}" for r in rows]
                reply = "\n".join(lines)
            else:
                reply = "今天沒有紀錄。"
        elif text == "本月":
            rows = query_records(user_id, "month")
            if rows:
                lines = [f"{r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5] or ''}" for r in rows]
                reply = "\n".join(lines)
            else:
                reply = "本月沒有紀錄。"
        elif text == "儲存" or text.lower()=="export":
            path = export_csv(user_id)
            reply = f"📊 已匯出最新紀錄到：{path}"
        elif is_mmdd(text):  # date query like 0902
            rows = query_records(user_id, "date", text)
            if rows:
                lines = [f"{r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5] or ''}" for r in rows]
                reply = "\n".join(lines)
            else:
                reply = f"{text} 沒有紀錄。"
        else:
            # 當作記帳輸入: 品項 種類 價錢 [備註]
            parts = text.split()
            if len(parts) >= 3:
                item = parts[0]
                category = parts[1]
                # 嘗試把第三個解析為數字（允許含小數點）
                try:
                    amount = float(parts[2])
                except:
                    # 若第三個不是數字，可能使用者打錯指令
                    raise ValueError("請確認金額為數字（例如 120 或 12.5）。")
                note = " ".join(parts[3:]) if len(parts) > 3 else ""
                add_record(user_id, item, category, amount, note)
                reply = f"✅ 已記帳：{item} | {category} | {amount} | {note}"
            else:
                reply = "指令格式不正確。請輸入：品項 種類 價錢 [備註]，或輸入 help 查看說明。"
    except Exception as e:
        logger.exception("Error handling message")
        reply = f"⚠️ 發生錯誤：{e}"

    if line_bot_api:
        try:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        except Exception as e:
            logger.exception("Failed to reply via LINE API")
    else:
        logger.warning("LINE API not configured; would reply: %s", reply)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=PORT, debug=True)
