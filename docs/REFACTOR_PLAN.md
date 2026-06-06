# 嘉義市知識庫 — 重構開發規劃 v2

> 建立日期：2026-06-06
> 基於 Phase 0-9 完成後的全面盤點與重構計畫
> 前次規劃：docs/DEVELOPMENT_PLAN.md (Phase 6-9，已結案)

---

## 📊 現況摘要

| 模組 | 狀態 | 問題 |
|------|------|------|
| ETL Pipeline | ✅ 可用 | data/raw/ 空的，processed CSV 是舊樣本 |
| 歷年歲入 (106-114) | ⚠️ 部分 | datasources.yml 有定義但 normalizer 沒處理 |
| 基金 3 類 | ❌ 缺漏 | 作業/營業/政事基金 normalizer 缺失 |
| 分類映射 | ⚠️ 有問題 | policy_domain 不一致、agency_map 覆蓋率低 (14/30+) |
| 前端 (15 頁) | ⚠️ 需重構 | 導覽擁擠、資訊架構混亂、KPI 硬編碼 |
| 設計系統 | ❌ 無 | 顏色/字體/間距不一致、無元件庫 |
| 錯誤處理 | ❌ 無 | 無空資料、載入、錯誤狀態 |
| 測試 | ✅ 33 支 | 通過 |

---

## 🗓️ 開發期程

### Phase 1：資料層建設 🔴

**目標：** 跑通真實資料流，補齊缺失 normalizer

| # | 任務 | 優先 | 預估 | 狀態 |
|---|------|------|------|------|
| 1-1 | `python -m etl.main run --force` 抓真實資料 | P0 | 30m | ✅ |
| 1-2 | 補 歷年歲入 normalizer (106-114) | P0 | 1h | ✅ |
| 1-3 | 補 基金 normalizer（作業/營業/政事） | P0 | 1h | ✅ |
| 1-4 | 驗證每張表資料品質、寫 validation report | P1 | 1h | ✅ |

**驗收標準：** data/raw/ 有真實 CSV、processed 表完整、validator 全 pass

---

### Phase 2：分類映射修正 🟡

**目標：** 統一政策分類、擴大機關覆蓋率、加信心度標記

| # | 任務 | 優先 | 預估 | 狀態 |
|---|------|------|------|------|
| 2-1 | 統一 policy_domain — 修正「經濟發展/交通支出」不一致 | P0 | 1h | ✅ |
| 2-2 | 建立 domain_classifier.py + CLI classify 命令 | P0 | 1h | ✅ |
| 2-3 | 擴充 agency_policy_map.csv 覆蓋所有 30+ 機關 | P1 | 2h | ⬜ |
| 2-4 | 增加信心度標記（confidence: high/medium/low） | P1 | 2h | ⬜ |
| 2-5 | 產出分類彙總表並驗證 | P1 | 1h | ⬜ |

**驗收標準：** 所有 function_category 有 policy_domain、agency 覆蓋率 >90%、信心度標記完備

**已知問題：**
- policy_domain_map.csv 第 4 行：`經濟發展支出` 歸 `economic_development + road`，但 L2 `交通支出` 另歸 `transport_infrastructure + hardware + road` — 需統一

---

### Phase 3：前端資訊架構重設計 🔵

**目標：** 15 頁面 → 6 大區塊，重寫導覽，定義每個頁面的職責

| # | 任務 | 優先 | 預估 | 狀態 |
|---|------|------|------|------|
| 3-1 | 定義 6 大區塊與對應頁面 | P0 | 1h | ⬜ |
| 3-2 | 重寫導覽列（sidebar/breadcrumb） | P0 | 1h | ⬜ |
| 3-3 | 定義每個頁面的職責（what it answers） | P1 | 1h | ⬜ |
| 3-4 | 路由重整（合併/拆分頁面） | P1 | 1h | ⬜ |
| 3-5 | Wireframe 每個區塊的佈局 | P2 | 1h | ⬜ |

**6 大區塊（初步規劃）：**

| 區塊 | 頁面 | 職責 |
|------|------|------|
| 🏠 概覽 Dashboard | Dashboard | 全市 KPI、趨勢摘要、快速導航 |
| 👥 人口 Population | Population, Comparison | 人口結構、趨勢、跨縣市比較 |
| 💰 財政 Budget | Budget, Funds, Policy | 預算結構、基金、政策領域分析 |
| 🏗️ 建設 Infrastructure | Infrastructure, Traffic, WaterSafety | 基礎建設、交通、水安全 |
| 🏛️ 議會 Council | Council, Briefing, Strategy | 議會議題、簡報、策略建議 |
| 📖 敘事 Narratives | Narratives | 故事線、深度分析 |

**驗收標準：** 導覽 ≤6 項、每個頁面有明確職責定義、路由正確

---

