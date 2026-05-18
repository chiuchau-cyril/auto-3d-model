# Req-1：鼓風機入口法蘭 DWG 產生器（第一階段需求）

**版本**: 0.4
**最後更新**: 2026-05-18
**狀態**: Ready — 13/14 項決策已確認，可送 `/speckit-specify`

**v0.4 變更**：§7 由「待澄清」改為「已確認決策」；同步更新 §3.1（材質鎖 SS400）、§3.3（選定方案 A）、
§4（local-only）、§6 API 改為無狀態（移除 id / expires_at）、§8 範圍外擴充、§9 驗收標準補上「英文標註」等。

**v0.3 變更**：新增 PDF 輸出需求（§3.2 / §6 API / §7 / §9）。理由：客戶端不一定安裝 AutoCAD，
需要一份任何裝置都能開啟、列印、轉寄的可攜文件。

---

## 1. 背景與目標

業務人員在面對客戶詢價／提案時，需要快速產出一份**鼓風機入口法蘭**的 3D 模型 (.dwg)，
作為規格確認與報價附件。此工具的目的：

- **縮短業務作業時間**：從「請工程師畫圖 → 等回稿」改為「輸入規格 → 立即拿到 DWG」
- **降低溝通誤差**：由系統依輸入規格產出，避免業務口述、工程師誤聽
- **客戶可視化**：客戶於現場即可看到模型外觀，提升決策速度

**非目標（v1 不做）**：

- 不作為加工依據（精度要求依 Constitution v2.0.0 原則 I）
- 不支援標準法蘭表（ASME/JIS/CNS）自動代入
- 不支援多階／異形法蘭

## 2. 使用者與場景

| 角色 | 場景 | 期望 |
|---|---|---|
| 業務人員 | 客戶來電詢價，需即時提供模型 | 30 秒內輸入完成、5 秒內看到模型 |
| 客戶 | 在會議中與業務對著螢幕確認規格 | 一眼看懂尺寸、孔位 |
| 主管 | 抽查業務提供的模型是否正確 | 能下載 DWG 與輸入規格對照 |

## 3. 功能需求

### 3.1 輸入（必填）

| 欄位 | 型別 | 單位 | 預設值 | 驗證規則 |
|---|---|---|---|---|
| 內徑 Inner Diameter | number | mm | — | > 0；最多 2 位小數 |
| PCD Pitch Circle Diameter | number | mm | — | > 內徑；最多 2 位小數 |
| 外徑 Outer Diameter | number | mm | — | > PCD；最多 2 位小數 |
| 孔數 Bolt Hole Count | integer | — | — | ≥ 1 |
| 孔徑 Bolt Hole Diameter | number | mm | — | > 0；< (外徑 − PCD)/2 與 (PCD − 內徑)/2；最多 2 位小數 |
| 厚度 Thickness | number | mm | — | > 0；最多 2 位小數 |
| 材質 Material | enum | — | **SS400** | v1 僅支援 SS400（鎖定不可改），其他材質列入後續階段 |

**單位顯示**：UI 上不在每個欄位旁標 "mm"，改為在區塊標題（如「尺寸（單位：mm）」）統一標示。

**數值精度**：所有 mm 欄位接受最多 2 位小數，超出部分前端截斷並提示。

**驗證行為**（依 Constitution 原則 IV）：

- 任一必填欄位缺漏 → 前端禁止送出，明確標示「請填寫 OOO」
- 幾何不合理（如 PCD ≤ 內徑） → 後端回拒並回傳具體錯誤訊息
- 系統 **不得自動補預設**（材質除外）

### 3.2 輸出

1. **DWG 預覽**：頁面上直接看到模型，需於圖面標註所有 7 個輸入欄位數值
2. **下載 DWG**：一鍵下載 AutoCAD R2000 .dwg 檔，檔名建議 `flange_{內徑}x{外徑}_PCD{PCD}_{孔數}H_{厚度}t_{timestamp}.dwg`
3. **下載 PDF**：一鍵下載 PDF 檔，供未安裝 AutoCAD 的客戶開啟、列印、轉寄。內容要求：
   - 主圖：法蘭工程圖（與 SVG 預覽同等視覺品質，含尺寸與孔位標註）
   - 規格表：列出全部 7 個輸入欄位數值（內徑、PCD、外徑、孔數、孔徑、厚度、材質）
   - 浮水印：「For Customer Preview Only — Not for Manufacturing」
   - 頁尾：產生時間、產生者識別（若 v1 無登入則留空或顯示 "Sales Tool"）
   - 紙張大小：A4 直式（預設）— 若超出可考慮 A3，待定見 §7
   - 檔名建議：`flange_{內徑}x{外徑}_PCD{PCD}_{孔數}H_{厚度}t_{timestamp}.pdf`（與 DWG 同字根，副檔名不同）
