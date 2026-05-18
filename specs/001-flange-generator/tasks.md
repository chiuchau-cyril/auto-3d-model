---
description: "Task list for 001-flange-generator implementation"
---

# Tasks: 鼓風機入口法蘭 DWG 產生器

**Input**: Design documents from `/specs/001-flange-generator/`

**Prerequisites**: plan.md (✓), spec.md (✓), research.md (✓), data-model.md (✓),
contracts/openapi.yaml (✓), quickstart.md (✓)

**Tests**: Included. Reason: spec acceptance scenarios (US1/US2) MUST be verifiable,
and Constitution v2.1.0 mandates 6 自動化 Quality Gates。

**Organization**: Tasks grouped by user story (US1, US2), both priority P1 and together
form MVP. Within each story: tests → models/services → endpoints → UI integration。

---

## Format

`- [ ] [TaskID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[US1]/[US2]**: Maps task to user story for traceability
- All file paths are repo-root relative

---

## Path Conventions

- Backend root: `backend/`
- Frontend root: `frontend/`
- Specs: `specs/001-flange-generator/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 建立前後端 scaffolding 與工具鏈，確保開發環境可運作。

- [ ] T001 Create monorepo structure with `backend/` and `frontend/` directories at repo root
- [ ] T002 [P] Initialize Python 3.11 venv and create `backend/requirements.txt` with fastapi, uvicorn[standard], pydantic, ezdxf[drawing], reportlab, svglib, pytest, pytest-asyncio, httpx, ruff
- [ ] T003 [P] Configure `backend/pyproject.toml` with ruff lint/format rules and pytest config (test paths, async mode, coverage)
- [ ] T004 [P] Initialize Next.js 15 App Router project in `frontend/` with TypeScript, Tailwind CSS, ESLint, and Vitest + Playwright dev deps
- [ ] T005 [P] Create `frontend/.env.local.example` with `NEXT_PUBLIC_API_BASE=http://localhost:8000` and `frontend/tailwind.config.ts`
- [ ] T006 [P] Add ODA File Converter installation check script at `backend/scripts/check_oda.sh` that verifies `ODAFC_EXEC_PATH` is set and executable; mirror to `backend/scripts/check_oda.ps1`
- [ ] T007 [P] Create `backend/README.md` and `frontend/README.md` referencing `specs/001-flange-generator/quickstart.md`

**Checkpoint**: 兩端皆可獨立啟動 dev server，ODA check 通過。

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Pipeline 各環節共用的純資料與純函式層；不含 IO 與外部呼叫。

**⚠️ CRITICAL**: US1 / US2 implementation 開始前必須完成此 Phase。

### Backend Foundational

- [ ] T008 [P] Create Pydantic `FlangeSpecification` model in `backend/src/models/flange_spec.py` per data-model.md (7 fields, Literal["SS400"] material, model_validator for geometry rules)
- [ ] T009 [P] Define DXF layer constants in `backend/src/lib/layers.py`: OUTLINE, HOLES, CENTERLINE, DIM, ANNOTATION, WATERMARK with colors per data-model.md
- [ ] T010 [P] Implement geometry helpers in `backend/src/lib/geometry.py`: `bolt_hole_positions(pcd_mm, count)` returning list of (x, y) tuples evenly distributed from 0° on +X axis (Constitution II)
- [ ] T011 [P] Define watermark text constant `"For Customer Preview Only — Not for Manufacturing"` in `backend/src/lib/watermark.py` plus helpers `insert_dxf_watermark(doc)`, `insert_svg_watermark(svg_bytes)` placeholders
- [ ] T012 [P] Implement filename helper in `backend/src/lib/filename.py`: `build_filename(spec, ext, now)` returns `flange_{inner}x{outer}_PCD{pcd}_{count}H_{thickness}t_{YYYYMMDDTHHMMSS}.{ext}` per FR-017
- [ ] T013 Create FastAPI app skeleton in `backend/src/main.py` with CORS middleware (allow `http://localhost:3000`), error handler returning `{errors: [{field, message}]}` format per openapi.yaml
- [ ] T014 [P] Create structured error response helpers in `backend/src/api/responses.py`: `validation_error_response()`, `oda_unavailable_response()`, `internal_error_response()` matching openapi.yaml ErrorResponse schema

