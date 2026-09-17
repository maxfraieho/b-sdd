/* =========================================================
   AdrReaderModal · dual-mode Preview / Editor + Ctrl+S save
   Persists to /api/adrs/save (with mock fallback).
   ========================================================= */
function AdrReaderModal({ open, adr, onClose, onSaved }) {
  const [mode, setMode] = useState('preview');
  const [content, setContent] = useState('');
  const [saving, setSaving] = useState(false);
  const [dirty, setDirty] = useState(false);
  const toast = useToast();

  useEffect(() => {
    if (adr) {
      setContent(window.BSDD.ADR_CONTENT[adr.id] || '# (no content)');
      setDirty(false);
      setMode('preview');
    }
  }, [adr?.id]);

  const stats = useMemo(() => {
    const lines = content.split('\n').length;
    const words = (content.match(/\S+/g) || []).length;
    const chars = content.length;
    return { lines, words, chars };
  }, [content]);

  const doSave = useCallback(async () => {
    if (!adr) return;
    setSaving(true);
    try {
      await window.BSDDApi.saveAdr(adr.file_path, content);
      setDirty(false);
      toast.push({ tone: 'success', title: 'ADR saved', message: `${adr.id} → recompiled active_rules.md` });
      onSaved && onSaved(adr, content);
    } finally {
      setSaving(false);
    }
  }, [adr, content, onSaved]);

  // Ctrl+S / ⌘+S
  useEffect(() => {
    if (!open) return;
    const h = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') {
        e.preventDefault();
        doSave();
      }
    };
    window.addEventListener('keydown', h);
    return () => window.removeEventListener('keydown', h);
  }, [open, doSave]);

  if (!adr) return null;

  return (
    <Dialog
      open={open} onClose={onClose}
      title={`${adr.id} · ${adr.title}`}
      width={1080} height={720}
      headerRight={
        <div className="row gap-2">
          <Badge tone={adr.status === 'accepted' ? 'emerald' : 'amber'}>{adr.status}</Badge>
          <Badge tone="cyan" outline>{adr.component}</Badge>
        </div>
      }
      footer={
        <>
          <div className="row gap-3">
            <span className="mono" style={{ fontSize: 10.5, color: 'var(--color-fg-muted)' }}>{adr.file_path}</span>
            <span className="mono tabnum" style={{ fontSize: 10.5, color: 'var(--color-fg-secondary)' }}>{stats.lines} lines · {stats.words} words · {stats.chars} chars</span>
            {dirty && <Badge tone="amber">unsaved changes</Badge>}
          </div>
          <div className="row gap-2">
            <Segmented value={mode} onChange={setMode} options={[
              { value: 'preview', label: 'Preview' },
              { value: 'editor', label: 'Editor' },
            ]}/>
            <Button variant="primary" size="sm" icon={saving ? Icons.spin : Icons.save} onClick={doSave} disabled={!dirty || saving}>
              Зберегти (⌘S)
            </Button>
          </div>
        </>
      }
    >
      <div className="row" style={{ height: '100%' }}>
        {/* Left: content */}
        <div className="col flex-1" style={{ minWidth: 0, borderRight: '1px solid var(--color-border-hair)' }}>
          {mode === 'preview' ? (
            <div style={{ padding: 24, overflow: 'auto', flex: 1 }}>
              <MarkdownPreview text={content} />
            </div>
          ) : (
            <textarea
              value={content}
              onChange={(e) => { setContent(e.target.value); setDirty(true); }}
              className="mono select-text"
              style={{
                flex: 1, padding: 16,
                background: 'var(--color-bg-canvas)',
                border: 'none',
                color: 'var(--color-fg-primary)',
                fontSize: 12,
                lineHeight: 1.6,
                resize: 'none',
                outline: 'none',
              }}
            />
          )}
        </div>
        {/* Right: invariants panel */}
        <div className="col shrink-0" style={{ width: 300, padding: 16, gap: 10, overflow: 'auto' }}>
          <div className="text-eyebrow">INVARIANTS ({adr.invariants.length})</div>
          {adr.invariants.map((inv) => (
            <div key={inv.id} className="col" style={{ padding: 10, background: 'var(--color-bg-card)', border: '1px solid var(--color-border-hair)', borderLeft: `3px solid var(--color-${sevTone(inv.severity)})`, gap: 4 }}>
              <div className="row" style={{ justifyContent: 'space-between' }}>
                <span className="mono" style={{ fontSize: 10.5, fontWeight: 700, color: `var(--color-${sevTone(inv.severity)})` }}>{inv.id}</span>
                <Badge tone={sevTone(inv.severity)}>{inv.severity}</Badge>
              </div>
              <div style={{ fontSize: 11, color: 'var(--color-fg-secondary)', lineHeight: 1.4 }}>{inv.statement}</div>
            </div>
          ))}
          <div className="text-eyebrow" style={{ marginTop: 8 }}>BITEMPORAL METADATA</div>
          <div className="col" style={{ background: 'var(--color-bg-card)', border: '1px solid var(--color-border-hair)', padding: 10, gap: 4, fontSize: 11 }}>
            <MetaRow label="valid_from" value={adr.valid_from}/>
            <MetaRow label="valid_to" value={adr.valid_to || '∞ current'}/>
            <MetaRow label="tx_time" value={adr.tx_time}/>
            <MetaRow label="supersedes" value={adr.supersedes || '—'}/>
            <MetaRow label="superseded_by" value={adr.superseded_by || '—'}/>
          </div>
        </div>
      </div>
    </Dialog>
  );
}

