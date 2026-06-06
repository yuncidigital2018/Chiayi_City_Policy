/**
 * Card — 通用容器元件
 *
 * Variants:
 *   <Card>一般卡片</Card>
 *   <Card variant="kpi" color="green">KPI 卡片</Card>
 *   <Card variant="chart">圖表容器</Card>
 *   <Card variant="narrative">敘事容器</Card>
 *
 * Props:
 *   variant: 'default' | 'kpi' | 'chart' | 'narrative'
 *   color: 'primary' | 'green' | 'red' | 'amber' | 'purple' (kpi variant only)
 *   title: string (顯示 h3 標題)
 *   className: string
 *   children
 */
export default function Card({
  variant = 'default',
  color,
  title,
  className = '',
  children,
  ...props
}) {
  const classes = [
    'card',
    variant === 'kpi' && 'kpi-card',
    variant === 'kpi' && color && `kpi-${color}`,
    variant === 'chart' && 'chart-card',
    variant === 'narrative' && 'narrative-content',
    className,
  ].filter(Boolean).join(' ')

  return (
    <div className={classes} {...props}>
      {title && <h3>{title}</h3>}
      {children}
    </div>
  )
}

/**
 * KPICard — KPI 數字卡片（語義化封裝）
 */
export function KPICard({ label, value, change, changeType, color = 'primary' }) {
  return (
    <Card variant="kpi" color={color}>
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">{value}</div>
      {change !== undefined && (
        <div className={`kpi-change ${changeType || ''}`}>
          {change}
        </div>
      )}
    </Card>
  )
}
