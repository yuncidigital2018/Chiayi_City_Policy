import { useState } from 'react'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js'
import { Bar, Line } from 'react-chartjs-2'
import { useData, formatNumber } from '../hooks/useData'

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend)

const CHIAYI_COLOR = '#1a73e8'
const OTHER_COLOR = '#cfd8dc'

export default function Comparison() {
  const { data: countyData, loading } = useData('county_population_comparison.json')
  const { data: popAnnual } = useData('population_annual.json')
  const [sortBy, setSortBy] = useState('population') // population | density

  if (loading) return <div className="container"><p>載入中...</p></div>

  const latest = countyData?.filter(d => d.year === Math.max(...countyData.map(x => x.year))) || []
  const sorted = [...latest].sort((a, b) =>
    sortBy === 'density' ? b.density - a.density : b.population - a.population
  )
  const chiayiRank = sorted.findIndex(d => d.county === '嘉義市') + 1
  const chiayi = sorted.find(d => d.county === '嘉義市')

  // Bar chart: top 15 + highlight Chiayi
  const top15 = sorted.slice(0, 15)
  const barLabels = top15.map(d => d.county)
  const barValues = top15.map(d => sortBy === 'density' ? d.density : d.population)
  const barColors = top15.map(d => d.county === '嘉義市' ? CHIAYI_COLOR : OTHER_COLOR)

  const barData = {
    labels: barLabels,
    datasets: [{
      label: sortBy === 'density' ? '人口密度 (人/km²)' : '人口數',
      data: barValues,
      backgroundColor: barColors,
      borderRadius: 4,
    }],
  }

  const barOptions = {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (ctx) => sortBy === 'density'
            ? `${ctx.raw.toLocaleString()} 人/km²`
            : `${ctx.raw.toLocaleString()} 人`,
        },
      },
    },
    scales: {
      x: {
        ticks: {
          callback: (v) => sortBy === 'density'
            ? v.toLocaleString()
            : (v / 10000).toFixed(0) + '萬',
        },
      },
    },
  }

  // Population trend: Chiayi vs similar-sized cities
  const years = [...new Set(popAnnual?.map(d => d.year) || [])].sort()
  const trendData = {
    labels: years.map(y => `${y}`),
    datasets: [{
      label: '嘉義市人口',
      data: popAnnual?.map(d => Number(d.total_population)) || [],
      borderColor: CHIAYI_COLOR,
      backgroundColor: CHIAYI_COLOR + '20',
      fill: true,
      tension: 0.3,
    }],
  }

  return (
    <>
      <div className="page-header">
        <h1>📊 縣市比較</h1>
        <p>嘉義市在全國 22 縣市中的人口排名與密度分析</p>
      </div>

      {/* KPI Cards */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-label">人口排名</div>
          <div className="kpi-value">第 {chiayiRank || '—'} 名</div>
          <div className="kpi-sub">/ {sorted.length} 縣市</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">嘉義市人口</div>
          <div className="kpi-value">{chiayi ? formatNumber(chiayi.population) : '—'}</div>
          <div className="kpi-sub">{chiayi?.year} 年底</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">人口密度</div>
          <div className="kpi-value">{chiayi ? chiayi.density.toLocaleString() : '—'}</div>
          <div className="kpi-sub">人/km²</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">面積</div>
          <div className="kpi-value">{chiayi ? chiayi.area_km2.toFixed(1) : '—'}</div>
          <div className="kpi-sub">km²</div>
        </div>
      </div>

      {/* Sort Toggle */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <h2 style={{ margin: 0 }}>全國排名</h2>
          <div>
            <button
              className={`btn ${sortBy === 'population' ? 'btn-primary' : 'btn-outline'}`}
              onClick={() => setSortBy('population')}
              style={{ marginRight: 8 }}
            >
              依人口
            </button>
            <button
              className={`btn ${sortBy === 'density' ? 'btn-primary' : 'btn-outline'}`}
              onClick={() => setSortBy('density')}
            >
              依密度
            </button>
          </div>
        </div>
        <div style={{ height: 500 }}>
          <Bar data={barData} options={barOptions} />
        </div>
      </div>

      {/* Chiayi Population Trend */}
      <div className="card" style={{ marginTop: 20 }}>
        <h2>嘉義市歷年人口趨勢</h2>
        <div style={{ height: 300 }}>
          <Line data={trendData} options={{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              tooltip: {
                callbacks: {
                  label: (ctx) => `${ctx.raw.toLocaleString()} 人`,
                },
              },
            },
            scales: {
              y: {
                ticks: { callback: (v) => (v / 10000).toFixed(1) + '萬' },
              },
            },
          }} />
        </div>
      </div>

      {/* Full Ranking Table */}
      <div className="card" style={{ marginTop: 20 }}>
        <h2>完整排名表</h2>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>排名</th>
                <th>縣市</th>
                <th style={{ textAlign: 'right' }}>人口</th>
                <th style={{ textAlign: 'right' }}>面積 (km²)</th>
                <th style={{ textAlign: 'right' }}>密度 (人/km²)</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((d, i) => (
                <tr key={d.county} className={d.county === '嘉義市' ? 'highlight-row' : ''}>
                  <td>{i + 1}</td>
                  <td>{d.county}</td>
                  <td style={{ textAlign: 'right' }}>{formatNumber(d.population)}</td>
                  <td style={{ textAlign: 'right' }}>{d.area_km2.toFixed(1)}</td>
                  <td style={{ textAlign: 'right' }}>{d.density.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  )
}
