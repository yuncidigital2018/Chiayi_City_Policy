# Phase 3：前端資訊架構重設計

> 建立日期：2026-06-06

---

## 現有頁面盤點

| 頁面 | 路由 | 內容 | 問題 |
|------|------|------|------|
| Dashboard | / | 6 KPI + 4 圖表 | 資訊密度適中，但缺乏導航入口 |
| Population | /population | 金字塔 + 趨勢 + 老化分析 | 功能完整 |
| Budget | /budget | 歲入/歲出 + 樹狀圖 | 政策領域分析缺 |
| Funds | /funds | 3 類基金 | 獨立性高 |
| Comparison | /comparison | 跨縣市比較 | 跟 Population 分離，導航不明確 |
| Narratives | /narratives | 敘事文字 | 缺互動 |

**共計 6 頁，非 15 頁。**

---

## 新資訊架構：5 區塊

| 區塊 | 圖示 | 頁面 | 職責（它回答什麼問題） |
|------|------|------|----------------------|
| 概覽 | 🏠 | Dashboard | 「嘉義市現在怎麼樣？」— 全市 KPI + 趨勢摘要 + 快速導航 |
| 人口 | 👥 | Population | 「人口結構如何？」— 金字塔、老化、趨勢 |
| 人口 | 👥 | Comparison | 「跟其他縣市比如何？」— 跨縣市排名 |
| 財政 | 💰 | Budget | 「錢花在哪？」— 歲入/歲出結構、政事別 |
| 財政 | 💰 | Policy | 「政策領域怎麼分？」— 政策領域分析 + 信心度 |
| 財政 | 💰 | Funds | 「基金狀況如何？」— 3 類基金儀表板 |
| 敘事 | 📖 | Narratives | 「數據說了什麼故事？」— 敘事分析 |
| 關於 | ℓ️ | About | 「資料從哪來？」— 資料源、方法論、更新頻率 |

---

## 導覽設計

### Sidebar（桌面）+ Bottom Tab（行動）

```
┌─────────────────────────────────────────┐
│ 🏛 嘉義市政                    [sidebar] │
├──────┬──────────────────────────────────┤
│      │                                  │
│ 🏠   │  頁面內容                         │
│ 概覽  │                                  │
│      │                                  │
│ 👥   │                                  │
│ 人口  │  └ Population                    │
│      │  └ Comparison                    │
│      │                                  │
│ 💰   │                                  │
│ 財政  │  └ Budget                        │
│      │  └ Policy                        │
│      │  └ Funds                         │
│      │                                  │
│ 📖   │                                  │
│ 敘事  │                                  │
│      │                                  │
│ ℹ️   │                                  │
│ 關於  │                                  │
│      │                                  │
└──────┴──────────────────────────────────┘
```

### 行動端 Bottom Tab

```
┌─────────────────────────────────────────┐
│ 🏠 概覽 │ 👥 人口 │ 💰 財政 │ 📖 敘事 │ ℹ️ │
└─────────────────────────────────────────┘
```

---

## 路由規劃

| 路由 | 頁面 | 區塊 |
|------|------|------|
| `/` | Dashboard | 概覽 |
| `/population` | Population | 人口 |
| `/population/comparison` | Comparison | 人口 |
| `/budget` | Budget | 財政 |
| `/budget/policy` | Policy | 財政 |
| `/budget/funds` | Funds | 財政 |
| `/narratives` | Narratives | 敘事 |
| `/about` | About | 關於 |

---

## 每頁職責定義

### Dashboard (`/`)
- **它回答：** 「嘉義市現在怎麼樣？」
- **內容：** 6 個 KPI 卡片（人口、自然增減、社會增減、歲入、歲出、性別比）+ 4 個迷你圖表
- **互動：** 點 KPI 卡片 → 跳轉對應詳細頁
- **資料來源：** population_annual.json, budget_revenue_by_source.json, budget_expenditure_by_function.json

### Population (`/population`)
- **它回答：** 「人口結構如何變化？」
- **內容：** 年齡金字塔、老化指數、人口趨勢、自然/社會增減
- **互動：** 年份切換、金字塔 tooltip
- **資料來源：** population_age_gender.json, population_annual.json

### Comparison (`/population/comparison`)
- **它回答：** 「嘉義市在全國的定位？」
- **內容：** 跨縣市人口排名、密度比較、嘉義市高亮
- **互動：** 排序切換（人口/密度）
- **資料來源：** county_population_comparison.json

### Budget (`/budget`)
- **它回答：** 「錢從哪來、花去哪？」
- **內容：** 歲入來源、歲出政事別（L1/L2 樹狀）、經常/資本門
- **互動：** 樹狀展開、金額格式切換
- **資料來源：** budget_revenue_by_source.json, budget_expenditure_by_function.json

### Policy (`/budget/policy`)
- **它回答：** 「政策領域怎麼分配？」
- **內容：** 14 個政策領域彙總、信心度標記、機關別對照
- **互動：** 信心度篩選、領域點擊展開
- **資料來源：** budget_by_policy_domain.json, budget_agency_by_domain.json

### Funds (`/budget/funds`)
- **它回答：** 「基金財務狀況如何？」
- **內容：** 3 類基金（政事型/作業/營業）預算明細
- **互動：** 基金類型切換
- **資料來源：** fund_affairs.json, fund_operating.json, fund_business.json

### Narratives (`/narratives`)
- **它回答：** 「數據背後的故事是什麼？」
- **內容：** 人口挑戰、財政結構、政策建議等敘事
- **互動：** 無（純文字 + 數據引用）
- **資料來源：** 所有 JSON

### About (`/about`)
- **它回答：** 「這些資料從哪來？怎麼更新？」
- **內容：** 資料源列表、更新頻率、方法論、技術架構
- **互動：** 無
- **資料來源：** 靜態內容

---

## 實施順序

1. **3-1** ✅ 定義 6 大區塊與對應頁面（本文件）
2. **3-2** 建立 Sidebar 元件 + Breadcrumb
3. **3-3** 重寫路由（App.jsx）
4. **3-4** 建立 Policy 頁面（新）
5. **3-5** 建立 About 頁面（新）
6. **3-6** 更新所有頁面的 breadcrumb 導航
