# 嘉義市人口與財政開放資料盤點、Markdown 知識庫與互動式網站系統開發交辦說明

## 1. 專案目標與輸出物

### 1.1 目標概述

本專案目標是針對嘉義市人口發展與市府預算（歲入、歲出）建立一套自動化的「資料 → Markdown 知識庫 → 互動式網站」系統，方便後續進行人口發展規劃、城市定位與財政情境分析。

重點：

- 從多個開放資料來源（嘉義市政府資料開放平台、戶政服務網、中央政府資料開放平台、內政部 STATCloud、主計處等）自動抓取人口與預算資料。
- 將原始資料清洗、整併為統一 schema，並用程式自動產出結構化的 Markdown 報告（分章節、分主題，如人口總量、區里人口、預算結構等）。
- 以這份 Markdown 知識庫為資料來源，產出一個互動式網站（儀表板＋敘事頁），可視化人口與預算結構，並保留文字說明。
- 系統設計要支援「排程更新」，定期重新抓資料並更新 Markdown 與網站。

### 1.2 主要輸出物

1. **資料層**
   - 清洗後的 CSV/Parquet（人口、預算相關表）。
   - ETL 腳本（抓取＋轉檔＋正規化）。

2. **內容層**
   - 一組以主題與年份分門別類的 Markdown 檔案（例如 population/overview.md, budget/revenue_structure.md 等）。

3. **應用層**
   - 一個互動式網站（單頁或多頁）：
     - 儀表板（人口趨勢、區里分布、預算結構、支出功能別、收入來源別）。
     - 敘事頁（城市定位、人口與財政重點敘事）。

4. **技術文件**
   - SDD（本檔案即為基礎）。
   - API/資料源設定檔（例如 `config/datasources.yml`）。
   - 部署與排程說明。

---

## 2. 現有資料盤點摘要（給系統開發參考）

> 以下只列「類型＋來源＋用途」，實際欄位與 OID/RID，請依來源網站 API 文件抓取。

### 2.1 資料來源總覽

1. **嘉義市政府資料開放平台（Open Chiayi）**
   - 網址：<https://data.chiayi.gov.tw>
   - 特性：每個資料集有 OID，提供檔案下載與 API (`opendata/api/getResource?oid=...&rid=...`)，並有開發指南。
   - 用途：歲入來源別預算總表、歲出機關別總表、東區人口各里統計、中低收入戶統計等主資料。

2. **中央政府資料開放平臺（data.gov.tw）**
   - 含「嘉義市總預算歲出政事別預算總表」、「嘉義市西區各里人口統計」等，與 Open Chiayi 有介接關係。

3. **嘉義市戶政服務網**
   - 網址：<https://household.chiayi.gov.tw>
   - 資料：本市人口即時數、歷年人口、區里戶數及人口數、戶籍登記分析表（含出生、死亡、遷入遷出、婚姻等）。

4. **內政部統計處 STATCloud（行政區人口統計）**
   - 提供縣市、鄉鎮市區、村里的戶數與人口數，支援 CSV/JSON/XML/GeoJSON 與 API。
   - 可用來做嘉義市 vs 其他縣市之比較。

5. **嘉義市政府主計處網站**
   - 「總預算」專區：年度預算書 PDF。
   - 「統計年報」、「統計月指標」：人口、財政與建設等指標。

6. **國網洞見（SCIDM）鏡像資料**
   - 「嘉義市總預算歲出機關別預算總表」、「嘉義市政府歲入來源別預算總表」等多年度 CSV。
   - 適合快速抓取 106 年起的歷年預算資料。

7. **媒體與新聞補充（敘事用）**
   - 例如 2026 年 1 月人口 261,682 人、淨遷入轉正但自然減少仍為負，報導中會引用市府數據，可做敘事輔助，不作為主數據源。

### 2.2 資料主題分類與用途