### Frontend Foundational

- [ ] T015 [P] Define zod schema in `frontend/src/lib/schema.ts` mirroring `FlangeSpecification` (positive numbers, max 2 decimal places, integer constraints, material literal "SS400")
- [ ] T016 [P] Generate TypeScript types in `frontend/src/types/flange.ts` from `specs/001-flange-generator/contracts/openapi.yaml` (or hand-write matching the schema)
- [ ] T017 [P] Implement API client wrappers in `frontend/src/lib/api.ts`: `fetchPreviewSvg(spec)`, `downloadDwg(spec)`, `downloadPdf(spec)`, `checkHealth()` using fetch with proper Content-Type
- [ ] T018 [P] Create base layout in `frontend/src/app/layout.tsx` with Traditional Chinese `lang="zh-Hant"` and `frontend/src/app/globals.css` with Tailwind directives

**Checkpoint**: 後端可啟動但 endpoints 尚空；前端可開啟空白頁；schema 雙端對齊。

---

## Phase 3: User Story 1 — 業務即時產出法蘭預覽 (Priority: P1) 🎯 MVP

**Goal**: 業務輸入 7 個欄位 → 點擊「產生」→ 5 秒內於右側看見含英文標註與浮水印的 SVG 法蘭工程圖。

**Independent Test**: 開瀏覽器 → 填入 (100, 150, 200, 8, 12, 20, SS400) → 點「產生」→ 看到法蘭圖。
不需下載即可驗證。對應 spec.md US1 acceptance scenarios 1–3。

### Tests for User Story 1 (Write FIRST, ensure they FAIL before implementation)

- [ ] T019 [P] [US1] Unit test for `FlangeSpecification` validation rules in `backend/tests/unit/test_flange_spec.py`: 合法輸入、PCD ≤ 內徑、孔徑過大、material ≠ SS400、小數位超過 2 位（涵蓋 FR-002, FR-005, FR-007, FR-008）
- [ ] T020 [P] [US1] Unit test for `geometry.bolt_hole_positions` in `backend/tests/unit/test_geometry.py`: 孔數 1 / 4 / 8 / 64、第一孔角度為 0°、均勻分布（FR-018）
- [ ] T021 [P] [US1] Contract test for `POST /api/flange/preview` in `backend/tests/contract/test_preview.py`: 回應 Content-Type=image/svg+xml、status 200 含 SVG、400 含 ErrorResponse schema
- [ ] T022 [P] [US1] Contract test for `GET /api/health` in `backend/tests/contract/test_health.py`: 回應含 status、oda_converter_available 兩欄位
- [ ] T023 [P] [US1] Unit test for `dxf_builder.build_dxf_document` in `backend/tests/unit/test_dxf_builder.py`: 驗證輸出 doc 含 OUTLINE/HOLES/DIM/ANNOTATION/WATERMARK 各 layer、entity 數量符合預期、dxfversion 為 R2000
- [ ] T024 [US1] Integration test US1 happy path in `backend/tests/integration/test_us1_preview.py`: 完整 request → SVG 字串含浮水印英文文字、含 7 個欄位數值的英文標註（grep 字串檢查）
- [ ] T025 [P] [US1] Frontend unit test for `FlangeForm` in `frontend/tests/unit/FlangeForm.test.tsx`: 缺填禁用提交按鈕、即時錯誤訊息為繁中、material 欄位 disabled 為 SS400
- [ ] T026 [P] [US1] Frontend E2E test us1 in `frontend/tests/e2e/us1-preview.spec.ts` (Playwright)，覆蓋 spec.md US1 acceptance scenarios 1, 2, 3

### Implementation for User Story 1

