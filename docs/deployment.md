# 部署與更新流程說明

## 資料來源狀態

| 資料集 | 來源 | 狀態 | OID | RID |
|--------|------|------|-----|-----|
| 歲出政事別預算總表 | data.chiayi.gov.tw | ✅ 可下載 | b05a221d-... | 3d4a410e-... |
| 歲出機關別預算總表 | data.chiayi.gov.tw | ✅ 可下載 | d9303734-... | ebdd0f86-... |
| 歲入來源別預算總表 | data.chiayi.gov.tw | ⚠️ 待補 RID | f6a1738a-... | — |
| 區里人口統計 | household.chiayi.gov.tw | ⚠️ 需 ASPX 爬蟲 | — | — |
| 歷年人口統計 | household.chiayi.gov.tw | ⚠️ 需 ASPX 爬蟲 | — | — |
| STATCloud 人口 | segis.moi.gov.tw | ⚠️ API 格式待確認 | — | — |
| 作業基金預算 | data.chiayi.gov.tw | ✅ 可下載 | 0cc4405f-... | 77a81878-... |
| 營業基金預算 | data.chiayi.gov.tw | ✅ 可下載 | 28a62ae9-... | bce44fc8-... |
| 政事型基金預算 | data.chiayi.gov.tw | ✅ 可下載 | 2977f687-... | 3fbe6b83-... |

## 本地更新

```bash
# 完整流程
bash scripts/update_all.sh

# 強制重新抓取（忽略快取）
bash scripts/update_all.sh --force
```

## GitHub Actions 排程更新

- 排程：每月 1 日 00:00 UTC
- 設定檔：`.github/workflows/update.yml`
- 觸發方式：
  1. 自動排程
  2. GitHub Actions 頁面手動 "Run workflow"

### 工作原理

1. checkout → install Python deps → run ETL pipeline
2. 檢查 data/processed/ 和 content/ 是否有變化
3. 有變化則自動 commit + push
4. 無變化則跳過（使用上次快取，符合 NFR-1）

## Fallback 機制

### ETL 層級（NFR-1）
- 如果 API 抓取失敗，fetcher 會使用上次成功的快取檔案
- 不會因為單一資料源失敗而中斷整個 pipeline
- log 會記錄 FAILED 的資料源

### 部署層級
- 如果前端 build 失敗，不影響已生成的 Markdown 內容
- GitHub Actions 會繼續 push 更新後的資料

## 環境變數

目前無需特殊環境變數。如果未來需要：

| 變數 | 用途 | 預設值 |
|------|------|--------|
| `HTTP_PROXY` | 代理伺服器（如 Open Chiayi 擋 IP） | 無 |
| `SSL_VERIFY` | SSL 驗證（政府網站憑證有問題） | `false` |

## 已知問題

1. **Open Chiayi SSL 憑證問題**：已透過 `verify=False` 繞過
2. **Open Chiayi 雲端 IP 限制**：如遇到 403，可設定 proxy 或改用 data.gov.tw 鏡像
3. **戶政服務網 ASPX 表單**：需要更複雜的爬蟲邏輯（viewstate 處理），目前使用樣本資料
4. **STATCloud API**：格式尚未完全確認，需要進一步研究

## 補齊待辦

- [ ] 取得歲入來源別預算總表的 RID
- [ ] 實作戶政服務網 ASPX 爬蟲
- [ ] 確認 STATCloud API 呼叫方式
- [ ] 補齊東西區各里人口的 Open Chiayi OID/RID
