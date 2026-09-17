/* =========================================================
   Zone 3 · DRAKON Studio
   Toolbar · 17-icon Palette · Canvas (widget|flow|json) · Inspector
   ========================================================= */
function DrakonStudio(props) {
  const {
    diagram, selectedSpecId, viewMode, onViewModeChange,
    selectedNodeId, onSelectNode,
    activeSocketType, onInsertIcon,
    onOpenPseudocode, onSave, saveState,
  } = props;

  return (
    <section className="app-studio">
      <DrakonToolbar
        selectedSpecId={selectedSpecId}
        viewMode={viewMode}
        onViewModeChange={onViewModeChange}
        onOpenPseudocode={onOpenPseudocode}
        onSave={onSave}
        saveState={saveState}
      />
      {viewMode === 'widget' && (
        <DrakonIconPalette activeSocketType={activeSocketType} onInsertIcon={onInsertIcon} />
      )}
      <div style={{ flex: 1, position: 'relative', overflow: 'hidden' }}>
        {viewMode === 'widget' && (
          <DrakonCanvas
            diagram={diagram}
            selectedNodeId={selectedNodeId}
            onSelectNode={onSelectNode}
            activeSocketType={activeSocketType}
          />
        )}
        {viewMode === 'flow' && <VisualFlowView diagram={diagram} selectedNodeId={selectedNodeId} onSelectNode={onSelectNode} />}
        {viewMode === 'json' && <RawIRView diagram={diagram} />}
      </div>
    </section>
  );
}

// -------------------- Toolbar --------------------
function DrakonToolbar({ selectedSpecId, viewMode, onViewModeChange, onOpenPseudocode, onSave, saveState }) {
  return (
    <div
      className="row shrink-0"
      style={{
        height: 'var(--h-toolbar)',
        background: 'var(--color-bg-panel)',
        borderBottom: '1px solid var(--color-border-hair)',
        padding: '0 10px',
        gap: 10,
        flexWrap: 'nowrap',
        overflow: 'hidden',
        whiteSpace: 'nowrap',
      }}
    >
      <div className="row gap-2">
        <span className="text-eyebrow" style={{ color: 'var(--color-fg-primary)' }}>DRAKON STUDIO</span>
        <Badge tone="cyan" outline>{selectedSpecId?.split('-')[0]}</Badge>
      </div>

      <div className="divider-v" />

      <div className="row gap-1">
        <IconButton size="sm" title="Zoom in">{Icons.plus}</IconButton>
        <IconButton size="sm" title="Zoom out">{Icons.minus}</IconButton>
        <IconButton size="sm" title="Home">{Icons.home}</IconButton>
        <IconButton size="sm" title="Undo">{Icons.undo}</IconButton>
        <IconButton size="sm" title="Redo">{Icons.redo}</IconButton>
      </div>

      <div className="divider-v" />

      <Segmented
        value={viewMode}
        onChange={onViewModeChange}
        options={[
          { value: 'widget', label: 'Widget' },
          { value: 'flow',   label: 'Visual Flow' },
          { value: 'json',   label: 'Raw IR JSON' },
        ]}
      />

      <div className="row gap-2 ml-auto" style={{ marginLeft: 'auto' }}>
        <div className="mono" style={{ fontSize: 10, color: 'var(--color-emerald)' }}>
          <span className="text-eyebrow" style={{ marginRight: 6 }}>PLANAR</span>
          crossings: 0 · nodes: 12
        </div>
        <div className="divider-v" />
        <Button size="sm" icon={Icons.code} onClick={onOpenPseudocode}>Псевдокод &amp; Правила</Button>
        <Button size="sm" variant="primary" icon={saveState === 'saving' ? Icons.spin : saveState === 'saved' ? Icons.check : Icons.save} onClick={onSave}>
          {saveState === 'saving' ? 'Збереження…' : saveState === 'saved' ? 'Збережено' : 'Зберегти (Ctrl+S)'}
        </Button>
      </div>
    </div>
  );
}

// -------------------- 17-icon Palette --------------------
const DRAKON_ICON_GROUPS = [
  { key: 'core',    label: 'Core' },
  { key: 'io',      label: 'I/O' },
  { key: 'control', label: 'Control' },
  { key: 'meta',    label: 'Meta' },
];