**後端 — DXF Pipeline 核心**

- [ ] T027 [US1] Implement annotations helper in `backend/src/lib/annotations.py`: 英文標註樣式定義（text height, offsets, ANSI dim style）、`add_dimensions(doc, spec)` 將 7 欄位以英文標註到 DIM/ANNOTATION layer
- [ ] T028 [US1] Implement `build_dxf_document(spec)` in `backend/src/services/dxf_builder.py`: 建立 ezdxf Drawing（dxfversion='R2000'、`$INSUNITS=4` mm）、設定 layers (T009)、繪製外徑/內徑/PCD 虛線/中心線/孔位（用 T010）/標註（T027）/浮水印（T011）—— 滿足 FR-018, FR-019, Constitution II/III
- [ ] T029 [US1] Implement SVG renderer in `backend/src/services/svg_renderer.py`: 用 `ezdxf.addons.drawing` 將 doc 轉 SVG bytes，回傳 utf-8 encoded SVG（含浮水印於 WATERMARK layer 自然渲染）
- [ ] T030 [US1] Implement `POST /api/flange/preview` route in `backend/src/api/routes.py`: 接收 FlangeSpecification、呼叫 build_dxf_document + render_svg、回傳 Response(content=svg_bytes, media_type="image/svg+xml")
- [ ] T031 [US1] Implement `GET /api/health` route in `backend/src/api/routes.py`: 檢查 `ODAFC_EXEC_PATH` 環境變數與檔案存在性，回 `{status: "ok", oda_converter_available: bool, version: "1.0.0"}`
- [ ] T032 [US1] Wire routes into FastAPI app in `backend/src/main.py` (T013) via `app.include_router()`

**前端 — 表單與預覽**

- [ ] T033 [P] [US1] Implement `FlangeForm` component in `frontend/src/components/FlangeForm.tsx`: 7 個欄位（材質 disabled = SS400）、繁中 label、即時 zod 驗證、提交鈕禁用直到所有欄位有效、區塊標題標示 "（單位：mm）"（FR-009/FR-024）
- [ ] T034 [P] [US1] Implement `ErrorBanner` component in `frontend/src/components/ErrorBanner.tsx`: 顯示後端回傳的英文 errors 並對應到繁中欄位名（如 pcd_mm → 「PCD」）
- [ ] T035 [US1] Implement `PreviewPane` component in `frontend/src/components/PreviewPane.tsx`: 接收 SVG 字串 props，用 `dangerouslySetInnerHTML` 渲染，含 loading / empty 兩狀態（US2 階段會加下載按鈕）
- [ ] T036 [US1] Wire main page in `frontend/src/app/page.tsx`: 左右分欄（form / preview）、useState 管理 spec + svg + error、點「產生」呼叫 `api.fetchPreviewSvg` 後 setState 更新 PreviewPane

**Checkpoint**: US1 完整可用。執行 T026 E2E 應通過。MVP 達成（可僅展示，不可下載）。

---

## Phase 4: User Story 2 — 提供客戶可攜的 DWG 與 PDF 檔案下載 (Priority: P1)

**Goal**: 業務於預覽完成後可分別點「下載 DWG」與「下載 PDF」取得兩種可攜檔案，
DWG 為 R2000 含英文標註，PDF 為 A4 直式含工程圖 + 純表格 + 浮水印。

**Independent Test**: 完成 US1 預覽後，點下載 DWG → 用 AutoCAD/DraftSight 開啟成功；
點下載 PDF → 在 macOS Preview/Acrobat 開啟成功，第一頁含圖+規格表+浮水印。
對應 spec.md US2 acceptance scenarios 1–4。

### Tests for User Story 2

