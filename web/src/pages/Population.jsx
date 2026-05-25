import { useState, useMemo } from 'react'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, Filler } from 'chart.js'
import { Bar, Line } from 'react-chartjs-2'
import { useData, formatNumber } from '../hooks/useData'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, Filler)

// ========================
// Pyramid shape classifier
// ========================

function classifyPyramidShape(ageData) {
  if (!ageData?.length) return { type: 'unknown', label: '資料不足' }

  const young = ageData.filter(a => ['0~4歲','5~9歲','10~14歲'].includes(a.age_group)).reduce((s,a) => s + Number(a.total), 0)
  const old = ageData.filter(a => /^(6[5-9]|7\d|8\d|9\d|100)/.test(a.age_group)).reduce((s,a) => s + Number(a.total), 0)
  const working = ageData.filter(a => /^1[5-9]|2\d|3\d|4\d|5\d|60~64/.test(a.age_group)).reduce((s,a) => s + Number(a.total), 0)

  const agingIndex = young > 0 ? old / young * 100 : 0
  const youngPct = (young + old + working) > 0 ? young / (young + old + working) * 100 : 0
  const oldPct = (young + old + working) > 0 ? old / (young + old + working) * 100 : 0

  if (agingIndex > 100) {
    return {
      type: 'inverted-bell',
      label: '倒金鐘型',
      icon: '🔔',
      desc: '老年人口 > 幼年人口，超高齡社會',
      agingIndex: agingIndex.toFixed(1),
      youngPct: youngPct.toFixed(1),
      oldPct: oldPct.toFixed(1),
    }
  }
  if (agingIndex > 50) {
    return {
      type: 'spindle',
      label: '紡錘型',
      icon: '🔵',
      desc: '青壯年為主，幼年人口縮減中',
      agingIndex: agingIndex.toFixed(1),
      youngPct: youngPct.toFixed(1),
      oldPct: oldPct.toFixed(1),
    }
  }
  if (agingIndex > 20) {
    return {
      type: 'lantern',
      label: '燈籠型',
      icon: '🏮',
      desc: '青壯年為主體，過渡階段',
      agingIndex: agingIndex.toFixed(1),
      youngPct: youngPct.toFixed(1),
      oldPct: oldPct.toFixed(1),
    }
  }
  return {
    type: 'classic',
    label: '金字塔型',
    icon: '🔺',
    desc: '幼年人口多，典型發展中國家',
    agingIndex: agingIndex.toFixed(1),
    youngPct: youngPct.toFixed(1),
    oldPct: oldPct.toFixed(1),
  }
}

// ========================
// Population Pyramid Chart
// ========================

