# Implementation Plan: 鼓風機入口法蘭 DWG 產生器

**Branch**: `001-flange-generator` | **Date**: 2026-05-18 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-flange-generator/spec.md`

---

## Summary

業務人員透過 Next.js Web UI 輸入 7 個法蘭規格欄位，後端 Python (FastAPI) 服務即時產生
**同源三種輸出**：SVG 預覽（內嵌前端）、DWG R2000 檔、A4 直式 PDF。

核心技術手段：

- 後端用 **ezdxf** 建立一份共用 DXF Document
- 從同一份 DXF 衍生：SVG（`ezdxf.addons.drawing`）、DWG R2000（`ezdxf.addons.odafc` 呼叫
  本機 ODA File Converter）、PDF（svglib 把 SVG 轉 reportlab Drawing + reportlab 純表格組合 A4 頁面）
- 完全無狀態 API，三 endpoints 各自從相同 JSON 輸入即時產生對應輸出

詳細決策依據見 [research.md](./research.md)。

---

## Technical Context

**Language/Version**: Python 3.11（後端） + TypeScript 5.x / Node 20（前端）

**Primary Dependencies**:
- 後端：FastAPI 0.115+、uvicorn、Pydantic v2、ezdxf 1.3+（含 drawing & odafc add-on）、
  matplotlib（SVG backend）、reportlab 4.1+、svglib 1.5+
- 前端：Next.js 15+（App Router）、React 18+、Tailwind CSS、zod（前端 schema 驗證）
- 系統工具：ODA File Converter 25.x（DXF → DWG）

**Storage**: N/A — 完全無狀態（FR-020），所有產物 in-memory 處理後即丟棄

**Testing**:
- 後端：pytest + pytest-asyncio + httpx（API 契約測試）+ 自訂 quality gate 套件
- 前端：Vitest（單元）+ Playwright（E2E 涵蓋 US1、US2 主路徑）

**Target Platform**: Local 開發環境（macOS / Linux / Windows）；單機運行

**Project Type**: Web application（frontend + backend 雙專案）

**Performance Goals**:
- SVG 預覽：95% 請求 ≤ 5 秒（SC-002）
- DWG / PDF 下載：95% 請求 ≤ 3 秒開始回傳（SC-003）
- v1 無並發要求（單機單使用者）

**Constraints**:
- 無狀態：禁止任何持久化（FR-020）
- DWG 必為 R2000（Constitution III）
- 圖面英文標註（FR-025），UI 繁中（FR-024）
- 三輸出同源（FR-019）

**Scale/Scope**: 單一功能（法蘭產生器）；後端 ~5 endpoint；前端 1 頁；
預估 backend ~800 LOC、frontend ~500 LOC、tests ~600 LOC

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

對應 `.specify/memory/constitution.md` v2.1.0：

### 原則對齊

| 原則 | 計畫如何遵循 | Status |
|---|---|---|
| I. 業務交付優先 | 輸出三檔案皆標 "For Customer Preview Only — Not for Manufacturing" 浮水印；UI 不宣稱為加工依據 | ✅ PASS |
| II. 標準合規（NON-NEGOTIABLE） | DXF `$INSUNITS=4` 鎖 mm；孔位 `2π/n` 均分由 0° 起；UI 鎖 SS400 | ✅ PASS |
| III. DWG 輸出可驗證 | ezdxf → DXF R2000 → odafc → DWG R2000；後端 quality gate 重讀驗證 | ✅ PASS |
| IV. 文字輸入規格化 | Pydantic 7 必填欄位無預設（材質固定 SS400）；缺漏即 400；幾何檢查在 schema 層級 | ✅ PASS |
| V. 結構一致性 | 三輸出同源（同一份 DXF Document）→ 結構一致天然保證 | ✅ PASS |

### Quality Gates 對應（後端 tests/quality_gates/）

| Gate | 實作方式 |
|---|---|
| §1 DWG 版本檢查 | `ezdxf.readfile()` 後檢查 `doc.dxfversion == 'AC1015'`（R2000） |
| §2 可開啟性檢查 | 寫檔後 `ezdxf.readfile()` 不拋例外 |
| §3 幾何完整性 | `doc.audit()` 與自訂多邊形封閉性檢查 |
| §4 尺寸合理性 | 從 DXF 反向萃取 7 欄位，與 input 比對；容忍 0.01 mm（≤ 2 位小數輸入精度） |
| §5 孔位驗證 | 萃取 HOLES 圖層 entity，驗證角度與距離 |
| §6 結構一致性 | 同 input 跑兩次，比對 layer 與 entity 計數 |

### 違反項與正當化

無違反項。**Complexity Tracking** 表格留空。

---

## Project Structure

### Documentation (this feature)

```text
specs/001-flange-generator/
├── plan.md              # This file
├── research.md          # Phase 0 — 三項技術選型決策依據
├── data-model.md        # Phase 1 — FlangeSpecification、FlangeRendering 實體
├── quickstart.md        # Phase 1 — 開發者本機 setup 與驗證流程
├── contracts/
│   └── openapi.yaml     # Phase 1 — 3 endpoint + health check 契約
├── checklists/
│   └── requirements.md  # /speckit-specify 已產出
└── tasks.md             # 待 /speckit-tasks 階段產出
```

### Source Code (repository root)

```text
backend/
├── pyproject.toml              # ruff + pytest config
├── requirements.txt
├── README.md
├── src/
│   ├── main.py                 # FastAPI app + CORS + 3 routes
│   ├── api/
│   │   ├── routes.py           # /preview, /dwg, /pdf, /health handlers
│   │   └── responses.py        # streaming response helpers
│   ├── models/
│   │   └── flange_spec.py      # Pydantic FlangeSpecification
│   ├── services/
│   │   ├── dxf_builder.py      # build_dxf_document(spec) -> ezdxf.Drawing
│   │   ├── svg_renderer.py     # render_svg(doc) -> bytes
│   │   ├── dwg_exporter.py     # export_dwg(doc) -> bytes (via odafc)
│   │   ├── pdf_renderer.py     # render_pdf(spec, svg) -> bytes
│   │   └── filename.py         # 依 FR-017 產生 timestamp 檔名
│   └── lib/
│       ├── layers.py           # DXF layer 規範常數
│       ├── annotations.py      # 英文標註樣式與位置計算
│       ├── watermark.py        # 浮水印插入（DWG/SVG/PDF 共用）
│       └── geometry.py         # 孔位 2π/n 均分等幾何計算
└── tests/
    ├── conftest.py
    ├── contract/               # API 契約測試（依 openapi.yaml）
    │   ├── test_preview.py
    │   ├── test_dwg.py
    │   ├── test_pdf.py
    │   └── test_health.py
    ├── integration/            # 端對端流程（含 odafc 真實調用）
    │   ├── test_us1_preview.py
    │   └── test_us2_download.py
    ├── unit/                   # 純函式測試
    │   ├── test_flange_spec.py
    │   ├── test_geometry.py
    │   ├── test_filename.py
    │   └── test_dxf_builder.py
    └── quality_gates/          # Constitution §1–§6 自動化檢查
        ├── test_dwg_version.py
        ├── test_dwg_openable.py
        ├── test_geometry_integrity.py
        ├── test_dimension_consistency.py
        ├── test_hole_positions.py
        └── test_structural_consistency.py

