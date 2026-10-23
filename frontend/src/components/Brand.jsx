export default function Brand({ light = false }) {
  return (
    <div className={`brand${light ? ' brand--light' : ''}`}>
      <span className="brand-mark" aria-hidden="true">
        S
      </span>
      <span className="brand-word">
        Stay<span className="brand-word-accent">Smart</span>
      </span>
    </div>
  )
}
