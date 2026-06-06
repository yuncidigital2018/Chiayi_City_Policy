import { Link, useLocation } from 'react-router-dom'

const ROUTE_MAP = {
  '/': { label: '概覽', section: '概覽' },
  '/population': { label: '人口結構', section: '人口' },
  '/population/comparison': { label: '跨縣市比較', section: '人口' },
  '/budget': { label: '預算總覽', section: '財政' },
  '/budget/policy': { label: '政策領域', section: '財政' },
  '/budget/funds': { label: '基金儀表板', section: '財政' },
  '/narratives': { label: '敘事', section: '敘事' },
  '/competitiveness': { label: '城市競爭力', section: '競爭力' },
  '/about': { label: '關於', section: '關於' },
}

export default function Breadcrumb() {
  const location = useLocation()
  const route = ROUTE_MAP[location.pathname]

  if (!route || location.pathname === '/') return null

  return (
    <nav className="breadcrumb" aria-label="breadcrumb">
      <Link to="/">概覽</Link>
      <span className="breadcrumb-sep">›</span>
      {route.section !== route.label && (
        <>
          <span className="breadcrumb-section">{route.section}</span>
          <span className="breadcrumb-sep">›</span>
        </>
      )}
      <span className="breadcrumb-current">{route.label}</span>
    </nav>
  )
}
