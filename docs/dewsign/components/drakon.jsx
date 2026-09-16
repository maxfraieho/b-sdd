// DRAKON Studio — SVG viewer with interactive nodes
// Skewer (happy path) on the left, degradation branches on the right

function DrakonStudio({ selectedNodeId, onNodeClick }) {
  const drn = BSDD.DRAKON;

  // Build map for edge routing
  const nodeMap = {};
  drn.nodes.forEach(n => { nodeMap[n.id] = n; });

  const renderNode = (n) => {
    const selected = selectedNodeId === n.id;
    const commonProps = {
      className: `drakon-node ${selected ? 'selected' : ''}`,
      onClick: () => onNodeClick(n),
    };

    let shape;
    switch (n.type) {
      case 'headline':
        // Pill (Заголовок)
        shape = <rect className="node-body node-headline" x={n.x} y={n.y} width={n.w} height={n.h} rx={n.h/2} ry={n.h/2}/>;
        break;
      case 'action': {
        const stateCls = n.state ? ` ${n.state}` : '';
        shape = <rect className={`node-body node-action${stateCls}`} x={n.x} y={n.y} width={n.w} height={n.h} rx={2}/>;
        break;
      }
      case 'question': {
        // Hexagon (rhomb-ish) for question
        const cx = n.x + n.w/2, cy = n.y + n.h/2;
        const pts = [
          [n.x + 12, n.y],
          [n.x + n.w - 12, n.y],
          [n.x + n.w, cy],
          [n.x + n.w - 12, n.y + n.h],
          [n.x + 12, n.y + n.h],
          [n.x, cy],
        ].map(p => p.join(',')).join(' ');
        shape = <polygon className="node-body node-question" points={pts}/>;
        break;
      }
      case 'silhouette':
        // Rect with double left edge (silhouette route)
        shape = (
          <g>
            <rect className="node-body node-silhouette" x={n.x} y={n.y} width={n.w} height={n.h} rx={2}/>
            <line x1={n.x + 4} y1={n.y + 4} x2={n.x + 4} y2={n.y + n.h - 4} stroke="var(--cyan)" strokeWidth="1"/>
          </g>
        );
        break;
      case 'end':
        // Rect with rounded bottom (end icon)
        shape = <rect className={`node-body node-end ${n.reject ? 'reject' : ''}`} x={n.x} y={n.y} width={n.w} height={n.h} rx={n.h/2}/>;
        break;
      default:
        shape = <rect className="node-body node-action" x={n.x} y={n.y} width={n.w} height={n.h}/>;
    }

    return (
      <g key={n.id} {...commonProps}>
        {shape}
        <text x={n.x + n.w/2} y={n.y + n.h/2 + 4} textAnchor="middle">
          {n.label}
        </text>
        {n.adr && (
          <text x={n.x + n.w - 6} y={n.y + 12} textAnchor="end" className="adr-tag">
            {n.adr}
          </text>
        )}
      </g>
    );
  };

  // Route an edge with orthogonal routing
  const renderEdge = (e, idx) => {
    const src = nodeMap[e.from], dst = nodeMap[e.to];
    if (!src || !dst) return null;

    const sx = src.x + src.w / 2;
    const sy = src.y + src.h;
    const dx = dst.x + dst.w / 2;
    const dy = dst.y;

    // If same column → straight down
    let path;
    if (Math.abs(sx - dx) < 4) {
      path = `M ${sx} ${sy} L ${dx} ${dy - 6}`;
    } else {
      // Orthogonal: down → right/left → down (with elbow)
      const midY = sy + Math.max(14, (dy - sy) / 2);
      path = `M ${sx} ${sy} L ${sx} ${midY} L ${dx} ${midY} L ${dx} ${dy - 6}`;
    }

    return (
      <g key={idx}>
        <path className={`drakon-edge ${e.kind || ''}`} d={path} markerEnd="url(#arrow)"/>
        {e.label && (
          <text
            x={sx + (dx - sx) / 2 + (dx > sx ? 8 : -8)}
            y={sy + 12}
            fontSize="9"
            fill={e.kind === 'reject' ? 'var(--rose)' : 'var(--emerald)'}
            fontFamily="var(--font-mono)"
          >
            {e.label}
          </text>
        )}
      </g>
    );
  };

  return (
    <div className="panel drakon-panel">
      <div className="panel-header">
        <div className="panel-title">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
            <rect x="6" y="1" width="4" height="14" fill="var(--violet)" opacity="0.4"/>
            <rect x="6" y="1" width="4" height="4" fill="var(--violet)"/>
            <rect x="6" y="6" width="4" height="4" fill="var(--blue)"/>
            <rect x="6" y="11" width="4" height="4" fill="var(--emerald)"/>
            <rect x="11" y="6" width="3" height="4" fill="var(--rose)" opacity="0.6"/>
          </svg>
          DRAKON Studio
          <span className="tag">Φ2 · Spec Locked</span>
        </div>
        <div className="panel-actions">
          <button className="icon-btn" title="Zoom to fit">
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M6 2v2M2 6h2M14 6h-2M6 14v-2M10 2v2M14 10h-2M10 14v-2M2 10h2" stroke="currentColor" strokeWidth="1.5"/></svg>
          </button>
          <button className="icon-btn" title="Export .drn">
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M8 2v9m0 0l-3-3m3 3l3-3M2 13h12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
          </button>
        </div>
      </div>

      <div className="drakon-toolbar">
        <span className="path-crumb">
          projects / accord-suisse / specs / <b className="mono">{drn.file}</b>
        </span>
        <span style={{marginLeft: 'auto', display: 'flex', gap: 12, alignItems: 'center'}}>
          <span className="mono badge-ok">✓ planar · 0 crossings</span>
          <span className="mono" style={{color: 'var(--text-muted)'}}>linked → {drn.linkedADR}</span>
        </span>
      </div>

      <div className="drakon-canvas">
        <svg className="drakon-svg" width="620" height="720" viewBox="0 0 620 720">
          <defs>
            <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
              <path d="M0,0 L10,5 L0,10 z" fill="var(--border-strong)"/>
            </marker>
            <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
              <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(255,255,255,0.02)" strokeWidth="0.5"/>
            </pattern>
          </defs>

          <rect width="620" height="720" fill="url(#grid)"/>

          {/* Shampur guideline */}
          <line x1={270} y1={80} x2={270} y2={680} stroke="var(--blue)" strokeWidth="0.5" strokeDasharray="2 4" opacity="0.3"/>
          <text x={278} y={78} fontSize="9" fill="var(--blue)" opacity="0.7" fontFamily="var(--font-mono)">SHAMPUR (happy path)</text>

          {/* Edges first, then nodes on top */}
          {drn.edges.map(renderEdge)}
          {drn.nodes.map(renderNode)}
        </svg>

        <div className="drakon-legend">
          <div className="row"><span className="swatch" style={{background: 'var(--violet)'}}/> Headline</div>
          <div className="row"><span className="swatch" style={{background: 'var(--blue)'}}/> Action</div>
          <div className="row"><span className="swatch" style={{background: 'var(--amber)'}}/> Question</div>
          <div className="row"><span className="swatch" style={{background: 'var(--cyan)'}}/> Silhouette</div>
          <div className="row"><span className="swatch" style={{background: 'var(--rose)'}}/> Reject / End</div>
        </div>
      </div>
    </div>
  );
}

window.DrakonStudio = DrakonStudio;
