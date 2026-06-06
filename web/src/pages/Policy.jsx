import { useState } from 'react'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend } from 'chart.js'
import { Bar, Doughnut } from 'react-chartjs-2'
import { useData, formatNumber, formatBudget } from '../hooks/useData'

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend)

const CONFIDENCE_LABELS = {
  high: { label: '高', color: '#10b981', icon: '🟢' },
  medium: { label: '中', color: '#f59e0b', icon: '🟡' },
  low: { label: '低', color: '#ef4444', icon: '🔴' },
}

const DOMAIN_COLORS = [
  '#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
  '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1',
  '#14b8a6', '#a855f7', '#64748b', '#78716c',
]

export default function Policy() {
  const { data: domainSummary, loading: domainLoading } = useData('budget_by_policy_domain.json')
  const { data: agencySummary, loading: agencyLoading } = useData('budget_agency_by_domain.json')
  const [confidenceFilter, setConfidenceFilter] = useState('all')

  if (domainLoading || agencyLoading) {
    return <div className="container"><p>載入中...</p></div>
  }

  const filtered = domainSummary?.filter(d =>
    confidenceFilter === 'all' || d.confidence === confidenceFilter
  ) || []

  const totalAmount = filtered.reduce((s, d) => s + Number(d.amount), 0)

  // Doughnut data
  const doughnutData = {
    labels: filtered.map(d => d.policy_domain),
    datasets: [{
      data: filtered.map(d => Number(d.amount)),
      backgroundColor: filtered.map((_, i) => DOMAIN_COLORS[i % DOMAIN_COLORS.length]),
    }],
  }

  // Bar data (horizontal)
  const barData = {
    labels: filtered.map(d => d.policy_domain),
    datasets: [{
      label: '金額（千元）',
      data: filtered.map(d => Number(d.amount)),
      backgroundColor: filtered.map((_, i) => DOMAIN_COLORS[i % DOMAIN_COLORS.length]),
      borderRadius: 6,
    }],
  }

  return (
    <>
      <div className="page-header">
        <h1>📊 政策領域分析</h1>
        <p>預算按政策領域分類 — 115 年度</p>
      </div>

      {/* Confidence filter */}
      <div className="filter-bar">
        <span className="filter-label">信心度篩選：</span>
        {['all', 'high', 'medium', 'low'].map(level => (
          <button
            key={level}
            className={`filter-btn ${confidenceFilter === level ? 'active' : ''}`}
            onClick={() => setConfidenceFilter(level)}
          >
            {level === 'all' ? '全部' : CONFIDENCE_LABELS[level].icon + ' ' + CONFIDENCE_LABELS[level].label}
          </button>
        ))}
      </div>

      {/* Summary KPI */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-label">政策領域數</div>
          <div className="kpi-value">{filtered.length}</div>
        </div>
        <div className="kpi-card green">
          <div className="kpi-label">總預算</div>
          <div className="kpi-value">{formatBudget(totalAmount)}</div>
          <div className="kpi-change">新台幣千元</div>
        </div>
        <div className="kpi-card amber">
          <div className="kpi-label">高信心度</div>
          <div className="kpi-value">{filtered.filter(d => d.confidence === 'high').length}</div>
          <div className="kpi-change">領域</div>
        </div>
        <div className="kpi-card red">
          <div className="kpi-label">低信心度</div>
          <div className="kpi-value">{filtered.filter(d => d.confidence === 'low').length}</div>
          <div className="kpi-change">需人工確認</div>
        </div>
      </div>

      {/* Charts */}
      <div className="chart-grid">
        <div className="chart-card">
          <h3>政策領域分布</h3>
          <Doughnut
            data={doughnutData}
            options={{
              responsive: true,
              plugins: {
                legend: { position: 'right', labels: { font: { size: 11 } } },
                tooltip: {
                  callbacks: {
                    label: (ctx) => {
                      const val = ctx.raw
                      const pct = totalAmount > 0 ? (val / totalAmount * 100).toFixed(1) : 0
                      return `${ctx.label}: ${formatBudget(val)} (${pct}%)`
                    }
                  }
                }
              }
            }}
          />
        </div>

        <div className="chart-card">
          <h3>政策領域金額排名</h3>
          <Bar
            data={barData}
            options={{
              responsive: true,
              indexAxis: 'y',
              plugins: { legend: { display: false } },
              scales: { x: { ticks: { callback: v => formatBudget(v) } } },
            }}
          />
        </div>
      </div>

      {/* Detail table */}
      <div className="chart-card">
        <h3>政策領域明細</h3>
        <table className="data-table">
          <thead>
            <tr>
              <th>政策領域</th>
              <th>英文名稱</th>
              <th style={{ textAlign: 'right' }}>金額（千元）</th>
              <th style={{ textAlign: 'right' }}>%</th>
              <th>信心度</th>
              <th style={{ textAlign: 'right' }}>項目數</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((d, i) => {
              const conf = CONFIDENCE_LABELS[d.confidence] || CONFIDENCE_LABELS.medium
              return (
                <tr key={i}>
                  <td><strong>{d.policy_domain}</strong></td>
                  <td className="text-muted">{d.policy_domain_en}</td>
                  <td style={{ textAlign: 'right' }}>{formatNumber(d.amount)}</td>
                  <td style={{ textAlign: 'right' }}>{d.percentage}%</td>
                  <td>
                    <span className="confidence-badge" style={{ backgroundColor: conf.color + '20', color: conf.color }}>
                      {conf.icon} {conf.label}
                    </span>
                  </td>
                  <td style={{ textAlign: 'right' }}>{d.item_count}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* Agency summary */}
      {agencySummary?.length > 0 && (
        <div className="chart-card">
          <h3>機關別政策領域對照</h3>
          <table className="data-table">
            <thead>
              <tr>
                <th>政策領域</th>
                <th style={{ textAlign: 'right' }}>金額（千元）</th>
                <th style={{ textAlign: 'right' }}>%</th>
                <th style={{ textAlign: 'right' }}>機關數</th>
                <th>信心度分佈</th>
              </tr>
            </thead>
            <tbody>
              {agencySummary.map((d, i) => (
                <tr key={i}>
                  <td><strong>{d.policy_domain}</strong></td>
                  <td style={{ textAlign: 'right' }}>{formatNumber(d.amount)}</td>
                  <td style={{ textAlign: 'right' }}>{d.percentage}%</td>
                  <td style={{ textAlign: 'right' }}>{d.agency_count}</td>
                  <td>
                    {d.high > 0 && <span className="confidence-mini high">{d.high}高</span>}
                    {d.medium > 0 && <span className="confidence-mini medium">{d.medium}中</span>}
                    {d.low > 0 && <span className="confidence-mini low">{d.low}低</span>}
                    {d.none > 0 && <span className="confidence-mini none">{d.none}未分</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  )
}
