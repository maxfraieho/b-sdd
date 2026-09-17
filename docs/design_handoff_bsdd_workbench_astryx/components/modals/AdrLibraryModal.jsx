/* =========================================================
   AdrLibraryModal · searchable ADR library with timeline tags
   ========================================================= */
function AdrLibraryModal({ open, onClose, adrs, onOpen }) {
  const [query, setQuery] = useState('');
  const [component, setComponent] = useState('all');

  const components = Array.from(new Set(adrs.map((a) => a.component)));
  const filtered = adrs.filter((a) => {
    if (component !== 'all' && a.component !== component) return false;
    if (!query) return true;
    const q = query.toLowerCase();
    return a.id.toLowerCase().includes(q) || a.title.toLowerCase().includes(q) || (a.decision_outcome || '').toLowerCase().includes(q);
  });

  return (
    <Dialog
      open={open} onClose={onClose}
      title="Бібліотека ADR · Architecture Decision Records"
      width={860} height={640}
      headerRight={<Badge tone="cyan" outline>{filtered.length} / {adrs.length}</Badge>}
    >
      <div className="col" style={{ height: '100%' }}>
        {/* Filter bar */}
        <div className="row shrink-0" style={{ padding: '10px 16px', borderBottom: '1px solid var(--color-border-hair)', gap: 10 }}>
          <div className="row gap-2 flex-1" style={{ maxWidth: 420 }}>
            <div className="row gap-2" style={{
              flex: 1,
              background: 'var(--color-bg-canvas)',
              border: '1px solid var(--color-border-hair)',
              padding: '0 8px', height: 28,
            }}>
              {Icons.search}
              <input
                placeholder="Search by ID, title, decision…"
                value={query} onChange={(e) => setQuery(e.target.value)}
                style={{ flex: 1, background: 'transparent', border: 'none', color: 'var(--color-fg-primary)', fontSize: 12 }}
              />
            </div>
          </div>
          <Selector
            value={component} onChange={setComponent}
            options={[{ value: 'all', label: 'All components' }, ...components.map((c) => ({ value: c, label: c }))]}
          />
        </div>

        {/* Rows */}
        <div className="col flex-1" style={{ overflow: 'auto' }}>
          {filtered.map((a) => (
            <button
              key={a.id}
              onClick={() => onOpen(a)}
              className="row gap-3"
              style={{
                padding: '10px 16px',
                borderBottom: '1px solid var(--color-border-hair)',
                textAlign: 'left',
                cursor: 'pointer',
                background: 'transparent',
                transition: 'background 100ms',
              }}
              onMouseEnter={(e) => e.currentTarget.style.background = 'var(--color-bg-hover)'}
              onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
            >
              <div className="mono" style={{ width: 76, fontSize: 12, fontWeight: 700, color: 'var(--color-amber)' }}>{a.id}</div>
              <div className="col flex-1" style={{ gap: 2, minWidth: 0 }}>
                <div style={{ fontSize: 12.5, fontWeight: 600 }}>{a.title}</div>
                <div style={{ fontSize: 11, color: 'var(--color-fg-secondary)' }} className="truncate">{a.decision_outcome}</div>
              </div>
              <div className="col" style={{ alignItems: 'flex-end', gap: 3, minWidth: 130 }}>
                <div className="row gap-1">
                  <Badge tone="emerald">{a.status}</Badge>
                  <Badge tone="cyan" outline>{a.component}</Badge>
                </div>
                <div className="mono tabnum" style={{ fontSize: 10, color: 'var(--color-fg-muted)' }}>
                  T_v {a.valid_from.slice(0, 10)} · {a.invariants.length} inv
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>
    </Dialog>
  );
}

window.AdrLibraryModal = AdrLibraryModal;
