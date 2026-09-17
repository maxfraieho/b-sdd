/* =========================================================
   NodeInspectorDrawer · label · severity · invariant binding
   ========================================================= */
function NodeInspectorDrawer({ open, onClose, nodeId, node, allNodes, adrs, onUpdate, onOpenAdr }) {
  const [label, setLabel] = useState('');
  const [severity, setSeverity] = useState('normal');
  const [boundInv, setBoundInv] = useState('');

  useEffect(() => {
    if (node) {
      setLabel(node.content || '');
      const m = (node.secondary || '').match(/\[([\w-]+)\]/);
      setBoundInv(m ? m[1] : '');
      setSeverity('normal');
    }
  }, [node?.nodeId, nodeId]);

  const boundAdr = adrs.find((a) => a.invariants.some((i) => i.id === boundInv));
  const allInv = adrs.flatMap((a) => a.invariants);

  if (!node) return null;

  return (
    <Drawer open={open} onClose={onClose} title="Інспектор вузла · Node Inspector" width={420}
      headerRight={<Badge tone="cyan" outline>{node.nodeId}</Badge>}
    >
      <div className="col" style={{ padding: 12, gap: 12, overflow: 'auto' }}>
        {/* Type banner */}
        <div className="row gap-2" style={{
          padding: 10,
          background: `var(--color-${nodeTone(node.type)}-glow)`,
          border: `1px solid var(--color-${nodeTone(node.type)})`,
        }}>
          <Dot tone={nodeTone(node.type)}/>
          <span className="mono" style={{ fontSize: 11, fontWeight: 700, color: `var(--color-${nodeTone(node.type)})`, textTransform: 'uppercase', letterSpacing: '0.12em' }}>
            {node.type}
          </span>
        </div>

        {/* Label edit */}
        <div className="col gap-1">
          <label className="text-eyebrow">LABEL · Мітка</label>
          <textarea
            value={label} onChange={(e) => setLabel(e.target.value)}
            className="textarea"
            style={{ minHeight: 60 }}
          />
        </div>

        {/* Severity radio */}
        <div className="col gap-1">
          <label className="text-eyebrow">Severity</label>
          <div className="row gap-1" style={{ flexWrap: 'wrap' }}>
            {['normal', 'mild', 'degraded', 'severe', 'fatal'].map((s) => {
              const tones = { normal: 'emerald', mild: 'cyan', degraded: 'amber', severe: 'amber', fatal: 'rose' };
              return (
                <button
                  key={s}
                  onClick={() => setSeverity(s)}
                  className="btn btn--sm"
                  style={{
                    borderColor: severity === s ? `var(--color-${tones[s]})` : undefined,
                    background: severity === s ? `var(--color-${tones[s]}-glow)` : undefined,
                    color: severity === s ? `var(--color-${tones[s]})` : undefined,
                  }}
                >
                  {s}
                </button>
              );
            })}
          </div>
        </div>

        {/* Invariant binding */}
        <div className="col gap-1">
          <label className="text-eyebrow">Semantic Binding · ADR Invariant</label>
          <Selector
            value={boundInv} onChange={setBoundInv}
            options={[
              { value: '', label: '— unbound —' },
              ...allInv.map((i) => ({ value: i.id, label: `${i.id} (${i.severity || 'mandatory'})` })),
            ]}
          />
          {boundAdr && (
            <button
              onClick={() => onOpenAdr(boundAdr)}
              className="col"
              style={{
                marginTop: 4,
                padding: 10,
                background: 'var(--color-bg-card)',
                border: '1px solid var(--color-cyan)',
                textAlign: 'left', cursor: 'pointer', gap: 2,
              }}
            >
              <div className="mono" style={{ fontSize: 11, fontWeight: 700, color: 'var(--color-cyan)' }}>{boundAdr.id}</div>
              <div style={{ fontSize: 11, color: 'var(--color-fg-primary)' }}>{boundAdr.title}</div>
              <div className="mono" style={{ fontSize: 10, color: 'var(--color-fg-muted)' }}>Click to open reader →</div>
            </button>
          )}
        </div>

        {/* Edges info */}
        <div className="col gap-1">
          <label className="text-eyebrow">Edges</label>
          <div className="mono" style={{ fontSize: 10.5, color: 'var(--color-fg-secondary)' }}>
            down → {node.one || '—'}<br/>
            right → {node.two || '—'}
          </div>
        </div>

        <div className="row gap-2" style={{ marginTop: 8 }}>
          <Button variant="primary" size="sm" onClick={() => {
            onUpdate({ ...node, content: label, secondary: boundInv ? `[${boundInv}]` : '' });
            onClose();
          }}>Apply changes</Button>
          <Button size="sm" onClick={onClose}>Cancel</Button>
        </div>
      </div>
    </Drawer>
  );
}

function nodeTone(type) {
  return {
    action: 'emerald',
    question: 'amber',
    end: 'rose',
    select: 'cyan',
    branch: 'violet',
    process: 'cyan',
  }[type] || 'muted';
}

window.NodeInspectorDrawer = NodeInspectorDrawer;
