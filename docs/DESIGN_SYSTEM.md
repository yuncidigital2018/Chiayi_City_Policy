# 嘉義市政儀表板 — 設計系統 v1.0

> Phase 4 建立，統一視覺語言

---

## 色系 (Color Palette)

### Primary
| Token | Hex | 用途 |
|-------|-----|------|
| `--primary` | `#2563eb` | 主色、連結、按鈕 |
| `--primary-dark` | `#1d4ed8` | hover 狀態 |
| `--primary-light` | `#eff6ff` | 背景高亮 |

### Semantic
| Token | Hex | 用途 |
|-------|-----|------|
| `--success` | `#10b981` | 正向、成長、通過 |
| `--danger` | `#ef4444` | 負向、減少、錯誤 |
| `--warning` | `#f59e0b` | 警告、注意 |
| `--info` | `#06b6d4` | 資訊 |

### Neutral
| Token | Hex | 用途 |
|-------|-----|------|
| `--bg` | `#f8fafc` | 頁面背景 |
| `--card-bg` | `#ffffff` | 卡片背景 |
| `--text` | `#1e293b` | 主文字 |
| `--text-muted` | `#64748b` | 次要文字 |
| `--border` | `#e2e8f0` | 邊框 |

### Chart Colors（依序使用）
```
#2563eb, #10b981, #f59e0b, #ef4444, #8b5cf6,
#ec4899, #06b6d4, #84cc16, #f97316, #6366f1,
#14b8a6, #a855f7, #64748b, #78716c
```

---

## 字階 (Typography)

| Token | Size | Weight | Line-height | 用途 |
|-------|------|--------|-------------|------|
| `h1` | 24px | 700 | 1.3 | 頁面標題 |
| `h2` | 20px | 600 | 1.4 | 區塊標題 |
| `h3` | 15px | 600 | 1.4 | 卡片標題 |
| `body` | 14px | 400 | 1.6 | 內文 |
| `body-sm` | 13px | 400 | 1.5 | 輔助文字 |
| `caption` | 12px | 500 | 1.4 | 標籤、表格 header |
| `kpi-value` | 28px | 700 | 1.2 | KPI 數字 |
| `kpi-label` | 13px | 500 | 1.4 | KPI 標籤 |

---

## 間距 (Spacing)

4px base grid：

| Token | Value | 用途 |
|-------|-------|------|
| `--space-1` | 4px | 最小間距 |
| `--space-2` | 8px | 緊湊間距 |
| `--space-3` | 12px | 元素內 padding |
| `--space-4` | 16px | 卡片間距 |
| `--space-5` | 20px | 區塊間距 |
| `--space-6` | 24px | 頁面 padding |
| `--space-8` | 32px | 大區塊分隔 |

---

## 圓角 (Border Radius)

| Token | Value | 用途 |
|-------|-------|------|
| `--radius-sm` | 6px | 按鈕、badge |
| `--radius` | 8px | 卡片、輸入框、工作型儀表板容器 |
| `--radius-full` | 9999px | 膠囊形 |

---

## 陰影 (Shadow)

| Token | Value | 用途 |
|-------|-------|------|
| `--shadow` | `0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06)` | 卡片預設 |
| `--shadow-md` | `0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.06)` | hover、浮動 |

---

## 元件清單

| 元件 | 檔案 | 用途 |
|------|------|------|
| Card | `components/Card.jsx` | KPI、圖表、表格容器 |
| DataTable | `components/DataTable.jsx` | 排序/搜尋/分頁表格 |
| ChartWrapper | `components/ChartWrapper.jsx` | 圖表容器 + 狀態處理 |
| StatusMessage | `components/StatusMessage.jsx` | Loading/Error/Empty 狀態 |
| Sidebar | `components/Sidebar.jsx` | 側邊導覽（Phase 3） |
| Breadcrumb | `components/Breadcrumb.jsx` | 麵包屑（Phase 3） |
| DataQualityBar | `components/DataQualityBar.jsx` | 全站資料狀態與 schema 健康摘要 |
| SegmentedControl | `components/SegmentedControl.jsx` | 頁內分析視角切換 |

## 資料狀態與互動規範

- 入口型 KPI 可使用 `KPICard to="/path"` 連往對應分析頁。
- 涉及多種判讀視角的頁面使用 `SegmentedControl`，例如人口時間序列與財政歲出視角。
- 所有資料表由 `config/data_catalog.json` 定義契約，build 後產出 `public/data/catalog.json`。
- 預算金額資料欄位單位為「千元」，前端顯示億元時以 `amount / 100000` 計算。
