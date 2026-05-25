import { useData, formatNumber, formatChange, formatBudget } from '../hooks/useData'

export default function Narratives() {
  const { data: population } = useData('population_annual.json')
  const { data: expFunc } = useData('budget_expenditure_by_function.json')
  const { data: revenue } = useData('budget_revenue_by_source.json')

  const latest = population?.[population.length - 1] || {}
  const first = population?.[0] || {}
  const totalExp = expFunc?.reduce((s, e) => s + Number(e.amount), 0) || 0
  const totalRev = revenue?.reduce((s, r) => s + Number(r.amount), 0) || 0

  const topExpense = [...(expFunc || [])].sort((a, b) => Number(b.amount) - Number(a.amount))[0]
  const topRevenue = [...(revenue || [])].sort((a, b) => Number(b.amount) - Number(a.amount))[0]

  return (
    <div className="narrative-content">
      <div className="page-header">
        <h1>📝 城市敘事</h1>
        <p>從數據看嘉義市的人口與財政</p>
      </div>

      <div className="card">
        <h2>人口挑戰：持續減少中的城市</h2>
        <p>
          嘉義市總人口從 106 年的 {formatNumber(first.total_population)} 人，
          下降至 115 年的 {formatNumber(latest.total_population)} 人，
          十年間減少 {formatChange(Number(latest.total_population) - Number(first.total_population))} 人。
        </p>
        <p>
          人口減少由兩大因素驅動：一是 <strong>自然減少</strong>（死亡大於出生），115 年為 {formatChange(latest.natural_increase)} 人；
          二是 <strong>社會減少</strong>（遷出大於遷入），115 年為 {formatChange(latest.social_increase)} 人。
          兩者的疊加效應使得年度總減少達 {formatChange(Number(latest.natural_increase) + Number(latest.social_increase))} 人。
        </p>
        <p>
          值得關注的是，性別比為 {latest.male && latest.female ? (Number(latest.male) / Number(latest.female) * 100).toFixed(1) : '—'}
          （男/百女），女性多於男性，反映全國性的女性壽命較長趨勢。
        </p>
      </div>

      <div className="card" style={{ marginTop: 20 }}>
        <h2>財政結構：教育與社福為大宗</h2>
        <p>
          115 年度歲入總額約 {formatBudget(totalRev)}，歲出總額約 {formatBudget(totalExp)}。
          歲入主要來源為 <strong>{topRevenue?.source_category}</strong>，
          占總歲入 {(totalRev > 0 ? Number(topRevenue?.amount) / totalRev * 100 : 0).toFixed(1)}%。
        </p>
        <p>
          歲出方面，最大支出項目為 <strong>{topExpense?.function_category}</strong>，
          金額 {formatNumber(topExpense?.amount)} 千元，
          占總歲出 {(totalExp > 0 ? Number(topExpense?.amount) / totalExp * 100 : 0).toFixed(1)}%。
          這反映出嘉義市在教育與社會福利上的持續投入。
        </p>
      </div>

      <div className="card" style={{ marginTop: 20 }}>
        <h2>城市定位與展望</h2>
        <p>
          面對人口持續減少的挑戰，嘉義市需要在以下幾個方向著力：
        </p>
        <p>
          <strong>1. 吸引年輕人口：</strong>透過產業發展、就業機會創造、居住補助等政策，降低社會遷出，吸引外來人口。
        </p>
        <p>
          <strong>2. 高齡社會準備：</strong>性別比失衡與自然減少反映高齡化趨勢，需要加強長照服務與高齡友善環境建設。
        </p>
        <p>
          <strong>3. 財政永續：</strong>在歲入依賴中央補助的情況下，提升地方稅收自主性是長期財政健康的重要課題。
        </p>
        <p>
          <strong>4. 區域治理：</strong>嘉義縣市合計僅約 70 萬人，升格直轄市人口門檻不足，但區域合作治理的模式值得持續探索。
        </p>
      </div>
    </div>
  )
}
