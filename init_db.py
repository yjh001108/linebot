# init_db.py - 初始化 SQLite 資料庫
import sqlite3
import os
DB_PATH = os.getenv('DB_PATH', 'bookkeeping.db')

def init(dbpath=DB_PATH):
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        category TEXT,
        amount REAL,
        note TEXT,
        created_at TEXT
    )
    ''')
    conn.commit()
    conn.close()
    print('Database initialized:', dbpath)

if __name__ == '__main__':
    init()
