# Chiayi City Policy — 嘉義市人口與財政知識庫

> 自動化「資料 → Markdown 知識庫 → 互動式網站」系統

## 專案說明

針對嘉義市人口發展與市府預算（歲入、歲出）建立一套自動化系統：

1. 從多個開放資料來源自動抓取人口與預算資料
2. 清洗整併為統一 schema，自動產出結構化 Markdown 報告
3. 以 Markdown 知識庫為資料來源，產出互動式網站（儀表板＋敘事頁）
4. 支援排程更新

## 專案結構

```
├── config/
│   └── datasources.yml     # 資料來源設定（OID、API、排程）
├── data/
│   ├── raw/                # 原始抓取的資料
│   └── processed/          # 清洗後的 CSV
├── docs/
│   └── SDD.md              # 系統設計文件
├── content/
│   ├── population/         # 人口主題 Markdown
│   └── budget/             # 預算主題 Markdown
├── app/                    # 互動式網站（待開發）
├── etl/
│   ├── __init__.py
│   ├── config_loader.py    # 讀取 datasources.yml
│   ├── fetcher.py          # 資料抓取模組
│   ├── normalizer.py       # 資料清洗與標準化
│   ├── md_generator.py     # Markdown 產生器
│   └── main.py             # CLI 入口
├── requirements.txt        # Python 依賴
└── README.md
```

## 快速開始

```bash
# 安裝依賴
pip install -r requirements.txt

# 完整 pipeline
python -m etl.main run

# 分步執行
python -m etl.main fetch          # 抓取原始資料
python -m etl.main normalize      # 清洗 → processed/
python -m etl.main generate       # 產生 Markdown → content/
python -m etl.main status         # 查看目前狀態

# 強制重新抓取
python -m etl.main run --force
```

## 資料來源

| 來源 | 用途 |
|------|------|
| [Open Chiayi](https://data.chiayi.gov.tw) | 歲入/歲出預算、區里人口 |
| [data.gov.tw](https://data.gov.tw) | 中央政府開放資料 |
| [戶政服務網](https://household.chiayi.gov.tw) | 人口即時數、歷年人口、戶籍登記 |
| [STATCloud](https://segis.moi.gov.tw) | 行政區人口統計（跨縣市比較） |
| [主計處](https://account.chiayi.gov.tw) | 預算書 PDF、統計年報 |
| [SCIDM](https://scidm.nchc.org.tw) | 歷年預算 CSV 鏡像 |

## 開發狀態

- [x] Phase 0: 專案初始化
- [x] Phase 1: 資料源設定與 ETL 架構
- [x] Phase 2: 資料抓取與清洗（真實預算資料 + 人口樣本）
- [x] Phase 3: Markdown 知識庫（4 份報告自動生成）
- [x] Phase 4: 互動式網站（Vite + React + Chart.js）
- [x] Phase 5: GitHub Actions 排程 + Netlify 部署設定

## 部署

### 前端（Netlify）

1. 在 [Netlify](https://app.netlify.com) 登入 GitHub
2. "Add new site" → "Import an existing project" → 選擇 `Chiayi_City_Policy`
3. 設定：
   - Base directory: `web`
   - Build command: `npm run build`
   - Publish directory: `dist`
4. 或直接使用 `netlify.toml`（已包含在 repo 中）

每次 push 到 main 會自動重新 build + deploy。

### 資料更新

```bash
# 本地執行完整 pipeline
bash scripts/update_all.sh

# 強制重新抓取
bash scripts/update_all.sh --force
```

GitHub Actions 每月 1 日自動執行。

## License

MIT