- [ ] T037 [P] [US2] Contract test for `POST /api/flange/dwg` in `backend/tests/contract/test_dwg.py`: 回應 Content-Type=application/acad、Content-Disposition 含 attachment + 檔名規則 (FR-017)、二進位 prefix 為 R2000 DWG magic header (`AC1015`)
- [ ] T038 [P] [US2] Contract test for `POST /api/flange/pdf` in `backend/tests/contract/test_pdf.py`: 回應 Content-Type=application/pdf、Content-Disposition 含 attachment + 檔名規則、二進位 prefix 為 `%PDF-`
- [ ] T039 [P] [US2] Unit test for filename helper in `backend/tests/unit/test_filename.py`: 整數/小數值、極端值、timestamp 格式驗證 (FR-017)
- [ ] T040 [US2] Integration test US2 download in `backend/tests/integration/test_us2_download.py`: 同一規格分別呼叫 /dwg 與 /pdf，DWG 可被 `ezdxf.readfile` 重新載入無例外；PDF 可被 `pypdf` 讀取且頁數 = 1
- [ ] T041 [P] [US2] Frontend E2E test us2 in `frontend/tests/e2e/us2-download.spec.ts` (Playwright)，覆蓋 spec.md US2 acceptance scenarios 1, 2, 4（含「修改欄位但未產生就下載」case）

### Implementation for User Story 2

**後端 — DWG / PDF 匯出**

- [ ] T042 [US2] Implement DWG exporter in `backend/src/services/dwg_exporter.py`: `export_dwg(doc) -> bytes` 使用 `ezdxf.addons.odafc.export_dwg` 寫入暫存檔（`tempfile.NamedTemporaryFile`）→ 讀回 bytes → 刪除暫存 (FR-013, FR-020)，包裝 ODA 失敗為 503 例外
- [ ] T043 [US2] Implement PDF renderer in `backend/src/services/pdf_renderer.py`: `render_pdf(spec, svg_bytes) -> bytes`，用 svglib 將 SVG → reportlab Drawing，組 A4 SimpleDocTemplate（svg 上半頁 + Table 規格 + 時間 + 對角浮水印 30% 透明），回 bytes (FR-014, FR-016)
- [ ] T044 [US2] Implement `POST /api/flange/dwg` route in `backend/src/api/routes.py`: 呼叫 build_dxf_document → export_dwg → Response(content=bytes, media_type="application/acad", headers={"Content-Disposition": f'attachment; filename="{filename}"'}) 用 T012 產 filename
- [ ] T045 [US2] Implement `POST /api/flange/pdf` route in `backend/src/api/routes.py`: build_dxf_document → render_svg → render_pdf → Response(media_type="application/pdf", attachment header)
- [ ] T046 [US2] Add ODA 503 error handler in `backend/src/main.py` to catch `OdaConverterNotInstalled` and return helpful English message per openapi.yaml 503 response

**前端 — 下載按鈕**

- [ ] T047 [US2] Extend `PreviewPane` in `frontend/src/components/PreviewPane.tsx` to add 「下載 DWG」與「下載 PDF」兩個按鈕（只在 svg 已存在時顯示），點擊呼叫 `api.downloadDwg(spec)` / `api.downloadPdf(spec)` 觸發瀏覽器下載
- [ ] T048 [US2] Implement download trigger helper in `frontend/src/lib/download.ts`: 將 fetch 回傳的 Blob 轉 object URL 並用 `<a download>` 觸發；自動釋放 URL；從 Content-Disposition header 萃取檔名
- [ ] T049 [US2] Wire download buttons to `frontend/src/app/page.tsx`: 將當下 form spec 而非 svg cache 傳給 download API（FR-022 確保「下載按下時為真」）

**Checkpoint**: US1 + US2 全部可用，業務完整 MVP 流程：填表 → 預覽 → 下載 DWG/PDF。

---

## Phase 5: Constitution Quality Gates

**Purpose**: 自動化驗證 Constitution v2.1.0 §1–§6 六項 Quality Gates，每次 commit 前 run。
所有檢查皆以 backend 為主，每個 gate 獨立檔案、可並行執行。

