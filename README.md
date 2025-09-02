# LINE Bot 記帳 — 完整教學（Windows 11 / PowerShell）

> 🎯 **目標**：建立一個簡單方便的 LINE Bot 記帳工具，支援 Excel 即時匯出 `records.csv`，適合初學者快速上手。

---

## 📁 一、檔案說明

| 檔案 | 說明 |
|------|------|
| `app.py` | 主程式（包含 DB 初始化、migration、指令解析、CSV 匯出） |
| `requirements.txt` | Python 套件需求清單 |
| `.env` | 環境變數檔案（**不應上傳到 GitHub**） |
| `bookkeeping.db` | SQLite 資料庫（程式啟動時自動建立與更新） |
| `records.csv` | 匯出用 CSV 檔（由 `儲存` 指令建立/覆蓋） |

---

## ⚙️ 二、前置作業（一次性）

1. 安裝 **Python 3.8+**（[Python 官網](https://www.python.org/)）。
2. 安裝 **ngrok** 並註冊帳號（[ngrok 官網](https://ngrok.com/)）。
3. 前往 [LINE Developers](https://developers.line.biz/) 建立 **Messaging API Channel**，取得：
   - Channel Secret
   - Channel Access Token

---

## 📦 三、下載專案

將專案下載並解壓縮至本機資料夾，例如：

```

C:\projects\linebot

````

---

## 🐍 四、建立虛擬環境並安裝相依套件（PowerShell）

```powershell
cd C:\projects\linebot
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
````

---

## 🛠️ 五、建立 `.env` 檔案

根據 `.env.example`，填入你的 LINE Channel Secret 與 Access Token，例如：

```
CHANNEL_SECRET=xxxxxxxxxxxxxxxx
CHANNEL_ACCESS_TOKEN=xxxxxxxxxxxxxxxx
```

---

## 🗃️ 六、初始化資料庫

```powershell
python init_db.py
```

---

## 🚀 七、啟動主程式（會自動建立 DB 並做 migration）

```powershell
python app.py
```

---

## 🌐 八、使用 ngrok 暴露本地服務至外網（**另開一個 PowerShell 視窗**）

```powershell
ngrok http 5000
```

* 找到輸出中的 Forwarding URL，例如：

  ```
  https://xxxx.ngrok-free.app
  ```

* 前往 LINE Developers > Channel > **Webhook settings**，貼上：

  ```
  https://xxxx.ngrok-free.app/callback
  ```

* 結尾需加 `/callback`
* 點擊「**Verify**」驗證 Webhook，若顯示成功，表示 LINE 已能正確呼叫你的伺服器。

---

## 💬 九、測試指令（在 LINE 傳訊給你的 Bot）

### ✅ 使用方式

1. 傳送以下格式的訊息給你的 Bot：

| 指令              | 說明                  |
| --------------- | ------------------- |
| `品項 種類 價錢 [備註]` | (範例：'午餐 食物 120 跟朋友) 新增一筆記帳資料（會自動加上今天日期） |
| `清單`            | 顯示最近 10 筆紀錄         |
| `0902`          | 顯示 9 月 2 號的紀錄       |
| `今日`            | 顯示今天所有紀錄            |
| `本月`            | 顯示本月所有紀錄            |
| `儲存`            | 匯出 records.csv 檔案   |

2. 開啟 `records.csv`（用 Excel 查看），即能看到所有紀錄。

---

## 🔁 十、下次啟動流程（快速啟動）

1. 啟動虛擬環境並執行程式：

```powershell
cd C:\projects\linebot
.\venv\Scripts\Activate.ps1
python app.py
```

2. 另開視窗啟動 ngrok：

```powershell
ngrok http 5000
```

> 📌 若 ngrok 網址改變，請回到 LINE Developers 更新 Webhook URL（結尾需加 `/callback`）

---

## ❓ 十一、常見問題與排除法 (FAQ)

| 問題                                                   | 解決方法                                              |
| ---------------------------------------------------- | ------------------------------------------------- |
| `502 Bad Gateway`（ngrok 顯示）                          | 確認 `python app.py` 是否有在執行。未啟動時 ngrok 會回傳 502。     |
| Webhook 驗證失敗 / HTTP 400                              | 檢查 `.env` 的 Channel Secret / Access Token 是否填寫正確。 |
| 匯出的 `records.csv` 為空                                 | 代表資料庫尚無資料。可先輸入一筆記帳指令測試。                           |
| 出現錯誤 `table records has no column named record_date` | 使用新版 `app.py`，會自動處理 migration 並新增缺少欄位。不必手動刪除 DB。  |

---


