/* =========================================================
   PseudocodeModal · Pythonic pseudocode + AST rules tree
   ========================================================= */
function PseudocodeModal({ open, onClose, diagram }) {
  const [tab, setTab] = useState('pseudo');
  const toast = useToast();

  const pseudo = useMemo(() => generatePseudocode(diagram), [diagram]);
  const astTree = useMemo(() => generateAstTree(diagram), [diagram]);

  const copyToClip = (text) => {
    navigator.clipboard.writeText(text);
    toast.push({ tone: 'success', title: 'Copied to clipboard', message: `${text.split('\n').length} lines` });
  };
  const download = (name, text) => {
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = name; a.click();
    URL.revokeObjectURL(url);
    toast.push({ tone: 'success', title: 'Downloaded', message: name });
  };

  const activeText = tab === 'pseudo' ? pseudo : astTree;

  return (
    <Dialog
      open={open} onClose={onClose}
      title="Псевдокод &amp; Правила · drakongen.js exporter"
      width={880} height={640}
      headerRight={
        <Segmented value={tab} onChange={setTab} options={[
          { value: 'pseudo', label: 'Algorithmic Pseudocode' },
          { value: 'ast', label: 'AST Rules Tree' },
        ]}/>
      }
      footer={
        <>
          <span className="mono" style={{ fontSize: 10.5, color: 'var(--color-fg-muted)' }}>
            Generated from {diagram.name} · {Object.keys(diagram.items).length - 1} nodes
          </span>
          <div className="row gap-2">
            <Button size="sm" icon={Icons.copy} onClick={() => copyToClip(activeText)}>Copy</Button>
            <Button size="sm" variant="primary" icon={Icons.download} onClick={() => download(tab === 'pseudo' ? 'hitl.pseudo.py' : 'hitl.ast.txt', activeText)}>
              Download
            </Button>
          </div>
        </>
      }
    >
      <pre className="mono select-text" style={{
        margin: 0, padding: 20,
        background: 'var(--color-bg-canvas)',
        color: 'var(--color-fg-primary)',
        fontSize: 12,
        lineHeight: 1.6,
        overflow: 'auto',
        height: '100%',
      }}>
        {activeText}
      </pre>
    </Dialog>
  );
}

function generatePseudocode(diagram) {
  const items = diagram.items;
  const lines = [`# ${diagram.name}`, `# params: ${diagram.params || 'none'}`, ''];
  lines.push(`def hitl_pipeline(${diagram.params || ''}):`);
  const walked = new Set();
  const walk = (nodeId, depth = 1) => {
    if (!nodeId || walked.has(nodeId) || !items[nodeId]) return;
    walked.add(nodeId);
    const it = items[nodeId];
    const pad = '    '.repeat(depth);
    if (it.type === 'branch') {
      lines.push(`${pad}# --- branch: ${it.content} ---`);
      walk(it.one, depth);
    } else if (it.type === 'question') {
      lines.push(`${pad}if ${it.content.replace(/\?$/, '')}:  ${it.secondary || ''}`);
      walk(it.one, depth + 1);
      lines.push(`${pad}else:`);
      walk(it.two, depth + 1);
    } else if (it.type === 'action') {
      lines.push(`${pad}${it.content.replace(/^Phase \d+: /, '')}()  ${it.secondary || ''}`);
      walk(it.one, depth);
    } else if (it.type === 'end') {
      lines.push(`${pad}return  # ${it.content}`);
    } else {
      lines.push(`${pad}# [${it.type}] ${it.content}`);
      walk(it.one, depth);
    }
  };
  const entry = items.b0 ? items.b0.one : Object.keys(items)[0];
  walk(entry);
  return lines.join('\n');
}

function generateAstTree(diagram) {
  const items = diagram.items;
  const lines = [`AST · ${diagram.name}`, '│'];
  const walked = new Set();
  const walk = (nodeId, prefix = '', isLast = true) => {
    if (!nodeId || walked.has(nodeId) || !items[nodeId]) return;
    walked.add(nodeId);
    const it = items[nodeId];
    const branch = isLast ? '└── ' : '├── ';
    lines.push(`${prefix}${branch}${it.type}: ${it.content} ${it.secondary || ''}`);
    const nextPrefix = prefix + (isLast ? '    ' : '│   ');
    const kids = [];
    if (it.one) kids.push({ id: it.one, edge: 'down' });
    if (it.two) kids.push({ id: it.two, edge: 'right(no)' });
    kids.forEach((k, i) => {
      lines.push(`${nextPrefix}│  [edge: ${k.edge}]`);
      walk(k.id, nextPrefix, i === kids.length - 1);
    });
  };
  const entry = items.b0 ? items.b0.one : Object.keys(items)[0];
  walk(entry);
  return lines.join('\n');
}

window.PseudocodeModal = PseudocodeModal;
