import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend } from 'chart.js'
import { Bar, Doughnut } from 'react-chartjs-2'
import { useData, formatNumber, formatBudget } from '../hooks/useData'

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend)

export default function Budget() {
  const { data: revenue, loading: revLoading } = useData('budget_revenue_by_source.json')
  const { data: expFunc, loading: expFuncLoading } = useData('budget_expenditure_by_function.json')
  const { data: expAgency, loading: expAgencyLoading } = useData('budget_expenditure_by_agency.json')

  if (revLoading || expFuncLoading || expAgencyLoading) return <div className="container"><p>載入中...</p></div>

  const totalRevenue = revenue?.reduce((s, r) => s + Number(r.amount), 0) || 0
  const totalExpFunc = expFunc?.reduce((s, e) => s + Number(e.amount), 0) || 0

  const revWithPct = (revenue || []).map(r => ({
    ...r,
    pct: totalRevenue > 0 ? ((Number(r.amount) / totalRevenue) * 100).toFixed(1) : 0
  }))

  const expFuncWithPct = (expFunc || []).map(e => ({
    ...e,
    pct: totalExpFunc > 0 ? ((Number(e.amount) / totalExpFunc) * 100).toFixed(1) : 0
  }))

  const agencyTop = [...(expAgency || [])].sort((a, b) => Number(b.amount) - Number(a.amount)).slice(0, 10)

  return (
    <>
      <div className="page-header">
        <h1>💰 預算詳情</h1>
        <p>115 年度歲入歲出結構分析</p>
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
          <div className="kpi-value">{formatBudget(totalExpFunc)}</div>
          <div className="kpi-change">新台幣千元</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">收支差額</div>
          <div className="kpi-value">{formatBudget(totalRevenue - totalExpFunc)}</div>
          <div className="kpi-change">{(totalRevenue - totalExpFunc) >= 0 ? '歲入大於歲出' : '歲出大於歲入'}</div>
        </div>
        <div className="kpi-card amber">
          <div className="kpi-label">最大歲入來源</div>
          <div className="kpi-value" style={{ fontSize: 18 }}>{revWithPct[0]?.source_category || '—'}</div>
          <div className="kpi-change">{revWithPct[0]?.pct}% of total</div>
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
                backgroundColor: ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'],
              }]
            }}
            options={{ responsive: true, plugins: { legend: { position: 'right', labels: { font: { size: 11 } } } } }}
          />
        </div>

        <div className="chart-card">
          <h3>歲出政事別</h3>
          <Bar
            data={{
              labels: expFuncWithPct.map(e => e.function_category),
              datasets: [{
                label: '金額',
                data: expFuncWithPct.map(e => Number(e.amount)),
                backgroundColor: expFuncWithPct.map(e =>
                  e.function_category.includes('教育') ? '#2563eb' :
                  e.function_category.includes('社會') ? '#10b981' :
                  e.function_category.includes('經濟') ? '#f59e0b' :
                  e.function_category.includes('退休') ? '#8b5cf6' :
                  '#64748b'
                ),
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

      {/* Tables */}
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
                const pct = totalExpFunc > 0 ? (Number(a.amount) / totalExpFunc * 100).toFixed(1) : 0
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
    </>
  )
}
