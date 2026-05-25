import { useState } from 'react'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend } from 'chart.js'
import { Bar, Doughnut } from 'react-chartjs-2'
import { useData, formatNumber, formatBudget } from '../hooks/useData'

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend)

// Color palette for top-level categories
const CAT_COLORS = [
  '#2563eb', '#10b981', '#f59e0b', '#ef4444',
  '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16',
]

function ExpenditureTree({ data, totalExp }) {
  const [expanded, setExpanded] = useState({})

  // Build tree: L1 items with L2 children
  const tree = []
  const childrenMap = {}

  for (const row of data || []) {
    const level = Number(row.level)
    const parent = row.parent_code ? String(row.parent_code) : ''
    if (level === 1) {
      tree.push({ ...row, key: String(row.parent_code) })
      childrenMap[String(row.parent_code)] = []
    } else if (level === 2 && parent) {
      if (!childrenMap[parent]) childrenMap[parent] = []
      childrenMap[parent].push(row)
    }
  }

  const toggle = (key) => setExpanded(prev => ({ ...prev, [key]: !prev[key] }))

  return (
    <table className="data-table">
      <thead>
        <tr>
          <th style={{ width: '60%' }}>政事別</th>
          <th>經常門</th>
          <th>資本門</th>
          <th>合計（千元）</th>
          <th>占比</th>
        </tr>
      </thead>
      <tbody>
        {tree.map((item, idx) => {
          const children = childrenMap[item.key] || []
          const isExp = expanded[item.key]
          const pct = totalExp > 0 ? (Number(item.amount) / totalExp * 100).toFixed(1) : '0.0'
          const color = CAT_COLORS[idx % CAT_COLORS.length]

          return (
            <span key={item.key}>
              <tr
                className="budget-l1"
                style={{ cursor: children.length ? 'pointer' : 'default', fontWeight: 600 }}
                onClick={() => children.length && toggle(item.key)}
              >
                <td>
                  <span style={{
                    display: 'inline-block',
                    width: 10,
                    height: 10,
                    borderRadius: '50%',
                    background: color,
                    marginRight: 8,
                  }} />
                  {children.length ? (isExp ? '▼' : '▶') : '  '} {item.function_category}
                </td>
                <td>{formatNumber(item.recurring)}</td>
                <td>{formatNumber(item.capital)}</td>
                <td>{formatNumber(item.amount)}</td>
                <td>{pct}%</td>
              </tr>
              {isExp && children.map((child, ci) => {
                const childPct = totalExp > 0 ? (Number(child.amount) / totalExp * 100).toFixed(1) : '0.0'
                return (
                  <tr key={ci} className="budget-l2">
                    <td style={{ paddingLeft: 36 }}>
                      <span style={{
                        display: 'inline-block',
                        width: 6,
                        height: 6,
                        borderRadius: '50%',
                        background: color,
                        marginRight: 8,
                        opacity: 0.6,
                      }} />
                      {child.function_category}
                    </td>
                    <td>{formatNumber(child.recurring)}</td>
                    <td>{formatNumber(child.capital)}</td>
                    <td>{formatNumber(child.amount)}</td>
                    <td>{childPct}%</td>
                  </tr>
                )
              })}
            </span>
          )
        })}
      </tbody>
    </table>
  )
}

