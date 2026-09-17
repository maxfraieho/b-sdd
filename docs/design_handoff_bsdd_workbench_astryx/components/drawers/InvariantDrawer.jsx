/* =========================================================
   InvariantDrawer · filterable list of active invariants
   with severity chips + DAG supersession
   ========================================================= */
function InvariantDrawer({ open, onClose, adrs, onSelectInvariant }) {
  const [severity, setSeverity] = useState('all');
  const [query, setQuery] = useState('');

  const allInv = adrs.flatMap((a) => a.invariants.map((inv) => ({ ...inv, adr: a })));
  const filtered = allInv.filter((i) => {
    if (severity !== 'all' && (i.severity || 'mandatory') !== severity) return false;
    if (!query) return true;
    const q = query.toLowerCase();
    return i.id.toLowerCase().includes(q) || i.statement.toLowerCase().includes(q);
  });

  const bySeverity = { critical: 0, mandatory: 0, recommended: 0 };
  allInv.forEach((i) => { bySeverity[i.severity || 'mandatory']++; });

  return (
    <Drawer open={open} onClose={onClose} title="Активні інваріанти · Bitemporal Rules" width={480}
      headerRight={<Badge tone="cyan" outline>{filtered.length} / {allInv.length}</Badge>}
    >
      <div className="col" style={{ padding: 12, gap: 10, overflow: 'auto' }}>
        {/* Summary chips */}
        <div className="row gap-2">
          <SummaryChip tone="rose" label="critical" value={bySeverity.critical}/>
          <SummaryChip tone="amber" label="mandatory" value={bySeverity.mandatory}/>
          <SummaryChip tone="cyan" label="recommended" value={bySeverity.recommended}/>
        </div>

        {/* Filters */}
        <div className="col gap-2">
          <input
            placeholder="Filter invariants…"
            value={query} onChange={(e) => setQuery(e.target.value)}
            className="input"
          />
          <div className="row gap-1">
            {['all', 'critical', 'mandatory', 'recommended'].map((s) => (
              <button
                key={s}
                onClick={() => setSeverity(s)}
                className="btn btn--sm"
                style={{
                  borderColor: severity === s ? `var(--color-${s === 'all' ? 'amber' : s === 'critical' ? 'rose' : s === 'mandatory' ? 'amber' : 'cyan'})` : undefined,
                  background: severity === s ? `var(--color-${s === 'all' ? 'amber' : s === 'critical' ? 'rose' : s === 'mandatory' ? 'amber' : 'cyan'}-glow)` : undefined,
                }}
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        {/* List */}
        <div className="col gap-2">
          {filtered.map((i) => {
            const tone = i.severity === 'critical' ? 'rose' : i.severity === 'recommended' ? 'cyan' : 'amber';
            return (
              <button
                key={i.id}
                onClick={() => onSelectInvariant(i.id)}
                className="col"
                style={{
                  padding: 10,
                  background: 'var(--color-bg-card)',
                  border: '1px solid var(--color-border-hair)',
                  borderLeft: `3px solid var(--color-${tone})`,
                  gap: 4, textAlign: 'left', cursor: 'pointer',
                }}
              >
                <div className="row" style={{ justifyContent: 'space-between' }}>
                  <span className="mono" style={{ fontSize: 11, fontWeight: 700, color: `var(--color-${tone})` }}>{i.id}</span>
                  <Badge tone={tone}>{i.severity || 'mandatory'}</Badge>
                </div>
                <div style={{ fontSize: 11.5, color: 'var(--color-fg-secondary)', lineHeight: 1.45 }}>{i.statement}</div>
                <div className="row gap-2" style={{ marginTop: 4 }}>
                  <Badge tone="cyan" outline>{i.adr.id}</Badge>
                  <span className="mono" style={{ fontSize: 10, color: 'var(--color-fg-muted)' }}>
                    T_v {i.adr.valid_from.slice(0, 10)} → {i.adr.valid_to || '∞'}
                  </span>
                  {i.adr.supersedes && (
                    <span className="mono" style={{ fontSize: 10, color: 'var(--color-fg-faint)' }}>
                      supersedes {i.adr.supersedes}
                    </span>
                  )}
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </Drawer>
  );
}

function SummaryChip({ tone, label, value }) {
  return (
    <div className="col flex-1" style={{
      padding: 8,
      background: 'var(--color-bg-card)',
      border: `1px solid var(--color-border-hair)`,
      borderTop: `2px solid var(--color-${tone})`,
      gap: 2,
    }}>
      <div className="text-eyebrow" style={{ fontSize: 8.5 }}>{label}</div>
      <div className="mono tabnum" style={{ fontSize: 16, fontWeight: 700, color: `var(--color-${tone})` }}>{value}</div>
    </div>
  );
}

window.InvariantDrawer = InvariantDrawer;
