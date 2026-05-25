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
│   └── cleaned/            # 清洗後的 CSV/Parquet
├── docs/
│   └── SDD.md              # 系統設計文件
├── markdown/
│   ├── population/         # 人口主題 Markdown
│   └── budget/             # 預算主題 Markdown
├── app/                    # 互動式網站
├── etl/                    # ETL 腳本（待建立）
└── README.md
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

- [x] 專案初始化
- [x] SDD 文件
- [x] 資料來源設定檔
- [ ] ETL 腳本開發
- [ ] Markdown 產生器
- [ ] 互動式網站
- [ ] 排程更新機制

## License

MIT
