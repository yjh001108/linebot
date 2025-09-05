# models.py - DB helper functions (可擴充)
import sqlite3
from datetime import datetime

def connect(dbpath):
    conn = sqlite3.connect(dbpath)
    conn.row_factory = sqlite3.Row
    return conn
