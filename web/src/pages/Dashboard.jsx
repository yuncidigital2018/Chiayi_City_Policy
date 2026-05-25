import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Title, Tooltip, Legend, Filler } from 'chart.js'
import { Line, Bar, Doughnut } from 'react-chartjs-2'
import { useData, formatNumber, formatChange, formatBudget } from '../hooks/useData'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Title, Tooltip, Legend, Filler)

export default function Dashboard() {
  const { data: population, loading: popLoading } = useData('population_annual.json')
  const { data: revenue, loading: revLoading } = useData('budget_revenue_by_source.json')
  const { data: expenditure, loading: expLoading } = useData('budget_expenditure_by_function.json')

  if (popLoading || revLoading || expLoading) return <div className="container"><p>載入中...</p></div>

  const latestPop = population?.[population.length - 1] || {}
  const prevPop = population?.[population.length - 2] || {}
  const popChange = Number(latestPop.total_population) - Number(prevPop.total_population)
  const totalRevenue = revenue?.reduce((s, r) => s + Number(r.amount), 0) || 0
  const totalExpenditure = expenditure?.reduce((s, e) => s + Number(e.amount), 0) || 0

  return (
    <>
      <div className="page-header">
        <h1>嘉義市政儀表板</h1>
        <p>人口與財政總覽 — 115 年度</p>
      </div>

      {/* KPI Cards */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-label">總人口</div>
          <div className="kpi-value">{formatNumber(latestPop.total_population)}</div>
          <div className={`kpi-change ${popChange >= 0 ? 'positive' : 'negative'}`}>
            {formatChange(popChange)} 較上年
          </div>
        </div>
        <div className="kpi-card red">
          <div className="kpi-label">自然增減</div>
          <div className="kpi-value">{formatChange(latestPop.natural_increase)}</div>
          <div className="kpi-change negative">出生 − 死亡</div>
        </div>
        <div className="kpi-card amber">
          <div className="kpi-label">社會增減</div>
          <div className="kpi-value">{formatChange(latestPop.social_increase)}</div>
          <div className="kpi-change negative">遷入 − 遷出</div>
        </div>
        <div className="kpi-card green">
          <div className="kpi-label">歲入總額</div>
          <div className="kpi-value">{formatBudget(totalRevenue)}</div>
          <div className="kpi-change">新台幣千元</div>
        </div>
        <div className="kpi-card purple">
          <div className="kpi-label">歲出總額</div>
          <div className="kpi-value">{formatBudget(totalExpenditure)}</div>
          <div className="kpi-change">新台幣千元</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">男女性別比</div>
          <div className="kpi-value">
            {latestPop.male && latestPop.female ? (Number(latestPop.male) / Number(latestPop.female) * 100).toFixed(1) : '—'}
          </div>
          <div className="kpi-change">男/百女</div>
        </div>
      </div>

      {/* Charts */}
      <div className="chart-grid">
        <div className="chart-card">
          <h3>人口長期趨勢</h3>
          <Line
            data={{
              labels: population?.map(p => `${p.year}年`) || [],
              datasets: [{
                label: '總人口',
                data: population?.map(p => Number(p.total_population)) || [],
                borderColor: '#2563eb',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                fill: true,
                tension: 0.3,
              }]
            }}
            options={{ responsive: true, plugins: { legend: { display: false } } }}
          />
        </div>

        <div className="chart-card">
          <h3>歲入來源結構</h3>
          <Doughnut
            data={{
              labels: revenue?.map(r => r.source_category) || [],
              datasets: [{
                data: revenue?.map(r => Number(r.amount)) || [],
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
              labels: expenditure?.map(e => e.function_category) || [],
              datasets: [{
                label: '金額（千元）',
                data: expenditure?.map(e => Number(e.amount)) || [],
                backgroundColor: '#2563eb',
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

        <div className="chart-card">
          <h3>人口增減結構</h3>
          <Bar
            data={{
              labels: population?.map(p => `${p.year}年`) || [],
              datasets: [
                { label: '自然增減', data: population?.map(p => Number(p.natural_increase)) || [], backgroundColor: '#10b981', borderRadius: 4 },
                { label: '社會增減', data: population?.map(p => Number(p.social_increase)) || [], backgroundColor: '#f59e0b', borderRadius: 4 },
              ]
            }}
            options={{ responsive: true, plugins: { legend: { position: 'top' } } }}
          />
        </div>
      </div>
    </>
  )
}
