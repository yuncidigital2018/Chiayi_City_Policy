import { useData, formatNumber } from '../hooks/useData'

function formatGeneratedAt(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '—'
  return date.toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export default function DataQualityBar() {
  const { data: catalog, loading, error } = useData('catalog.json')

  if (loading) return null

  if (error) {
    return (
      <section className="data-quality-bar warning" aria-label="資料狀態">
        <span className="quality-dot warning" />
        <span>資料目錄尚未產生</span>
      </section>
    )
  }

  const datasets = catalog?.datasets || []
  const okCount = datasets.filter(dataset => dataset.status === 'ok').length
  const issueCount = datasets.length - okCount
  const rowCount = datasets.reduce((sum, dataset) => sum + Number(dataset.rows || 0), 0)
  const requiredIssues = datasets.filter(dataset =>
    dataset.required && dataset.status !== 'ok'
  )

  return (
    <section className={`data-quality-bar ${requiredIssues.length ? 'warning' : ''}`} aria-label="資料狀態">
      <div className="quality-item strong">
        <span className={`quality-dot ${requiredIssues.length ? 'warning' : 'ok'}`} />
        <span>資料狀態 {okCount}/{datasets.length}</span>
      </div>
      <div className="quality-item">
        <span>{formatNumber(rowCount)} 筆資料列</span>
      </div>
      <div className="quality-item">
        <span>更新 {formatGeneratedAt(catalog?.generatedAt)}</span>
      </div>
      {issueCount > 0 && (
        <div className="quality-item issue">
          <span>{issueCount} 張表需檢查</span>
        </div>
      )}
    </section>
  )
}
