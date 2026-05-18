# Quickstart — 001-flange-generator

開發者本機 setup 與驗證流程。對應 spec.md US1/US2 驗收路徑。

---

## 系統需求

| 項目 | 版本 |
|---|---|
| macOS / Linux / Windows | 任一 |
| Python | 3.11+ |
| Node.js | 20+ |
| pnpm 或 npm | 任一 |
| ODA File Converter | 25.x+（DXF → DWG R2000 用） |

---

## 安裝 ODA File Converter

DWG 輸出依賴 ODA File Converter（免費，需註冊接受授權條款）。

### macOS

```bash
# 從官網下載 .dmg 並安裝至 /Applications/ODAFileConverter.app
# 下載：https://www.opendesign.com/guestfiles/oda_file_converter
# 安裝後驗證：
/Applications/ODAFileConverter.app/Contents/MacOS/ODAFileConverter --version
```

### Linux

```bash
# 下載 .deb 或 .rpm 套件後安裝
sudo dpkg -i ODAFileConverter_QT*.deb
ODAFileConverter --version
```

### Windows

從官網下載 `.exe` 安裝程式，路徑加入系統 PATH。

設定 ezdxf 找得到 ODA：

```bash
# macOS / Linux
export ODAFC_EXEC_PATH="/Applications/ODAFileConverter.app/Contents/MacOS/ODAFileConverter"

# Windows
set ODAFC_EXEC_PATH=C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe
```

---

## 後端 setup

```bash
cd backend/
python3.11 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 啟動 dev server
uvicorn main:app --reload --port 8000
```

驗證後端：

```bash
# Health check（應回傳 {"status":"ok","oda_converter_available":true,...}）
curl http://localhost:8000/api/health
```

---

## 前端 setup

```bash
cd frontend/
pnpm install
pnpm dev   # 預設 http://localhost:3000
```

`.env.local` 設定後端位址：

```
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

---

## 端對端驗證（US1 + US2 acceptance path）

### Step 1 — 開啟工具

瀏覽器訪問 `http://localhost:3000`。應看到單頁 UI：左側表單、右側預覽區。

### Step 2 — 輸入規格

於表單填入：

| 欄位 | 範例值 |
|---|---|
| 內徑 | 100 |
| PCD | 150 |
| 外徑 | 200 |
| 孔數 | 8 |
| 孔徑 | 12 |
| 厚度 | 20 |
| 材質 | SS400（鎖定不可改） |

### Step 3 — 產生預覽（US1 acceptance）

點擊「產生」。預期：

- ≤ 5 秒內右側出現法蘭 2D 工程圖
- 圖面以**英文**標註 7 欄位數值
- 含浮水印「For Customer Preview Only — Not for Manufacturing」

### Step 4 — 下載 DWG（US2 acceptance scenario 1）

點擊「下載 DWG」。預期：

- ≤ 3 秒內瀏覽器開始下載
- 檔名格式 `flange_100x200_PCD150_8H_20t_<timestamp>.dwg`
- 用 AutoCAD / DraftSight / LibreCAD 開啟，可見完整法蘭圖、英文標註、浮水印

### Step 5 — 下載 PDF（US2 acceptance scenario 2）

點擊「下載 PDF」。預期：

- ≤ 3 秒內瀏覽器開始下載
- A4 直式單頁
- 含法蘭工程圖、7 欄位純表格、浮水印、產生時間
- 用 macOS Preview / Chrome / Acrobat Reader / iPad 皆可開啟

### Step 6 — 驗證錯誤處理（US1 acceptance scenario 3）

修改 PCD 為 50（< 內徑 100），點擊「產生」。預期：

- 中文錯誤訊息明確指出「PCD 必須大於內徑」
- 不產生任何預覽或檔案

### Step 7 — 驗證結構一致性（US2 acceptance scenario 3 / SC-006）

維持相同規格，再次點擊「下載 DWG」，比對兩次下載檔。預期：

- DXF/DWG 拓樸結構（layer、entity 數量、類型）一致
- 主要尺寸（內徑、外徑、PCD、孔徑、厚度、孔數）100% 一致

### Step 8 — 驗證無狀態（FR-020）

關閉前後端進程，重新啟動。檢查：

- `backend/` 目錄無遺留 `.dxf` / `.dwg` / `.pdf` / `.svg` 檔
- 健康檢查 `/api/health` 仍正常

---

## Constitution Quality Gates 驗證

於後端執行：

```bash
cd backend/
pytest tests/quality_gates/ -v
```

預期 6 項全通過：

1. ✓ DWG 版本檢查（R2000）
2. ✓ 可開啟性檢查（ezdxf re-read）
3. ✓ 幾何完整性檢查（audit）
4. ✓ 尺寸合理性比對（萃取 7 欄位）
5. ✓ 孔位驗證（角度均布、PCD 距離）
6. ✓ 結構一致性檢查（兩次產出比對）

---

## 故障排除

| 症狀 | 排查 |
|---|---|
| `/api/health` 回 `oda_converter_available: false` | 檢查 `ODAFC_EXEC_PATH` 環境變數，或確認 ODA File Converter 已安裝 |
| 下載的 DWG 無法在 AutoCAD 開啟 | 確認 ODA File Converter 版本 ≥ 25.x；查看後端 log 是否有 `odafc` 警告 |
| 前端無法連線後端 | 確認 `NEXT_PUBLIC_API_BASE` 與後端 port 一致；確認 CORS 設定（dev 預設允許 localhost） |
| `5 秒內` SLO 未達成 | 第一次啟動 ezdxf drawing add-on 載入 matplotlib 較慢；第二次起應穩定於 1–2 秒 |
| PDF 中 SVG 渲染變形 | svglib 對部分 SVG feature 支援有限，檢查後端 log；必要時調整 ezdxf drawing 輸出選項 |