### Phase 4：設計系統與元件庫 🟣

**目標：** 統一視覺語言，建立可複用元件庫

| # | 任務 | 優先 | 預估 | 狀態 |
|---|------|------|------|------|
| 4-1 | 定義色系（primary/secondary/semantic） | P0 | 1h | ⬜ |
| 4-2 | 定義字階（h1-h6/body/caption） | P0 | 0.5h | ⬜ |
| 4-3 | 定義間距系統（4px base grid） | P0 | 0.5h | ⬜ |
| 4-4 | 建立 Card 元件（KPI、圖表、表格容器） | P1 | 2h | ⬜ |
| 4-5 | 建立 DataTable 元件（排序/搜尋/分頁） | P1 | 3h | ⬜ |
| 4-6 | 建立 ChartWrapper 元件（tooltip/legend/responsive） | P1 | 2h | ⬜ |
| 4-7 | 建立 Loading/Error/Empty 狀態元件 | P1 | 2h | ⬜ |
| 4-8 | 建立 Navigation 元件（sidebar + breadcrumb） | P2 | 1h | ⬜ |

**驗收標準：** 所有元件有 props 文件、chromatic 視覺一致、無硬編碼樣式

---

### Phase 5：頁面逐一重構 🟠

**目標：** 用設計系統重寫每個頁面

| # | 頁面 | 預估 | 狀態 |
|---|------|------|------|
| 5-1 | Dashboard — KPI 卡片 + 趨勢迷你圖 + 快速導航 | 2h | ⬜ |
| 5-2 | Population — 年齡金字塔 + 趨勢 + 結構分析 | 2h | ⬜ |
| 5-3 | Budget — 歲入/歲出表格 + 政策領域分析 | 2h | ⬜ |
| 5-4 | Policy — 政策領域視覺化 + 信心度篩選 | 2h | ⬜ |
| 5-5 | Infrastructure — 建設總覽 + 地圖/列表 | 2h | ⬜ |
| 5-6 | Traffic — 交通數據 + 趨勢 | 1.5h | ⬜ |
| 5-7 | WaterSafety — 水安全指標 | 1.5h | ⬜ |
| 5-8 | Council — 議會議題 + 追蹤 | 2h | ⬜ |
| 5-9 | Funds — 基金儀表板 | 2h | ⬜ |
| 5-10 | Comparison — 跨縣市比較 | 2h | ⬜ |
| 5-11 | Narratives — 敘事頁模板 | 2h | ⬜ |
| 5-12 | Briefing — 簡報模式 | 1.5h | ⬜ |
| 5-13 | Strategy — 策略建議 | 1.5h | ⬜ |

**驗收標準：** 每頁用設計系統元件、無硬編碼 KPI、有 Loading/Error/Empty 狀態

---

### Phase 6：建置驗收與部署 ⚪

**目標：** 確保 build 成功、資料正確、部署穩定

| # | 任務 | 優先 | 預估 | 狀態 |
|---|------|------|------|------|
| 6-1 | `npm run build` 成功無 error | P0 | 0.5h | ⬜ |
| 6-2 | 驗證 dist/ 有所有 JSON + 頁面 | P0 | 0.5h | ⬜ |
| 6-3 | 本地開 dist/ 逐頁檢查 | P1 | 2h | ⬜ |
| 6-4 | Netlify 部署 + 線上驗證 | P1 | 1h | ⬜ |
| 6-5 | ETL → JSON → 前端 end-to-end 測試 | P1 | 2h | ⬜ |
| 6-6 | 更新 README + SDD 文件 | P2 | 1h | ⬜ |
| 6-7 | Git tag v2.0 | P2 | 5m | ⬜ |

**驗收標準：** build 成功、Netlify 部署、所有頁面可瀏覽、資料即時

---

## 📐 設計原則

1. **現有架構不動** — 三層分離（ETL → Markdown → Web）已驗證可行
2. **增量改善** — 每次改動不超過一個 module，確保可回退
3. **測試先行** — 新功能必須附測試
4. **文件同步** — 每個 phase 完成更新此文件 + README

---

## ✅ 完成追蹤

| Phase | 開始 | 完成 | 備註 |
|-------|------|------|------|
| Phase 1 | 2026-05-26 | 2026-05-26 | ETL + normalizer + validation |
| Phase 2 | 2026-06-06 | ⬜ 進行中 | domain_map + classify 完成，agency_map 待擴充 |
| Phase 3 | ⬜ | ⬜ | |
| Phase 4 | ⬜ | ⬜ | |
| Phase 5 | ⬜ | ⬜ | |
| Phase 6 | ⬜ | ⬜ | |

---

## 📎 相關文件

- [系統設計文件](SDD.md)
- [部署說明](deployment.md)
- [前次開發規劃](DEVELOPMENT_PLAN.md)（Phase 6-9，已結案）
