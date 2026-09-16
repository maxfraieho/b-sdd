// Sovereign LLM Copilot Panel — streaming SSE simulation
const { useState: _useState, useEffect: _useEffect, useRef: _useRef } = React;

function CopilotPanel({ streaming, onToggleStream }) {
  const [activeSlot, setActiveSlot] = _useState('coding');
  const [tokensStreamed, setTokensStreamed] = _useState(842);
  const [tokRate, setTokRate] = _useState(42);
  const [visibleLines, setVisibleLines] = _useState(streaming ? 6 : BSDD.STREAM_CODE.length);
  const [cursorLine, setCursorLine] = _useState(streaming ? 6 : -1);
  const [partial, setPartial] = _useState('');
  const streamRef = _useRef(null);

  // Simulate token streaming
  _useEffect(() => {
    if (!streaming) {
      setVisibleLines(BSDD.STREAM_CODE.length);
      setCursorLine(-1);
      return;
    }
    let idx = visibleLines;
    let charIdx = 0;
    const tick = () => {
      if (idx >= BSDD.STREAM_CODE.length) {
        setCursorLine(-1);
        return;
      }
      const line = BSDD.STREAM_CODE[idx].code;
      if (charIdx >= line.length) {
        idx++;
        charIdx = 0;
        setVisibleLines(idx);
        setPartial('');
        setCursorLine(idx);
      } else {
        charIdx += Math.max(1, Math.floor(Math.random() * 3));
        setPartial(line.slice(0, charIdx));
      }
      setTokensStreamed(t => t + 1);
    };
    const iv = setInterval(tick, 42);
    return () => clearInterval(iv);
  }, [streaming, visibleLines]);

  _useEffect(() => {
    if (streamRef.current) streamRef.current.scrollTop = streamRef.current.scrollHeight;
  }, [visibleLines, partial]);

  const budget = BSDD.TOKEN_BUDGET;
  const pct = (v) => (v / budget.total * 100).toFixed(1);
  const freeTokens = budget.total - budget.invariants - budget.handoff - budget.drakon - budget.code;

  // Simple Python syntax coloring — token-by-token walk (no regex placeholder tricks)
  const colorize = (line) => {
    if (!line) return <span> </span>;
    const kw = /^(from|import|class|def|async|await|if|not|for|in|self|yield|return|None|True|False|assert)$/;
    // If a comment starts the line, color the whole thing
    if (line.trim().startsWith('#')) {
      return <span className="tok-com">{line}</span>;
    }
    // Tokenize: strings, identifiers, numbers, whitespace, punctuation
    const tokens = [];
    const re = /("[^"]*"|'[^']*'|#.*$|[A-Za-z_][A-Za-z0-9_]*|\d+\.?\d*|\s+|[^\sA-Za-z0-9_"'#])/g;
    let m;
    while ((m = re.exec(line)) !== null) {
      const t = m[0];
      let cls = null;
      if (t.startsWith('#')) cls = 'tok-com';
      else if (t.startsWith('"') || t.startsWith("'")) cls = 'tok-str';
      else if (/^\d/.test(t)) cls = 'tok-num';
      else if (kw.test(t)) cls = 'tok-kw';
      else if (/^[A-Z]/.test(t)) cls = 'tok-fn';
      tokens.push({ t, cls });
    }
    return tokens.map((tk, i) =>
      tk.cls ? <span key={i} className={tk.cls}>{tk.t}</span> : <span key={i}>{tk.t}</span>
    );
  };

  return (
    <div className="panel copilot-panel">
      <div className="panel-header">
        <div className="panel-title">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
            <path d="M8 1l1.8 4.5L14 6l-3.4 2.7L11.8 14 8 11.3 4.2 14l1.2-5.3L2 6l4.2-.5L8 1z" fill="var(--amber)"/>
          </svg>
          Sovereign LLM Copilot
          <span className="tag">SSE · mTLS · .184:18880</span>
        </div>
        <div className="panel-actions">
          <span className="mono" style={{fontSize: 10, color: 'var(--emerald)'}}>● live</span>
        </div>
      </div>

      <div className="copilot-body">
        {/* Slot selector */}
        <div className="slot-selector">
          {BSDD.SLOTS.map(s => (
            <div
              key={s.id}
              className={`slot-card ${activeSlot === s.id ? 'active' : ''}`}
              onClick={() => setActiveSlot(s.id)}
            >
              <div className="slot-name">{s.name}</div>
              <div className="slot-meta">{s.model}</div>
              <div className="slot-meta">↦ {s.latency}</div>
            </div>
          ))}
        </div>

        {/* Token budget */}
        <div className="token-budget">
          <div className="head">
            <span>Context Token Budget</span>
            <span><span className="val">{(budget.total - freeTokens).toLocaleString()}</span> / {budget.total.toLocaleString()} tok</span>
          </div>
          <div className="token-bar">
            <i className="invariants" style={{width: pct(budget.invariants) + '%'}} title={`Invariants ${budget.invariants} tok`}/>
            <i className="handoff" style={{width: pct(budget.handoff) + '%'}} title={`Handoff ${budget.handoff} tok`}/>
            <i className="drakon" style={{width: pct(budget.drakon) + '%'}} title={`DRAKON-IR ${budget.drakon} tok`}/>
            <i style={{width: pct(budget.code) + '%', background: 'var(--blue)'}} title={`Generated ${budget.code} tok`}/>
            <i className="free" style={{width: pct(freeTokens) + '%'}} title={`Free ${freeTokens} tok`}/>
          </div>
          <div className="token-legend">
            <span className="item"><span className="dot" style={{background:'var(--violet)'}}/>Invariants {budget.invariants}w</span>
            <span className="item"><span className="dot" style={{background:'var(--amber)'}}/>Handoff {budget.handoff}</span>
            <span className="item"><span className="dot" style={{background:'var(--cyan)'}}/>DRAKON-IR {budget.drakon}</span>
            <span className="item"><span className="dot" style={{background:'var(--blue)'}}/>Generated {budget.code}</span>
            <span className="item"><span className="dot" style={{background:'var(--border-strong)'}}/>Free {freeTokens}</span>
          </div>
        </div>

        {/* Stream window */}
        <div className="stream-window" ref={streamRef}>
          {BSDD.STREAM_CODE.slice(0, visibleLines).map((row, i) => (
            <div key={i} className="stream-line">
              <span className="ln">{i + 1}</span>
              <span className="code">{colorize(row.code)}</span>
            </div>
          ))}
          {streaming && cursorLine >= 0 && cursorLine < BSDD.STREAM_CODE.length && (
            <div className="stream-line">
              <span className="ln">{cursorLine + 1}</span>
              <span className="code">
                {colorize(partial)}<span className="stream-cursor"/>
              </span>
            </div>
          )}
        </div>

        {/* Attach chips */}
        <div className="attach-row">
          <button className="attach-chip"><span className="plus">+</span> Active ADR-008</button>
          <button className="attach-chip"><span className="plus">+</span> DRAKON graph</button>
          <button className="attach-chip"><span className="plus">+</span> pytest report</button>
          <button className="attach-chip"><span className="plus">+</span> Utopia fact</button>
        </div>

        {/* Stream status */}
        <div className="stream-status">
          <span className="stat">slot: <b>{BSDD.SLOTS.find(s => s.id === activeSlot).name}</b></span>
          <span className="stat">rate: <b>{tokRate} tok/s</b></span>
          <span className="stat">streamed: <b>{tokensStreamed.toLocaleString()}</b></span>
          <span className="stat">latency: <b>18ms</b></span>
          <button className="kill-btn" onClick={onToggleStream}>
            {streaming ? '■ Kill Stream' : '▶ Resume Stream'}
          </button>
        </div>
      </div>
    </div>
  );
}

window.CopilotPanel = CopilotPanel;