export default function Budget() {
  const { data: revenue, loading: revLoading } = useData('budget_revenue_by_source.json')
  const { data: expFunc, loading: expFuncLoading } = useData('budget_expenditure_by_function.json')
  const { data: expAgency, loading: expAgencyLoading } = useData('budget_expenditure_by_agency.json')

  if (revLoading || expFuncLoading || expAgencyLoading) return <div className="container"><p>載入中...</p></div>

  // Only L1 items for charts and totals
  const expL1 = (expFunc || []).filter(e => Number(e.level) === 1)
  const totalRevenue = revenue?.reduce((s, r) => s + Number(r.amount), 0) || 0
  const totalExp = expL1.reduce((s, e) => s + Number(e.amount), 0)

  const revWithPct = (revenue || []).map(r => ({
    ...r,
    pct: totalRevenue > 0 ? ((Number(r.amount) / totalRevenue) * 100).toFixed(1) : 0
  }))

  const expFuncWithPct = expL1.map(e => ({
    ...e,
    pct: totalExp > 0 ? ((Number(e.amount) / totalExp) * 100).toFixed(1) : 0
  }))

  const agencyTop = [...(expAgency || [])].sort((a, b) => Number(b.amount) - Number(a.amount)).slice(0, 10)

  return (
    <>
      <div className="page-header">
        <h1>💰 預算詳情</h1>
        <p>115 年度歲入歲出結構分析 — 歲出可點擊展開子項目</p>
      </div>

      {/* Summary */}
      <div className="kpi-grid">
        <div className="kpi-card green">
          <div className="kpi-label">歲入總額</div>
          <div className="kpi-value">{formatBudget(totalRevenue)}</div>
          <div className="kpi-change">新台幣千元</div>
        </div>
        <div className="kpi-card red">
          <div className="kpi-label">歲出總額</div>
          <div className="kpi-value">{formatBudget(totalExp)}</div>
          <div className="kpi-change">新台幣千元</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">收支差額</div>
          <div className="kpi-value">{formatBudget(totalRevenue - totalExp)}</div>
          <div className="kpi-change">{(totalRevenue - totalExp) >= 0 ? '歲入大於歲出' : '歲出大於歲入'}</div>
        </div>
        <div className="kpi-card amber">
          <div className="kpi-label">最大歲入來源</div>
          <div className="kpi-value" style={{ fontSize: 18 }}>{revWithPct[0]?.source_category || '—'}</div>
          <div className="kpi-change">{revWithPct[0]?.pct}%</div>
        </div>
      </div>

      {/* Charts */}
      <div className="chart-grid">
        <div className="chart-card">
          <h3>歲入來源結構</h3>
          <Doughnut
            data={{
              labels: revWithPct.map(r => `${r.source_category} (${r.pct}%)`),
              datasets: [{
                data: revWithPct.map(r => Number(r.amount)),
                backgroundColor: CAT_COLORS,
              }]
            }}
            options={{ responsive: true, plugins: { legend: { position: 'right', labels: { font: { size: 11 } } } } }}
          />
        </div>

        <div className="chart-card">
          <h3>歲出政事別（大類）</h3>
          <Bar
            data={{
              labels: expFuncWithPct.map(e => e.function_category),
              datasets: [{
                label: '金額',
                data: expFuncWithPct.map(e => Number(e.amount)),
                backgroundColor: expFuncWithPct.map((_, i) => CAT_COLORS[i % CAT_COLORS.length]),
                borderRadius: 6,
              }]
            }}
            options={{
              responsive: true,
              indexAxis: 'y',
              plugins: { legend: { display: false } },
              scales: { x: { ticks: { callback: v => formatBudget(v) } } }
            }}
          />
        </div>
      </div>

      {/* Detailed Tables */}
      <div className="chart-grid">
        <div className="chart-card">
          <h3>歲入來源別明細</h3>
          <table className="data-table">
            <thead><tr><th>來源</th><th>金額（千元）</th><th>占比</th></tr></thead>
            <tbody>
              {revWithPct.map((r, i) => (
                <tr key={i}>
                  <td>{r.source_category}</td>
                  <td>{formatNumber(r.amount)}</td>
                  <td>{r.pct}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="chart-card">
          <h3>機關別預算 Top 10</h3>
          <table className="data-table">
            <thead><tr><th>機關</th><th>金額（千元）</th><th>占比</th></tr></thead>
            <tbody>
              {agencyTop.map((a, i) => {
                const pct = totalExp > 0 ? (Number(a.amount) / totalExp * 100).toFixed(1) : 0
                return (
                  <tr key={i}>
                    <td>{a.agency_name}</td>
                    <td>{formatNumber(a.amount)}</td>
                    <td>{pct}%</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* 歲出政事別分層表 */}
      <div className="chart-card full-width" style={{ marginTop: 24 }}>
        <h3>歲出政事別分層明細（點擊 ▶ 展開子項目）</h3>
        <ExpenditureTree data={expFunc} totalExp={totalExp} />
      </div>
    </>
  )
}
