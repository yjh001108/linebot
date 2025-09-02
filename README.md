# LINE Bot 記帳 — 完整教學（Windows 11 / PowerShell）

> 目標：建立一個簡單方便的 LINE Bot 記帳 ，提供 Excel 即時匯出 `records.csv`。
> 適合初學者快速上手。

---

## 一、檔案說明
- `app.py`：主程式（包含 DB 初始化、migration、指令解析、CSV 匯出）
- `requirements.txt`：Python 套件需求
- `.env`：環境變數（不應上傳到 GitHub）
- `bookkeeping.db`：SQLite 資料庫（啟動程式會自動建立 / migration）
- `records.csv`：CSV 匯出檔（由 `儲存` 指令建立或覆蓋）

---

## 二、前置作業（一次性）
1. 安裝 Python 3.8+（官網下載並安裝）。
2. 下載並安裝 ngrok（註冊後可在官網取得可執行檔）。
3. 取得 LINE Developers 的 Channel Secret 與 Channel Access Token（建立 Messaging API channel）。

---

## 三、下載zip.
把此專案下載到本機資料夾，例如："C:\projects\linebot"

---

## 四、建立虛擬環境並安裝相依套件（PowerShell）
```powershell
cd C:\projects\linebot
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

---

## 五、建立 .env 檔案
填入 LINE 的 Channel Secret 與 Access Token，（參考 .env.example）。

---

## 六、初始化資料庫：
```
python init_db.py
```

## 七、啟動程式（第一次會建立 DB 與做 migration）
```
python app.py

```

## 八、使用 ngrok 將本地服務暴露到外網（另一個 PowerShell 視窗）
```
ngrok http 5000

```
- 取得 https://xxxx.ngrok-free.app（Forwarding 行）
- 複製該網址，並在 LINE Developers 的 Channel > Webhook settings，填入：
```
https://xxxx.ngrok-free.app**/callback**

```
- 結尾須加上 /callback
- 點選 Verify（Webhook 驗證）。若顯示成功，表示 LINE 能正確呼叫你的 server。

```

## 九、測試指令（在 LINE 傳給你的 Bot）
### 使用方式
1. 指令範例（使用者傳訊息）
-  格式：`品項 種類 價錢 [備註]` (範例：'午餐 食物 120 跟朋友`) → 記帳（自動加上今天日期）
- `清單` → 最近 10 筆
- `0902` → 9 月 2 號所有紀錄
- `今日` → 今天所有紀錄
- `本月` → 本月所有紀錄
- `儲存` → 更新 records.csv
2. 打開 records.csv（Excel），看到所有紀錄。

```

## 十、下次開啟-後續快速啟動
1. 啟動虛擬環境，輸入：
```
cd C:\projects\linebot
.\venv\Scripts\Activate.ps1
python app.py

```

2. 另一個視窗開啟 ngrok:
```
ngrok http 5000

```
若 ngrok 換了網址，請記得回到 LINE Developers 更新 webhook URL（.../callback）。

---

## 十一、常見問題與排除法 (FAQ)
-  502 Bad Gateway（ngrok 顯示）
-> 檢查 python app.py 是否正在執行。若沒在跑，ngrok 會 502。
-  Webhook 驗證失敗或 400
-> 檢查 .env 的 Channel Secret / Access Token 是否正確。若 token 錯誤，LINE 會收到非 200。
-  匯出後 records.csv 為空
-> 確認資料有寫入 DB（用上方的 Python snippet 或 sqlite3 查看）。若 DB 沒資料，代表 Bot 未成功執行 add_record（輸入格式錯誤或程式未正確回應）。
-  出現錯誤 table records has no column named record_date
-> 新版 app.py 已內建 migration。只要你使用新版 app.py 啟動，程式會自動加入缺少欄位並填補資料。不需手動刪 DB（除非你想從頭開始）。
