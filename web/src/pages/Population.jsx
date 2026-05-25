import { useState } from 'react'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, Filler } from 'chart.js'
import { Bar, Line } from 'react-chartjs-2'
import { useData, formatNumber } from '../hooks/useData'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, Filler)

function PyramidChart({ ageData }) {
  if (!ageData?.length) return null

  const sorted = [...ageData].sort((a, b) => Number(a.age_midpoint) - Number(b.age_midpoint))
  const labels = sorted.map(a => a.age_group.replace('歲', ''))
  const maleData = sorted.map(a => -Number(a.male))  // Negative for left side
  const femaleData = sorted.map(a => Number(a.female))

  return (
    <div className="chart-card full-width">
      <h3>📊 人口金字塔（性別年齡分布）</h3>
      <Bar
        data={{
          labels,
          datasets: [
            {
              label: '男性',
              data: maleData,
              backgroundColor: '#3b82f6',
              borderRadius: 3,
            },
            {
              label: '女性',
              data: femaleData,
              backgroundColor: '#ec4899',
              borderRadius: 3,
            }
          ]
        }}
        options={{
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              stacked: false,
              ticks: {
                callback: v => formatNumber(Math.abs(v)),
              },
              grid: { color: 'rgba(100,116,139,0.1)' }
            },
            y: {
              grid: { display: false }
            }
          },
          plugins: {
            legend: { position: 'top' },
            tooltip: {
              callbacks: {
                label: ctx => `${ctx.dataset.label}: ${formatNumber(Math.abs(ctx.raw))} 人`
              }
            }
          }
        }}
        height={400}
      />
    </div>
  )
}

