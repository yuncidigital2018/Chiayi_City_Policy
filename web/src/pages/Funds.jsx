import { useState } from 'react'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js'
import { Bar } from 'react-chartjs-2'
import { useData, formatNumber } from '../hooks/useData'
import ChartWrapper from '../components/ChartWrapper'
import DataTable from '../components/DataTable'
import StatusMessage from '../components/StatusMessage'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const FUND_COLORS = {
  '政事型基金': '#8b5cf6',
  '作業基金': '#f59e0b',
  '營業基金': '#10b981',
}

function FundSummaryCard({ fundType, data }) {
  if (!data?.length) return null

  const total = data.reduce((s, d) => s + Number(d.amount), 0)

  return (
    <ChartWrapper title={fundType} empty={!data.length}>
      <div style={{ marginBottom: 12 }}>
        <span style={{ fontSize: 24, fontWeight: 700, color: FUND_COLORS[fundType] || '#1e293b' }}>
          {formatNumber(total)}
        </span>
        <span style={{ fontSize: 13, color: '#64748b', marginLeft: 8 }}>千元</span>
      </div>
      <DataTable
        columns={[
          { key: 'item_name', label: '項目' },
          { key: 'amount', label: '金額（千元）', align: 'right', render: row => formatNumber(row.amount) },
        ]}
        data={data}
        pageSize={5}
        searchable={false}
        emptyMessage="暫無資料"
      />
    </ChartWrapper>
  )
}

export default function Funds() {
  const { data: operating, loading: opLoading, error: opError } = useData('fund_operating.json')
  const { data: business, loading: bizLoading, error: bizError } = useData('fund_business.json')
  const { data: affairs, loading: affLoading, error: affError } = useData('fund_affairs.json')

  const loading = opLoading || bizLoading || affLoading
  const error = opError || bizError || affError

  if (loading) return <StatusMessage type="loading" />
  if (error) return <StatusMessage type="error" message={error} />

  const allFunds = [
    ...(operating || []).map(d => ({ ...d, fund_type: '營業基金' })),
    ...(business || []).map(d => ({ ...d, fund_type: '作業基金' })),
    ...(affairs || []).map(d => ({ ...d, fund_type: '政事型基金' })),
  ]

  return (
    <>
      <div className="page-header">
        <h1>📊 基金儀表板</h1>
        <p>嘉義市各類基金預算概覽</p>
      </div>

      <div className="chart-grid">
        <FundSummaryCard fundType="營業基金" data={operating} />
        <FundSummaryCard fundType="作業基金" data={business} />
        <FundSummaryCard fundType="政事型基金" data={affairs} />
      </div>

      {allFunds.length > 0 && (
        <ChartWrapper title="各基金金額比較">
          <Bar
            data={{
              labels: allFunds.map(d => d.item_name || d.fund_type),
              datasets: [{
                label: '金額（千元）',
                data: allFunds.map(d => Number(d.amount)),
                backgroundColor: allFunds.map(d => FUND_COLORS[d.fund_type] || '#64748b'),
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
      )}
    </>
  )
}
