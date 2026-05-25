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
- [ ] Phase 2: 資料抓取與清洗（需填入 OID 後執行）
- [ ] Phase 3: Markdown 知識庫
- [ ] Phase 4: 互動式網站
- [ ] Phase 5: 排程與部署

## License

MIT
