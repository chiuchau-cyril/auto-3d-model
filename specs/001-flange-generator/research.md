# Phase 0 Research — 001-flange-generator

**Date**: 2026-05-18
**Status**: Complete — all NEEDS CLARIFICATION resolved
**Inputs**: spec.md, Constitution v2.1.0, req-1.md v0.4

本研究解決 plan.md Technical Context 中三項關鍵技術選型。

---

## Decision 1: CAD 函式庫（DWG R2000 與 SVG 產生）

**Decision**: 採用 **ezdxf** + **ezdxf 內建的 `odafc` add-on**（需配合 ODA File Converter）

### Rationale

- 任務本質為 **2D 對稱平面工程圖**（法蘭為平面件），不需要 3D B-rep solid modeling kernel
- ezdxf 為純 Python 套件，無系統級 C++ 依賴；安裝 `pip install ezdxf` 即可
- ezdxf 提供完整 DXF R2000 寫入支援（圖層、尺寸標註、線型、文字、實體區塊）
- `ezdxf.addons.odafc` 可呼叫本機安裝的 ODA File Converter 將 DXF 轉為 **DWG R2000**，滿足 Constitution 原則 III 硬性要求
- ezdxf 另提供 `ezdxf.addons.drawing` 模組，可將同一份 DXF Document 渲染為 SVG —— 達成 **三輸出同源**（FR-019）
- ezdxf 可直接讀回自己的輸出做幾何驗證（Quality Gate §2）

### Alternatives considered

| 方案 | 為什麼不選 |
|---|---|
| **OpenCASCADE (pythonocc)** | 3D B-rep kernel 過於 overkill；不原生輸出 DWG；C++ 依賴與安裝門檻高；單體應用啟動時間長 |
| **FreeCAD Python API** | 需完整 FreeCAD 安裝；不適合 headless server 進程；DWG 輸出仍需 LibreDWG/ODA 轉換 |
| **直接寫 DXF 不轉 DWG** | 違反 Constitution 原則 III「輸出 MUST 為 .dwg」與 FR-013 |
| **LibreDWG 直接寫 DWG** | Python binding 成熟度低；近年仍不時有 segfault 與 R2000 兼容性報告 |
| **AutoCAD COM/ObjectARX** | 需 Windows 與付費 AutoCAD 授權；違反「local 開發環境」與「免授權」隱含假設 |

### 風險與緩解

- **ODA File Converter 依賴**：使用者需於 local 環境另行安裝（macOS / Linux / Windows 皆有版本）
  - 緩解：quickstart.md 提供安裝指引；後端啟動時檢查可執行檔存在，缺失則回明確錯誤訊息
- **ODA 授權**：免費但禁止商用嵌入式發行
  - 緩解：v1 僅 local 環境使用，符合條款；雲端部署再評估替代方案

### 相依套件版本

- `ezdxf >= 1.3.0`（穩定 R2000 支援與 drawing add-on）
- `ODA File Converter >= 25.x`（持續更新）

---

## Decision 2: PDF 生成方式

**Decision**: 採用 **reportlab + svglib** 組合

### Rationale

- 使用者明示「PDF 規格表為**純表格**」「**無公司 Logo、無報價單版型**」「**所見即所得**」
- reportlab 是 Python 純套件、無系統依賴（不需 Cairo/Pango），安裝門檻最低
- reportlab 的 `platypus`（Table、Paragraph、SimpleDocTemplate）對純表格 PDF 是業界最簡實作
- svglib（`svg2rlg`）將 SVG 直接轉為 reportlab Drawing，可保留向量品質
- 三輸出同源原則：同一份 SVG 用於前端預覽 + 嵌入 PDF，視覺一致（FR-019）
- A4 直式為 reportlab 預設（`pagesize=A4`），無需自訂版型

### Alternatives considered

| 方案 | 為什麼不選 |
|---|---|
| **weasyprint (HTML→PDF)** | 系統依賴重（Pango、Cairo、GDK-PixBuf）；對純表格、無 HTML 排版需求是 overkill |
| **cairosvg 把 SVG 直接渲染為 PDF** | 只能輸出單一 SVG 為單頁 PDF；無法簡單加入下方規格表；需 Cairo 系統依賴 |
| **Playwright/Puppeteer 截圖 HTML 為 PDF** | 需 Chromium 安裝；啟動慢；對「3 秒內開始下載」（FR-014）SLO 不友善 |
| **fpdf2** | 對 SVG 支援不如 svglib + reportlab |

### PDF 結構

```
A4 直式單頁：
┌──────────────────────────────┐
│  [浮水印 字串 對角灰色文字]    │
│                              │
│  [法蘭 SVG 工程圖]            │
│   含 7 欄位英文標註           │
│                              │
│  ─────────────────────       │
│  Specification (純表格)       │
│   Inner Diameter      ◯◯ mm  │
│   PCD                 ◯◯ mm  │
│   Outer Diameter      ◯◯ mm  │
│   Bolt Hole Count     ◯◯     │
│   Bolt Hole Diameter  ◯◯ mm  │
│   Thickness           ◯◯ mm  │
│   Material            SS400  │
│                              │
│  Generated: 2026-05-18 14:30 │
│  For Customer Preview Only — │
│  Not for Manufacturing       │
└──────────────────────────────┘
```

### 相依套件版本

- `reportlab >= 4.1.0`
- `svglib >= 1.5.1`

---

## Decision 3: SVG 預覽生成方式

**Decision**: 採用 **ezdxf.addons.drawing** 從同一份 DXF Document 渲染 SVG

### Rationale