function PyramidChart({ ageData, year, highlightShape }) {
  if (!ageData?.length) return null

  const sorted = [...ageData].sort((a, b) => Number(a.age_midpoint) - Number(b.age_midpoint))
  const labels = sorted.map(a => a.age_group.replace('歲', ''))
  const maleData = sorted.map(a => -Number(a.male))
  const femaleData = sorted.map(a => Number(a.female))

  // Color coding by age group
  const barColors = sorted.map(a => {
    const mid = Number(a.age_midpoint)
    if (mid < 15) return 'rgba(52, 211, 153, 0.8)'    // young: green
    if (mid < 65) return 'rgba(59, 130, 246, 0.8)'     // working: blue
    return 'rgba(239, 68, 68, 0.8)'                      // old: red
  })

  return (
    <div className="chart-card full-width">
      <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:12}}>
        <h3 style={{margin:0}}>📊 人口金字塔 {year ? `(${year})` : ''}</h3>
        {highlightShape && (
          <span style={{
            padding: '4px 12px',
            borderRadius: 16,
            fontSize: '0.85em',
            fontWeight: 600,
            background: highlightShape.type === 'inverted-bell' ? 'rgba(239,68,68,0.1)' :
                        highlightShape.type === 'spindle' ? 'rgba(245,158,11,0.1)' :
                        'rgba(59,130,246,0.1)',
            color: highlightShape.type === 'inverted-bell' ? '#ef4444' :
                   highlightShape.type === 'spindle' ? '#f59e0b' : '#3b82f6',
          }}>
            {highlightShape.icon} {highlightShape.label}
          </span>
        )}
      </div>
      <Bar
        data={{
          labels,
          datasets: [
            {
              label: '男性',
              data: maleData,
              backgroundColor: sorted.map(a => {
                const mid = Number(a.age_midpoint)
                if (mid < 15) return 'rgba(52, 211, 153, 0.7)'
                if (mid < 65) return 'rgba(59, 130, 246, 0.7)'
                return 'rgba(239, 68, 68, 0.7)'
              }),
              borderRadius: 3,
            },
            {
              label: '女性',
              data: femaleData,
              backgroundColor: sorted.map(a => {
                const mid = Number(a.age_midpoint)
                if (mid < 15) return 'rgba(52, 211, 153, 0.7)'
                if (mid < 65) return 'rgba(236, 72, 153, 0.7)'
                return 'rgba(239, 68, 68, 0.7)'
              }),
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
              ticks: { callback: v => formatNumber(Math.abs(v)) },
              grid: { color: 'rgba(100,116,139,0.1)' }
            },
            y: { grid: { display: false } }
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
        height={380}
      />
      <div style={{display:'flex', gap:16, marginTop:12, fontSize:'0.8em', color:'var(--text-secondary)'}}>
        <span>🟢 0-14歲（幼年）</span>
        <span>🔵 15-64歲（工作）</span>
        <span>🔴 65歲以上（老年）</span>
      </div>
    </div>
  )
}

// ========================
// Shape evolution timeline (placeholder for future multi-year)
// ========================

function ShapeEvolution({ population, ageData }) {
  const shape = classifyPyramidShape(ageData)
  
  // All known shape stages with approximate years for Taiwan
  const stages = [
    { year: '080', type: 'spindle', label: '紡錘型', icon: '🔵' },
    { year: '090', type: 'spindle', label: '紡錘型', icon: '🔵' },
    { year: '100', type: 'inverted-bell', label: '倒金鐘型', icon: '🔔' },
    { year: '110', type: 'inverted-bell', label: '倒金鐘型', icon: '🔔' },
    { year: '114', type: 'inverted-bell', label: '倒金鐘型', icon: '🔔', current: true },
  ]

  return (
    <div className="chart-card">
      <h3>🔄 金字塔形狀演變</h3>
      <p style={{fontSize:'0.9em', color:'var(--text-secondary)', marginBottom:16}}>
        大多數國家的發展，由幼年人口較多的典型金字塔型，逐漸變為青壯年為主的燈籠型，
        然後變成幼年人口減少的紡錘型，最後變成倒金鐘型。
      </p>
      <div style={{display:'flex', gap:8, overflowX:'auto', paddingBottom:8}}>
        {stages.map(s => (
          <div key={s.year} style={{
            flex: '0 0 auto',
            padding: '12px 16px',
            borderRadius: 12,
            textAlign: 'center',
            minWidth: 80,
            background: s.current ? 'rgba(239,68,68,0.1)' : 'var(--bg-card)',
            border: s.current ? '2px solid rgba(239,68,68,0.3)' : '1px solid var(--bg-border)',
          }}>
            <div style={{fontSize:'1.5em'}}>{s.icon}</div>
            <div style={{fontSize:'0.85em', fontWeight:600, marginTop:4}}>{s.year}年</div>
            <div style={{fontSize:'0.8em', color:'var(--text-secondary)'}}>{s.label}</div>
            {s.current && <div style={{fontSize:'0.7em', color:'#ef4444', marginTop:2}}>← 目前</div>}
          </div>
        ))}
      </div>
      <div style={{marginTop:16, padding:'12px 16px', borderRadius:8, background:'rgba(239,68,68,0.05)', border:'1px solid rgba(239,68,68,0.15)'}}>
        <div style={{fontWeight:600, color:'#ef4444'}}>⚠️ 超高齡社會警訊</div>
        <div style={{fontSize:'0.85em', color:'var(--text-secondary)', marginTop:4}}>
          嘉義市老化指數已超過 100，老年人口多於幼年人口。
          需關注長照、醫療、勞動力等政策議題。
        </div>
      </div>
    </div>
  )
}

// ========================
// Age Structure Indicators
// ========================

function AgeStructureTable({ ageData }) {
  if (!ageData?.length) return null

  const sorted = [...ageData].sort((a, b) => Number(a.age_midpoint) - Number(b.age_midpoint))
  const young = sorted.filter(a => ['0~4歲','5~9歲','10~14歲'].includes(a.age_group)).reduce((s,a) => s + Number(a.total), 0)
  const working = sorted.filter(a => /^1[5-9]|2\d|3\d|4\d|5\d|60~64/.test(a.age_group)).reduce((s,a) => s + Number(a.total), 0)
  const old = sorted.filter(a => /^(6[5-9]|7\d|8\d|9\d|100)/.test(a.age_group)).reduce((s,a) => s + Number(a.total), 0)
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
          老化指數 = 65歲以上 ÷ 0-14歲 × 100（超過 100 = 超高齡社會）
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

// ========================
// Main Page
// ========================

export default function Population() {
  const { data: population, loading: popLoading } = useData('population_annual.json')
  const { data: ageGender, loading: ageLoading } = useData('population_age_gender.json')
  const { data: village, loading: villageLoading } = useData('population_village_monthly.json')

  const shape = useMemo(() => classifyPyramidShape(ageGender), [ageGender])

  if (popLoading || ageLoading || villageLoading) return <div className="container"><p>載入中...</p></div>

  const latest = population?.[population.length - 1] || {}
  const trendLabels = population?.map(p => `${p.year}年`) || []
  const trendData = population?.map(p => Number(p.total_population)) || []
  const sortedVillages = [...(village || [])].sort((a, b) => Number(b.population) - Number(a.population)).slice(0, 15)

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

      {/* Shape evolution */}
      <ShapeEvolution population={population} ageData={ageGender} />

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
              scales: { y: { ticks: { callback: v => formatNumber(v) } } }
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

      {/* Population Pyramid with shape marker */}
      <PyramidChart ageData={ageGender} year={`民國${latest.year}年`} highlightShape={shape} />

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
