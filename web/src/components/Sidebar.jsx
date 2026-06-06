import { NavLink, useLocation } from 'react-router-dom'
import { useState } from 'react'

const NAV_SECTIONS = [
  {
    label: '概覽',
    icon: '🏠',
    path: '/',
    exact: true,
  },
  {
    label: '人口',
    icon: '👥',
    children: [
      { label: '人口結構', path: '/population' },
      { label: '跨縣市比較', path: '/population/comparison' },
    ],
  },
  {
    label: '財政',
    icon: '💰',
    children: [
      { label: '預算總覽', path: '/budget' },
      { label: '政策領域', path: '/budget/policy' },
      { label: '基金儀表板', path: '/budget/funds' },
    ],
  },
  {
    label: '敘事',
    icon: '📖',
    path: '/narratives',
  },
  {
    label: '關於',
    icon: 'ℹ️',
    path: '/about',
  },
]

export default function Sidebar() {
  const location = useLocation()
  const [collapsed, setCollapsed] = useState({})
  const [mobileOpen, setMobileOpen] = useState(false)

  const toggleSection = (label) => {
    setCollapsed(prev => ({ ...prev, [label]: !prev[label] }))
  }

  const isActiveSection = (section) => {
    if (section.exact) return location.pathname === section.path
    if (section.path) return location.pathname.startsWith(section.path)
    return section.children?.some(c => location.pathname.startsWith(c.path))
  }

  return (
    <>
      {/* Mobile hamburger */}
      <button
        className="sidebar-mobile-toggle"
        onClick={() => setMobileOpen(!mobileOpen)}
        aria-label="Toggle navigation"
      >
        {mobileOpen ? '✕' : '☰'}
      </button>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div className="sidebar-overlay" onClick={() => setMobileOpen(false)} />
      )}

      <aside className={`sidebar ${mobileOpen ? 'open' : ''}`}>
        <div className="sidebar-brand">
          <NavLink to="/" onClick={() => setMobileOpen(false)}>
            🏛 嘉義市政
          </NavLink>
        </div>

        <nav className="sidebar-nav">
          {NAV_SECTIONS.map((section) => {
            const active = isActiveSection(section)
            const hasChildren = section.children?.length > 0
            const isCollapsed = collapsed[section.label]

            return (
              <div key={section.label} className={`sidebar-section ${active ? 'active' : ''}`}>
                {hasChildren ? (
                  <button
                    className={`sidebar-section-header ${active ? 'active' : ''}`}
                    onClick={() => toggleSection(section.label)}
                  >
                    <span className="sidebar-icon">{section.icon}</span>
                    <span className="sidebar-label">{section.label}</span>
                    <span className={`sidebar-arrow ${isCollapsed ? 'collapsed' : ''}`}>▾</span>
                  </button>
                ) : (
                  <NavLink
                    to={section.path}
                    className={({ isActive }) =>
                      `sidebar-link ${isActive ? 'active' : ''}`
                    }
                    onClick={() => setMobileOpen(false)}
                    end={section.exact}
                  >
                    <span className="sidebar-icon">{section.icon}</span>
                    <span className="sidebar-label">{section.label}</span>
                  </NavLink>
                )}

                {hasChildren && !isCollapsed && (
                  <div className="sidebar-children">
                    {section.children.map((child) => (
                      <NavLink
                        key={child.path}
                        to={child.path}
                        className={({ isActive }) =>
                          `sidebar-child-link ${isActive ? 'active' : ''}`
                        }
                        onClick={() => setMobileOpen(false)}
                      >
                        {child.label}
                      </NavLink>
                    ))}
                  </div>
                )}
              </div>
            )
          })}
        </nav>

        <div className="sidebar-footer">
          <span>嘉義市知識庫 v2.0</span>
        </div>
      </aside>
    </>
  )
}
