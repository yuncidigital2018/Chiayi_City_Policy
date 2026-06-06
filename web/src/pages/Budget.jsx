import { useState } from 'react'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, ArcElement, PointElement, LineElement, Title, Tooltip, Legend, Filler } from 'chart.js'
import { Bar, Doughnut, Line } from 'react-chartjs-2'
import { useData, formatNumber, formatBudget } from '../hooks/useData'
import { KPICard } from '../components/Card'
import ChartWrapper from '../components/ChartWrapper'
import DataTable from '../components/DataTable'
import StatusMessage from '../components/StatusMessage'

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, PointElement, LineElement, Title, Tooltip, Legend, Filler)

const CAT_COLORS = [
  '#2563eb', '#10b981', '#f59e0b', '#ef4444',
  '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16',
]

function ExpenditureTree({ data, totalExp }) {
  const [expanded, setExpanded] = useState({})

  const tree = []
  const childrenMap = {}

  for (const row of data || []) {
    const level = Number(row.level)
    const parent = row.parent_code ? String(row.parent_code) : ''
    if (level === 1) {
      tree.push({ ...row, key: String(row.parent_code) })
      childrenMap[String(row.parent_code)] = []
    } else if (level === 2 && parent) {
      if (!childrenMap[parent]) childrenMap[parent] = []
      childrenMap[parent].push(row)
    }
  }

  const toggle = (key) => setExpanded(prev => ({ ...prev, [key]: !prev[key] }))

  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>政事別</th>
          <th style={{ textAlign: 'right' }}>經常門</th>
          <th style={{ textAlign: 'right' }}>資本門</th>
          <th style={{ textAlign: 'right' }}>合計</th>
          <th style={{ textAlign: 'right' }}>%</th>
        </tr>
      </thead>
      <tbody>
        {tree.map((item, idx) => {
          const key = item.key
          const children = childrenMap[key] || []
          const isExpanded = expanded[key]
          const pct = totalExp > 0 ? (Number(item.amount) / totalExp * 100).toFixed(1) : 0

          return (
            <>
              <tr key={key} className="budget-l1" onClick={() => toggle(key)}>
                <td>{isExpanded ? '▾' : '▸'} {item.function_category}</td>
                <td style={{ textAlign: 'right' }}>{formatBudget(item.recurring)}</td>
                <td style={{ textAlign: 'right' }}>{formatBudget(item.capital)}</td>
                <td style={{ textAlign: 'right' }}>{formatBudget(item.amount)}</td>
                <td style={{ textAlign: 'right' }}>{pct}%</td>
              </tr>
              {isExpanded && children.map((child, ci) => {
                const cPct = totalExp > 0 ? (Number(child.amount) / totalExp * 100).toFixed(1) : 0
                return (
                  <tr key={`${key}-${ci}`} className="budget-l2">
                    <td style={{ paddingLeft: 24 }}>　{child.function_category}</td>
                    <td style={{ textAlign: 'right' }}>{formatBudget(child.recurring)}</td>
                    <td style={{ textAlign: 'right' }}>{formatBudget(child.capital)}</td>
                    <td style={{ textAlign: 'right' }}>{formatBudget(child.amount)}</td>
                    <td style={{ textAlign: 'right' }}>{cPct}%</td>
                  </tr>
                )
              })}
            </>
          )
        })}
      </tbody>
    </table>
  )
}

export default function Budget() {
  const { data: revenue, loading: revLoading, error: revError } = useData('budget_revenue_by_source.json')
  const { data: expenditure, loading: expLoading, error: expError } = useData('budget_expenditure_by_function.json')

  const loading = revLoading || expLoading
  const error = revError || expError

  if (loading) return <StatusMessage type="loading" />
  if (error) return <StatusMessage type="error" message={error} />

  const totalRev = revenue?.reduce((s, r) => s + Number(r.amount), 0) || 0
  const totalExp = expenditure?.filter(e => Number(e.level) === 1).reduce((s, e) => s + Number(e.amount), 0) || 0
  const surplus = totalRev - totalExp

  return (
    <>
      <div className="page-header">
        <h1>💰 預算總覽</h1>
        <p>嘉義市 115 年度歲入歲出分析</p>
      </div>

      {/* KPI */}
      <div className="kpi-grid">
        <KPICard
          label="歲入總額"
          value={formatBudget(totalRev)}
          change="新台幣千元"
          color="green"
        />
        <KPICard
          label="歲出總額"
          value={formatBudget(totalExp)}
          change="新台幣千元"
          color="primary"
        />
        <KPICard
          label="賸餘/短絀"
          value={formatBudget(surplus)}
          change={surplus >= 0 ? '賸餘' : '短絀'}
          changeType={surplus >= 0 ? 'positive' : 'negative'}
          color={surplus >= 0 ? 'green' : 'red'}
        />
      </div>

      {/* Charts */}
      <div className="chart-grid">
        <ChartWrapper title="歲入來源結構" empty={!revenue?.length}>
          <Doughnut
            data={{
              labels: revenue?.map(r => r.source_category) || [],
              datasets: [{
                data: revenue?.map(r => Number(r.amount)) || [],
                backgroundColor: CAT_COLORS,
              }]
            }}
            options={{ responsive: true, plugins: { legend: { position: 'right', labels: { font: { size: 11 } } } } }}
          />
        </ChartWrapper>

        <ChartWrapper title="歲出政事別" empty={!expenditure?.length}>
          <Bar
            data={{
              labels: expenditure?.filter(e => Number(e.level) === 1).map(e => e.function_category) || [],
              datasets: [{
                label: '金額（千元）',
                data: expenditure?.filter(e => Number(e.level) === 1).map(e => Number(e.amount)) || [],
                backgroundColor: CAT_COLORS,
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
      </div>

      {/* Expenditure tree table */}
      <div className="chart-card full-width-card">
        <h3>歲出政事別明細</h3>
        <ExpenditureTree data={expenditure} totalExp={totalExp} />
      </div>

      {/* Revenue table */}
      <div className="chart-card full-width-card">
        <h3>歲入來源明細</h3>
        <DataTable
          columns={[
            { key: 'source_category', label: '來源別' },
            { key: 'amount', label: '金額（千元）', align: 'right', render: row => formatNumber(row.amount) },
          ]}
          data={revenue || []}
          pageSize={0}
          searchable={false}
          emptyMessage="暫無歲入資料"
        />
      </div>
    </>
  )
}
