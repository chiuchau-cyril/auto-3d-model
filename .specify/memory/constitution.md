<!--
SYNC IMPACT REPORT
==================
Version change: 2.0.0 → 2.1.0
Bump rationale: MINOR — 原則 IV 必填欄位清單擴充（新增「厚度」），
                屬於 materially expanded guidance，不改變原則用途與精神，
                依規則升 MINOR。同步源自 docs/req/req-1.md v0.2 第一階段需求。

Modified principles:
- IV. 文字輸入規格化 — 必填欄位由 6 個擴為 7 個（新增「厚度 Thickness」）

Unchanged principles:
- I. 業務交付優先 (Customer-Facing Delivery First)
- II. 標準合規 (Standards Compliance, NON-NEGOTIABLE)
- III. DWG 輸出可驗證 (Verifiable DWG Output)
- V. 結構一致性 (Structural Consistency)

Modified sections:
- Quality Gates §4 — 尺寸合理性比對範圍補上「厚度」

Removed sections:
- 無

Templates requiring updates:
- ⚠ .specify/templates/plan-template.md — Constitution Check 仍待補入專案閘門
- ⚠ .specify/templates/spec-template.md — Functional Requirements 應反映 7 個必填欄位
- ⚠ .specify/templates/tasks-template.md — 任務類別暫不需要嚴格精度驗證任務
- ✅ .specify/memory/constitution.md — updated (this file)
- ✅ docs/req/req-1.md — 已同步 (v0.2)

Deferred items / TODOs:
- TODO(TOLERANCE_TABLE): 客戶提供的工程公差表格尚未到位；到位後 MUST 觸發 MAJOR 升版，
  將原則 I 與 V 升級回嚴格精度與可重現性控管，並補回對應的 Quality Gate。
- CAD library 选定 deferred to /speckit-plan phase (候選: ezdxf, OpenCASCADE,
  FreeCAD Python API)。
- Governance/amendment workflow 仍依使用者指示不納入。

Historical:
- 1.0.0 (2026-05-18) Initial ratification — 工程精度導向。
- 2.0.0 (2026-05-18) Pivot — 改為業務交付導向，放寬精度與一致性要求。
- 2.1.0 (2026-05-18) 新增「厚度」必填欄位。
-->

# Auto 3D Model — Blower Inlet Flange Generator Constitution

## Core Principles

### I. 業務交付優先 (Customer-Facing Delivery First)

此模型於現階段的用途為**業務人員提供給客戶**作為法蘭結構展示、規格確認與報價依據，
**非**用於最終生產加工或檢圖。產出 MUST 在外觀與比例上正確反映輸入規格，使客戶能直觀
辨識法蘭主要結構（內徑、外徑、PCD、孔位、孔數），但於此階段**不**要求嚴格工程公差或
浮點級精度控管。

明訂限制：

- 數值轉換可採合理的浮點實作，無 1e-6 mm 容忍上限要求
- 視覺呈現（如倒角、圓角細節）允許以合理近似呈現
- 此模型 MUST NOT 被宣稱或使用為加工依據；輸出檔或附屬資訊中 SHOULD 標示「For Customer
  Preview Only — Not for Manufacturing」

**升版觸發條件**: 客戶提供工程公差表格後，本原則 MUST 升級為嚴格精度控管，並觸發 MAJOR
版本升級。

**Rationale**: 業務階段優先「能快速向客戶溝通法蘭規格」而非「能直接送加工」。提早綁定
嚴格精度反而增加開發成本與交付時程，且無公差表時無法定義「夠精準」的閾值。

### II. 標準合規 (Standards Compliance, NON-NEGOTIABLE)

- 所有尺寸 MUST 使用公制單位（mm），且於模型與輸出中明確標註單位
- 禁止隱式單位換算；若輸入含英制需求，MUST 由呼叫端先行換算並標明
- 螺栓孔數、孔徑、PCD MUST 與輸入規格完全一致；不可自動套用「最接近的標準法蘭」
- 孔位 MUST 以 PCD 圓周均布，第一孔的角度起點需有一致規範（預設 0° 於 +X 軸）

**Rationale**: 此專案不假設使用者一定遵循 ASME/JIS/CNS 任一具名標準——使用者輸入即為
規格真值。標準的角色是約束「如何呈現」而非「呈現什麼」。即使用途為業務展示，孔數、
孔徑、PCD 等可被客戶肉眼核對的欄位仍 MUST 完全忠於輸入。

### III. DWG 輸出可驗證 (Verifiable DWG Output)

