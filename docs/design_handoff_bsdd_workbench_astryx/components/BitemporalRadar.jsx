/* =========================================================
   Zone 4b · Bitemporal ADR Radar (112px)
   Dual-slider (T_v Valid Time / T_t Transaction Time) +
   horizontal ADR strip.
   ========================================================= */
function BitemporalRadar({ adrs, playheadTvDay, playheadTtDay, onScrub, onSelectAdr, selectedAdrId }) {
  const activeAdrs = adrs.filter((a) => {
    const validDay = parseInt(a.valid_from.slice(8, 10), 10);
    return validDay <= playheadTvDay;
  });
  const supersededCount = adrs.length - activeAdrs.length;

  return (
    <footer
      className="row shrink-0"
      style={{
        height: 'var(--h-radar)',
        background: 'var(--color-bg-card)',
        borderTop: '1px solid var(--color-border-hair)',
        gap: 0,
      }}
    >
      {/* Left meta */}
      <div
        className="col shrink-0"
        style={{
          width: 220, padding: '10px 12px', gap: 4,
          borderRight: '1px solid var(--color-border-hair)',
        }}
      >
        <div className="row gap-2">
          <div style={{ width: 22, height: 22, background: 'var(--color-cyan)', borderRadius: 2, display: 'grid', placeItems: 'center', fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: 11, color: '#0b0f16' }}>R</div>
          <div className="col" style={{ gap: 0, lineHeight: 1.1 }}>
            <div style={{ fontSize: 11.5, fontWeight: 700 }}>Bitemporal ADR Radar</div>
            <div className="mono" style={{ fontSize: 9, color: 'var(--color-fg-muted)' }}>Utopia DB · pgvector · Tantivy</div>
          </div>
        </div>
        <div className="row gap-3" style={{ marginTop: 6 }}>
          <div className="col" style={{ gap: 0 }}>
            <div className="text-eyebrow">ACTIVE</div>
            <div className="mono tabnum" style={{ fontSize: 14, color: 'var(--color-emerald)', fontWeight: 700 }}>{activeAdrs.length}</div>
          </div>
          <div className="col" style={{ gap: 0 }}>
            <div className="text-eyebrow">SUPERSEDED</div>
            <div className="mono tabnum" style={{ fontSize: 14, color: 'var(--color-fg-faint)', fontWeight: 700 }}>{supersededCount}</div>
          </div>
        </div>
        <div className="mono" style={{ fontSize: 9.5, color: 'var(--color-cyan)', marginTop: 4 }}>
          Δ (T_t − T_v) = {playheadTtDay - playheadTvDay}d
        </div>
      </div>

      {/* Timeline sliders */}
      <div className="col flex-1" style={{ padding: '8px 16px', minWidth: 0, gap: 8 }}>
        <TimelineTrack
          label="T_v · Valid Time (domain reality)"
          tone="emerald"
          playhead={playheadTvDay}
          markers={adrs.map((a) => ({ id: a.id, day: parseInt(a.valid_from.slice(8, 10), 10), status: 'active' }))}
          onScrub={(d) => onScrub('tv', d)}
        />
        <TimelineTrack
          label="T_t · Transaction Time (physical commit log)"
          tone="cyan"
          playhead={playheadTtDay}
          markers={adrs.map((a) => ({ id: a.id, day: parseInt(a.tx_time.slice(8, 10), 10), status: 'tx' }))}
          onScrub={(d) => onScrub('tt', d)}
        />
      </div>

      {/* Right: ADR chip strip */}
      <div className="col shrink-0" style={{ width: 340, padding: '8px 10px', gap: 4, borderLeft: '1px solid var(--color-border-hair)', overflow: 'hidden' }}>
        <div className="text-eyebrow">Active ADRs @ T_v {formatDay(playheadTvDay)}</div>
        <div className="row" style={{ flexWrap: 'wrap', gap: 4, overflow: 'auto' }}>
          {activeAdrs.map((a) => {
            const sel = a.id === selectedAdrId;
            return (
              <button
                key={a.id}
                onClick={() => onSelectAdr(a)}
                className="row gap-1"
                title={a.title}
                style={{
                  padding: '3px 6px',
                  background: sel ? 'var(--color-amber-glow)' : 'var(--color-bg-elevated)',
                  border: `1px solid ${sel ? 'var(--color-amber)' : 'var(--color-border-hair)'}`,
                  fontFamily: 'var(--font-mono)',
                  fontSize: 10, fontWeight: 600,
                  color: sel ? 'var(--color-amber)' : 'var(--color-fg-primary)',
                  borderRadius: 2, cursor: 'pointer',
                }}
              >
                <Dot tone={sel ? 'amber' : 'emerald'} />
                {a.id}
              </button>
            );
          })}
        </div>
      </div>
    </footer>
  );
}

