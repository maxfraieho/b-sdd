/* =========================================================
   Zone 4 · Sovereign LLM Copilot Panel (420px)
   Model slots · Token Budget gauge · SSE token stream
   ========================================================= */
function CopilotPanel({ slots, activeSlotId, onSelectSlot, activeRules, streaming, onToggleStream, budgetOverride, onOpenReviewGate }) {
  return (
    <section className="app-copilot">
      {/* Header */}
      <div className="row shrink-0" style={{ height: 40, padding: '0 12px', borderBottom: '1px solid var(--color-border-hair)', gap: 8 }}>
        <span className="text-eyebrow" style={{ color: 'var(--color-amber)' }}>⚡ SOVEREIGN LLM COPILOT</span>
        <div className="grow" />
        <Badge tone="cyan" outline>SSE</Badge>
        <Badge tone="emerald" outline>mTLS</Badge>
        <span className="mono" style={{ fontSize: 10, color: 'var(--color-fg-muted)' }}>.184:18880</span>
      </div>

      {/* Model slots */}
      <div className="col shrink-0" style={{ padding: 10, gap: 6, borderBottom: '1px solid var(--color-border-hair)' }}>
        <div className="row" style={{ justifyContent: 'space-between' }}>
          <span className="text-eyebrow">MODEL SLOTS</span>
          <span className="mono" style={{ fontSize: 10, color: 'var(--color-fg-muted)' }}>3 available</span>
        </div>
        {slots.map((s) => (
          <SlotCard key={s.id} slot={s} active={s.id === activeSlotId} onClick={() => onSelectSlot(s.id)} />
        ))}
      </div>

      {/* Context Token Budget */}
      <div className="col shrink-0" style={{ padding: 10, gap: 8, borderBottom: '1px solid var(--color-border-hair)' }}>
        <div className="row" style={{ justifyContent: 'space-between', whiteSpace: 'nowrap' }}>
          <span className="text-eyebrow" style={{ whiteSpace: 'nowrap' }}>TOKEN BUDGET</span>
          <span className="mono tabnum" style={{ fontSize: 10, color: 'var(--color-fg-muted)', whiteSpace: 'nowrap' }}>
            {budgetOverride ?? activeRules.word_count}w / {activeRules.max_budget}w · {activeRules.latency_ms}ms
          </span>
        </div>
        <TokenGauge current={budgetOverride ?? activeRules.word_count} max={activeRules.max_budget} />
        <div className="row gap-1" style={{ flexWrap: 'wrap' }}>
          {activeRules.recommended_skills.map((s) => (
            <Badge key={s} tone="neutral" outline style={{ whiteSpace: 'nowrap' }}>{s}</Badge>
          ))}
        </div>
      </div>

      {/* Stream area */}
      <CopilotStream streaming={streaming} onToggleStream={onToggleStream} />

      {/* Review Gate CTA (visible in Φ6) */}
      <div className="shrink-0" style={{ padding: 10, borderTop: '1px solid var(--color-border-hair)' }}>
        <Button size="lg" variant="primary" onClick={onOpenReviewGate} style={{ width: '100%', justifyContent: 'center' }}>
          Відкрити Human Review Gate (Φ6)
        </Button>
      </div>
    </section>
  );
}

function SlotCard({ slot, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className="col"
      style={{
        padding: 8,
        background: active ? 'var(--color-amber-glow)' : 'var(--color-bg-card)',
        border: `1px solid ${active ? 'var(--color-amber)' : 'var(--color-border-hair)'}`,
        borderLeft: `3px solid ${active ? 'var(--color-amber)' : 'transparent'}`,
        borderRadius: 2,
        textAlign: 'left',
        gap: 3,
        cursor: 'pointer',
      }}
    >
      <div className="row" style={{ justifyContent: 'space-between' }}>
        <span className="mono" style={{ fontSize: 11, fontWeight: 600, color: active ? 'var(--color-amber)' : 'var(--color-fg-primary)' }}>
          {slot.name}
        </span>
        <span className="mono tabnum" style={{ fontSize: 10, color: 'var(--color-fg-muted)' }}>~{(slot.latencyAvg/1000).toFixed(1)}s</span>
      </div>
      <div className="mono" style={{ fontSize: 10, color: 'var(--color-fg-secondary)' }}>{slot.model}</div>
      <div style={{ fontSize: 10.5, color: 'var(--color-fg-muted)', lineHeight: 1.35 }}>{slot.description}</div>
    </button>
  );
}

