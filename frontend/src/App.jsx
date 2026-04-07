import { useState, useRef, useCallback } from 'react'

const ACCEPTED = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg', 'image/webp', 'image/tiff', 'image/bmp']

function FileSlot({ index, file, onFile, onRemove }) {
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef()

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setDragging(false)
    const f = e.dataTransfer.files[0]
    if (f && ACCEPTED.includes(f.type)) onFile(index, f)
  }, [index, onFile])

  const handleChange = (e) => {
    const f = e.target.files[0]
    if (f) onFile(index, f)
    e.target.value = ''
  }

  const isImg = file && file.type.startsWith('image/')
  const isPdf = file && file.type === 'application/pdf'
  const previewUrl = isImg ? URL.createObjectURL(file) : null

  return (
    <div
      className={`slot ${dragging ? 'slot--drag' : ''} ${file ? 'slot--filled' : ''}`}
      onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      onClick={() => !file && inputRef.current.click()}
      style={{ cursor: file ? 'default' : 'pointer' }}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,image/*"
        style={{ display: 'none' }}
        onChange={handleChange}
      />

      {!file ? (
        <div className="slot__empty">
          <div className="slot__icon">
            {dragging ? '⬇' : index === 0 ? '①' : '②'}
          </div>
          <p className="slot__label">File {index + 1}</p>
          <p className="slot__hint">drop PDF or image here<br />or click to browse</p>
          <div className="slot__types">PDF · PNG · JPG · WEBP · TIFF</div>
        </div>
      ) : (
        <div className="slot__preview">
          {isImg && (
            <img src={previewUrl} alt="preview" className="slot__thumb" />
          )}
          {isPdf && (
            <div className="slot__pdf-icon">
              <span>PDF</span>
            </div>
          )}
          <div className="slot__meta">
            <p className="slot__filename">{file.name}</p>
            <p className="slot__size">{(file.size / 1024).toFixed(1)} KB</p>
          </div>
          <button
            className="slot__remove"
            onClick={(e) => { e.stopPropagation(); onRemove(index) }}
          >✕</button>
        </div>
      )}
    </div>
  )
}

function WordBadge({ word }) {
  return <span className="word-badge">{word}</span>
}

function ResultPanel({ filename, data }) {
  const [view, setView] = useState('badges')
  return (
    <div className="result-panel">
      <div className="result-panel__header">
        <div>
          <p className="result-panel__filename">{filename}</p>
          <p className="result-panel__count">{data.word_count} words extracted</p>
        </div>
        <div className="result-panel__toggle">
          <button
            className={view === 'badges' ? 'active' : ''}
            onClick={() => setView('badges')}
          >Tags</button>
          <button
            className={view === 'json' ? 'active' : ''}
            onClick={() => setView('json')}
          >JSON</button>
        </div>
      </div>

      {view === 'badges' ? (
        <div className="word-cloud">
          {data.words.map((w, i) => <WordBadge key={i} word={w} />)}
        </div>
      ) : (
        <pre className="json-view">{JSON.stringify(data, null, 2)}</pre>
      )}
    </div>
  )
}

export default function App() {
  const [files, setFiles] = useState([null, null])
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)

  const handleFile = useCallback((index, file) => {
    setFiles(prev => { const n = [...prev]; n[index] = file; return n })
    setResults(null)
    setError(null)
  }, [])

  const handleRemove = useCallback((index) => {
    setFiles(prev => { const n = [...prev]; n[index] = null; return n })
    setResults(null)
    setError(null)
  }, [])

  const handleExtract = async () => {
    if (!files[0] || !files[1]) return
    setLoading(true)
    setError(null)
    setResults(null)

    const fd = new FormData()
    fd.append('file1', files[0])
    fd.append('file2', files[1])

    try {
      const res = await fetch('/extract', { method: 'POST', body: fd })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Extraction failed')
      }
      const data = await res.json()
      setResults(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const ready = files[0] && files[1]

  return (
    <div className="app">
      <header className="header">
        <div className="header__tag">v1.0 · GPT-4o ENGINE</div>
        <h1 className="header__title">LEGAL<br />MOVE</h1>
        <p className="header__sub">Drop two files. Get every word as JSON.</p>
      </header>

      <main className="main">
        <section className="upload-section">
          <div className="slots">
            <FileSlot index={0} file={files[0]} onFile={handleFile} onRemove={handleRemove} />
            <div className="slots__divider">
              <span>+</span>
            </div>
            <FileSlot index={1} file={files[1]} onFile={handleFile} onRemove={handleRemove} />
          </div>

          <div className="action-row">
            <button
              className={`extract-btn ${ready ? 'extract-btn--ready' : ''} ${loading ? 'extract-btn--loading' : ''}`}
              disabled={!ready || loading}
              onClick={handleExtract}
            >
              {loading ? (
                <span className="spinner-text">PROCESSING<span className="dots">...</span></span>
              ) : (
                'GENERATE JSON →'
              )}
            </button>
          </div>

          {error && (
            <div className="error-banner">
              <span>⚠ {error}</span>
            </div>
          )}
        </section>

        {results && (
          <section className="results-section">
            <div className="results-header">
              <div className="results-header__line" />
              <span>RESULTS</span>
              <div className="results-header__line" />
            </div>
            <div className="full-json-wrap">
              <details>
                <summary>Full JSON response</summary>
                <pre className="json-view json-view--full">{JSON.stringify(results, null, 2)}</pre>
              </details>
            </div>
            <div className="results-grid">
              {Object.entries(results).map(([fname, data]) => (
                <ResultPanel key={fname} filename={fname} data={data} />
              ))}
            </div>
            <div className="full-json-wrap">
              <details>
                <summary>Full JSON response</summary>
                <pre className="json-view json-view--full">{JSON.stringify(results, null, 2)}</pre>
              </details>
            </div>
          </section>
        )}
      </main>

      <footer className="footer">
        FastAPI  · gpt-4o · LangChain · Langfuse · React + Vite
      </footer>

      <style>{`
        .app {
          max-width: 960px;
          margin: 0 auto;
          padding: 0 24px 80px;
          min-height: 100vh;
        }

        /* HEADER */
        .header {
          padding: 60px 0 48px;
          border-bottom: 1px solid var(--border);
          margin-bottom: 48px;
          position: relative;
        }
        .header__tag {
          font-size: 11px;
          letter-spacing: 0.15em;
          color: var(--accent);
          margin-bottom: 16px;
          font-family: var(--font-mono);
        }
        .header__title {
          font-family: var(--font-display);
          font-size: clamp(52px, 10vw, 96px);
          font-weight: 800;
          line-height: 0.92;
          letter-spacing: -0.03em;
          color: var(--text);
        }
        .header__sub {
          margin-top: 20px;
          color: var(--muted);
          font-size: 13px;
          letter-spacing: 0.05em;
        }

        /* SLOTS */
        .slots {
          display: grid;
          grid-template-columns: 1fr auto 1fr;
          gap: 0;
          align-items: center;
        }
        .slots__divider {
          width: 48px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--muted);
          font-size: 24px;
          font-family: var(--font-display);
          font-weight: 700;
        }

        .slot {
          height: 240px;
          border: 1px solid var(--border);
          background: var(--surface);
          transition: border-color 0.2s, background 0.2s, transform 0.15s;
          position: relative;
          overflow: hidden;
        }
        .slot::before {
          content: '';
          position: absolute;
          inset: 0;
          background: linear-gradient(135deg, transparent 60%, rgba(232,255,71,0.03));
          pointer-events: none;
        }
        .slot--drag {
          border-color: var(--accent);
          background: rgba(232,255,71,0.05);
          transform: scale(1.01);
        }
        .slot--filled {
          border-color: rgba(77,255,180,0.3);
        }
        .slot:hover:not(.slot--filled) {
          border-color: var(--muted);
        }

        .slot__empty {
          height: 100%;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 8px;
          padding: 24px;
          text-align: center;
        }
        .slot__icon {
          font-size: 32px;
          font-family: var(--font-display);
          font-weight: 800;
          color: var(--accent);
          line-height: 1;
          margin-bottom: 4px;
        }
        .slot__label {
          font-size: 11px;
          letter-spacing: 0.2em;
          text-transform: uppercase;
          color: var(--muted);
        }
        .slot__hint {
          font-size: 12px;
          color: var(--muted);
          line-height: 1.5;
        }
        .slot__types {
          margin-top: 8px;
          font-size: 10px;
          color: rgba(255,255,255,0.15);
          letter-spacing: 0.1em;
        }

        .slot__preview {
          height: 100%;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 12px;
          padding: 20px;
          position: relative;
        }
        .slot__thumb {
          max-height: 100px;
          max-width: 100%;
          object-fit: contain;
          border: 1px solid var(--border);
        }
        .slot__pdf-icon {
          width: 64px;
          height: 80px;
          background: var(--bg);
          border: 1px solid var(--border);
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 11px;
          letter-spacing: 0.15em;
          color: var(--accent2);
          font-weight: 500;
        }
        .slot__meta {
          text-align: center;
        }
        .slot__filename {
          font-size: 11px;
          color: var(--success);
          word-break: break-all;
          max-width: 180px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        .slot__size {
          font-size: 10px;
          color: var(--muted);
          margin-top: 2px;
        }
        .slot__remove {
          position: absolute;
          top: 10px;
          right: 10px;
          background: rgba(255,92,87,0.15);
          border: 1px solid rgba(255,92,87,0.3);
          color: var(--accent2);
          width: 24px;
          height: 24px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          font-size: 10px;
          transition: background 0.15s;
        }
        .slot__remove:hover { background: rgba(255,92,87,0.3); }

        /* ACTION */
        .action-row {
          margin-top: 28px;
          display: flex;
          justify-content: center;
        }
        .extract-btn {
          background: var(--surface);
          border: 1px solid var(--border);
          color: var(--muted);
          font-family: var(--font-display);
          font-weight: 700;
          font-size: 15px;
          letter-spacing: 0.1em;
          padding: 14px 40px;
          cursor: not-allowed;
          transition: all 0.2s;
          position: relative;
          overflow: hidden;
        }
        .extract-btn--ready {
          border-color: var(--accent);
          color: var(--accent);
          cursor: pointer;
        }
        .extract-btn--ready:hover {
          background: var(--accent);
          color: var(--bg);
        }
        .extract-btn--loading {
          border-color: var(--muted);
          color: var(--muted);
          cursor: wait;
        }
        .dots {
          display: inline-block;
          animation: blink 1.2s steps(3, end) infinite;
          width: 18px;
          text-align: left;
        }
        @keyframes blink {
          0%, 100% { opacity: 0; }
          33% { opacity: 1; }
        }

        /* ERROR */
        .error-banner {
          margin-top: 20px;
          padding: 12px 20px;
          border: 1px solid rgba(255,92,87,0.4);
          background: rgba(255,92,87,0.07);
          color: var(--accent2);
          font-size: 13px;
          text-align: center;
        }

        /* RESULTS */
        .results-section { margin-top: 56px; }
        .results-header {
          display: flex;
          align-items: center;
          gap: 16px;
          margin-bottom: 32px;
          font-size: 11px;
          letter-spacing: 0.2em;
          color: var(--muted);
        }
        .results-header__line {
          flex: 1;
          height: 1px;
          background: var(--border);
        }

        .results-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
          gap: 20px;
        }

        .result-panel {
          border: 1px solid var(--border);
          background: var(--surface);
          overflow: hidden;
        }
        .result-panel__header {
          padding: 16px 20px;
          border-bottom: 1px solid var(--border);
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 12px;
        }
        .result-panel__filename {
          font-size: 12px;
          color: var(--success);
          word-break: break-all;
        }
        .result-panel__count {
          font-size: 11px;
          color: var(--muted);
          margin-top: 2px;
        }
        .result-panel__toggle {
          display: flex;
          border: 1px solid var(--border);
          flex-shrink: 0;
        }
        .result-panel__toggle button {
          background: none;
          border: none;
          color: var(--muted);
          font-family: var(--font-mono);
          font-size: 11px;
          padding: 6px 12px;
          cursor: pointer;
          transition: all 0.15s;
          letter-spacing: 0.05em;
        }
        .result-panel__toggle button.active {
          background: var(--accent);
          color: var(--bg);
        }
        .result-panel__toggle button:not(.active):hover {
          color: var(--text);
        }

        .word-cloud {
          padding: 16px 20px;
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
          max-height: 260px;
          overflow-y: auto;
        }
        .word-badge {
          background: rgba(232,255,71,0.07);
          border: 1px solid rgba(232,255,71,0.15);
          color: rgba(232,255,71,0.8);
          font-size: 11px;
          padding: 3px 8px;
          letter-spacing: 0.03em;
          transition: background 0.15s;
        }
        .word-badge:hover {
          background: rgba(232,255,71,0.15);
        }

        .json-view {
          padding: 16px 20px;
          font-size: 11px;
          color: var(--muted);
          line-height: 1.7;
          overflow-x: auto;
          max-height: 260px;
          overflow-y: auto;
        }
        .json-view--full {
          max-height: 400px;
          font-size: 11px;
        }

        .full-json-wrap {
          margin-top: 20px;
          border: 1px solid var(--border);
        }
        .full-json-wrap summary {
          padding: 12px 20px;
          font-size: 11px;
          letter-spacing: 0.1em;
          color: var(--muted);
          cursor: pointer;
          user-select: none;
          transition: color 0.15s;
        }
        .full-json-wrap summary:hover { color: var(--text); }
        .full-json-wrap[open] summary { border-bottom: 1px solid var(--border); }

        /* FOOTER */
        .footer {
          margin-top: 80px;
          padding: 24px 0;
          border-top: 1px solid var(--border);
          font-size: 10px;
          letter-spacing: 0.12em;
          color: rgba(255,255,255,0.1);
          text-align: center;
        }

        @media (max-width: 600px) {
          .slots { grid-template-columns: 1fr; }
          .slots__divider { display: none; }
          .results-grid { grid-template-columns: 1fr; }
        }
      `}</style>
    </div>
  )
}
