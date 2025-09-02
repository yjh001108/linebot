# LINE Bot 記帳 (Railway PostgreSQL 版)

## 部署步驟
1. Fork 或 push 本專案到 GitHub。
2. Railway 建立新專案 → 連接 GitHub Repo。
3. Railway 自動偵測 Procfile 並部署。
4. 在 Railway Variables 設定：
   - LINE_CHANNEL_SECRET
   - LINE_CHANNEL_ACCESS_TOKEN
   - PORT=5000
   - DATABASE_URL (Railway Postgres 插件提供)
5. Railway 會給一個 https URL，例如：https://xxx.up.railway.app
6. LINE Developers → Messaging API → Webhook URL 設定為：https://xxx.up.railway.app/callback
7. Verify → 成功。

## Bot 指令
- 記帳 類別 金額 [備註]
- list [n]
- help
