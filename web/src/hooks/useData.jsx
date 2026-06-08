import { useState, useEffect } from 'react'

export function useData(filename) {
  const [state, setState] = useState({
    filename: null,
    data: null,
    error: null,
  })

  useEffect(() => {
    const controller = new AbortController()

    async function load() {
      try {
        const response = await fetch(`/data/${filename}`, { signal: controller.signal })
        if (!response.ok) {
          throw new Error(`${filename} 載入失敗 (${response.status})`)
        }

        const data = await response.json()
        setState({ filename, data, error: null })
      } catch (err) {
        if (err.name === 'AbortError') return
        setState({
          filename,
          data: null,
          error: err.message || `${filename} 載入失敗`,
        })
      }
    }

    load()
    return () => controller.abort()
  }, [filename])

  const current = state.filename === filename

  return {
    data: current ? state.data : null,
    loading: !current,
    error: current ? state.error : null,
  }
}

export function formatNumber(n) {
  if (n == null) return '—'
  const num = Number(n)
  if (!Number.isFinite(num)) return '—'
  return num.toLocaleString('zh-TW')
}

export function formatChange(n) {
  if (n == null) return '—'
  const num = Number(n)
  if (!Number.isFinite(num)) return '—'
  return num >= 0 ? `+${num.toLocaleString('zh-TW')}` : num.toLocaleString('zh-TW')
}

function trimFixed(value, digits = 1) {
  return Number(value).toFixed(digits).replace(/\.0$/, '')
}

export function formatBudget(n, options = {}) {
  const { includeUnit = false } = options
  if (n == null) return '—'
  const num = Number(n)
  if (!Number.isFinite(num)) return '—'

  const abs = Math.abs(num)
  let text
  if (abs >= 100000) {
    text = `${trimFixed(num / 100000, abs >= 1000000 ? 0 : 1)} 億`
  } else if (abs >= 10000) {
    text = `${trimFixed(num / 10000)} 千萬`
  } else if (abs >= 10) {
    text = `${trimFixed(num / 10)} 萬`
  } else {
    text = `${num.toLocaleString('zh-TW')} 千元`
  }

  return includeUnit ? `${text}元` : text
}

export function parseGrowthPct(value) {
  if (value == null) return null
  const num = Number(String(value).replace('%', ''))
  return Number.isFinite(num) ? num : null
}
