import csv, os, datetime
from dotenv import load_dotenv
load_dotenv()

class RecordManager:
    def __init__(self, csv_path='./records.csv'):
        self.csv_path = csv_path
        # in-memory store: {user_id: [records]}
        self.store = {}
        # load existing csv if present
        if os.path.exists(self.csv_path):
            try:
                with open(self.csv_path, newline='', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        uid = row.get('user_id', 'default')
                        self.store.setdefault(uid, []).append(row)
            except Exception:
                pass

    def _today(self):
        return datetime.date.today().strftime('%Y-%m-%d')

    def add_record(self, user_id, item, category, amount, date=None):
        if date is None:
            date = self._today()
        rec = {'日期': date, '品項': item, '分類': category, '金額': str(amount)}
        self.store.setdefault(user_id, []).insert(0, rec)  # newest first

    def list_recent(self, user_id, n=10):
        return self.store.get(user_id, [])[:n]

    def list_today(self, user_id):
        today = datetime.date.today().strftime('%Y-%m-%d')
        return [r for r in self.store.get(user_id, []) if r['日期'] == today]

    def list_month(self, user_id):
        yyyy_mm = datetime.date.today().strftime('%Y-%m')
        return [r for r in self.store.get(user_id, []) if r['日期'].startswith(yyyy_mm)]

    def list_by_mmdd(self, user_id, mmdd):
        # mmdd like '0902' -> compare with record日期's MMDD
        return [r for r in self.store.get(user_id, []) if r['日期'][5:7]+r['日期'][8:10] == mmdd]

    def format_items(self, items):
        if not items:
            return '沒有紀錄。'
        lines = [f"{r['日期']} | {r['品項']} | {r['分類']} | {r['金額']}" for r in items]
        return '\n'.join(lines)

    def export_csv(self):
        # write CSV with UTF-8-SIG
        fieldnames = ['日期','品項','分類','金額','user_id']
        with open(self.csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for uid, recs in self.store.items():
                for r in recs:
                    row = {'日期': r['日期'], '品項': r['品項'], '分類': r['分類'], '金額': r['金額'], 'user_id': uid}
                    writer.writerow(row)

    def delete_user(self, user_id):
        if user_id in self.store:
            del self.store[user_id]