4. **產出標示**：DWG 與 PDF 皆 SHOULD 顯示「For Customer Preview Only — Not for Manufacturing」浮水印或文字（依 Constitution 技術約束）

### 3.3 預覽方式

**選定方案 A：伺服器端產生 SVG 2D 工程圖**

- 後端在收到產生請求時，直接產出 SVG（含全部標註）回傳前端
- SVG 可內嵌於 HTML、可向量縮放、可直接嵌入 PDF
- 法蘭為對稱件，2D 工程圖即足以與客戶溝通
- DWG 與 PDF 皆基於同一份規格資料生成，確保三者視覺一致（WYSIWYG）

## 4. 非功能需求

| 類別 | 要求 |
|---|---|
| 效能 | 從點擊「產生」到 SVG 預覽出現 ≤ 5 秒；點擊「下載 PDF/DWG」到開始下載 ≤ 3 秒 |
| 可用性 | 介面簡單到無需教學文件，業務首次使用 ≤ 1 分鐘上手 |
| 瀏覽器支援 | Chrome、Edge、Safari 最新兩版 |
| 響應式 | 至少支援 1366×768 桌機 與 iPad 直橫式（業務常用筆電/平板） |
| 語系 | UI 介面繁體中文；DWG / PDF 圖面標註**英文** |
| 並行 | 單機 local 環境，無多人並行壓力 |
| 安全 | 後端 API 需基本輸入驗證；v1 不要求登入（local 工具） |
| 部署 | v1 僅在開發者本機 local 環境執行（Next.js dev server + Python local server） |
| 狀態管理 | 完全無狀態：不持久化任何產生結果，每次下載即時重新生成 |

## 5. 介面設計原則

依「介面要越簡單越好」：

- **單頁應用**：左半邊輸入表單，右半邊預覽 + 下載按鈕
- **欄位即時驗證**：輸入時顯示綠色 ✓ / 紅色 ✗
- **產生按鈕**：在所有必填欄位通過驗證前保持 disabled
- **錯誤訊息**：明確指出哪一欄、為什麼錯
- **不需要的元素**：登入、設定、歷史紀錄、使用者資料 — v1 都不做

## 6. 技術架構

| 層級 | 技術 | 備註 |
|---|---|---|
| 前端 | Next.js（App Router） | TypeScript、Tailwind CSS（建議） |
| 後端 | Python | FastAPI（建議，因相依 OpenAPI 自動產生） |
| CAD 函式庫 | ezdxf / OpenCASCADE / FreeCAD API | 於 `/speckit-plan` 階段決選 |
| 通訊 | HTTP REST API（local 環境）：`POST /api/flange/preview`、`POST /api/flange/dwg`、`POST /api/flange/pdf` | 三個端點皆無狀態，request body 皆為 7 欄位 JSON |
| 預覽格式 | SVG（伺服器端產生） | 預覽 endpoint 即時回傳，不持久化 |
| PDF 產生 | 無限制（所見即所得） | 以同一份 SVG 嵌入 PDF 即可（建議 weasyprint，但不強制） |
| 部署 | Local 開發環境 | v1 僅在開發者本機執行；雲端/Docker 列為後續階段 |

### API 草案（無狀態設計）

三個端點皆接收**相同的 7 欄位 JSON**，後端依當下請求即時生成、回傳，**不持久化任何結果**：

```
POST /api/flange/preview      → 回傳 SVG（image/svg+xml）
POST /api/flange/dwg          → 回傳 DWG R2000（application/acad）
POST /api/flange/pdf          → 回傳 PDF（application/pdf）

Common Request Body:
{
  "inner_diameter_mm": 100.00,
  "pcd_mm": 150.00,
  "outer_diameter_mm": 200.00,
  "bolt_hole_count": 8,
  "bolt_hole_diameter_mm": 12.00,
  "thickness_mm": 20.00,
  "material": "SS400"
}

Success Response (200):
  Content-Type 對應上述格式之一，body 即為檔案內容（適合直接觸發瀏覽器下載）

Error Response (400):
{
  "errors": [
    { "field": "pcd_mm", "message": "PCD must be greater than inner diameter" }
  ]
}
```

