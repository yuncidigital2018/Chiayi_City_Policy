import { useData, formatNumber, formatChange, formatBudget } from '../hooks/useData'
import StatusMessage from '../components/StatusMessage'

export default function Narratives() {
  const { data: population, loading: popLoading, error: popError } = useData('population_annual.json')
  const { data: expFunc, loading: expLoading, error: expError } = useData('budget_expenditure_by_function.json')
  const { data: revenue, loading: revLoading, error: revError } = useData('budget_revenue_by_source.json')

  const loading = popLoading || expLoading || revLoading
  const error = popError || expError || revError

  if (loading) return <StatusMessage type="loading" />
  if (error) return <StatusMessage type="error" message={error} />

  const latest = population?.[population.length - 1] || {}
  const first = population?.[0] || {}
  const totalExp = expFunc?.reduce((s, e) => s + Number(e.amount), 0) || 0
  const totalRev = revenue?.reduce((s, r) => s + Number(r.amount), 0) || 0

  const topExpense = [...(expFunc || [])].sort((a, b) => Number(b.amount) - Number(a.amount))[0]
  const topRevenue = [...(revenue || [])].sort((a, b) => Number(b.amount) - Number(a.amount))[0]

  const popChange = Number(latest.total_population) - Number(first.total_population)
  const popYears = first.year && latest.year ? `${first.year} ~ ${latest.year}` : '歷年'

  return (
    <div className="narrative-content">
      <div className="page-header">
        <h1>📝 城市敘事</h1>
        <p>從數據看嘉義市的人口與財政</p>
      </div>

      <div className="card">
        <h2>人口挑戰：持續減少中的城市</h2>
        <p>
          嘉義市總人口從 {popYears} 年間，
          從 {formatNumber(first.total_population)} 人
          下降至 {formatNumber(latest.total_population)} 人，
          共減少 {formatChange(popChange)} 人。
        </p>
        <p>
          自然增減為 {formatChange(latest.natural_increase)}（出生 − 死亡），
          社會增減為 {formatChange(latest.social_increase)}（遷入 − 遷出），
          兩者皆為負值，顯示嘉義市面臨人口外流與少子化的雙重挑戰。
        </p>
      </div>

      <div className="card">
        <h2>財政結構：教育與社會福利為主</h2>
        <p>
          115 年度歲出總額為 {formatBudget(totalExp)} 千元，
          其中最大支出項目為「{topExpense?.function_category}」，
          金額 {formatBudget(topExpense?.amount)} 千元，
          佔總歲出 {(Number(topExpense?.amount) / totalExp * 100).toFixed(1)}%。
        </p>
        <p>
          歲入總額為 {formatBudget(totalRev)} 千元，
          主要來源為「{topRevenue?.source_category}」。
          {totalRev >= totalExp
            ? `歲入大於歲出，財政尚有賸餘。`
            : `歲出大於歲入，需關注財政紀律。`
          }
        </p>
      </div>

      <div className="card">
        <h2>政策建議</h2>
        <p>
          基於上述數據分析，嘉義市可關注以下方向：
        </p>
        <ul>
          <li><strong>人口振興：</strong>提升生育率、吸引青年回流、改善居住環境</li>
          <li><strong>財政紀律：</strong>控制歲出成長、提升自有財源比例</li>
          <li><strong>政策聚焦：</strong>將有限資源投入高效益領域（教育、社福、基礎建設）</li>
        </ul>
      </div>
    </div>
  )
}