frontend/
├── package.json
├── tsconfig.json
├── next.config.ts
├── tailwind.config.ts
├── .env.local.example
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx            # 單頁 UI（表單 + 預覽）
│   │   └── globals.css
│   ├── components/
│   │   ├── FlangeForm.tsx      # 7 欄位表單 + 即時驗證
│   │   ├── PreviewPane.tsx     # SVG 預覽 + 下載按鈕
│   │   └── ErrorBanner.tsx     # 繁中錯誤訊息顯示
│   ├── lib/
│   │   ├── schema.ts           # zod schema（與後端 Pydantic 對齊）
│   │   ├── api.ts              # 3 個 fetch 函式
│   │   └── filename.ts         # 下載觸發
│   └── types/
│       └── flange.ts           # TypeScript 型別（從 OpenAPI 衍生）
└── tests/
    ├── unit/
    │   ├── FlangeForm.test.tsx
    │   └── schema.test.ts
    └── e2e/
        ├── us1-preview.spec.ts
        └── us2-download.spec.ts

# Repo 根層級
docs/req/req-1.md               # 已存在（需求記錄）
specs/                          # 已存在
.specify/                       # 已存在
CLAUDE.md                       # 由本指令更新（指向 plan.md）
README.md                       # 已存在（待補使用說明 → /speckit-tasks）
```

**Structure Decision**: 採前後端分離 monorepo 結構（**backend/** + **frontend/**）。
理由：spec.md 明確要求前端 Next.js + 後端 Python；雙語系與不同 lifecycle；
便於分別在 local 跑 dev server。共用合約由 `specs/001-flange-generator/contracts/openapi.yaml`
作為單一真相來源，前端 `src/types/flange.ts` 可由 openapi.yaml 自動生成。

---

## Phase Plan

### Phase 0 (Complete)

- [research.md](./research.md) — 三項技術選型已決：ezdxf + odafc / reportlab + svglib /
  ezdxf drawing add-on

### Phase 1 (Complete)

- [data-model.md](./data-model.md) — `FlangeSpecification` Pydantic 設計、DXF Layer 規範、
  Pipeline、檔名規則
- [contracts/openapi.yaml](./contracts/openapi.yaml) — 3 endpoint + health check 完整契約
- [quickstart.md](./quickstart.md) — 含 ODA File Converter 安裝、雙端啟動、US1/US2 acceptance
  walk-through、Quality Gates 驗證
- CLAUDE.md updated（本指令）→ 指向 `specs/001-flange-generator/plan.md`

### Phase 2 (Pending — `/speckit-tasks`)

預計 task 群組：

- **Setup**: 後端 Python venv + requirements、前端 Next.js 初始化、ODA File Converter 安裝指引
- **Foundational**: Pydantic schema、DXF builder skeleton、CORS、layer 常數、檔名 helper
- **US1 (P1)**: SVG renderer、`/preview` endpoint、FlangeForm UI、PreviewPane、整合 E2E
- **US2 (P1)**: DWG exporter (odafc)、PDF renderer、`/dwg` + `/pdf` endpoints、下載按鈕、E2E
- **Quality Gates**: 六項自動化檢查實作於 `tests/quality_gates/`
- **Polish**: 錯誤訊息中英對齊、效能測試（SC-002/SC-003 SLO）、quickstart 驗證

---

## Constitution Check Re-evaluation (Post Phase 1)

Phase 1 設計後重新對齊：

| 檢查項 | Phase 1 對應 | Status |
|---|---|---|
| 三輸出同源 | data-model.md Pipeline 明確自一份 DXF 衍生 | ✅ |
| 圖層、單位、原點規範 | data-model.md 表格已列六個 Layer 與 `$INSUNITS=4` | ✅ |
| 7 欄位驗證 | data-model.md Pydantic `model_validator` 已具 | ✅ |
| API 契約反映 spec | openapi.yaml 三 endpoint + 錯誤回應對應 FR-006/FR-007 | ✅ |
| Quality Gates 可實作 | tests/quality_gates/ 結構於 Project Structure 明列 | ✅ |
| 浮水印對齊 | data-model.md 規範三輸出皆含浮水印 | ✅ |
| 無狀態 | openapi.yaml 三 endpoint 皆無 session/id；data-model.md 強調生命週期僅單一請求 | ✅ |

無新增違反項，Constitution Check 維持 PASS。

---

## Complexity Tracking

> 無 Constitution 違反項，本表留空。
