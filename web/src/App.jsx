import { Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Breadcrumb from './components/Breadcrumb'
import DataQualityBar from './components/DataQualityBar'
import Dashboard from './pages/Dashboard'
import Population from './pages/Population'
import Budget from './pages/Budget'
import Policy from './pages/Policy'
import Funds from './pages/Funds'
import Comparison from './pages/Comparison'
import Narratives from './pages/Narratives'
import About from './pages/About'
import Competitiveness from './pages/Competitiveness'

export default function App() {
  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-area">
        <Breadcrumb />
        <DataQualityBar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/population" element={<Population />} />
            <Route path="/population/comparison" element={<Comparison />} />
            <Route path="/budget" element={<Budget />} />
            <Route path="/budget/policy" element={<Policy />} />
            <Route path="/budget/funds" element={<Funds />} />
            <Route path="/narratives" element={<Narratives />} />
            <Route path="/competitiveness" element={<Competitiveness />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </main>
        <footer className="footer">
          <p>嘉義市人口與財政開放資料系統 · Data from <a href="https://data.chiayi.gov.tw" target="_blank" rel="noopener">Open Chiayi</a> & <a href="https://www.ris.gov.tw" target="_blank" rel="noopener">內政部戶政司</a></p>
        </footer>
      </div>
    </div>
  )
}
