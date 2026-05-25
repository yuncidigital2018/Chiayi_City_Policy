import { useState } from 'react'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, Filler } from 'chart.js'
import { Bar } from 'react-chartjs-2'
import { useData, formatNumber, formatChange } from '../hooks/useData'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, Filler)

export default function Population() {
  const { data: population, loading: popLoading } = useData('population_annual.json')
  const { data: village, loading: villageLoading } = useData('population_village_monthly.json')

  if (popLoading || villageLoading) return <div className="container"><p>載入中...</p></div>

  const latest = population?.[population.length - 1] || {}

  // Group village by district
  const districts = {}
  village?.forEach(v => {
    if (!districts[v.district]) districts[v.district] = []
    districts[v.district].push(v)
  })

  // Top villages by population
  const sortedVillages = [...(village || [])].sort((a, b) => Number(b.population) - Number(a.population)).slice(0, 15)

  return (
    <>
      <div className="page-header">
        <h1>👥 人口詳情</h1>
        <p>嘉義市人口趨勢與區里分布</p>
      </div>

      {/* Summary */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-label">最新年度總人口</div>
          <div className="kpi-value">{formatNumber(latest.total_population)}</div>
        </div>
        <div className="kpi-card green">
          <div className="kpi-label">男性</div>
          <div className="kpi-value">{formatNumber(latest.male)}</div>
        </div>
        <div className="kpi-card purple">
          <div className="kpi-label">女性</div>
          <div className="kpi-value">{formatNumber(latest.female)}</div>
        </div>
        <div className="kpi-card red">
          <div className="kpi-label">年度總增減</div>
          <div className="kpi-value">{formatChange(Number(latest.natural_increase) + Number(latest.social_increase))}</div>
        </div>
      </div>

      {/* Village chart */}
      <div className="chart-grid">
        <div className="chart-card">
          <h3>各里人口 Top 15</h3>
          <Bar
            data={{
              labels: sortedVillages.map(v => v.village),
              datasets: [{
                label: '人口數',
                data: sortedVillages.map(v => Number(v.population)),
                backgroundColor: sortedVillages.map(v => v.district === '東區' ? '#2563eb' : '#10b981'),
                borderRadius: 6,
              }]
            }}
            options={{
              responsive: true,
              indexAxis: 'y',
              plugins: { legend: { display: false } }
            }}
          />
        </div>

        <div className="chart-card">
          <h3>人口年增減</h3>
          <table className="data-table">
            <thead>
              <tr><th>年度</th><th>總人口</th><th>自然增減</th><th>社會增減</th><th>合計</th></tr>
            </thead>
            <tbody>
              {(population || []).slice().reverse().map(p => (
                <tr key={p.year}>
                  <td>{p.year}年</td>
                  <td>{formatNumber(p.total_population)}</td>
                  <td style={{ color: Number(p.natural_increase) >= 0 ? 'var(--accent-green)' : 'var(--accent-red)' }}>
                    {formatChange(p.natural_increase)}
                  </td>
                  <td style={{ color: Number(p.social_increase) >= 0 ? 'var(--accent-green)' : 'var(--accent-red)' }}>
                    {formatChange(p.social_increase)}
                  </td>
                  <td style={{ fontWeight: 600 }}>
                    {formatChange(Number(p.natural_increase) + Number(p.social_increase))}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  )
}