- 用 ezdxf 同一份 DXF document 渲染 SVG，**自動保證 SVG 與 DWG 同源**，滿足 Constitution 原則 V（結構一致性）與 spec FR-019
- ezdxf drawing add-on 以 matplotlib backend 輸出 SVG，可控制圖層顯隱、線寬、標註樣式
- 不需另寫 SVG 生成程式，減少程式碼量與不一致風險
- 渲染為純後端流程，回傳 SVG 字串即可直接內嵌前端 `<img>` 或 `dangerouslySetInnerHTML`

### Alternatives considered

| 方案 | 為什麼不選 |
|---|---|
| **svgwrite 程式化產生 SVG** | 需獨立維護一份 SVG 生成邏輯，與 DXF 邏輯雙軌易不一致 |
| **手工字串拼接 SVG** | 不可維護；標註位置計算複雜 |
| **DWG → SVG 用外部工具（如 LibreCAD CLI）** | 需額外進程；可能引入版本不一致 |
| **Three.js 在前端從 JSON 規格繪 SVG** | 邏輯下放前端意味前後端各維護一份繪圖規則；違反 FR-019 同源原則 |

### 相依

- `ezdxf[drawing]` 額外安裝 matplotlib 作為 backend
- `matplotlib >= 3.8.0`

---

## 衍生技術決策

### Python 版本

**Decision**: Python 3.11

- 與所有依賴（ezdxf、reportlab、svglib、FastAPI、matplotlib）兼容
- 同步穩定的型別系統（Self type、improved generics）
- 啟動速度比 3.10 快約 10%（PEP 659 specializing adaptive interpreter）

### Web Framework

**Decision**: **FastAPI** + **uvicorn**（dev server）

- 內建 Pydantic 模型驗證直接對應 FR-005、FR-007 的幾何合理性檢查
- 自動 OpenAPI schema 文件，方便前後端契約對齊
- 完全 async，符合三 endpoint 並行下載（FR-023）
- local 開發 `uvicorn main:app --reload` 一行起動

### 前端 Stack

**Decision**: **Next.js 15+ (App Router)** + **TypeScript** + **Tailwind CSS**

- App Router 對 React Server Components 與 Streaming 支援完整
- TypeScript 對前後端共用型別（透過 OpenAPI codegen）有利
- Tailwind 對「介面要越簡單越好」目標有助：少寫 CSS、樣式內嵌
- 不引入額外狀態管理（如 Redux/Zustand）——表單為單頁區域狀態，React `useState` 即足

### 測試框架

**Decision**:
- 後端：**pytest** + **pytest-asyncio**（FastAPI 端點測試用 `httpx.AsyncClient`）
- 前端：**Vitest** + **Playwright**（E2E 涵蓋 US1 + US2 兩條 P1 路徑）

### Linting / Formatting

- 後端：**ruff**（取代 black + isort + flake8，速度與設定簡潔）
- 前端：**ESLint** + **Prettier**（Next.js 預設）

### CAD 函式庫總相依（後端）

```
fastapi >= 0.115
uvicorn[standard] >= 0.32
pydantic >= 2.9
ezdxf >= 1.3
ezdxf[drawing]  # 引入 matplotlib
reportlab >= 4.1
svglib >= 1.5
# 外部工具：ODA File Converter（系統層安裝）
```

---

## Constitution 對齊檢核

| Constitution 要求 | 本研究的對應 |
|---|---|
| 原則 II 公制 mm 全程一致 | ezdxf header set `$INSUNITS=4`（mm）；所有座標以 mm 為單位 |
| 原則 II 孔位 PCD 圓周均布 | 後端服務以 `2π/n` 均分；第一孔 0°（+X 軸） |
| 原則 III DWG 必為 R2000 | ezdxf 寫 DXF 時指定 `dxfversion='R2000'`；odafc 轉檔指定 `outversion='R14'`（DWG R2000 對應 R14 數值）— 待實作時實測確認 |
| 原則 III 圖層、單位、原點一致 | 規範 layer 名稱（OUTLINE、HOLES、DIM、ANNOTATION、WATERMARK）；原點 (0,0,0) 於法蘭中心 |
| 原則 IV 7 必填欄位、缺漏回拒 | Pydantic model 全欄位 required，無 default（材質除外，UI 鎖定 SS400） |
| 原則 V 結構一致性 | 同源產出（DXF → DWG / SVG / PDF）天然保證 |
| Quality Gate §1 DWG 版本 | 寫檔後 ezdxf 重讀 `dxfversion`；odafc 結果以 ezdxf 重讀檢核 |
| Quality Gate §2 可開啟性 | 後端寫檔後 `ezdxf.readfile()` 與重新解析 |
| Quality Gate §3 幾何完整性 | ezdxf audit() 工具；對 outline 多邊形封閉性檢查 |
| Quality Gate §5 孔位驗證 | 萃取孔 entity 並驗證角度均布與 PCD 距離 |
| Quality Gate §6 結構一致性 | 同輸入連跑兩次，比對萃取的 7 欄位數值 |

---

## 仍待實作階段確認

- ezdxf `odafc.export_dwg(doc, path, version='R14')` 的 version 字串對應 R2000 — 文件版本字串對應需查官方文件實測
- 標註自動避讓（極小/極大法蘭、孔數極多）：先用 ezdxf dim 的預設 offset；若 user story P1 acceptance 失敗則進入 Phase 2 強化
- 浮水印於 DWG 中的呈現方式：選用「文字實體位於 WATERMARK 圖層 + 灰色 + 旋轉 -30°」

以上待 `/speckit-tasks` 階段轉為具體 task，再於實作驗證。

---

**Output for Phase 1**: 所有 Technical Context 不確定項已解決，可進入 data-model.md 與 contracts/ 設計。
