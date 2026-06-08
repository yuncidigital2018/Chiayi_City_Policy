import { useState } from 'react'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js'
import { Bar } from 'react-chartjs-2'
import { useData, formatNumber } from '../hooks/useData'
import { KPICard } from '../components/Card'
import ChartWrapper from '../components/ChartWrapper'
import DataTable from '../components/DataTable'
import StatusMessage from '../components/StatusMessage'

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend)

const CHIAYI_COLOR = '#1a73e8'
const OTHER_COLOR = '#cfd8dc'

export default function Comparison() {
  const { data: countyData, loading, error } = useData('county_population_comparison.json')
  const [sortBy, setSortBy] = useState('population')

  if (loading) return <StatusMessage type="loading" />
  if (error) return <StatusMessage type="error" message={error} />

  const latest = countyData?.filter(d => d.year === Math.max(...countyData.map(x => x.year))) || []
  const sorted = [...latest].sort((a, b) =>
    sortBy === 'density' ? b.density - a.density : b.population - a.population
  )
  const chiayiRank = sorted.findIndex(d => d.county === '嘉義市') + 1
  const chiayi = sorted.find(d => d.county === '嘉義市')

  const top15 = sorted.slice(0, 15)
  const barLabels = top15.map(d => d.county)
  const barValues = top15.map(d => sortBy === 'density' ? d.density : d.population)
  const barColors = top15.map(d => d.county === '嘉義市' ? CHIAYI_COLOR : OTHER_COLOR)

  return (
    <>
      <div className="page-header">
        <h1>📊 跨縣市人口比較</h1>
        <p>嘉義市在全國的定位</p>
      </div>

      {/* KPI */}
      <div className="kpi-grid">
        <KPICard
          label="全國排名"
          value={chiayiRank ? `第 ${chiayiRank} 名` : '—'}
          change={`共 ${sorted.length} 縣市`}
          color="primary"
        />
        <KPICard
          label="嘉義市人口"
          value={formatNumber(chiayi?.population)}
          change="人"
          color="green"
        />
        <KPICard
          label="人口密度"
          value={chiayi?.density ? `${formatNumber(chiayi.density)}` : '—'}
          change="人/km²"
          color="amber"
        />
      </div>

      {/* Sort toggle */}
      <div className="filter-bar">
        <span className="filter-label">排序依據：</span>
        <button
          className={`filter-btn ${sortBy === 'population' ? 'active' : ''}`}
          onClick={() => setSortBy('population')}
        >
          人口
        </button>
        <button
          className={`filter-btn ${sortBy === 'density' ? 'active' : ''}`}
          onClick={() => setSortBy('density')}
        >
          密度
        </button>
      </div>

      {/* Chart */}
      <ChartWrapper title={`${sortBy === 'density' ? '人口密度' : '人口數'}排名（前 15）`}>
        <Bar
          data={{
            labels: barLabels,
            datasets: [{
              data: barValues,
              backgroundColor: barColors,
              borderRadius: 6,
            }]
          }}
          options={{
            responsive: true,
            indexAxis: 'y',
            plugins: { legend: { display: false } },
            scales: { x: { ticks: { callback: v => formatNumber(v) } } }
          }}
        />
      </ChartWrapper>

      {/* Table */}
      <div className="chart-card">
        <h3>全部縣市排名</h3>
        <DataTable
          columns={[
            { key: 'rank', label: '排名', align: 'right', sortable: true },
            { key: 'county', label: '縣市' },
            { key: 'population', label: '人口數', align: 'right', render: row => formatNumber(row.population) },
            { key: 'density', label: '密度（人/km²）', align: 'right', render: row => formatNumber(row.density) },
          ]}
          data={sorted.map((d, i) => ({ ...d, rank: i + 1 }))}
          pageSize={10}
          searchable={true}
          searchPlaceholder="搜尋縣市..."
          highlightRow={row => row.county === '嘉義市'}
        />
      </div>
    </>
  )
}
