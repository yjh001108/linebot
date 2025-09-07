# LINE Bot 記帳 — 建立教學

> 🎯 **目標**：建立一個簡單方便的 LINE Bot 記帳工具，支援 Excel 即時匯出，適合初學者快速上手。

---

## 📁 一、檔案說明

| 檔案               | 說明                                             |
|--------------------|--------------------------------------------------|
| `app.py`           | 主程式（Flask），處理 LINE webhook 與記帳指令       |
| `requirements.txt` | Python 套件清單                                  |
| `.env.example`     | 範例環境變數檔，請複製為 並填入你的憑證。.env       |
| `utils.py      `   | 處理 CSV 與記錄的輔助函式                         |
| `records.db`       | 本地範例 sqlite 檔（專案啟動後會建立）             |

---

## ⚙️ 二、前置作業（一次性）

### 1. 安裝 Python 3.8+

- 前往 [Python 官網下載頁面](https://www.python.org/downloads/)，下載 **Python 3.8 或以上版本**。
- 安裝時請勾選 **「Add Python to PATH」**。

<img src="https://github.com/user-attachments/assets/1e0dc982-9ea5-4255-9dc7-4fe8160b09b3" alt="Python 安裝畫面" width="500" />

---

### 2. 安裝 ngrok 並設定 Authtoken

1. 前往 [ngrok 官網](https://ngrok.com/)，註冊一個免費帳號。
2. 下載並安裝 ngrok。
3. 登入 ngrok 官網 → 點選 Dashboard → 複製你的 **Authtoken**。
4. 在 PowerShell 輸入以下指令來設定：

```powershell
ngrok config add-authtoken <你的Authtoken>
```

<img src="https://github.com/user-attachments/assets/18be64f9-59fd-4b25-bf72-50646adc4da1" alt="ngrok Authtoken 設定" width="500" />
<img src="https://github.com/user-attachments/assets/e3ccc1cc-b4cd-4a74-8954-b20ebc209ad2" alt="ngrok Authtoken 完成" width="500" />

---

### 3. 建立 LINE Messaging API Channel

1. 前往 [LINE Developers](https://developers.line.biz/)。
2. 使用 LINE 帳號登入。
3. 建立一個 **Provider**（提供者，隨便填寫一個名稱即可）。
4. 在該 Provider 下，建立 **Messaging API Channel**：

   * App 名稱：隨意（例如「記帳小幫手」）
   * App Icon：可上傳任意圖片
   * 類型：Messaging API
   * Email：填寫有效 Email
5. 建立完成後，進入 Channel 頁面 → 複製以下資訊：

   * Channel Secret (在 Basic settings )
   * Channel Access Token（在Messaging API ，點選「發行」）

<img src="https://github.com/user-attachments/assets/2f0a364a-d8e2-45e0-8498-3c3de23cef05" alt="LINE Developers Channel 設定畫面" width="500" />
<img src="https://github.com/user-attachments/assets/c83269e3-a574-4746-956b-283f0270fe91" alt="LINE Developers Channel 設定畫面" width="500" />


---

## 📦 三、下載專案

將專案下載並解壓縮至本機資料夾，例如：

```text
C:\projects\linebot
```

---

## 🐍 四、建立虛擬環境並安裝相依套件（PowerShell）

```powershell
cd C:\projects\linebot
python -m venv venv
.\venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🛠️ 五、建立 `.env` 檔案

請依照 `.env.example` 填入你的 LINE Channel Secret 與 Access Token：

```text
LINE CHANNEL_SECRET=xxxxxxxxxxxxxxxx
LINE CHANNEL_ACCESS_TOKEN=xxxxxxxxxxxxxxxx
```

---

## 🚀 六、啟動主程式（ Flask 伺服器： 預設會在 http://127.0.0.1:5000 運行）

```powershell
python app.py
```

---

## 🌐 七、使用 ngrok 暴露本地服務至外網（**另開一個 PowerShell 視窗**）

```powershell
ngrok http 5000
```

* 找到命令輸出中的 Forwarding URL，例如：

  ```text
  https://xxxx.ngrok-free.app
  ```

<img src="https://github.com/user-attachments/assets/e309927e-16ea-4542-84c4-986bcd89a346" alt="ngrok Forwarding URL" width="500" />

* 前往 LINE Developers → Channel → **Webhook settings**，貼上：

  ```text
  https://xxxx.ngrok-free.app/callback
  ```

  * URL 結尾需加上 `/callback`
  * 點擊「**Verify**」驗證 Webhook，若成功表示 LINE 可正確呼叫你的伺服器。

<img src="https://github.com/user-attachments/assets/66d820a5-1ce1-4254-8377-70d1bc40968a" alt="Webhook settings 畫面" width="500" />
<img src="https://github.com/user-attachments/assets/79679946-afe0-44c6-969a-628ef474cd2b" alt="Webhook 驗證成功畫面" width="500" />

---

## ✅ 安裝成功後畫面

<img src="https://github.com/user-attachments/assets/8fcd3147-3892-46a6-8176-8926f62f503e" alt="安裝成功畫面 1" width="200" />

---

## 💬 八、測試指令（在 LINE 傳訊給你的 Bot）

### 使用方式：

1. 傳送以下格式的訊息給你的 Bot：

| 指令            | 說明                                    |
| ------------- | ------------------------------------- |
| `品項 種類 價錢` | 新增一筆記帳資料（自動加上今天日期），例如：`午餐 食物 120` |
| `清單`          | 顯示最近 10 筆記錄                                      |
| `MMDD`          | 指定日期（例如 0902，顯示 9 月 2 號的紀錄）              |
| `今日`          | 顯示今天所有紀錄                                        |
| `本月`          | 顯示本月所有紀錄                                        |
| `儲存`          | 更新 `records.csv` 檔案                                |
| `刪除`          | 刪除紀錄的所有資料                                      |

2. 開啟 `records.csv`（用 Excel 查看），即可看到所有記錄。

<img src="https://github.com/user-attachments/assets/6630a375-d135-4f10-a4c2-68f0d4871660" alt="安裝成功畫面 2" width="500" />

---

## 🔁 十、下次啟動流程（快速啟動）

1. 啟動虛擬環境並執行程式：

```powershell
cd C:\projects\linebot
.\venv\Scripts\activate
python app.py
```

2. 另開視窗啟動 ngrok：

```powershell
ngrok http 5000
```

> 若 ngrok 網址改變，請回到 LINE Developers 更新 Webhook URL（結尾需加 `/callback`）

---

## ❓ 十一、常見問題與排除法 (FAQ)

| 問題                                                   | 解決方法                                               |
| ---------------------------------------------------- | -------------------------------------------------- |
| `502 Bad Gateway`（ngrok 顯示）                          | 確認 `python app.py` 是否有在執行—未啟動時 ngrok 會回傳 502。  |
| Webhook 驗證失敗 / HTTP 400                              | 檢查 `.env` 中的 Channel Secret / Access Token 是否填寫正確。 |
| 匯出的 `records.csv` 為空                                 | 代表資料庫尚無資料，可先輸入一筆記帳指令測試。                 |

