import { useState, useMemo } from 'react'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend, Filler } from 'chart.js'
import { Bar, Line } from 'react-chartjs-2'
import { useData, formatNumber } from '../hooks/useData'
import { KPICard } from '../components/Card'
import ChartWrapper from '../components/ChartWrapper'
import StatusMessage from '../components/StatusMessage'

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend, Filler)

function classifyPyramidShape(ageData) {
  if (!ageData?.length) return { type: 'unknown', label: '資料不足' }

  const young = ageData.filter(a => ['0~4歲','5~9歲','10~14歲'].includes(a.age_group)).reduce((s,a) => s + Number(a.total), 0)
  const old = ageData.filter(a => /^(6[5-9]|7\d|8\d|9\d|100)/.test(a.age_group)).reduce((s,a) => s + Number(a.total), 0)
  const working = ageData.filter(a => /^1[5-9]|\d{2}|3\d|4\d|5\d|60~64/.test(a.age_group)).reduce((s,a) => s + Number(a.total), 0)

  const agingIndex = young > 0 ? old / young * 100 : 0
  const total = young + old + working
  const youngPct = total > 0 ? young / total * 100 : 0
  const oldPct = total > 0 ? old / total * 100 : 0

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
  return {
    type: 'bell',
    label: '金鐘型',
    icon: '🔔',
    desc: '幼年人口 > 老年人口',
    agingIndex: agingIndex.toFixed(1),
    youngPct: youngPct.toFixed(1),
    oldPct: oldPct.toFixed(1),
  }
}

export default function Population() {
  const { data: ageGender, loading: agLoading, error: agError } = useData('population_age_gender.json')
  const { data: population, loading: popLoading, error: popError } = useData('population_annual.json')

  const loading = agLoading || popLoading
  const error = agError || popError

  if (loading) return <StatusMessage type="loading" />
  if (error) return <StatusMessage type="error" message={error} />

  const shape = classifyPyramidShape(ageGender)
  const latestPop = population?.[population.length - 1] || {}
  const prevPop = population?.[population.length - 2] || {}
  const popChange = Number(latestPop.total_population) - Number(prevPop.total_population)

  return (
    <>
      <div className="page-header">
        <h1>👥 人口結構分析</h1>
        <p>嘉義市人口年齡結構與趨勢</p>
      </div>

      {/* KPI */}
      <div className="kpi-grid">
        <KPICard
          label="總人口"
          value={formatNumber(latestPop.total_population)}
          change={`${popChange >= 0 ? '+' : ''}${formatNumber(popChange)} 較上年`}
          changeType={popChange >= 0 ? 'positive' : 'negative'}
          color="primary"
        />
        <KPICard
          label="老化指數"
          value={shape.agingIndex || '—'}
          change={shape.label}
          color="red"
        />
        <KPICard
          label="幼年人口比"
          value={`${shape.youngPct || '—'}%`}
          change="0-14 歲"
          color="amber"
        />
        <KPICard
          label="老年人口比"
          value={`${shape.oldPct || '—'}%`}
          change="65+ 歲"
          color="purple"
        />
      </div>

      {/* Pyramid shape analysis */}
      <ChartWrapper title="人口金字塔型態判定" empty={!ageGender?.length}>
        <div style={{ textAlign: 'center', padding: '20px 0' }}>
          <div style={{ fontSize: 48, marginBottom: 8 }}>{shape.icon}</div>
          <div style={{ fontSize: 20, fontWeight: 700, marginBottom: 4 }}>{shape.label}</div>
          <div style={{ color: '#64748b', marginBottom: 16 }}>{shape.desc}</div>
          <div style={{ display: 'flex', justifyContent: 'center', gap: 32, fontSize: 14 }}>
            <div>
              <div style={{ fontWeight: 600, color: '#2563eb' }}>{shape.youngPct}%</div>
              <div style={{ color: '#64748b' }}>幼年</div>
            </div>
            <div>
              <div style={{ fontWeight: 600, color: '#ef4444' }}>{shape.oldPct}%</div>
              <div style={{ color: '#64748b' }}>老年</div>
            </div>
          </div>
        </div>
      </ChartWrapper>

      {/* Charts */}
      <div className="chart-grid">
        <ChartWrapper title="年齡人口金字塔" empty={!ageGender?.length}>
          <Bar
            data={{
              labels: ageGender?.map(a => a.age_group) || [],
              datasets: [
                {
                  label: '男',
                  data: ageGender?.map(a => -Number(a.male)) || [],
                  backgroundColor: '#2563eb',
                  borderRadius: 4,
                },
                {
                  label: '女',
                  data: ageGender?.map(a => Number(a.female)) || [],
                  backgroundColor: '#ec4899',
                  borderRadius: 4,
                },
              ]
            }}
            options={{
              responsive: true,
              indexAxis: 'y',
              plugins: {
                legend: { position: 'top' },
                tooltip: {
                  callbacks: {
                    label: (ctx) => `${ctx.dataset.label}: ${formatNumber(Math.abs(ctx.raw))}`
                  }
                }
              },
              scales: {
                x: {
                  ticks: { callback: v => formatNumber(Math.abs(v)) }
                }
              }
            }}
          />
        </ChartWrapper>

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