function DrakonIconPalette({ activeSocketType, onInsertIcon }) {
  const icons = window.BSDD.DRAKON_ICONS;
  return (
    <div
      className="row shrink-0"
      style={{
        height: 'var(--h-palette)',
        background: 'var(--color-bg-card)',
        borderBottom: '1px solid var(--color-border-hair)',
        padding: '0 12px',
        gap: 12,
        overflowX: 'auto',
        alignItems: 'center',
      }}
    >
      {DRAKON_ICON_GROUPS.map((g, gi) => {
        const groupIcons = icons.filter((i) => i.group === g.key);
        return (
          <React.Fragment key={g.key}>
            {gi > 0 && <div style={{ width: 1, height: 32, background: 'var(--color-border-hair)', flexShrink: 0 }} />}
            <div className="row gap-1 shrink-0" style={{ position: 'relative', alignItems: 'center' }}>
              {groupIcons.map((ic) => (
                <PaletteButton
                  key={ic.type}
                  icon={ic}
                  active={activeSocketType === ic.type}
                  onClick={() => onInsertIcon(ic.type)}
                />
              ))}
            </div>
          </React.Fragment>
        );
      })}
      {activeSocketType && (
        <div className="row gap-2 shrink-0" style={{ marginLeft: 'auto', padding: '2px 8px', background: 'var(--color-cyan-glow)', border: '1px solid var(--color-cyan)', borderRadius: 2 }}>
          <Dot tone="cyan" pulse/>
          <span className="mono" style={{ fontSize: 10, color: 'var(--color-cyan)' }}>SOCKET · {activeSocketType.toUpperCase()}</span>
        </div>
      )}
    </div>
  );
}

function PaletteButton({ icon, active, onClick }) {
  return (
    <button
      onClick={onClick}
      title={`${icon.label} · ${icon.hint}`}
      className="col"
      style={{
        minWidth: 46, height: 38, padding: '2px 4px',
        alignItems: 'center', justifyContent: 'center',
        gap: 1,
        background: active ? 'var(--color-cyan-glow)' : 'var(--color-bg-elevated)',
        border: `1px solid ${active ? 'var(--color-cyan)' : 'var(--color-border-hair)'}`,
        borderRadius: 2,
        cursor: 'pointer',
        transition: 'all 100ms',
        flexShrink: 0,
        whiteSpace: 'nowrap',
      }}
    >
      <DrakonIconSvg type={icon.type} size={14} color={active ? 'var(--color-cyan)' : 'var(--color-fg-secondary)'} />
      <div style={{ fontSize: 8.5, color: active ? 'var(--color-cyan)' : 'var(--color-fg-secondary)', fontWeight: 500, letterSpacing: '0.01em' }}>
        {icon.label}
      </div>
    </button>
  );
}

// Miniature icon glyphs for the palette (crisp SVG, no PNG dependency)
function DrakonIconSvg({ type, size = 14, color = 'currentColor' }) {
  const s = size, S = 1.4;
  const path = {
    action:    <rect x="2" y="4" width={s-4} height={s-8} fill="none" stroke={color} strokeWidth={S}/>,
    question:  <polygon points={`${s/2},2 ${s-2},${s/2} ${s/2},${s-2} 2,${s/2}`} fill="none" stroke={color} strokeWidth={S}/>,
    select:    <polygon points={`4,4 ${s-4},4 ${s-2},${s-4} 2,${s-4}`} fill="none" stroke={color} strokeWidth={S}/>,
    case:      <polygon points={`3,${s-4} ${s/2},4 ${s-3},${s-4}`} fill="none" stroke={color} strokeWidth={S}/>,
    branch:    <><rect x="2" y="3" width={s-4} height="3" fill={color}/><line x1={s/2} y1="6" x2={s/2} y2={s-2} stroke={color} strokeWidth={S}/></>,
    end:       <rect x="2" y="4" width={s-4} height={s-8} rx={s/2-4} fill="none" stroke={color} strokeWidth={S}/>,
    input:     <path d={`M2,4 L${s-4},4 L${s-2},${s/2} L${s-4},${s-4} L2,${s-4} Z`} fill="none" stroke={color} strokeWidth={S}/>,
    output:    <path d={`M4,4 L${s-2},4 L${s-4},${s/2} L${s-2},${s-4} L4,${s-4} L2,${s/2} Z`} fill="none" stroke={color} strokeWidth={S}/>,
    shelf:     <><rect x="2" y="4" width={s-4} height={s-8} fill="none" stroke={color} strokeWidth={S}/><line x1={s/2} y1="4" x2={s/2} y2={s-4} stroke={color} strokeWidth="1"/></>,
    process:   <><rect x="2" y="4" width={s-4} height={s-8} fill="none" stroke={color} strokeWidth={S}/><line x1="4" y1="4" x2="4" y2={s-4} stroke={color}/><line x1={s-4} y1="4" x2={s-4} y2={s-4} stroke={color}/></>,
    timer:     <><circle cx={s/2} cy={s/2} r={s/2-3} fill="none" stroke={color} strokeWidth={S}/><line x1={s/2} y1={s/2} x2={s/2} y2="4" stroke={color} strokeWidth={S}/></>,
    pause:     <><rect x="4" y="4" width="2" height={s-8} fill={color}/><rect x={s-6} y="4" width="2" height={s-8} fill={color}/></>,
    duration:  <><rect x="2" y="5" width={s-4} height={s-10} fill="none" stroke={color} strokeWidth={S}/><line x1="2" y1={s/2} x2={s-2} y2={s/2} stroke={color} strokeDasharray="2 1"/></>,
    foreach:   <><path d={`M3,4 h${s-8} a2,2 0 0 1 0,4 h-${s-8} M${s-5},${s-4} L${s-3},${s-6} L${s-1},${s-4}`} fill="none" stroke={color} strokeWidth={S}/></>,
    par:       <><line x1="4" y1="3" x2="4" y2={s-3} stroke={color} strokeWidth={S}/><line x1={s-4} y1="3" x2={s-4} y2={s-3} stroke={color} strokeWidth={S}/><line x1="6" y1={s/2} x2={s-6} y2={s/2} stroke={color} strokeWidth={S}/></>,
    insertion: <><rect x="2" y="4" width={s-4} height={s-8} fill="none" stroke={color} strokeWidth={S} strokeDasharray="2 2"/></>,
    comment:   <path d={`M2,3 L${s-4},3 L${s-2},5 L${s-2},${s-3} L2,${s-3} Z`} fill="none" stroke={color} strokeWidth={S}/>,
  }[type];
  return <svg width={s} height={s} viewBox={`0 0 ${s} ${s}`} style={{ display: 'block' }}>{path}</svg>;
}

