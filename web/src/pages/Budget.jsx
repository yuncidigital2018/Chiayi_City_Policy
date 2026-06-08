import { Fragment, useState } from 'react'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, ArcElement, PointElement, LineElement, Title, Tooltip, Legend, Filler } from 'chart.js'
import { Bar, Doughnut } from 'react-chartjs-2'
import { useData, formatNumber, formatBudget } from '../hooks/useData'
import { KPICard } from '../components/Card'
import ChartWrapper from '../components/ChartWrapper'
import DataTable from '../components/DataTable'
import StatusMessage from '../components/StatusMessage'
import SegmentedControl from '../components/SegmentedControl'

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
        {tree.map((item) => {
          const key = item.key
          const children = childrenMap[key] || []
          const isExpanded = expanded[key]
          const pct = totalExp > 0 ? (Number(item.amount) / totalExp * 100).toFixed(1) : 0

          return (
            <Fragment key={key}>
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
                    <td style={{ paddingLeft: 24 }}>{child.function_category}</td>
                    <td style={{ textAlign: 'right' }}>{formatBudget(child.recurring)}</td>
                    <td style={{ textAlign: 'right' }}>{formatBudget(child.capital)}</td>
                    <td style={{ textAlign: 'right' }}>{formatBudget(child.amount)}</td>
                    <td style={{ textAlign: 'right' }}>{cPct}%</td>
                  </tr>
                )
              })}
            </Fragment>
          )
        })}
      </tbody>
    </table>
  )
}

export default function Budget() {
  const { data: revenue, loading: revLoading, error: revError } = useData('budget_revenue_by_source.json')
  const { data: expenditure, loading: expLoading, error: expError } = useData('budget_expenditure_by_function.json')
  const { data: policyDomains, loading: policyLoading, error: policyError } = useData('budget_by_policy_domain.json')
  const { data: agencies, loading: agencyLoading, error: agencyError } = useData('budget_expenditure_by_agency.json')
  const [viewMode, setViewMode] = useState('function')

  const loading = revLoading || expLoading || policyLoading || agencyLoading
  const error = revError || expError || policyError || agencyError

  if (loading) return <StatusMessage type="loading" />
  if (error) return <StatusMessage type="error" message={error} />

  const totalRev = revenue?.reduce((s, r) => s + Number(r.amount), 0) || 0
  const totalExp = expenditure?.filter(e => Number(e.level) === 1).reduce((s, e) => s + Number(e.amount), 0) || 0
  const surplus = totalRev - totalExp
  const expenditureL1 = expenditure?.filter(e => Number(e.level) === 1) || []
  const sortedPolicyDomains = [...(policyDomains || [])].sort((a, b) => Number(b.amount) - Number(a.amount))
  const sortedAgencies = [...(agencies || [])].sort((a, b) => Number(b.amount) - Number(a.amount))
  const viewConfig = {
    function: {
      title: '歲出政事別',
      rows: expenditureL1,
      labelKey: 'function_category',
      valueKey: 'amount',
    },
    policy: {
      title: '政策領域分布',
      rows: sortedPolicyDomains,
      labelKey: 'policy_domain',
      valueKey: 'amount',
    },
    agency: {
      title: '機關別歲出排名',
      rows: sortedAgencies,
      labelKey: 'agency_name',
      valueKey: 'amount',
    },
  }[viewMode]

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
          value={formatBudget(totalRev, { includeUnit: true })}
          change="115 年度"
          color="green"
        />
        <KPICard
          label="歲出總額"
          value={formatBudget(totalExp, { includeUnit: true })}
          change="L1 政事別合計"
          color="primary"
        />
        <KPICard
          label="賸餘/短絀"
          value={formatBudget(surplus, { includeUnit: true })}
          change={surplus >= 0 ? '賸餘' : '短絀'}
          changeType={surplus >= 0 ? 'positive' : 'negative'}
          color={surplus >= 0 ? 'green' : 'red'}
        />
      </div>

      <SegmentedControl
        label="歲出視角"
        value={viewMode}
        onChange={setViewMode}
        options={[
          { value: 'function', label: '政事別' },
          { value: 'policy', label: '政策領域' },
          { value: 'agency', label: '機關別' },
        ]}
      />

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

        <ChartWrapper title={viewConfig.title} empty={!viewConfig.rows.length}>
          <Bar
            data={{
              labels: viewConfig.rows.map(row => row[viewConfig.labelKey]),
              datasets: [{
                label: '金額（千元）',
                data: viewConfig.rows.map(row => Number(row[viewConfig.valueKey])),
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
      {viewMode === 'function' && <div className="chart-card full-width-card">
        <h3>歲出政事別明細</h3>
        <ExpenditureTree data={expenditure} totalExp={totalExp} />
      </div>}

      {viewMode === 'policy' && <div className="chart-card full-width-card">
        <h3>政策領域明細</h3>
        <DataTable
          columns={[
            { key: 'policy_domain', label: '政策領域' },
            { key: 'amount', label: '金額（千元）', align: 'right', render: row => formatNumber(row.amount) },
            { key: 'percentage', label: '占比', align: 'right', render: row => `${row.percentage}%` },
            { key: 'confidence', label: '信心度' },
            { key: 'item_count', label: '項目數', align: 'right' },
          ]}
          data={sortedPolicyDomains}
          pageSize={0}
          searchable={false}
          emptyMessage="暫無政策領域資料"
        />
      </div>}

      {viewMode === 'agency' && <div className="chart-card full-width-card">
        <h3>機關別歲出明細</h3>
        <DataTable
          columns={[
            { key: 'agency_name', label: '機關' },
            { key: 'amount', label: '金額（千元）', align: 'right', render: row => formatNumber(row.amount) },
            {
              key: 'percentage',
              label: '占比',
              align: 'right',
              render: row => `${(Number(row.amount) / totalExp * 100).toFixed(1)}%`,
            },
          ]}
          data={sortedAgencies}
          pageSize={0}
          searchable={false}
          emptyMessage="暫無機關別資料"
        />
      </div>}

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