- [ ] T050 [P] Implement Quality Gate §1 (DWG version) in `backend/tests/quality_gates/test_dwg_version.py`: 產生 DWG → `ezdxf.readfile` 後 `assert doc.dxfversion == 'AC1015'`（R2000 識別碼）
- [ ] T051 [P] Implement Quality Gate §2 (DWG openable) in `backend/tests/quality_gates/test_dwg_openable.py`: 三組規格各產 DWG → `ezdxf.readfile` 不拋例外
- [ ] T052 [P] Implement Quality Gate §3 (geometry integrity) in `backend/tests/quality_gates/test_geometry_integrity.py`: `doc.audit()` 結果 error/warning 計數為 0；自訂多邊形封閉檢查
- [ ] T053 [P] Implement Quality Gate §4 (dimension consistency) in `backend/tests/quality_gates/test_dimension_consistency.py`: 從 DWG 反向萃取 OUTLINE 圓 / HOLES 圓 / 厚度 ANNOTATION，與輸入比對容忍 0.01 mm（FR-019、Constitution §4）
- [ ] T054 [P] Implement Quality Gate §5 (hole positions) in `backend/tests/quality_gates/test_hole_positions.py`: 萃取 HOLES 圖層孔中心座標，驗證距原點 = PCD/2、第一孔角度 0°、相鄰孔角度差 = 360°/n
- [ ] T055 [P] Implement Quality Gate §6 (structural consistency) in `backend/tests/quality_gates/test_structural_consistency.py`: 同 spec 連跑兩次，比對 layer 名稱集合、各 layer entity 數量、7 個尺寸欄位反向萃取結果完全相同

**Checkpoint**: 6 個 quality gates 全綠燈。Constitution v2.1.0 合規。

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: edge cases、SLO 效能驗證、文件、整體 walk-through。

- [ ] T056 [P] Edge case tests for extreme dimensions in `backend/tests/integration/test_edge_cases.py`: 極小法蘭 (1, 3, 5, 1, 0.5, 2 mm)、極大法蘭 (500, 750, 1000, 32, 30, 50 mm)、孔數 = 1、孔數 = 64（spec.md Edge Cases）
- [ ] T057 [P] SLO performance test in `backend/tests/integration/test_performance.py`: /preview 95% < 5 秒（SC-002），/dwg 與 /pdf 95% < 3 秒（SC-003）；用 pytest-benchmark 或 manual timing
- [ ] T058 [P] Frontend responsive check in `frontend/tests/e2e/responsive.spec.ts`: viewport 1366×768 與 768×1024、1024×768，UI 可用（FR-027）
- [ ] T059 [P] Polish 繁中錯誤訊息對映表 in `frontend/src/lib/error-messages.ts`: 後端英文 errors 對映到繁中描述，含所有 FR-005 / FR-006 規則
- [ ] T060 [P] Update `backend/README.md` 與 `frontend/README.md` 補上「以 quickstart.md 為主要文件」與最小 npm/uvicorn 啟動指令
- [ ] T061 Run end-to-end walk-through against `specs/001-flange-generator/quickstart.md` Steps 1–8，逐項勾選；找到落差就回該 phase 補 task
- [ ] T062 Run full test suite (backend pytest + frontend vitest + playwright + quality_gates) on a clean checkout 確認綠燈

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: 無依賴，可立即開始
- **Phase 2 (Foundational)**: 依賴 Phase 1 完成；BLOCKS 所有 US
- **Phase 3 (US1)**: 依賴 Phase 2 完成；可獨立交付為 SVG-only MVP
- **Phase 4 (US2)**: 依賴 Phase 2 完成，**且** 依賴 US1 的 `dxf_builder` (T028) 完成（兩者共用 DXF Document），但可在 US1 完成前就先準備 US2 的測試 T037–T041
- **Phase 5 (Quality Gates)**: 依賴 US1 + US2 全部實作完成
- **Phase 6 (Polish)**: 依賴前面所有 Phase

### Within Each User Story

- Tests MUST be written and FAIL before corresponding implementation tasks
- 後端 models / lib 先於 services 先於 routes
- 前端 schema / types 先於 components 先於 page

