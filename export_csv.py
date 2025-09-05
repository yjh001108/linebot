# export_csv.py - 匯出使用者資料為 CSV
import sqlite3, csv, os
from datetime import datetime

def export_csv_for_user(dbpath, user_id, out_dir='exports'):
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f'{user_id}_records_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}.csv')
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    c.execute('SELECT id, category, amount, note, created_at FROM records WHERE user_id=? ORDER BY id', (user_id,))
    rows = c.fetchall()
    conn.close()
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id','category','amount','note','created_at'])
        writer.writerows(rows)
    return out_path

if __name__ == '__main__':
    print('測試匯出: not connected to real DB')
