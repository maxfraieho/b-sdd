// Bitemporal timeline: Valid Time (T_v) and Transaction Time (T_t)
const { useState: __useState, useRef: __useRef, useEffect: __useEffect } = React;

function fmtDate(ms) {
  const d = new Date(ms);
  return d.toISOString().slice(0, 10);
}

function BitemporalTimeline({ playheadTv, playheadTt, onScrub }) {
  const { startMs, endMs } = BSDD.TIMELINE;
  const rangeMs = endMs - startMs;
  const trackRef = __useRef(null);
  const [dragging, setDragging] = __useState(null); // 'tv' | 'tt' | null

  const posPct = (ms) => Math.max(0, Math.min(100, ((ms - startMs) / rangeMs) * 100));

  const handleMouseDown = (which) => (e) => {
    setDragging(which);
    e.preventDefault();
  };

  __useEffect(() => {
    if (!dragging) return;
    const onMove = (e) => {
      if (!trackRef.current) return;
      const rect = trackRef.current.getBoundingClientRect();
      const pct = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
      const ms = startMs + pct * rangeMs;
      onScrub(dragging, ms);
    };
    const onUp = () => setDragging(null);
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onUp);
    return () => {
      window.removeEventListener('mousemove', onMove);
      window.removeEventListener('mouseup', onUp);
    };
  }, [dragging]);

  // Compute which ADRs are "active" at current Tv (based on tv date and superseded logic)
  const activeAdrs = BSDD.ADRS.filter(a => {
    const created = Date.parse(a.tv);
    if (created > playheadTv) return false;
    if (a.status === 'superseded') {
      const successor = BSDD.ADRS.find(x => x.id === a.supersededBy);
      if (successor && Date.parse(successor.tv) <= playheadTv) return false;
    }
    return true;
  }).length;

  const supersededNow = BSDD.ADRS.filter(a => {
    if (a.status !== 'superseded') return false;
    const successor = BSDD.ADRS.find(x => x.id === a.supersededBy);
    return successor && Date.parse(successor.tv) <= playheadTv;
  }).length;

  // Month ticks
  const months = [];
  let cur = new Date(startMs);
  cur.setDate(1);
  while (cur.getTime() < endMs) {
    months.push(cur.getTime());
    cur.setMonth(cur.getMonth() + 1);
  }

  const renderTrack = (which, playhead) => {
    const trackColor = which === 'tv' ? 'emerald' : 'cyan';
    return (
      <div className="track" ref={which === 'tv' ? trackRef : null}>
        <span className="track-label">
          {which === 'tv' ? 'T_v · Valid Time (domain reality)' : 'T_t · Transaction Time (physical commit log)'}
        </span>

        {/* ADR markers */}
        {which === 'tv' && BSDD.ADRS.map(a => {
          const ms = Date.parse(a.tv);
          const isFaded = a.status === 'superseded' && (() => {
            const s = BSDD.ADRS.find(x => x.id === a.supersededBy);
            return s && Date.parse(s.tv) <= playheadTv;
          })();
          const cls = a.status === 'accepted' ? 'accepted' : a.status === 'superseded' ? (isFaded ? 'superseded' : 'accepted') : 'proposed';
          return (
            <div
              key={a.id}
              className={`marker ${cls}`}
              style={{ left: posPct(ms) + '%' }}
              title={`${a.id}: ${a.title}`}
            >
              <span className="lbl mono">{a.id}</span>
            </div>
          );
        })}
        {which === 'tt' && BSDD.ADRS.map(a => {
          const ms = Date.parse(a.tt);
          return (
            <div
              key={a.id}
              className="marker accepted"
              style={{ left: posPct(ms) + '%', background: 'var(--cyan)', boxShadow: '0 0 4px var(--cyan)' }}
              title={`${a.id} committed`}
            />
          );
        })}

        {/* Supersede edges (only on Tv track) */}
        {which === 'tv' && BSDD.ADRS.filter(a => a.supersededBy).map(a => {
          const target = BSDD.ADRS.find(x => x.id === a.supersededBy);
          if (!target) return null;
          const left = posPct(Date.parse(a.tv));
          const width = posPct(Date.parse(target.tv)) - left;
          return (
            <div
              key={`e-${a.id}`}
              className="supersede-edge"
              style={{ left: left + '%', width: width + '%' }}
              title={`${a.id} → superseded by ${target.id}`}
            />
          );
        })}

        {/* Ticks */}
        <div className="track-scale">
          {months.map((m, i) => (
            <React.Fragment key={m}>
              <div className="tick" style={{ left: posPct(m) + '%' }}/>
              {i % 2 === 0 && (
                <div className="tick-label" style={{ left: posPct(m) + '%' }}>
                  {new Date(m).toLocaleDateString('en', { month: 'short', year: '2-digit' })}
                </div>
              )}
            </React.Fragment>
          ))}
        </div>

        {/* Playhead */}
        <div
          className={`playhead ${which === 'tt' ? 'tt' : ''}`}
          style={{ left: posPct(playhead) + '%' }}
          onMouseDown={handleMouseDown(which)}
        >
          <div className="cap"/>
          <div className="val">{fmtDate(playhead)}</div>
        </div>
      </div>
    );
  };

  return (
    <div className="timeline-zone">
      <div className="timeline-title">
        <h4>Bitemporal ADR Radar</h4>
        <div className="sub">Utopia DB · pgvector + Tantivy · 8 rulings tracked</div>
        <div className="legend-dots">
          <span className="tv">T_v</span>
          <span className="tt">T_t</span>
          <span style={{color: 'var(--rose)'}}>▶ superseded</span>
        </div>
      </div>

      <div className="timeline-tracks">
        {renderTrack('tv', playheadTv)}
        {renderTrack('tt', playheadTt)}
      </div>

      <div className="timeline-summary">
        <div className="row"><span className="k">Active ADRs @ T_v</span><span className="v ok">{activeAdrs} / {BSDD.ADRS.length}</span></div>
        <div className="row"><span className="k">Superseded now</span><span className="v warn">{supersededNow}</span></div>
        <div className="row"><span className="k">Δ (T_t − T_v)</span><span className="v">{Math.round((playheadTt - playheadTv) / 86400000)}d</span></div>
        <div className="row"><span className="k">Snapshot integrity</span><span className="v ok">✓ WORM</span></div>
      </div>
    </div>
  );
}

window.BitemporalTimeline = BitemporalTimeline;
