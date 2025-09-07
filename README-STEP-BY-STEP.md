# 詳細安裝與使用步驟（給沒有使用過 LINE Bot 的使用者）

## 前置準備（非技術使用者也能跟著做）
1. 註冊 LINE Developers:
   - 前往 https://developers.line.biz/ 並以你的 LINE 帳號登入。
   - 建立 Provider（隨便填名稱，例如：MyLineBot）。
   - 建立 Messaging API channel，選擇「LINE Official Account」或「Developer trial」。
   - 在 Channel 的 Basic settings 找到 `Channel secret`，在 Messaging API 取得 `Channel access token (long-lived)`。
   - 記下 `Channel secret` 與 `Channel access token`（待會會放入 `.env`）。

2. 在本機安裝 Python（若已安裝請略過）：
   - 下載並安裝 Python 3.10+（建議從 https://python.org 下載）。
   - 開啟終端機 (Windows: PowerShell / macOS: Terminal)，輸入 `python --version` 檢查。

3. 取得 ngrok（將本機伺服器暴露成公開網址）：
   - 前往 https://ngrok.com/ 註冊並下載 ngrok（免費帳號可使用）。
   - 下載後在終端機輸入 `ngrok authtoken <你的token>` 完成設定。

## 專案檔案說明
- `app.py`：主程式（Flask），處理 LINE webhook 與記帳指令。
- `requirements.txt`：Python 套件清單。
- `.env.example`：範例環境變數檔，請複製為 `.env` 並填入你的憑證。
- `utils.py`：處理 CSV 與記錄的輔助函式。
- `records.db`：本地範例 sqlite 檔（專案啟動後會建立）。

## 第一次啟動（在本機）
1. 下載並解壓專案。
2. 開啟終端機並進到專案資料夾：
   ```
   cd path/to/linebot_template
   ```
3. 建議建立虛擬環境（可選但推薦）：
   - Windows:
     ```
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - macOS / Linux:
     ```
     python3 -m venv venv
     source venv/bin/activate
     ```
4. 安裝套件：
   ```
   pip install -r requirements.txt
   ```
5. 建立 `.env`：
   - 將 `.env.example` 複製成 `.env`，並填入 `LINE_CHANNEL_SECRET`、`LINE_CHANNEL_ACCESS_TOKEN`、`CSV_PATH`（例如：./records.csv）。
6. 啟動本機 Flask 伺服器：
   ```
   python app.py
   ```
   預設會在 http://127.0.0.1:5000 運行。
7. 啟動 ngrok（把 5000 port 暴露出來）：
   ```
   ngrok http 5000
   ```
   ngrok 會印出一個 `https://xxxxxx.ngrok.app`（或 ngrok.io）URL，複製該網址。
8. 在 LINE Developers 的 Messaging API → Webhook settings，把 Webhook URL 設為：
   ```
   https://<你的-ngrok-domain>/callback
   ```
   並開啟 Webhook（Enable）。

## 指令範例（使用 LINE 對 Bot 發訊息）
- 新增記帳（會自動加入今日日期）：
  ```
  午餐 食物 120
  ```
- 顯示最近 10 筆：
  ```
  清單
  ```
- 顯示今天的所有：
  ```
  今日
  ```
- 顯示本月的所有：
  ```
  本月
  ```
- 指定日期（MMDD，例如 0902）：
  ```
  0902
  ```
- 匯出 CSV（會依 .env 中的 CSV_PATH 輸出 UTF-8-SIG）：
  ```
  儲存
  ```
- 刪除使用者所有資料（以 user_id 為區分）：
  ```
  刪除
  ```

## 下次開啟所需操作（快速清單）
1. 啟動虛擬環境（如有）：
   - Windows: `.env\Scriptsctivate`
   - macOS/Linux: `source venv/bin/activate`
2. 啟動 Flask：`python app.py`
3. 啟動 ngrok：`ngrok http 5000`
4. 確認 ngrok 的 URL 是否有變動，若變動請更新 LINE Webhook URL。

## 推上 GitHub（基本流程）
1. 在 GitHub 建立新 repo（例如：linebot-bookkeeping）。
2. 在本地專案執行：
   ```
   git init
   git add .
   git commit -m "initial commit"
   git branch -M main
   git remote add origin https://github.com/<你的帳號>/<repo>.git
   git push -u origin main
   ```
3. 若想用 GitHub Desktop 或者 GitHub 網站上傳也可（拖拉上傳 zip）。

## 注意事項
- CSV 使用 UTF-8-SIG，以確保 Excel 在 Windows 上顯示中文正常。
- 若要 24/7 運行，請選擇 Render / Railway / Fly.io 等付費方案或穩定方案（免費方案多會睡眠）。
