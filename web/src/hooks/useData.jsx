import { useState, useEffect } from 'react'

export function useData(filename) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    fetch(`/data/${filename}`)
      .then(r => r.json())
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [filename])

  return { data, loading }
}

export function formatNumber(n) {
  if (n == null) return '—'
  return Number(n).toLocaleString('zh-TW')
}

export function formatChange(n) {
  if (n == null) return '—'
  const num = Number(n)
  return num >= 0 ? `+${num.toLocaleString('zh-TW')}` : num.toLocaleString('zh-TW')
}

export function formatBudget(n) {
  if (n == null) return '—'
  const num = Number(n)
  if (num >= 1000000) return `${(num / 10000).toFixed(0)} 億`
  if (num >= 1000) return `${(num / 1000).toFixed(1)} 千萬`
  return num.toLocaleString('zh-TW')
}