// -------------------- Canvas · SVG mock --------------------
function DrakonCanvas({ diagram, selectedNodeId, onSelectNode, activeSocketType }) {
  const svgString = React.useMemo(
    () => window.DrakonMock.render(diagram, { selectedId: selectedNodeId, activeSocketType }),
    [diagram, selectedNodeId, activeSocketType]
  );
  const containerRef = useRef(null);

  useEffect(() => {
    const node = containerRef.current;
    if (!node) return;
    const handler = (e) => {
      const g = e.target.closest('[data-node-id]');
      if (g) onSelectNode(g.getAttribute('data-node-id'));
    };
    node.addEventListener('click', handler);
    return () => node.removeEventListener('click', handler);
  }, [onSelectNode]);

  return (
    <div
      ref={containerRef}
      style={{
        width: '100%', height: '100%', overflow: 'auto',
        background: 'var(--color-bg-canvas)',
      }}
      dangerouslySetInnerHTML={{ __html: svgString }}
    />
  );
}

// -------------------- Visual Flow (simplified list-view fallback) --------------------
function VisualFlowView({ diagram, selectedNodeId, onSelectNode }) {
  const items = Object.entries(diagram.items || {}).filter(([id]) => id !== 'b0');
  return (
    <div style={{ padding: 24, overflow: 'auto', height: '100%' }}>
      <div className="col gap-2" style={{ maxWidth: 640, margin: '0 auto' }}>
        {items.map(([id, it]) => (
          <div
            key={id}
            onClick={() => onSelectNode(id)}
            style={{
              padding: '10px 14px',
              background: selectedNodeId === id ? 'var(--color-amber-glow)' : 'var(--color-bg-card)',
              border: `1px solid ${selectedNodeId === id ? 'var(--color-amber)' : 'var(--color-border-hair)'}`,
              borderLeft: `3px solid ${it.type === 'question' ? 'var(--color-amber)' : it.type === 'end' ? 'var(--color-rose)' : 'var(--color-emerald)'}`,
              cursor: 'pointer',
              display: 'flex', gap: 12, alignItems: 'center',
            }}
          >
            <Badge tone={it.type === 'question' ? 'amber' : it.type === 'end' ? 'rose' : 'emerald'} outline>{it.type}</Badge>
            <div style={{ flex: 1, fontSize: 12 }}>{it.content}</div>
            {it.secondary && <span className="mono" style={{ fontSize: 10, color: 'var(--color-amber)' }}>{it.secondary}</span>}
          </div>
        ))}
      </div>
    </div>
  );
}

// -------------------- Raw IR JSON --------------------
function RawIRView({ diagram }) {
  return (
    <div className="mono select-text" style={{ padding: 20, overflow: 'auto', height: '100%', fontSize: 11.5, lineHeight: 1.55, color: 'var(--color-fg-primary)', background: 'var(--color-bg-canvas)' }}>
      <pre style={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(diagram, null, 2)}</pre>
    </div>
  );
}

window.DrakonStudio = DrakonStudio;