| 主題 | 來源 | 用途 |
|------|------|------|
| 人口總量與長期趨勢 | 戶政歷年人口、STATCloud | 嘉義市總人口變化、年增減率 |
| 區里尺度人口與空間分布 | 戶政區里戶數及人口數、東區/西區各里人口統計 | 東西區與各里人口分布地圖、人口密度、重要里別 |
| 人口結構與脆弱族群 | 戶籍登記分析表、中低收入戶統計、STATCloud | 高齡者、兒少、原住民、經濟弱勢的空間分布與變化 |
| 歲出預算 | 歲出政事別總表、歲出機關別總表、SCIDM 歷年 CSV | 教育、社福、建設等支出結構與局處預算比重、歷年變化 |
| 歲入預算 | 歲入來源別預算總表、SCIDM 歷年 CSV | 財源自主度、對中央補助依賴度、財政體質分析 |
| 基金與其他財政資料 | 營業基金、政事型基金預算資料集 | 特定事業（公車、停車場等）或專案的財政影響 |

---

## 3. 系統整體架構概念

### 3.1 高階架構（三層）

1. **資料層（Data Layer）**
   - 元件：Data Fetcher、Normalizer、Storage。
   - 工作：從各資料源抓取原始檔案（CSV、XML、XLS 轉換成 CSV）、標準化欄位、存到本地資料夾或簡易 DB（如 SQLite / DuckDB）。

2. **內容層（Content / Markdown Layer）**
   - 元件：Markdown Generator、Template Engine。
   - 工作：讀取整理後的資料表，依模板產出結構化 Markdown，分主題與年份存放。

3. **應用層（App / Web Layer）**
   - 元件：前端單頁應用（SPA 或 SSG），包含：
     - 儀表板：圖表與互動篩選。
     - 敘事頁：引用 Markdown 片段＋圖表。

### 3.2 技術建議

| 層 | 技術 | 說明 |
|----|------|------|
| ETL & Markdown 生成 | Python (pandas) | 優先 Python，處理資料清洗與 Markdown 產出 |
| 前端（靜態） | Astro / Next.js (SSG) + React | 偏靜態內容網站 |
| 前端（儀表板） | Vite + React | 偏單頁儀表板 |
| 圖表 | Chart.js / Recharts | 視框架選擇 |
| 部署 | Vercel / Netlify / 自家靜態伺服器 | CI/CD 自動 build |

---

## 4. SDD：Software Design Description

### 4.1 功能需求（FR）

| ID | 需求 | 說明 |
|----|------|------|
| FR-1 | 資料抓取與更新 | 從 Open Chiayi、data.gov.tw、戶政服務網、STATCloud 自動抓取指定資料集 |
| FR-2 | ETL 更新 | 支援重新執行（每日或每週） |
| FR-3 | 資料清洗彙整 | 將不同年度、不同來源資料整併成統一 schema |
| FR-4 | 邏輯表產出 | 產出 population_annual, population_district_village_monthly, population_structure, budget_revenue_by_source, budget_expenditure_by_function, budget_expenditure_by_agency |
| FR-5 | Markdown 生成 | 依章節架構自動產出 Markdown 檔案（含表格與關鍵指標） |
| FR-6 | 前端可解析 | Markdown 檔案要能被前端框架解析 |
| FR-7 | 互動儀表板 | 可選年份／區／主題的人口與預算儀表板 |
| FR-8 | 敘事頁 | 用 Markdown 文字解釋趨勢與城市定位 |
| FR-9 | RWD | 支援桌機與手機 |
| FR-10 | 排程更新 | 定期執行資料更新、Markdown 生成與前端重新 build/deploy |

### 4.2 非功能需求（NFR）

| ID | 需求 | 說明 |
|----|------|------|
| NFR-1 | 快取 fallback | API 失敗時採用上次成功的快取 |
| NFR-2 | 效能 | ETL + frontend build 在 10 分鐘內完成 |
| NFR-3 | 載入時間 | 前端首屏 3 秒內 |
| NFR-4 | 可維護性 | 程式碼可讀性高，適合後續維護 |

### 4.3 系統模組與責任

