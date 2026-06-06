# Chiayi City Policy — 嘉義市人口與財政知識庫

> 自動化「資料 → 知識庫 → 互動式網站」系統

## 專案說明

針對嘉義市人口發展與市府預算（歲入、歲出）建立一套自動化系統：

1. 從多個開放資料來源自動抓取人口與預算資料
2. 清洗整併為統一 schema，自動產出結構化 Markdown 報告
3. 以 Markdown 知識庫為資料來源，產出互動式網站（儀表板＋敘事頁）
4. 支援排程更新

## 專案結構

```
├── config/
│   ├── datasources.yml           # 資料來源設定（API、scraper、歷年資料）
│   ├── policy_domain_map.csv     # 政事別 → 政策領域映射（30 筆）
│   └── agency_policy_map.csv     # 機關 → 政策領域映射（13 筆）
├── data/
│   ├── raw/                      # 原始抓取的資料
│   └── processed/                # 清洗後的 CSV（14 張表）
├── docs/
│   ├── SDD.md                    # 系統設計文件
│   ├── REFACTOR_PLAN.md          # 重構開發規劃
│   ├── DESIGN_SYSTEM.md          # 設計系統文件
│   └── PHASE3_ARCHITECTURE.md    # 資訊架構文件
├── content/                      # Markdown 知識庫
├── web/                          # Vite + React + Chart.js 前端
│   ├── src/
│   │   ├── components/           # 可複用元件（Sidebar, Card, DataTable, etc.）
│   │   └── pages/                # 頁面（Dashboard, Population, Budget, etc.）
│   └── dist/                     # 建置輸出
├── etl/                          # Python ETL pipeline
│   ├── main.py                   # CLI 入口
│   ├── domain_classifier.py      # 政策領域分類
│   └── ...
└── scripts/                      # 工具腳本
```

## 快速開始

```bash
# 安裝依賴
pip install -r requirements.txt
cd web && npm install

# 完整 pipeline
python -m etl.main run

# 分類映射
python -m etl.main classify

# 前端建置
cd web && npm run build

# 開發模式
cd web && npm run dev
```

## 資料來源

| 來源 | 用途 |
|------|------|
| [Open Chiayi](https://data.chiayi.gov.tw) | 歲入/歲出預算、區里人口 |
| [data.gov.tw](https://data.gov.tw) | 中央政府開放資料 |
| [戶政服務網](https://household.chiayi.gov.tw) | 人口即時數、歷年人口 |
| [STATCloud](https://segis.moi.gov.tw) | 行政區人口統計（跨縣市比較） |
| [主計處](https://account.chiayi.gov.tw) | 預算書 PDF、統計年報 |
| [SCIDM](https://scidm.nchc.org.tw) | 歷年預算 CSV 鏡像 |

## 前端架構

### 5 大區塊

| 區塊 | 頁面 | 職責 |
|------|------|------|
| 🏠 概覽 | Dashboard | 全市 KPI + 趨勢摘要 |
| 👥 人口 | Population, Comparison | 人口結構、跨縣市比較 |
| 💰 財政 | Budget, Policy, Funds | 預算結構、政策領域、基金 |
| 📖 敘事 | Narratives | 數據故事 |
| ℹ️ 關於 | About | 資料源、方法論 |

### 設計系統

- **色系：** primary #2563eb / success #10b981 / danger #ef4444 / warning #f59e0b
- **字階：** h1 24px / h2 20px / h3 15px / body 14px / caption 12px
- **間距：** 4px base grid
- **元件：** Card, KPICard, DataTable, ChartWrapper, StatusMessage, Sidebar, Breadcrumb

## 開發狀態

| Phase | 狀態 | 內容 |
|-------|------|------|
| Phase 1 | ✅ | 資料層建設（ETL + normalizer + validation） |
| Phase 2 | ✅ | 分類映射修正（domain + agency + confidence） |
| Phase 3 | ✅ | 前端資訊架構重設計（sidebar + breadcrumb） |
| Phase 4 | ✅ | 設計系統與元件庫 |
| Phase 5 | ✅ | 頁面逐一重構（7 頁完成，6 頁待資料來源） |
| Phase 6 | ✅ | 建置驗收與部署 |

## 部署

### 前端（Netlify）

1. 在 [Netlify](https://app.netlify.com) 登入 GitHub
2. "Add new site" → "Import an existing project" → 選擇 `Chiayi_City_Policy`
3. 設定：
   - Base directory: `web`
   - Build command: `npm run build`
   - Publish directory: `dist`

### 資料更新

```bash
# 完整 pipeline
python -m etl.main run

# 分類映射
python -m etl.main classify

# 前端建置
cd web && npm run build
```

## License

MIT
