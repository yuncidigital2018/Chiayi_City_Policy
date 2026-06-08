export default function SegmentedControl({ label, value, options, onChange }) {
  return (
    <div className="segmented-control" role="group" aria-label={label}>
      {label && <span className="segmented-label">{label}</span>}
      <div className="segmented-options">
        {options.map(option => (
          <button
            key={option.value}
            type="button"
            className={`segmented-btn ${value === option.value ? 'active' : ''}`}
            onClick={() => onChange(option.value)}
            aria-pressed={value === option.value}
          >
            {option.label}
          </button>
        ))}
      </div>
    </div>
  )
}
