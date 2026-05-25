import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'
import Population from './pages/Population'
import Budget from './pages/Budget'
import Funds from './pages/Funds'
import Narratives from './pages/Narratives'

export default function App() {
  return (
    <div className="app">
      <Navbar />
      <main className="container">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/population" element={<Population />} />
          <Route path="/budget" element={<Budget />} />
          <Route path="/funds" element={<Funds />} />
          <Route path="/narratives" element={<Narratives />} />
        </Routes>
      </main>
      <footer className="footer">
        <p>嘉義市人口與財政開放資料系統 · Data from <a href="https://data.chiayi.gov.tw" target="_blank" rel="noopener">Open Chiayi</a></p>
      </footer>
    </div>
  )
}
