import { useState, useMemo } from 'react'

/**
 * DataTable — 可排序/搜尋/分頁的表格元件
 *
 * Props:
 *   columns: [{ key, label, align?, render?, sortable? }]
 *   data: array
 *   pageSize: number (default 10, 0 = no pagination)
 *   searchable: boolean (default true)
 *   searchPlaceholder: string
 *   highlightRow: (row) => boolean
 *   emptyMessage: string
 */
export default function DataTable({
  columns,
  data = [],
  pageSize = 10,
  searchable = true,
  searchPlaceholder = '搜尋...',
  highlightRow,
  emptyMessage = '暫無資料',
}) {
  const [search, setSearch] = useState('')
  const [sortKey, setSortKey] = useState(null)
  const [sortDir, setSortDir] = useState('asc')
  const [page, setPage] = useState(0)

  // Filter
  const filtered = useMemo(() => {
    if (!search.trim()) return data
    const q = search.toLowerCase()
    return data.filter(row =>
      columns.some(col => {
        const val = col.render ? col.render(row) : row[col.key]
        return String(val).toLowerCase().includes(q)
      })
    )
  }, [data, search, columns])

  // Sort
  const sorted = useMemo(() => {
    if (!sortKey) return filtered
    const col = columns.find(c => c.key === sortKey)
    return [...filtered].sort((a, b) => {
      let va = col?.render ? col.render(a) : a[sortKey]
      let vb = col?.render ? col.render(b) : b[sortKey]
      // Numeric sort if both are numbers
      const na = Number(va), nb = Number(vb)
      if (!isNaN(na) && !isNaN(nb)) {
        return sortDir === 'asc' ? na - nb : nb - na
      }
      // String sort
      va = String(va || '')
      vb = String(vb || '')
      return sortDir === 'asc' ? va.localeCompare(vb) : vb.localeCompare(va)
    })
  }, [filtered, sortKey, sortDir, columns])

  // Paginate
  const totalPages = pageSize > 0 ? Math.ceil(sorted.length / pageSize) : 1
  const paged = pageSize > 0 ? sorted.slice(page * pageSize, (page + 1) * pageSize) : sorted

  const handleSort = (key) => {
    if (sortKey === key) {
      setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    } else {
      setSortKey(key)
      setSortDir('asc')
    }
    setPage(0)
  }

  return (
    <div className="data-table-wrapper">
      {searchable && (
        <div className="data-table-search">
          <input
            type="text"
            placeholder={searchPlaceholder}
            value={search}
            onChange={e => { setSearch(e.target.value); setPage(0) }}
            className="data-table-input"
          />
          {search && (
            <span className="data-table-count">{sorted.length} 筆結果</span>
          )}
        </div>
      )}

      <div className="data-table-scroll">
        <table className="data-table">
          <thead>
            <tr>
              {columns.map(col => (
                <th
                  key={col.key}
                  style={{ textAlign: col.align || 'left', cursor: col.sortable !== false ? 'pointer' : 'default' }}
                  onClick={() => col.sortable !== false && handleSort(col.key)}
                >
                  {col.label}
                  {sortKey === col.key && (
                    <span className="sort-indicator">{sortDir === 'asc' ? ' ▲' : ' ▼'}</span>
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paged.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="data-table-empty">
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              paged.map((row, i) => (
                <tr key={i} className={highlightRow?.(row) ? 'highlight-row' : ''}>
                  {columns.map(col => (
                    <td key={col.key} style={{ textAlign: col.align || 'left' }}>
                      {col.render ? col.render(row) : row[col.key]}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="data-table-pagination">
          <button
            className="btn btn-sm"
            disabled={page === 0}
            onClick={() => setPage(p => p - 1)}
          >
            ← 上一頁
          </button>
          <span className="pagination-info">
            {page + 1} / {totalPages}
          </span>
          <button
            className="btn btn-sm"
            disabled={page >= totalPages - 1}
            onClick={() => setPage(p => p + 1)}
          >
            下一頁 →
          </button>
        </div>
      )}
    </div>
  )
}
