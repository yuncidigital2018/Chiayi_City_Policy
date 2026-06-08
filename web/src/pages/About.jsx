import { useData, formatNumber } from '../hooks/useData'

export default function About() {
  const { data: catalog } = useData('catalog.json')
  const datasets = catalog?.datasets || []

  return (
    <div className="narrative-content wide-content">
      <div className="page-header">
        <h1>ℹ️ 關於本系統</h1>
        <p>嘉義市人口與財政開放資料系統</p>
      </div>

      <div className="card">
        <h2>系統說明</h2>
        <p>
          本系統自動化收集、清洗、分析嘉義市的人口與財政資料，
          並以互動式儀表板呈現，讓市民與決策者能快速掌握城市現況。
        </p>
      </div>

      <div className="card">
        <h2>資料來源</h2>
        <table className="data-table">
          <thead>
            <tr><th>來源</th><th>內容</th><th>更新頻率</th></tr>
          </thead>
          <tbody>
            <tr>
              <td><a href="https://data.chiayi.gov.tw" target="_blank" rel="noopener">Open Chiayi</a></td>
              <td>歲入/歲出預算、區里人口</td>
              <td>年度</td>
            </tr>
            <tr>
              <td><a href="https://www.ris.gov.tw" target="_blank" rel="noopener">內政部戶政司</a></td>
              <td>人口統計、年齡結構</td>
              <td>月度</td>
            </tr>
            <tr>
              <td><a href="https://data.gov.tw" target="_blank" rel="noopener">data.gov.tw</a></td>
              <td>中央政府開放資料</td>
              <td>不定期</td>
            </tr>
            <tr>
              <td><a href="https://scidm.nchc.org.tw" target="_blank" rel="noopener">國網洞見 SCIDM</a></td>
              <td>歷年預算 CSV 鏡像</td>
              <td>年度</td>
            </tr>
          </tbody>
        </table>
      </div>

      {datasets.length > 0 && (
        <div className="card">
          <h2>資料表目錄</h2>
          <table className="data-table">
            <thead>
              <tr>
                <th>資料表</th>
                <th>領域</th>
                <th style={{ textAlign: 'right' }}>列數</th>
                <th style={{ textAlign: 'right' }}>欄位</th>
                <th>狀態</th>
              </tr>
            </thead>
            <tbody>
              {datasets.map(dataset => (
                <tr key={dataset.id}>
                  <td>
                    <strong>{dataset.title}</strong>
                    <div className="text-muted">{dataset.id}</div>
                  </td>
                  <td>{dataset.domain}</td>
                  <td style={{ textAlign: 'right' }}>{formatNumber(dataset.rows)}</td>
                  <td style={{ textAlign: 'right' }}>{formatNumber(dataset.columns?.length)}</td>
                  <td>
                    <span className={`dataset-status ${dataset.status === 'ok' ? 'ok' : 'warning'}`}>
                      {dataset.status === 'ok' ? 'OK' : dataset.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="card">
        <h2>分類方法</h2>
        <p>
          預算資料按「政事別」（function_category）映射至 14 個政策領域。
          每個映射帶有信心度標記（高/中/低），表示分類的確定程度。
        </p>
        <ul>
          <li><strong>🟢 高信心度：</strong>對應明確，如「教育支出 → 教育與文化」</li>
          <li><strong>🟡 中信心度：</strong>含多項業務，如「民政處 → 治理與行政」</li>
          <li><strong>🔴 低信心度：</strong>需人工確認，如「其他經濟服務支出 → 經濟與產業」</li>
        </ul>
      </div>

      <div className="card">
        <h2>技術架構</h2>
        <ul>
          <li><strong>ETL：</strong>Python + pandas — 自動抓取、清洗、驗證</li>
          <li><strong>前端：</strong>React + Vite + Chart.js — 互動式儀表板</li>
          <li><strong>部署：</strong>Netlify — 自動 build + CDN</li>
          <li><strong>更新：</strong>GitHub Actions — 每月自動執行 pipeline</li>
        </ul>
      </div>

      <div className="card">
        <h2>資料更新流程</h2>
        <ol>
          <li>ETL 抓取最新資料（<code>python -m etl.main fetch</code>）</li>
          <li>清洗標準化（<code>python -m etl.main normalize</code>）</li>
          <li>政策分類（<code>python -m etl.main classify</code>）</li>
          <li>產出 Markdown + JSON（<code>python -m etl.main generate</code>）</li>
          <li>前端 build + 部署（<code>npm run build</code>）</li>
        </ol>
      </div>

      <div className="card">
        <h2>聯絡與貢獻</h2>
        <p>
          本系統為開源專案，歡迎提出建議或貢獻。
          <br />
          GitHub: <a href="https://github.com/yuncidigital2018/Chiayi_City_Policy" target="_blank" rel="noopener">Chiayi_City_Policy</a>
        </p>
      </div>
    </div>
  )
}
