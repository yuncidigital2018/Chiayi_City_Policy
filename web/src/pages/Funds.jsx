import { useState } from 'react'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js'
import { Bar } from 'react-chartjs-2'
import { useData, formatNumber } from '../hooks/useData'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const FUND_COLORS = {
  '政事型基金': '#8b5cf6',
  '作業基金': '#f59e0b',
  '營業基金': '#10b981',
}

function FundSummaryCard({ fundType, data }) {
  if (!data?.length) return null

  const total = data.reduce((s, d) => s + Number(d.amount), 0)
  const items = data.slice(0, 8)

  return (
    <div className="chart-card">
      <h3 style={{color: FUND_COLORS[fundType] || 'inherit'}}>
        {fundType}
      </h3>
      <table className="data-table">
        <thead>
          <tr><th>項目</th><th style={{textAlign:'right'}}>金額（千元）</th></tr>
        </thead>
        <tbody>
          {items.map((d, i) => (
            <tr key={i}>
              <td>{d.item}</td>
              <td style={{textAlign:'right', fontWeight: 600}}>{formatNumber(d.amount)}</td>
            </tr>
          ))}
          {data.length > 8 && (
            <tr style={{borderTop:'2px solid var(--bg-border)'}}>
              <td><strong>共 {data.length} 項</strong></td>
              <td style={{textAlign:'right', fontWeight: 700, color: FUND_COLORS[fundType]}}>
                {formatNumber(total)}
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}

function FundComparisonChart({ operating, business, affairs }) {
  const datasets = []

  // Aggregate by fund type
  if (operating?.length) {
    const total = operating.reduce((s, d) => s + Number(d.amount), 0)
    datasets.push({
      label: '作業基金',
      data: [total],
      backgroundColor: '#f59e0b',
      borderRadius: 6,
    })
  }
  if (business?.length) {
    const total = business.reduce((s, d) => s + Number(d.amount), 0)
    datasets.push({
      label: '營業基金',
      data: [total],
      backgroundColor: '#10b981',
      borderRadius: 6,
    })
  }
  if (affairs?.length) {
    const current = affairs.filter(d => d.category === 'current')
    const source = current.find(d => d.item === '基金來源')
    const usage = current.find(d => d.item === '基金用途')
    if (source) datasets.push({
      label: '政事型-來源',
      data: [Number(source.amount)],
      backgroundColor: '#8b5cf6',
      borderRadius: 6,
    })
    if (usage) datasets.push({
      label: '政事型-用途',
      data: [Number(usage.amount)],
      backgroundColor: '#a78bfa',
      borderRadius: 6,
    })
  }

  return (
    <div className="chart-card">
      <h3>📊 基金規模比較</h3>
      <Bar
        data={{
          labels: ['基金規模（千元）'],
          datasets,
        }}
        options={{
          responsive: true,
          plugins: { legend: { position: 'top' } },
          scales: {
            y: { ticks: { callback: v => formatNumber(v) } }
          }
        }}
        height={300}
      />
    </div>
  )
}

function AffairsDetail({ data }) {
  if (!data?.length) return null

  // Group by fund name
  const byFund = {}
  data.forEach(d => {
    if (!byFund[d.fund_name]) byFund[d.fund_name] = {}
    const key = `${d.item}_${d.category}`
    byFund[d.fund_name][key] = Number(d.amount)
  })

  return (
    <div className="chart-card">
      <h3>💼 政事型基金明細</h3>
      <table className="data-table">
        <thead>
          <tr>
            <th>基金名稱</th>
            <th style={{textAlign:'right'}}>本年度來源</th>
            <th style={{textAlign:'right'}}>本年度用途</th>
            <th style={{textAlign:'right'}}>賸餘</th>
            <th style={{textAlign:'right'}}>上年度來源</th>
            <th style={{textAlign:'right'}}>上年度用途</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(byFund).map(([name, vals]) => (
            <tr key={name}>
              <td>{name}</td>
              <td style={{textAlign:'right'}}>{formatNumber(vals['基金來源_current'] || 0)}</td>
              <td style={{textAlign:'right'}}>{formatNumber(vals['基金用途_current'] || 0)}</td>
              <td style={{textAlign:'right', color: (vals['賸餘_current'] || 0) >= 0 ? 'var(--accent-green)' : 'var(--accent-red)'}}>
                {formatNumber(vals['賸餘_current'] || 0)}
              </td>
              <td style={{textAlign:'right'}}>{formatNumber(vals['基金來源_previous'] || 0)}</td>
              <td style={{textAlign:'right'}}>{formatNumber(vals['基金用途_previous'] || 0)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default function Funds() {
  const { data: operating, loading: opLoading } = useData('fund_operating.json')
  const { data: business, loading: bizLoading } = useData('fund_business.json')
  const { data: affairs, loading: afLoading } = useData('fund_affairs.json')

  if (opLoading || bizLoading || afLoading) return <div className="container"><p>載入中...</p></div>

  const opTotal = operating?.reduce((s, d) => s + Number(d.amount), 0) || 0
  const bizTotal = business?.reduce((s, d) => s + Number(d.amount), 0) || 0
  const afTotal = affairs?.filter(d => d.category === 'current' && d.item === '基金來源')
    .reduce((s, d) => s + Number(d.amount), 0) || 0

  return (
    <>
      <div className="page-header">
        <h1>💰 基金預算</h1>
        <p>嘉義市作業基金、營業基金、政事型基金綜計</p>
      </div>

      <div className="kpi-grid">
        <div className="kpi-card" style={{borderLeft:'4px solid #f59e0b'}}>
          <div className="kpi-label">作業基金合計</div>
          <div className="kpi-value">{formatNumber(opTotal)}</div>
        </div>
        <div className="kpi-card" style={{borderLeft:'4px solid #10b981'}}>
          <div className="kpi-label">營業基金合計</div>
          <div className="kpi-value">{formatNumber(bizTotal)}</div>
        </div>
        <div className="kpi-card" style={{borderLeft:'4px solid #8b5cf6'}}>
          <div className="kpi-label">政事型基金來源</div>
          <div className="kpi-value">{formatNumber(afTotal)}</div>
        </div>
      </div>

      <FundComparisonChart operating={operating} business={business} affairs={affairs} />

      <div className="chart-grid">
        <FundSummaryCard fundType="作業基金" data={operating} />
        <FundSummaryCard fundType="營業基金" data={business} />
      </div>

      <AffairsDetail data={affairs} />
    </>
  )
}
