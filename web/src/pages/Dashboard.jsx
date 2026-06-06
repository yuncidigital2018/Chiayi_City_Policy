import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Title, Tooltip, Legend, Filler } from 'chart.js'
import { Line, Bar, Doughnut } from 'react-chartjs-2'
import { useData, formatNumber, formatChange, formatBudget } from '../hooks/useData'
import { KPICard } from '../components/Card'
import ChartWrapper from '../components/ChartWrapper'
import StatusMessage from '../components/StatusMessage'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Title, Tooltip, Legend, Filler)

export default function Dashboard() {
  const { data: population, loading: popLoading, error: popError } = useData('population_annual.json')
  const { data: revenue, loading: revLoading, error: revError } = useData('budget_revenue_by_source.json')
  const { data: expenditure, loading: expLoading, error: expError } = useData('budget_expenditure_by_function.json')

  const loading = popLoading || revLoading || expLoading
  const error = popError || revError || expError

  if (loading) return <StatusMessage type="loading" />
  if (error) return <StatusMessage type="error" message={error} />

  const latestPop = population?.[population.length - 1] || {}
  const prevPop = population?.[population.length - 2] || {}
  const popChange = Number(latestPop.total_population) - Number(prevPop.total_population)
  const totalRevenue = revenue?.reduce((s, r) => s + Number(r.amount), 0) || 0
  const totalExpenditure = expenditure?.reduce((s, e) => s + Number(e.amount), 0) || 0
  const genderRatio = latestPop.male && latestPop.female
    ? (Number(latestPop.male) / Number(latestPop.female) * 100).toFixed(1)
    : '—'

  return (
    <>
      <div className="page-header">
        <h1>嘉義市政儀表板</h1>
        <p>人口與財政總覽 — 115 年度</p>
      </div>

      {/* KPI Cards */}
      <div className="kpi-grid">
        <KPICard
          label="總人口"
          value={formatNumber(latestPop.total_population)}
          change={`${formatChange(popChange)} 較上年`}
          changeType={popChange >= 0 ? 'positive' : 'negative'}
          color="primary"
        />
        <KPICard
          label="自然增減"
          value={formatChange(latestPop.natural_increase)}
          change="出生 − 死亡"
          changeType="negative"
          color="red"
        />
        <KPICard
          label="社會增減"
          value={formatChange(latestPop.social_increase)}
          change="遷入 − 遷出"
          changeType="negative"
          color="amber"
        />
        <KPICard
          label="歲入總額"
          value={formatBudget(totalRevenue)}
          change="新台幣千元"
          color="green"
        />
        <KPICard
          label="歲出總額"
          value={formatBudget(totalExpenditure)}
          change="新台幣千元"
          color="purple"
        />
        <KPICard
          label="男女性別比"
          value={genderRatio}
          change="男/百女"
          color="primary"
        />
      </div>

      {/* Charts */}
      <div className="chart-grid">
        <ChartWrapper title="人口長期趨勢" empty={!population?.length}>
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
        </ChartWrapper>

        <ChartWrapper title="歲入來源結構" empty={!revenue?.length}>
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
        </ChartWrapper>

        <ChartWrapper title="歲出政事別" empty={!expenditure?.length}>
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
        </ChartWrapper>

        <ChartWrapper title="人口增減結構" empty={!population?.length}>
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
        </ChartWrapper>
      </div>
    </>
  )
}