**前端流程**：
1. 表單通過驗證後，呼叫 `/preview` 取得 SVG，內嵌顯示於右半邊
2. 「下載 DWG」按鈕 = 觸發 `POST /api/flange/dwg`，瀏覽器直接下載
3. 「下載 PDF」按鈕 = 觸發 `POST /api/flange/pdf`，瀏覽器直接下載

**SS400 鎖定**：後端收到 `material` 不為 `"SS400"` 時 MUST 回 400 錯誤。

## 7. 已確認決策

| # | 議題 | 決議 |
|---|---|---|
| 1 | 材質欄位 | **v1 僅 SS400（鎖定）**；其他材質列入後續階段 |
| 2 | 預覽方式 | **方案 A**：伺服器端 SVG 2D 工程圖 |
| 3 | DWG 標註語系 | **英文** |
| 4 | 第一孔角度 | **0°（+X 軸）** — 沿用 Constitution 預設值（待客戶反映才調整） |
| 5 | 檔案保留 | **不保留** — 完全無狀態，每次請求即時生成 |
| 6 | 歷史紀錄 | **不做** — v1 無歷史清單 |
| 7 | 部署環境 | **Local 開發環境** — v1 僅本機跑 |
| 8 | 數值精度 | **小數點第 2 位** |
| 9 | 單位顯示 | **統一在區塊標題標示「mm」**，不在每欄位後標 |
| 10 | 浮水印位置 | **全部皆放**：DWG / SVG 預覽 / PDF 都有 |
| 11 | PDF 紙張大小 | **統一 A4 直式** — 不依尺寸自動切換 |
| 12 | PDF 規格表格式 | **純表格** — 無公司 Logo、無報價單版型 |
| 13 | PDF 生成方式 | **無限制（所見即所得）** — 預覽 SVG 即 PDF 主圖內容 |
| 14 | PDF 產生時機 | **按下載時才產生** — 不在預覽階段預先生成 |

## 8. 範圍外（明確不做）

- SS400 以外的材質（鎖死於 v1）
- 多階法蘭、異形法蘭、橢圓法蘭
- 3D 預覽、第三方 DWG viewer
- DWG / PDF 圖面標註中文
- 第一孔起始角度的客製化
- 雲端／Docker／Electron 部署
- 多人並行、登入、帳號權限
- 歷史紀錄、模型版本控管、變更歷史
- 自動套用 ASME/JIS/CNS 標準表
- 公差表格（依 Constitution 待客戶提供後升版）
- 直接送 CAM/加工系統
- PDF 自動依尺寸切換紙張、附公司 Logo / 報價單版型
- 持久化儲存產生結果

## 9. 驗收標準

第一階段完成的定義：

- [ ] 業務可在 ≤ 30 秒內輸入完 7 個欄位（材質欄位預鎖 SS400 不可改）
- [ ] 送出後 ≤ 5 秒可看到 SVG 預覽，圖面標註為英文
- [ ] 點擊「下載 DWG」≤ 3 秒開始下載，檔案為 R2000 格式且可被 AutoCAD 開啟
- [ ] 點擊「下載 PDF」≤ 3 秒開始下載，可在 macOS Preview、Chrome、Acrobat Reader、iPad 開啟
- [ ] PDF 為 A4 直式、含法蘭工程圖、7 欄位純表格、浮水印
- [ ] DWG、SVG 預覽、PDF 三者皆含「For Customer Preview Only — Not for Manufacturing」浮水印
- [ ] DWG、PDF 圖面皆以英文標註全部 7 個欄位數值
- [ ] 所有數值欄位接受小數點 2 位
- [ ] 任一欄位錯誤輸入皆有明確錯誤訊息（中文 UI 提示）
- [ ] 後端完全無狀態，重啟伺服器後不留任何檔案
- [ ] 通過 Constitution v2.1.0 Quality Gates §1–§6 全部檢查

---

**下一步**：確認 §7 待澄清項目 → 執行 `/speckit-specify` 產出正式 spec.md
