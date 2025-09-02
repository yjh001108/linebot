# db.py - PostgreSQL 連線
import os, psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS records (
        id SERIAL PRIMARY KEY,
        user_id TEXT,
        category TEXT,
        amount REAL,
        note TEXT,
        created_at TIMESTAMP DEFAULT NOW()
    )
    ''')
    conn.commit()
    cur.close()
    conn.close()
