import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, RadialLinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js'
import { Bar, Radar } from 'react-chartjs-2'
import { useData } from '../hooks/useData'
import { KPICard } from '../components/Card'
import ChartWrapper from '../components/ChartWrapper'
import DataTable from '../components/DataTable'
import StatusMessage from '../components/StatusMessage'

ChartJS.register(CategoryScale, LinearScale, BarElement, RadialLinearScale, PointElement, LineElement, Title, Tooltip, Legend)

export default function Competitiveness() {
  const { data: rankings, loading: rankLoading, error: rankError } = useData('cw_happy_city_rankings.json')
  const { data: dimensions, loading: dimLoading, error: dimError } = useData('cw_happy_city_dimensions.json')
  const { data: satisfaction, loading: satLoading, error: satError } = useData('gvm_mayor_satisfaction.json')

  const loading = rankLoading || dimLoading || satLoading
  const error = rankError || dimError || satError

  if (loading) return <StatusMessage type="loading" />
  if (error) return <StatusMessage type="error" message={error} />

  const hasAnyData = Boolean(rankings?.length || dimensions?.length || satisfaction?.length)

  // 天下 data
  const nonSix = rankings?.filter(r => r.group === '非六都') || []
  const chiayiRank = nonSix.find(r => r.county === '嘉義市')
  const chiayiDims = dimensions?.filter(d => d.county === '嘉義市' && d.score) || []

  // 遠見 data
  const chiayiSatisfaction = satisfaction?.find(s => s.county === '嘉義市')

  // Bar chart: 非六都排名
  const barData = {
    labels: nonSix.map(r => r.county),
    datasets: [{
      label: '總分',
      data: nonSix.map(r => Number(r.total_score)),
      backgroundColor: nonSix.map(r => r.county === '嘉義市' ? '#2563eb' : '#cfd8dc'),
      borderRadius: 6,
    }]
  }

  // Radar chart: 嘉義市各面向
  const radarLabels = chiayiDims.map(d => d.dimension)
  const radarData = {
    labels: radarLabels,
    datasets: [{
      label: '嘉義市',
      data: chiayiDims.map(d => Number(d.score)),
      backgroundColor: 'rgba(37, 99, 235, 0.2)',
      borderColor: '#2563eb',
      borderWidth: 2,
      pointBackgroundColor: '#2563eb',
    }]
  }

  return (
    <>
      <div className="page-header">
        <h1>🏆 城市競爭力</h1>
        <p>天下雜誌永續幸福城市 + 遠見雜誌施政滿意度</p>
      </div>

      {!hasAnyData && (
        <StatusMessage
          type="empty"
          message="尚未產生城市競爭力資料，請先執行 scripts/scrape_city_surveys.py 與 survey normalizer。"
        />
      )}

      {/* KPI */}
      {hasAnyData && <div className="kpi-grid">
        <KPICard
          label="幸福城市排名"
          value={chiayiRank ? `非六都 #${chiayiRank.rank}` : '—'}
          change={chiayiRank ? `${chiayiRank.total_score} 分` : ''}
          color="primary"
        />
        <KPICard
          label="市長滿意度"
          value={chiayiSatisfaction ? `${chiayiSatisfaction.overall_satisfaction}%` : '—'}
          change={chiayiSatisfaction?.star_rating ? '⭐'.repeat(chiayiSatisfaction.star_rating) : ''}
          color="green"
        />
        <KPICard
          label="八大面向平均"
          value={chiayiSatisfaction ? `${chiayiSatisfaction.avg_dimension_score}%` : '—'}
          change={chiayiSatisfaction ? '突破 8 成' : ''}
          color="amber"
        />
        <KPICard
          label="最佳面向"
          value={chiayiDims.length > 0 ? chiayiDims[0].dimension : '—'}
          change={chiayiDims.length > 0 ? `#${chiayiDims[0].rank_in_non_six} 非六都` : ''}
          color="purple"
        />
      </div>}

      {/* Charts */}
      {hasAnyData && <div className="chart-grid">
        <ChartWrapper title="非六都幸福城市排名 2025（天下雜誌）" empty={!nonSix.length}>
          <Bar
            data={barData}
            options={{
              responsive: true,
              indexAxis: 'y',
              plugins: { legend: { display: false } },
              scales: { x: { min: 400, max: 700 } }
            }}
          />
        </ChartWrapper>

        <ChartWrapper title="嘉義市各面向表現（天下雜誌）" empty={!chiayiDims.length}>
          <Radar
            data={radarData}
            options={{
              responsive: true,
              scales: {
                r: {
                  min: 2,
                  max: 4,
                  ticks: { stepSize: 0.5 },
                  pointLabels: { font: { size: 12 } }
                }
              },
              plugins: { legend: { display: false } }
            }}
          />
        </ChartWrapper>
      </div>}

      {/* 遠見 detail */}
      {hasAnyData && chiayiSatisfaction && (
        <div className="chart-card">
          <h3>遠見雜誌 2026 施政滿意度 — 嘉義市</h3>
          <div style={{ padding: '16px 0' }}>
            <div style={{ fontSize: 48, textAlign: 'center', marginBottom: 8 }}>
              {'⭐'.repeat(chiayiSatisfaction.star_rating || 0)}
            </div>
            <div style={{ fontSize: 20, fontWeight: 700, textAlign: 'center', marginBottom: 4 }}>
              五星首長
            </div>
            <div style={{ color: '#64748b', textAlign: 'center', marginBottom: 16 }}>
              {chiayiSatisfaction.note}
            </div>
            <table className="data-table">
              <tbody>
                <tr><td>市長</td><td><strong>{chiayiSatisfaction.mayor}</strong></td></tr>
                <tr><td>整體滿意度</td><td><strong>{chiayiSatisfaction.overall_satisfaction}%</strong></td></tr>
                <tr><td>八大面向平均</td><td><strong>{chiayiSatisfaction.avg_dimension_score}%</strong></td></tr>
                <tr><td>全國排名</td><td><strong>#{chiayiSatisfaction.rank_national}</strong></td></tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 天下 rankings table */}
      {hasAnyData && <div className="chart-card">
        <h3>天下雜誌 永續幸福城市 2025 — 非六都排名</h3>
        <DataTable
          columns={[
            { key: 'rank', label: '排名', align: 'right' },
            { key: 'county', label: '縣市' },
            { key: 'total_score', label: '總分', align: 'right', render: row => Number(row.total_score).toFixed(1) },
          ]}
          data={nonSix}
          pageSize={0}
          searchable={false}
          highlightRow={row => row.county === '嘉義市'}
        />
      </div>}

      {/* 天下 dimensions table */}
      {hasAnyData && chiayiDims.length > 0 && (
        <div className="chart-card">
          <h3>嘉義市各面向得分（天下雜誌）</h3>
          <DataTable
            columns={[
              { key: 'dimension', label: '面向' },
              { key: 'score', label: '得分', align: 'right', render: row => row.score ? Number(row.score).toFixed(2) : '—' },
              { key: 'rank_in_non_six', label: '非六都排名', align: 'right', render: row => row.rank_in_non_six ? `#${row.rank_in_non_six}` : '—' },
              { key: 'note', label: '備註' },
            ]}
            data={chiayiDims}
            pageSize={0}
            searchable={false}
          />
        </div>
      )}

      {/* Data source */}
      {hasAnyData && <div className="card" style={{ fontSize: 13, color: '#64748b' }}>
        <strong>資料來源：</strong>
        天下雜誌第 832 期「2025 永續幸福城市大調查」（樣本 14,764 份）；
        遠見雜誌「2026 縣市長施政滿意度調查」。
        本頁資料為手動整理，非即時更新。
      </div>}
    </>
  )
}
