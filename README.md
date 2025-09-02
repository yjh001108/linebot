# LINE Bot 記帳範本 (簡體 / 繁體可用)

本範本提供一個最小可行的 LINE Bot 記帳系統，適合初學者快速上手並後續擴充功能（圖表、查詢、分類）。

## 特色
1. 使用 Flask 作為 webhook server
2. SQLite 作為本地資料庫，容易攜帶與備份
3. 匯出 CSV 的功能，方便離線分析
4. 具備初始化腳本與推向 GitHub 的操作說明

## 快速開始（本地測試）
1. 複製或下載專案
2. 建議建立虛擬環境並安裝依賴：
   ```
   python -m venv venv
   source venv/bin/activate    # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. 建立 .env 檔案（參考 .env.example），填入 LINE 的 Channel Secret 與 Access Token
4. 初始化資料庫：
   ```
   python init_db.py
   ```
5. 啟動 Flask：
   ```
   python app.py
   ```
6. 使用 ngrok 或類似工具把本地 5000 port 暴露到外網，並在 LINE Developers 設定 webhook URL (例如 https://xxxxx.ngrok.io/callback)

## 指令範例（使用者傳訊息）
- 記帳: `記帳 類別 金額 備註` 例如：`記帳 午餐 120 與朋友`
- 查詢: `list 10` 取得最新 10 筆
- 匯出: `export` 產生 CSV 並回傳檔案路徑

## 部署（免費或低成本選項）
常見免費/低成本平台：
- Railway.app（有免費額度）
- Render.com（有免費方案）
- Vercel（適合無伺服器函式）
- Fly.io
(注意：各服務條款及免費額度會變動，部署前請確認當前方案)

## 推到 GitHub（簡易步驟，請參考 push_instructions.sh）
1. git init
2. git add .
3. git commit -m "initial"
4. 在 GitHub 建立 repo，加入 remote
5. git push -u origin main

## 下次開啟/重啟要做的事
1. 啟動虛擬環境
2. 確認 .env 與 DB 在預期位置
3. python app.py 或使用 process manager（pm2、systemd）

