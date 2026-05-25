import { NavLink } from 'react-router-dom'

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <NavLink to="/" className="navbar-brand">🏛 嘉義市政</NavLink>
        <div className="navbar-links">
          <NavLink to="/">總覽</NavLink>
          <NavLink to="/population">人口</NavLink>
          <NavLink to="/budget">預算</NavLink>
          <NavLink to="/narratives">敘事</NavLink>
        </div>
      </div>
    </nav>
  )
}