function TimelineTrack({ label, tone, playhead, markers, onScrub }) {
  const trackRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const totalDays = 30; // Sep 1–30 window
  const pct = ((playhead - 1) / (totalDays - 1)) * 100;

  const posFromClient = (clientX) => {
    if (!trackRef.current) return playhead;
    const r = trackRef.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(r.width, clientX - r.left));
    const d = Math.round((x / r.width) * (totalDays - 1)) + 1;
    return Math.max(1, Math.min(totalDays, d));
  };

  useEffect(() => {
    if (!dragging) return;
    const move = (e) => onScrub(posFromClient(e.clientX));
    const up = () => setDragging(false);
    window.addEventListener('mousemove', move);
    window.addEventListener('mouseup', up);
    return () => { window.removeEventListener('mousemove', move); window.removeEventListener('mouseup', up); };
  }, [dragging]);

  return (
    <div className="col" style={{ gap: 2 }}>
      <div className="row" style={{ justifyContent: 'space-between' }}>
        <span className="mono" style={{ fontSize: 10, color: `var(--color-${tone})`, letterSpacing: '0.02em' }}>{label}</span>
        <span className="mono tabnum" style={{ fontSize: 10, color: 'var(--color-fg-muted)' }}>2026-09-{String(playhead).padStart(2, '0')}</span>
      </div>
      <div
        ref={trackRef}
        onMouseDown={(e) => { onScrub(posFromClient(e.clientX)); setDragging(true); }}
        style={{
          position: 'relative',
          height: 24,
          background: 'var(--color-bg-canvas)',
          border: '1px solid var(--color-border-hair)',
          borderRadius: 2,
          cursor: 'ew-resize',
        }}
      >
        {/* day tick marks */}
        {Array.from({ length: totalDays }, (_, i) => i + 1).map((d) => (
          <div key={d} style={{
            position: 'absolute', top: 0, bottom: 0,
            left: `${((d - 1) / (totalDays - 1)) * 100}%`,
            width: 1, background: d % 5 === 0 ? 'var(--color-border-hair)' : 'transparent',
          }} />
        ))}
        {/* markers */}
        {markers.map((m, i) => (
          <div
            key={i}
            title={`${m.id} @ Sep ${m.day}`}
            style={{
              position: 'absolute',
              top: '50%',
              left: `${((m.day - 1) / (totalDays - 1)) * 100}%`,
              transform: 'translate(-50%, -50%)',
              width: 8, height: 8,
              background: `var(--color-${tone})`,
              boxShadow: `0 0 6px var(--color-${tone}-glow)`,
              borderRadius: 1,
            }}
          />
        ))}
        {/* playhead */}
        <div style={{
          position: 'absolute',
          top: -3, bottom: -3,
          left: `${pct}%`,
          transform: 'translateX(-50%)',
          width: 2,
          background: 'var(--color-amber)',
          boxShadow: '0 0 6px var(--color-amber-glow)',
        }}>
          <div style={{
            position: 'absolute', top: -6, left: '50%', transform: 'translateX(-50%)',
            width: 10, height: 10,
            background: 'var(--color-amber)',
            borderRadius: 1,
          }}/>
        </div>
      </div>
      {/* day labels */}
      <div className="row" style={{ justifyContent: 'space-between', fontSize: 8.5, fontFamily: 'var(--font-mono)', color: 'var(--color-fg-faint)' }}>
        {[1, 8, 16, 24, 30].map((d) => <span key={d}>Sep {d}</span>)}
      </div>
    </div>
  );
}

function formatDay(day) {
  return `Sep ${day}, 2026`;
}

window.BitemporalRadar = BitemporalRadar;