function TokenGauge({ current, max }) {
  const pct = Math.min(100, (current / max) * 100);
  const over = current > max;
  // Palantir-style stacked bar: invariants (green) → handoff (cyan) → drakon (amber) → generated
  const segments = over
    ? [{ pct: 100, color: 'var(--color-rose)' }]
    : [
        { pct: (250/max)*100,           color: 'var(--color-emerald)' },
        { pct: ((320-250)/max)*100,     color: 'var(--color-cyan)'    },
        { pct: ((current-320)/max)*100 > 0 ? ((current-320)/max)*100 : 0, color: 'var(--color-amber)' },
      ];
  return (
    <div className="col gap-1">
      <div style={{ height: 12, background: 'var(--color-bg-canvas)', border: '1px solid var(--color-border-hair)', display: 'flex', overflow: 'hidden' }}>
        {segments.map((seg, i) => (
          <div key={i} style={{ width: `${seg.pct}%`, background: seg.color, transition: 'width 200ms' }} />
        ))}
        {!over && <div style={{ flex: 1, background: 'transparent' }} />}
      </div>
      {over && (
        <div className="mono" style={{ fontSize: 10, color: 'var(--color-rose)' }}>
          ⚠ BUDGET EXCEEDED · ADR-002-INV-02 violation · rollback required
        </div>
      )}
      {!over && (
        <div className="row gap-3" style={{ fontSize: 9.5, color: 'var(--color-fg-muted)', flexWrap: 'wrap' }}>
          <span className="row gap-1"><Dot tone="emerald"/><span>Invariants 250w</span></span>
          <span className="row gap-1"><Dot tone="cyan"/><span>Handoff 70w</span></span>
          <span className="row gap-1"><Dot tone="amber"/><span>DRAKON {Math.max(0, current-320)}w</span></span>
        </div>
      )}
    </div>
  );
}

function CopilotStream({ streaming, onToggleStream }) {
  const [buf, setBuf] = useState('');
  const [i, setI] = useState(0);
  const preRef = useRef(null);

  useEffect(() => {
    if (!streaming) return;
    const chunks = window.BSDD.STREAM_SAMPLE;
    const id = setInterval(() => {
      setI((prev) => {
        const next = (prev + 1) % chunks.length;
        setBuf((b) => b + chunks[prev]);
        return next;
      });
    }, 420);
    return () => clearInterval(id);
  }, [streaming]);

  useEffect(() => {
    if (preRef.current) preRef.current.scrollTop = preRef.current.scrollHeight;
  }, [buf]);

  // Truncate to keep buffer sane
  useEffect(() => {
    if (buf.length > 2000) setBuf(buf.slice(-1400));
  }, [buf]);

  return (
    <div className="col flex-1" style={{ minHeight: 0 }}>
      <div className="row shrink-0" style={{ padding: '6px 10px', borderBottom: '1px solid var(--color-border-hair)', gap: 8 }}>
        <span className="text-eyebrow">STREAM</span>
        <div className="grow" />
        <IconButton size="sm" title={streaming ? 'Pause' : 'Play'} onClick={onToggleStream}>
          {streaming ? Icons.pause : Icons.play}
        </IconButton>
        <span className="mono tabnum" style={{ fontSize: 10, color: 'var(--color-fg-muted)' }}>
          {streaming ? <span style={{ color: 'var(--color-emerald)' }}>● live</span> : <span style={{ color: 'var(--color-fg-muted)' }}>○ paused</span>}
        </span>
      </div>
      <pre
        ref={preRef}
        className="mono select-text flex-1"
        style={{
          margin: 0, padding: '10px 12px',
          background: 'var(--color-bg-canvas)',
          color: 'var(--color-fg-primary)',
          fontSize: 11,
          lineHeight: 1.55,
          overflow: 'auto',
          whiteSpace: 'pre-wrap',
        }}
      >
        {buf || '# Ready — press ▶ to start streaming from :18880'}
        {streaming && <span style={{ color: 'var(--color-amber)', animation: 'pulse-dot 900ms infinite' }}>▊</span>}
      </pre>
    </div>
  );
}

window.CopilotPanel = CopilotPanel;
