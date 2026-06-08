import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Title, Tooltip, Legend, Filler } from 'chart.js'
import { Line, Bar, Doughnut } from 'react-chartjs-2'
import { useData, formatNumber, formatChange, formatBudget, parseGrowthPct } from '../hooks/useData'
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
  const popChange = latestPop.total_population && prevPop.total_population
    ? Number(latestPop.total_population) - Number(prevPop.total_population)
    : null
  const latestGrowth = parseGrowthPct(latestPop.growth_pct)
  const populationChanges = population?.map((p, i) => ({
    ...p,
    annual_change: i === 0
      ? null
      : Number(p.total_population) - Number(population[i - 1].total_population),
  })) || []
  const totalRevenue = revenue?.reduce((s, r) => s + Number(r.amount), 0) || 0
  const expenditureL1 = expenditure?.filter(e => Number(e.level) === 1) || []
  const totalExpenditure = expenditureL1.reduce((s, e) => s + Number(e.amount), 0)
  const genderRatio = latestPop.male && latestPop.female
    ? (Number(latestPop.male) / Number(latestPop.female) * 100).toFixed(1)
    : '—'
  const popChangeType = popChange == null ? undefined : (popChange >= 0 ? 'positive' : 'negative')
  const growthType = latestGrowth == null ? undefined : (latestGrowth >= 0 ? 'positive' : 'negative')

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
          changeType={popChangeType}
          color="primary"
          to="/population"
        />
        <KPICard
          label="年度增減"
          value={formatChange(popChange)}
          change="總人口較上年"
          changeType={popChangeType}
          color="red"
          to="/population"
        />
        <KPICard
          label="成長率"
          value={latestGrowth == null ? '—' : `${latestGrowth.toFixed(3)}%`}
          change="戶政年度資料"
          changeType={growthType}
          color="amber"
          to="/population/comparison"
        />
        <KPICard
          label="歲入總額"
          value={formatBudget(totalRevenue, { includeUnit: true })}
          change="115 年度"
          color="green"
          to="/budget"
        />
        <KPICard
          label="歲出總額"
          value={formatBudget(totalExpenditure, { includeUnit: true })}
          change="115 年度，L1 政事別合計"
          color="purple"
          to="/budget"
        />
        <KPICard
          label="男女性別比"
          value={genderRatio}
          change="男/百女"
          color="primary"
          to="/population"
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
              labels: expenditureL1.map(e => e.function_category),
              datasets: [{
                label: '金額（千元）',
                data: expenditureL1.map(e => Number(e.amount)),
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

        <ChartWrapper title="年度人口增減" empty={!populationChanges?.length}>
          <Bar
            data={{
              labels: populationChanges.map(p => `${p.year}年`),
              datasets: [{
                label: '較上年增減',
                data: populationChanges.map(p => p.annual_change),
                backgroundColor: populationChanges.map(p => Number(p.annual_change) >= 0 ? '#10b981' : '#ef4444'),
                borderRadius: 4,
              }]
            }}
            options={{ responsive: true, plugins: { legend: { display: false } } }}
          />
        </ChartWrapper>
      </div>
    </>
  )
}