- 輸出檔 MUST 為 AutoCAD R2000 (.dwg) 版本
- 輸出檔 MUST 可被 AutoCAD 及主流 CAD 軟體（如 BricsCAD、DraftSight、FreeCAD）開啟而無錯誤
- 幾何 MUST 通過自動化檢查：封閉實體、無破面、無自相交、無零厚度面
- 圖層 (Layer)、單位 (mm)、座標原點 (0,0,0 於法蘭中心、Z 軸垂直法蘭面) MUST 採一致規範
- 模型 MUST 包含可辨識的中繼資料（輸入規格摘要）作為 DWG 附屬資訊或同名 sidecar 檔

**Rationale**: DWG R2000 為相容性最廣的中介格式，可被舊版 AutoCAD 與多數第三方 CAD
讀取；幾何驗證與一致原點規範確保客戶端開啟、檢視、組裝不需手動修整。

### IV. 文字輸入規格化 (Structured Text Input)

必要輸入欄位（缺一不可）：

1. 內徑 (Inner Diameter, mm)
2. PCD (Pitch Circle Diameter, mm)
3. 外徑 (Outer Diameter, mm)
4. 孔數 (Bolt Hole Count, integer ≥ 1)
5. 孔徑 (Bolt Hole Diameter, mm)
6. 厚度 (Thickness, mm)
7. 材質 (Material, 預設 SS400)

規則：

- 缺漏任一非預設欄位時，系統 MUST 回拒並回報缺漏欄位清單，禁止任何形式的猜測或預設值替代
- 僅「材質」欄位允許套用預設值 SS400；其餘欄位無預設
- 幾何合理性 MUST 在生成前驗證：內徑 < PCD < 外徑；孔徑 < (外徑 − PCD)/2 與 (PCD − 內徑)/2
- 不合理輸入 MUST 以明確錯誤訊息回拒，不得自動修正

**Rationale**: 法蘭設計錯誤的最常見來源是「填表者漏填、系統補預設」。明確拒絕勝過默默猜測。

### V. 結構一致性 (Structural Consistency)

相同輸入文字 MUST 產生**結構一致**的 DWG：拓樸結構相同、孔數相同、主要尺寸欄位
（內徑、外徑、PCD、孔徑）於合理範圍內一致。此階段**不**要求位元組級或 1e-6 mm 級的
精確一致；只要客戶在比對兩次產出時能辨識為「同一規格」即可。

**升版觸發條件**: 客戶提供工程公差表格後，本原則 MUST 升級為嚴格幾何級可重現性
（同拓樸、同浮點精度），並觸發 MAJOR 版本升級。

**Rationale**: 業務階段重視「能向客戶重複展示同一規格的可辨識模型」，無需達到工程審圖
等級的位元組一致；過嚴會增加實作成本而未產生對應價值。

## Technology Constraints

- **DWG 版本**: AutoCAD R2000 (固定，不允許其他版本作為主要輸出)
- **程式語言**: Python（版本於 /speckit-plan 階段確定）
- **CAD 函式庫**: 候選 ezdxf、OpenCASCADE (pythonocc)、FreeCAD Python API；最終選擇 MUST 滿足
  「能輸出 R2000 .dwg」與「能進行基本幾何驗證」兩項硬性條件
- **單位系統**: 公制 mm，全程一致
- **座標系**: 法蘭中心為原點 (0,0,0)，Z 軸垂直法蘭面，孔位起始於 +X 軸 0°
- **用途標示**: 產出 SHOULD 標示「For Customer Preview Only — Not for Manufacturing」

## Quality Gates

每個生成的模型於交付前 MUST 通過下列自動化檢查：

1. **DWG 版本檢查**: 確認輸出檔為 R2000 格式
2. **可開啟性檢查**: 以函式庫重新載入輸出 DWG 不得拋出例外
3. **幾何完整性檢查**: 封閉實體、無破面、無自相交、無零厚度
4. **尺寸合理性比對**: 從輸出 DWG 反向萃取內徑、外徑、PCD、孔數、孔徑、厚度，與輸入規格在
   合理範圍內一致（具體容忍值待工程公差表格提供）
5. **孔位驗證**: 孔數正確、PCD 圓周均布、第一孔位於規範角度
6. **結構一致性檢查**: 同一輸入連續執行兩次，產出之拓樸結構與主要尺寸欄位 MUST 一致

任一檢查未通過，產出 MUST 視為失敗，不得交付。

**Version**: 2.1.0 | **Ratified**: 2026-05-18 | **Last Amended**: 2026-05-18