1. **DataSource Config 模組** — `config/datasources.yml`
2. **Data Fetcher 模組** — 讀取設定、HTTP 下載、儲存到 `data/raw/`
3. **Data Normalizer / ETL 模組** — 欄位對應、型別轉換、輸出到 `data/processed/`
4. **Markdown Generator 模組** — Jinja2 模板生成 Markdown 到 `content/`
5. **Web App / Frontend 模組** — 從 processed JSON 讀取資料，提供 `/`、`/population`、`/budget`、`/narratives`
6. **Scheduler / DevOps 模組** — CI/CD 或 crontab 觸發 pipeline

### 4.4 資料模型（簡化）

#### PopulationAnnual
| 欄位 | 類型 | 說明 |
|------|------|------|
| year | int | 年度 |
| total_population | int | 總人口 |
| male | int | 男性 |
| female | int | 女性 |
| natural_increase | int | 自然增減 |
| social_increase | int | 社會增減 |

#### PopulationVillageMonthly
| 欄位 | 類型 | 說明 |
|------|------|------|
| year | int | 年度 |
| month | int | 月份 |
| district | str | 東區/西區 |
| village | str | 里名 |
| households | int | 戶數 |
| population | int | 人口數 |

#### PopulationStructure
| 欄位 | 類型 | 說明 |
|------|------|------|
| year | int | 年度 |
| district | str | 區域 |
| age_group | str | 0-14, 15-64, 65+ |
| population | int | 人口數 |
| low_income_households | int | 中低收入戶數 |

#### BudgetRevenueBySource
| 欄位 | 類型 | 說明 |
|------|------|------|
| fiscal_year | int | 會計年度 |
| source_category | str | 地方稅、統籌分配款、補助款等 |
| amount | int | 金額（千元） |

#### BudgetExpenditureByFunction
| 欄位 | 類型 | 說明 |
|------|------|------|
| fiscal_year | int | 會計年度 |
| function_category | str | 教育、社福、建設等 |
| amount | int | 金額（千元） |

#### BudgetExpenditureByAgency
| 欄位 | 類型 | 說明 |
|------|------|------|
| fiscal_year | int | 會計年度 |
| agency_name | str | 機關名稱 |
| amount | int | 金額（千元） |

---

## 5. 開發分階段任務

### Phase 0：專案初始化 ✅
- [x] 建立 repo 與專案骨架
- [x] SDD 文件
- [x] 資料來源設定檔

### Phase 1：資料源設定與 ETL 架構 ✅
- [x] 整理所有資料源設定
- [x] 設計 ETL 腳本骨架
- [x] Data Fetcher 模組
- [x] Data Normalizer 模組

### Phase 2：資料抓取與清洗 ✅
- [x] 實作各資料源的 fetcher
- [x] 欄位標準化與統一 schema
- [x] 產出 processed CSV

### Phase 3：Markdown 知識庫 ✅
- [x] Jinja2 模板設計
- [x] Markdown Generator
- [x] 內容驗證

### Phase 4：互動式網站 ✅
- [x] 前端框架搭建
- [x] 儀表板頁面
- [x] 敘事頁
- [x] RWD 優化

### Phase 5：排程與部署 ✅
- [x] CI/CD pipeline
- [x] GitHub Actions monthly cron
- [x] Netlify 部署設定

### Phase 6：Bug 修復 & 品質強化 🔄
- [x] 修復 Narratives.jsx import bug
- [x] 修正 index.html title
- [x] 補上 favicon.svg
- [x] 更新 SDD checkbox
- [ ] 新增 etl/validator.py
- [ ] ETL 加 logging
- [ ] fetcher 加 retry

### Phase 7：測試覆蓋 ✅
- [x] normalizer unit tests (33 tests)
- [x] validator unit tests
- [x] ETL integration test (pipeline + retry)
- [x] CI 加入 test step

### Phase 8：功能擴展 ⬜
- [ ] STATCloud API 串接
- [ ] 前端年份/區域篩選器
- [ ] 多縣市架構抽象化
