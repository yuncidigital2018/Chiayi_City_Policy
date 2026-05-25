# 嘉義市知識庫 — 持續開發規劃

> 建立日期：2026-05-26
> 基於 Phase 0-5 完成後的全面盤點

---

## 📊 現況摘要

| 模組 | 狀態 | 品質 |
|------|------|------|
| ETL Pipeline (8 檔) | ✅ 完成 | 無 validation、無 logging |
| 資料來源 (2 條) | ✅ 完成 | Open Chiayi + 戶政爬蟲，STATCloud 未實作 |
| Markdown 產出 (4 份) | ✅ 完成 | 正常運作 |
| 前端儀表板 (5 頁) | ✅ 完成 | 有 1 個 import bug |
| CI/CD | ✅ 完成 | 每月自動更新 |
| 測試覆蓋 | ❌ 零 | 0 支測試 |
| 資料驗證 | ❌ 零 | 無 schema 驗證 |
| 歷史資料 | ⚠️ 不完整 | 歲入僅 115 年，106-114 未跑 |

---

## 🗓️ 開發期程

### Phase 6：Bug 修復 & 文件同步 🔴 — 2026-05-26（今日）

| # | 任務 | 優先 | 預估 |
|---|------|------|------|
| 6-1 | 修復 `Narratives.jsx` 缺少 `formatBudget` import | P0 | 5 min |
| 6-2 | 修正 `index.html` title 為「嘉義市政儀表板」 | P1 | 2 min |
| 6-3 | 補上 favicon.svg | P1 | 10 min |
| 6-4 | 更新 SDD.md checkbox（Phase 1-5 → ✅）| P1 | 10 min |

### Phase 7：資料補齊 & Pipeline 強化 🟡 — 2026-05-26~27

| # | 任務 | 優先 | 預估 |
|---|------|------|------|
| 7-1 | 補跑歲入歷史資料（106-114 年 RID） | P0 | 1 hr |
| 7-2 | 新增 `etl/validator.py` — schema validation | P1 | 2 hr |
| 7-3 | ETL 加 logging（取代 print） | P1 | 1 hr |
| 7-4 | fetcher 加 retry + 錯誤摘要 | P2 | 1 hr |

### Phase 8：測試與品質保證 🟢 — 2026-05-28~30

| # | 任務 | 優先 | 預估 |
|---|------|------|------|
| 8-1 | normalizer unit tests（pytest） | P1 | 2 hr |
| 8-2 | validator unit tests | P2 | 1 hr |
| 8-3 | ETL integration test（run-pipeline dry-run） | P2 | 1 hr |
| 8-4 | CI 加入 test step | P1 | 30 min |

### Phase 9：功能擴展 🔵 — 2026-06

| # | 任務 | 優先 | 預估 |
|---|------|------|------|
| 9-1 | STATCloud API 串接（跨縣市比較） | P2 | 3 hr |
| 9-2 | 前端加年份/區域篩選器 | P2 | 4 hr |
| 9-3 | 資料更新通知（pipeline 異動 → email/LINE） | P3 | 2 hr |
| 9-4 | 多縣市架構抽象化 | P3 | 1 day |

---

## 📐 設計原則

1. **現有架構不動** — 三層分離（ETL → Markdown → Web）已驗證可行
2. **增量改善** — 每次改動不超過一個 module，確保可回退
3. **測試先行** — Phase 8 起新功能必須附測試
4. **文件同步** — 每個 phase 完成更新 README + SDD

---

## ✅ 完成追蹤

| Phase | 開始 | 完成 | 備註 |
|-------|------|------|------|
| Phase 6 | 2026-05-26 | ⬜ | |
| Phase 7 | ⬜ | ⬜ | |
| Phase 8 | ⬜ | ⬜ | |
| Phase 9 | ⬜ | ⬜ | |
