/**
 * StatusMessage — Loading / Error / Empty 狀態元件
 *
 * Props:
 *   type: 'loading' | 'error' | 'empty'
 *   message: string (override default message)
 */
export default function StatusMessage({ type, message }) {
  const configs = {
    loading: {
      icon: '⏳',
      defaultMsg: '載入中...',
      className: 'status-loading',
    },
    error: {
      icon: '❌',
      defaultMsg: '資料載入失敗',
      className: 'status-error',
    },
    empty: {
      icon: '📭',
      defaultMsg: '暫無資料',
      className: 'status-empty',
    },
  }

  const config = configs[type] || configs.empty

  return (
    <div className={`status-message ${config.className}`}>
      <span className="status-icon">{config.icon}</span>
      <span className="status-text">{message || config.defaultMsg}</span>
    </div>
  )
}