function AgeStructureTable({ ageData }) {
  if (!ageData?.length) return null

  const sorted = [...ageData].sort((a, b) => Number(a.age_midpoint) - Number(b.age_midpoint))
  const young = sorted.filter(a => ['0~4歲','5~9歲','10~14歲'].includes(a.age_group)).reduce((s,a) => s + Number(a.total), 0)
  const working = sorted.filter(a => /^1[5-9]|2\d|3\d|4\d|5\d|60~64/.test(a.age_group)).reduce((s,a) => s + Number(a.total), 0)
  const old = sorted.filter(a => /^6[5-9]|7\d|8\d|9\d|100/.test(a.age_group)).reduce((s,a) => s + Number(a.total), 0)
  const agingIndex = young > 0 ? (old / young * 100).toFixed(1) : '—'
  const depRatio = working > 0 ? ((young + old) / working * 100).toFixed(1) : '—'

  return (
    <div className="chart-grid">
      <div className="chart-card">
        <h3>🔢 年齡結構指標</h3>
        <table className="data-table">
          <tbody>
            <tr><td>0-14歲（幼年人口）</td><td style={{textAlign:'right',fontWeight:600}}>{formatNumber(young)}</td></tr>
            <tr><td>15-64歲（工作年齡）</td><td style={{textAlign:'right',fontWeight:600}}>{formatNumber(working)}</td></tr>
            <tr><td>65歲以上（老年人口）</td><td style={{textAlign:'right',fontWeight:600}}>{formatNumber(old)}</td></tr>
            <tr style={{borderTop:'2px solid var(--bg-border)'}}><td><strong>老化指數</strong></td><td style={{textAlign:'right',fontWeight:700,color:'var(--accent-red)'}}>{agingIndex}</td></tr>
            <tr><td><strong>扶養比</strong></td><td style={{textAlign:'right',fontWeight:700,color:'var(--accent-orange)'}}>{depRatio}%</td></tr>
          </tbody>
        </table>
        <p style={{fontSize:'0.85em',color:'var(--text-secondary)',marginTop:12}}>
          老化指數 = 65歲以上人口 ÷ 0-14歲人口 × 100<br/>
          超過 100 表示老年人口多於幼年人口（高齡社會警戒線）
        </p>
      </div>
      <div className="chart-card">
        <h3>📋 各年齡層明細</h3>
        <table className="data-table">
          <thead>
            <tr><th>年齡層</th><th style={{textAlign:'right'}}>男性</th><th style={{textAlign:'right'}}>女性</th><th style={{textAlign:'right'}}>合計</th></tr>
          </thead>
          <tbody>
            {sorted.map(a => (
              <tr key={a.age_group}>
                <td>{a.age_group}</td>
                <td style={{textAlign:'right'}}>{formatNumber(a.male)}</td>
                <td style={{textAlign:'right'}}>{formatNumber(a.female)}</td>
                <td style={{textAlign:'right',fontWeight:600}}>{formatNumber(a.total)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default function Population() {
  const { data: population, loading: popLoading } = useData('population_annual.json')
  const { data: ageGender, loading: ageLoading } = useData('population_age_gender.json')
  const { data: village, loading: villageLoading } = useData('population_village_monthly.json')

  if (popLoading || ageLoading || villageLoading) return <div className="container"><p>載入中...</p></div>

  const latest = population?.[population.length - 1] || {}

  // Population trend chart
  const trendLabels = population?.map(p => `${p.year}年`) || []
  const trendData = population?.map(p => Number(p.total_population)) || []

  // Village data
  const sortedVillages = [...(village || [])].sort((a, b) => Number(b.population) - Number(a.population)).slice(0, 15)

  // Calculate year-over-year change
  const yoyChanges = []
  for (let i = 1; i < (population?.length || 0); i++) {
    const prev = population[i - 1]
    const curr = population[i]
    yoyChanges.push({
      year: curr.year,
      change: Number(curr.total_population) - Number(prev.total_population),
      pct: Number(prev.total_population) > 0
        ? ((Number(curr.total_population) - Number(prev.total_population)) / Number(prev.total_population) * 100).toFixed(2)
        : 0
    })
  }

  return (
    <>
      <div className="page-header">
        <h1>👥 人口詳情</h1>
        <p>嘉義市人口趨勢、年齡結構與區里分布</p>
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
        <div className="kpi-card orange">
          <div className="kpi-label">戶數</div>
          <div className="kpi-value">{formatNumber(latest.households)}</div>
        </div>
      </div>

      {/* Population trend */}
      <div className="chart-grid">
        <div className="chart-card">
          <h3>📈 歷年人口趨勢</h3>
          <Line
            data={{
              labels: trendLabels,
              datasets: [{
                label: '總人口',
                data: trendData,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59,130,246,0.1)',
                fill: true,
                tension: 0.3,
              }]
            }}
            options={{
              responsive: true,
              plugins: { legend: { display: false } },
              scales: {
                y: { ticks: { callback: v => formatNumber(v) } }
              }
            }}
          />
        </div>

        <div className="chart-card">
          <h3>📉 年增減變化</h3>
          <table className="data-table">
            <thead>
              <tr><th>年度</th><th style={{textAlign:'right'}}>增減人數</th><th style={{textAlign:'right'}}>增減率</th></tr>
            </thead>
            <tbody>
              {yoyChanges.slice().reverse().map(c => (
                <tr key={c.year}>
                  <td>{c.year}年</td>
                  <td style={{textAlign:'right', color: Number(c.change) >= 0 ? 'var(--accent-green)' : 'var(--accent-red)'}}>
                    {Number(c.change) >= 0 ? '+' : ''}{formatNumber(c.change)}
                  </td>
                  <td style={{textAlign:'right', color: Number(c.change) >= 0 ? 'var(--accent-green)' : 'var(--accent-red)'}}>
                    {c.pct}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Population Pyramid */}
      <PyramidChart ageData={ageGender} />

      {/* Age structure indicators */}
      <AgeStructureTable ageData={ageGender} />

      {/* Village chart */}
      {sortedVillages.length > 0 && (
        <div className="chart-card" style={{marginTop: 24}}>
          <h3>🏘️ 各里人口 Top 15</h3>
          <Bar
            data={{
              labels: sortedVillages.map(v => v.village),
              datasets: [{
                label: '人口數',
                data: sortedVillages.map(v => Number(v.population)),
                backgroundColor: sortedVillages.map(v => v.district === '東區' ? '#3b82f6' : '#10b981'),
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
      )}
    </>
  )
}
