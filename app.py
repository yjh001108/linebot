from flask import Flask, request, abort
import os
from dotenv import load_dotenv
from utils import RecordManager
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

load_dotenv()
CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
CSV_PATH = os.getenv('CSV_PATH', './records.csv')

if not CHANNEL_SECRET or not CHANNEL_ACCESS_TOKEN:
    raise RuntimeError('請先在 .env 填入 LINE_CHANNEL_SECRET 與 LINE_CHANNEL_ACCESS_TOKEN')

app = Flask(__name__)
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

rm = RecordManager(csv_path=CSV_PATH)

@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text.strip()
    # 指令處理
    if text == '清單':
        items = rm.list_recent(user_id, 10)
        if not items:
            reply = '沒有紀錄。'
        else:
            lines = []
            for r in items:
                lines.append(f"{r['日期']} | {r['品項']} | {r['分類']} | {r['金額']}")
            reply = '\n'.join(lines)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return
    if text == '今日':
        items = rm.list_today(user_id)
        reply = rm.format_items(items)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return
    if text == '本月':
        items = rm.list_month(user_id)
        reply = rm.format_items(items)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return
    if text == '儲存':
        rm.export_csv()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='📊 已匯出最新紀錄到：records.csv'))
        return
    if text == '刪除':
        rm.delete_user(user_id)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='🗑️ 已刪除所有紀錄'))
        return
    # 指定日期格式 MMDD (例如 0902)
    if len(text) == 4 and text.isdigit():
        items = rm.list_by_mmdd(user_id, text)
        reply = rm.format_items(items)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return
    # 新增記帳：格式：品項 分類 金額
    parts = text.split()
    if len(parts) == 3 and parts[2].isdigit():
        item, cat, price = parts
        rm.add_record(user_id, item, cat, int(price))
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='✅ 已新增記帳'))
        return
    # 未知指令
    help_text = '指令格式錯誤。\n範例新增：午餐 食物 120\n查詢：清單 / 今日 / 本月 / 0902\n匯出：儲存\n刪除：刪除'
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=help_text))

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