function sevTone(s) { return s === 'critical' ? 'rose' : s === 'mandatory' ? 'amber' : 'cyan'; }
function MetaRow({ label, value }) {
  return (
    <div className="row" style={{ justifyContent: 'space-between' }}>
      <span className="mono" style={{ color: 'var(--color-fg-muted)' }}>{label}</span>
      <span className="mono tabnum" style={{ color: 'var(--color-fg-primary)' }}>{value}</span>
    </div>
  );
}

// Minimal Markdown renderer (headings, bold, code, invariant badges)
function MarkdownPreview({ text }) {
  const html = useMemo(() => {
    if (!text) return '';
    let out = text
      // escape
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      // code fences
      .replace(/```([\s\S]*?)```/g, (_, code) => `<pre class="md-code">${code}</pre>`)
      // headers
      .replace(/^###### (.*)$/gm, '<h6>$1</h6>')
      .replace(/^##### (.*)$/gm, '<h5>$1</h5>')
      .replace(/^#### (.*)$/gm, '<h4>$1</h4>')
      .replace(/^### (.*)$/gm, '<h3>$1</h3>')
      .replace(/^## (.*)$/gm, '<h2>$1</h2>')
      .replace(/^# (.*)$/gm, '<h1>$1</h1>')
      // bold + italic
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      // inline code
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      // invariant IDs → badge
      .replace(/\b(ADR-\d+-INV-\d+)\b/g, '<span class="md-invariant">$1</span>')
      // bullet lists
      .replace(/^- (.*)$/gm, '<li>$1</li>')
      // paragraphs (double newline → </p><p>)
      .replace(/\n\n+/g, '</p><p>');
    return '<p>' + out + '</p>';
  }, [text]);
  return (
    <>
      <div className="md-view select-text" dangerouslySetInnerHTML={{ __html: html }} />
      <style>{`
        .md-view { color: var(--color-fg-primary); font-size: 13px; line-height: 1.7; max-width: 720px; }
        .md-view h1 { font-size: 20px; font-weight: 700; margin: 24px 0 12px; color: var(--color-fg-primary); border-bottom: 1px solid var(--color-border-hair); padding-bottom: 6px; }
        .md-view h2 { font-size: 15px; font-weight: 700; margin: 20px 0 8px; color: var(--color-amber); letter-spacing: 0.02em; text-transform: uppercase; }
        .md-view h3 { font-size: 13px; font-weight: 600; margin: 14px 0 6px; color: var(--color-fg-primary); }
        .md-view p { margin: 8px 0; }
        .md-view code { font-family: var(--font-mono); font-size: 0.9em; background: var(--color-bg-elevated); padding: 1px 5px; border-radius: 2px; color: var(--color-cyan); }
        .md-view pre.md-code { font-family: var(--font-mono); background: var(--color-bg-canvas); border: 1px solid var(--color-border-hair); border-left: 3px solid var(--color-amber); padding: 12px; font-size: 11.5px; line-height: 1.55; overflow-x: auto; margin: 12px 0; white-space: pre; }
        .md-view li { margin: 4px 0 4px 24px; }
        .md-view strong { color: var(--color-fg-primary); font-weight: 700; }
        .md-view em { color: var(--color-fg-secondary); font-style: italic; }
        .md-invariant { display: inline-block; font-family: var(--font-mono); font-size: 10.5px; padding: 1px 6px; margin: 0 2px; background: var(--color-cyan-glow); color: var(--color-cyan); border: 1px solid var(--color-cyan); border-radius: 2px; letter-spacing: 0.04em; }
      `}</style>
    </>
  );
}

window.AdrReaderModal = AdrReaderModal;
