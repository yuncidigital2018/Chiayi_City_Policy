import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js'
import { Bar } from 'react-chartjs-2'
import { useData, formatBudget, formatNumber } from '../hooks/useData'
import ChartWrapper from '../components/ChartWrapper'
import DataTable from '../components/DataTable'
import StatusMessage from '../components/StatusMessage'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const FUND_COLORS = {
  '政事型基金': '#8b5cf6',
  '作業基金': '#f59e0b',
  '營業基金': '#10b981',
}

const METRIC_COLORS = {
  income: '#10b981',
  expense: '#2563eb',
  balance: '#f59e0b',
}

function findAmount(data, { item, fundName = '合計', category }) {
  const row = data?.find(d =>
    d.item === item &&
    d.fund_name === fundName &&
    (category ? d.category === category : true)
  )
  return row ? Number(row.amount) : null
}

function buildFundOverview({ operating, business, affairs }) {
  return [
    {
      fund_type: '作業基金',
      income_label: '業務收入',
      expense_label: '業務成本與費用',
      balance_label: '本期賸餘(短絀)',
      income: findAmount(operating, { item: '業務收入' }),
      expense: findAmount(operating, { item: '業務成本與費用' }),
      balance: findAmount(operating, { item: '本期賸餘(短絀－)' }),
    },
    {
      fund_type: '營業基金',
      income_label: '營業收入',
      expense_label: '營業費用',
      balance_label: '本期純益(純損)',
      income: findAmount(business, { item: '營業收入' }),
      expense: findAmount(business, { item: '營業費用' }),
      balance: findAmount(business, { item: '本期純益(純損-)' }),
    },
    {
      fund_type: '政事型基金',
      income_label: '基金來源',
      expense_label: '基金用途',
      balance_label: '賸餘',
      income: findAmount(affairs, { item: '基金來源', category: 'current' }),
      expense: findAmount(affairs, { item: '基金用途', category: 'current' }),
      balance: findAmount(affairs, { item: '賸餘', category: 'current' }),
    },
  ]
}

function formatCategory(value) {
  if (value === 'current') return '本年度'
  if (value === 'previous') return '上年度'
  return '本年度'
}

function FundSummaryCard({ fundType, data }) {
  if (!data?.length) return null

  const topItem = [...data].sort((a, b) => Number(b.amount) - Number(a.amount))[0]

  return (
    <ChartWrapper title={fundType} empty={!data.length}>
      <div style={{ marginBottom: 12 }}>
        <span style={{ fontSize: 24, fontWeight: 700, color: FUND_COLORS[fundType] || '#1e293b' }}>
          {formatNumber(topItem?.amount)}
        </span>
        <span style={{ fontSize: 13, color: '#64748b', marginLeft: 8 }}>千元</span>
        <div style={{ fontSize: 13, color: '#64748b', marginTop: 4 }}>
          最大列示項目：{topItem?.item || topItem?.fund_name || '—'}
        </div>
      </div>
      <DataTable
        columns={[
          { key: 'item', label: '項目', render: row => row.item || row.item_name || '—' },
          { key: 'fund_name', label: '基金/單位', render: row => row.fund_name || '—' },
          { key: 'category', label: '口徑', render: row => formatCategory(row.category) },
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

  const fundOverview = buildFundOverview({ operating, business, affairs })
  const hasOverview = fundOverview.some(row =>
    [row.income, row.expense, row.balance].some(value => value != null)
  )

  return (
    <>
      <div className="page-header">
        <h1>📊 基金儀表板</h1>
        <p>嘉義市各類基金預算概覽</p>
      </div>

      <div className="chart-grid">
        <FundSummaryCard fundType="作業基金" data={operating} />
        <FundSummaryCard fundType="營業基金" data={business} />
        <FundSummaryCard fundType="政事型基金" data={affairs} />
      </div>

      {hasOverview && (
        <ChartWrapper title="基金類型收支比較（彙總口徑）">
          <Bar
            data={{
              labels: fundOverview.map(d => d.fund_type),
              datasets: [
                {
                  label: '收入/來源',
                  data: fundOverview.map(d => d.income),
                  backgroundColor: METRIC_COLORS.income,
                  borderRadius: 6,
                },
                {
                  label: '支出/用途',
                  data: fundOverview.map(d => d.expense),
                  backgroundColor: METRIC_COLORS.expense,
                  borderRadius: 6,
                },
                {
                  label: '賸餘/純益',
                  data: fundOverview.map(d => d.balance),
                  backgroundColor: METRIC_COLORS.balance,
                  borderRadius: 6,
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
                    label: (ctx) => `${ctx.dataset.label}: ${formatBudget(ctx.raw, { includeUnit: true })}`
                  }
                }
              },
              scales: { x: { ticks: { callback: v => formatBudget(v) } } }
            }}
          />
        </ChartWrapper>
      )}

      {hasOverview && (
        <div className="chart-card">
          <h3>比較口徑說明</h3>
          <DataTable
            columns={[
              { key: 'fund_type', label: '基金類型' },
              { key: 'income_label', label: '收入/來源科目' },
              { key: 'income', label: '收入/來源', align: 'right', render: row => formatNumber(row.income) },
              { key: 'expense_label', label: '支出/用途科目' },
              { key: 'expense', label: '支出/用途', align: 'right', render: row => formatNumber(row.expense) },
              { key: 'balance_label', label: '結果科目' },
              { key: 'balance', label: '賸餘/純益', align: 'right', render: row => formatNumber(row.balance) },
            ]}
            data={fundOverview}
            pageSize={0}
            searchable={false}
            emptyMessage="暫無基金彙總資料"
          />
        </div>
      )}
    </>
  )
}
