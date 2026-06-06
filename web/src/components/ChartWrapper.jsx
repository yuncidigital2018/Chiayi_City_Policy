import StatusMessage from './StatusMessage'

/**
 * ChartWrapper — 圖表容器，處理 loading/empty/error 狀態
 *
 * Props:
 *   loading: boolean
 *   error: string | null
 *   empty: boolean (data is empty/null)
 *   title: string
 *   children: chart component
 *   className: string
 */
export default function ChartWrapper({
  loading = false,
  error = null,
  empty = false,
  title,
  children,
  className = '',
}) {
  return (
    <div className={`chart-card ${className}`}>
      {title && <h3>{title}</h3>}
      {loading ? (
        <StatusMessage type="loading" />
      ) : error ? (
        <StatusMessage type="error" message={error} />
      ) : empty ? (
        <StatusMessage type="empty" />
      ) : (
        children
      )}
    </div>
  )
}