### Parallel Opportunities

**Phase 1**: T002, T003, T004, T005, T006, T007 全部 [P] 可並行（不同檔案）

**Phase 2**:
- 後端 [P]: T008, T009, T010, T011, T012, T014（純檔案各異）
- 前端 [P]: T015, T016, T017, T018（純檔案各異）
- T013 必須最後做（依賴 T014 的 helpers）

**Phase 3 Tests**: T019, T020, T021, T022, T023, T025, T026 全部 [P]（T024 整合測試需 dxf 邏輯就緒）

**Phase 3 Impl**: T027 → T028（依賴）；T029 依賴 T028；T030/T031 依賴 services；
T033/T034 [P]；T035 依賴 T034；T036 依賴 T033/T035

**Phase 4 Tests**: T037, T038, T039, T041 [P]；T040 依賴整合層就緒

**Phase 4 Impl**: T042 / T043 [P]（不同檔案）；T044 依賴 T042、T045 依賴 T043；
T047 / T048 [P]；T049 依賴 T047/T048

**Phase 5**: T050–T055 全部 [P]（六個獨立檔案）

**Phase 6**: T056–T060 [P]；T061、T062 序列收尾

---

## Parallel Example: Phase 2 Foundational

```bash
# 後端純函式層平行展開：
Task: "T008 Pydantic FlangeSpecification model in backend/src/models/flange_spec.py"
Task: "T009 DXF layer constants in backend/src/lib/layers.py"
Task: "T010 Geometry helpers in backend/src/lib/geometry.py"
Task: "T011 Watermark constant + helpers in backend/src/lib/watermark.py"
Task: "T012 Filename helper in backend/src/lib/filename.py"

# 同時前端 scaffolding 平行展開：
Task: "T015 zod schema in frontend/src/lib/schema.ts"
Task: "T016 TypeScript types in frontend/src/types/flange.ts"
Task: "T017 API client wrappers in frontend/src/lib/api.ts"
Task: "T018 Base layout in frontend/src/app/layout.tsx"
```

---

## Implementation Strategy

### MVP-Only Path (僅 US1)

若需要最快 demo（僅展示，不下載）：

1. Phase 1 完成
2. Phase 2 完成
3. Phase 3 完成
4. **STOP and DEMO**：業務可填表 → 預覽，但無 DWG/PDF 下載
5. Phase 5 §3 (geometry integrity) + §5 (hole positions) 即可保證圖正確

### Full MVP Path (US1 + US2 — 建議)

1. Phase 1 + 2 完成
2. Phase 3 (US1) 完成 → SVG 預覽可用
3. Phase 4 (US2) 完成 → DWG/PDF 下載可用
4. Phase 5 全部 Quality Gates 綠燈
5. Phase 6 polish + walk-through
6. **READY**：第一階段交付完成

### Parallel Team Strategy

兩位開發者：

- 一位主攻後端：Phase 1 (T002, T003, T006) → Phase 2 backend (T008–T014) → US1 backend (T019–T024, T027–T032) → US2 backend (T037–T040, T042–T046) → Quality Gates
- 一位主攻前端：Phase 1 (T004, T005, T007) → Phase 2 frontend (T015–T018) → US1 frontend (T025, T026, T033–T036) → US2 frontend (T041, T047–T049) → Polish T058, T059
- 會合點：Phase 1 結束 / US1 結束 / US2 結束 / 全部完成

---

## Notes

- [P] = 不同檔案、無未完成相依
- [US1] / [US2] 標籤對應 spec.md user stories
- 測試 MUST FAIL 才能進入對應 implementation（紅燈先於綠燈）
- 每完成一個 task 立即 commit 與勾選
- Edge cases (spec.md) 集中在 T056 一次涵蓋
- 與 Constitution v2.1.0 Quality Gates 嚴格對應於 Phase 5
- 避免：模糊任務、共用檔案的並行衝突、跨故事相依破壞獨立可測試性
