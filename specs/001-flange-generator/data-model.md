# Data Model — 001-flange-generator

**Date**: 2026-05-18
**Status**: Phase 1 design

無持久化儲存。所有實體存在於單一 HTTP 請求生命週期內。

---

## Entity: FlangeSpecification

使用者輸入的完整法蘭規格。對應 Pydantic model 與前端表單 schema。

### Fields

| Field | Type | Unit | Constraint | Source |
|---|---|---|---|---|
| `inner_diameter_mm` | float | mm | > 0；≤ 2 位小數；< `pcd_mm` | FR-001, FR-003, FR-004, FR-005 |
| `pcd_mm` | float | mm | > `inner_diameter_mm`；< `outer_diameter_mm`；≤ 2 位小數 | FR-005 |
| `outer_diameter_mm` | float | mm | > `pcd_mm`；≤ 2 位小數 | FR-005 |
| `bolt_hole_count` | int | — | ≥ 1 | FR-005 |
| `bolt_hole_diameter_mm` | float | mm | > 0；< (`outer_diameter_mm` − `pcd_mm`)/2；< (`pcd_mm` − `inner_diameter_mm`)/2；≤ 2 位小數 | FR-005 |
| `thickness_mm` | float | mm | > 0；≤ 2 位小數 | FR-005 |
| `material` | enum | — | 固定值 `"SS400"`（v1） | FR-002 |

### Validation Rules（後端 Pydantic）

```python
class FlangeSpecification(BaseModel):
    inner_diameter_mm: Annotated[float, Field(gt=0, decimal_places=2)]
    pcd_mm: Annotated[float, Field(gt=0, decimal_places=2)]
    outer_diameter_mm: Annotated[float, Field(gt=0, decimal_places=2)]
    bolt_hole_count: Annotated[int, Field(ge=1)]
    bolt_hole_diameter_mm: Annotated[float, Field(gt=0, decimal_places=2)]
    thickness_mm: Annotated[float, Field(gt=0, decimal_places=2)]
    material: Literal["SS400"]

    @model_validator(mode="after")
    def check_geometry(self) -> Self:
        if not (self.inner_diameter_mm < self.pcd_mm < self.outer_diameter_mm):
            raise ValueError("Diameters must satisfy: inner < PCD < outer")
        max_hole_outer = (self.outer_diameter_mm - self.pcd_mm) / 2
        max_hole_inner = (self.pcd_mm - self.inner_diameter_mm) / 2
        if self.bolt_hole_diameter_mm >= min(max_hole_outer, max_hole_inner):
            raise ValueError(
                "Bolt hole diameter would overlap inner or outer edge"
            )
        return self
```

### Lifetime

- 由前端表單於送出時序列化為 JSON
- 後端 Pydantic 反序列化並驗證
- 用於產生 `FlangeRendering`
- 請求結束即丟棄，**不持久化**（FR-020）

---

## Entity: FlangeRendering

基於 `FlangeSpecification` 產生的可視化輸出集合。

### Fields（概念，非持久化）

| Field | Type | 對應產出 |
|---|---|---|
| `dxf_document` | `ezdxf.document.Drawing` | 中介 DXF（in-memory） |
| `svg_bytes` | bytes | `/preview` 回傳 |
| `dwg_bytes` | bytes | `/dwg` 回傳 |
| `pdf_bytes` | bytes | `/pdf` 回傳 |

### Generation Pipeline

```
FlangeSpecification
    │
    ├─► build_dxf_document() ─► ezdxf Drawing
    │       │
    │       ├─► render_svg()  ─► svg_bytes  ─► /preview response
    │       ├─► export_dwg()  ─► dwg_bytes  ─► /dwg response
    │       │       (via ezdxf.addons.odafc)
    │       └─► render_pdf()  ─► pdf_bytes  ─► /pdf response
    │               (svg_bytes → svglib → reportlab Drawing
    │                + spec table → A4 PDF)
    │
    └─► (request lifecycle ends, all in-memory data discarded)
```

### DXF Layer 規範（依 Constitution 原則 III）

| Layer Name | 內容 | 顏色 | 線型 |
|---|---|---|---|
| `OUTLINE` | 外徑、內徑圓 | white (7) | CONTINUOUS |
| `HOLES` | 螺栓孔圓 | white (7) | CONTINUOUS |
| `CENTERLINE` | PCD 虛線圓、中心十字線 | red (1) | DASHED |
| `DIM` | 尺寸標註（直徑、PCD） | yellow (2) | CONTINUOUS |
| `ANNOTATION` | 文字標註（厚度、孔數、材質、孔徑） | green (3) | — |
| `WATERMARK` | 浮水印文字 | gray (8) | — |

### 座標系（依 Constitution）

- 原點 (0, 0, 0) 於法蘭中心
- Z 軸垂直法蘭面
- 第一孔角度：0°（+X 軸正方向，逆時針均布）
- 單位：mm（`$INSUNITS = 4`）

### 浮水印規範

- 文字：`"For Customer Preview Only — Not for Manufacturing"`
- DWG：WATERMARK 圖層，灰色（color 8），文字旋轉 -30°，置於圖形中央
- SVG：同等位置與樣式
- PDF：A4 頁面對角浮水印，半透明 30%

### File Naming

依 FR-017：
```
flange_{內徑}x{外徑}_PCD{PCD}_{孔數}H_{厚度}t_{timestamp}.{dwg|pdf}

範例：flange_100x200_PCD150_8H_20t_20260518T143022.dwg
```

- 數值不含小數點時直接呈現；含小數點時以底線替代（避免檔名衝突）
- timestamp 格式：`YYYYMMDDTHHMMSS`（ISO 8601 basic format）

---

## State Transitions

```
[Empty Form]
    │  (使用者輸入)
    ▼
[Form Partially Filled] ──┐
    │                     │ (任何欄位變更)
    │  (所有必填皆有效)    │
    ▼                     │
[Form Valid] ─────────────┘
    │  (點擊「產生」)
    ▼
[Generating Preview]
    │  (POST /api/flange/preview)
    │  (5 秒內完成)
    ▼
[Preview Shown]
    │  (使用者點擊下載)
    ├─► (POST /api/flange/dwg)  ──► [DWG Downloaded]
    └─► (POST /api/flange/pdf)  ──► [PDF Downloaded]

任何狀態 ─► (頁面關閉) ─► [Stateless: 一切清除]
```

---

## 沒有的 Entity（明確排除）

依 FR-020 完全無狀態，**不**設計以下實體：

- `User` / `Session` — 無登入、無使用者識別
- `GenerationHistory` — 不記錄
- `GeneratedFile` — 不持久化檔案
- `Project` / `Folder` — 不分群
