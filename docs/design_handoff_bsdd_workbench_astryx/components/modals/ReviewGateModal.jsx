/* =========================================================
   ReviewGateModal · HITL Φ6 Decision
   Approve & Dispatch  vs  Reject & Branch (COW Snapshot)
   ========================================================= */
function ReviewGateModal({ open, onClose, sprintState, onSubmit }) {
  const [mode, setMode] = useState('choose'); // choose | approve | reject
  const [reason, setReason] = useState('');
  const [branchName, setBranchName] = useState(`cow/sprint-${sprintState.sprintId}-${Date.now().toString(36).slice(-4)}`);
  const [rollbackDepth, setRollbackDepth] = useState(1);
  const toast = useToast();

  useEffect(() => {
    if (open) { setMode('choose'); setReason(''); }
  }, [open]);

  const fs = sprintState.fitnessSummary;

  const handleApprove = async () => {
    await window.BSDDApi.submitReview({ decision: 'approve', sprint_id: sprintState.sprintId });
    toast.push({ tone: 'success', title: 'Sprint approved', message: 'Handoff dispatched → Φ7 distillation' });
    onSubmit('approve');
    onClose();
  };
  const handleReject = async () => {
    if (reason.trim().length < 10) {
      toast.push({ tone: 'error', title: 'Rationale required', message: 'Enter at least 10 characters of rationale for the ΔC ledger' });
      return;
    }
    await window.BSDDApi.submitReview({
      decision: 'reject',
      parent_sprint_id: sprintState.sprintId,
      branch_name: branchName,
      reason,
      rollback_depth: rollbackDepth,
    });
    toast.push({ tone: 'error', title: 'Reject & Branch executed', message: `COW snapshot → ${branchName}` });
    onSubmit('reject', { reason, branchName, rollbackDepth });
    onClose();
  };

  return (
    <Dialog
      open={open} onClose={onClose}
      title="Human Review Gate · Φ6 Decision"
      width={960} height={640}
      headerRight={<Badge tone="amber">BLOCKING · SPRINT {sprintState.sprintId.split('-').slice(-2).join('-')}</Badge>}
    >
      {mode === 'choose' && (
        <div className="row" style={{ height: '100%' }}>
          {/* Approve column */}
          <div
            className="col flex-1"
            style={{ padding: 24, borderRight: '1px solid var(--color-border-hair)', gap: 16, cursor: 'pointer' }}
            onClick={() => setMode('approve')}
          >
            <div className="row gap-3">
              <div style={{ width: 40, height: 40, background: 'var(--color-emerald-glow)', border: '1px solid var(--color-emerald)', display: 'grid', placeItems: 'center', color: 'var(--color-emerald)' }}>
                {Icons.check}
              </div>
              <div className="col" style={{ gap: 2 }}>
                <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--color-emerald)' }}>Затвердити та підписати</div>
                <div style={{ fontSize: 11.5, color: 'var(--color-fg-secondary)' }}>Approve &amp; Dispatch to Φ7 Distillation</div>
              </div>
            </div>
            <div className="col gap-2">
              <div className="text-eyebrow">FITNESS GATES</div>
              <FitnessRow label="Unit tests" value={`${fs.passed}/${fs.total}`} pass/>
              <FitnessRow label="AST isolation" value={`${fs.astIsolationScore}%`} pass/>
              <FitnessRow label="Coverage" value={`${fs.coverage}%`} pass/>
              <FitnessRow label="Latency" value={`${fs.latencyMs}ms`} pass/>
              <FitnessRow label="Token budget" value={`${fs.tokenCount}/500w`} pass={fs.tokenCount <= 500}/>
            </div>
            <div className="mono select-text" style={{ fontSize: 10.5, color: 'var(--color-fg-secondary)', background: 'var(--color-bg-canvas)', padding: 10, border: '1px solid var(--color-border-hair)', whiteSpace: 'pre-wrap', flex: 1, overflow: 'auto' }}>
              {sprintState.handoffPayload?.markdown_preview}
            </div>
            <Button variant="success" size="lg" onClick={handleApprove} icon={Icons.check} style={{ justifyContent: 'center' }}>
              Затвердити (⌘⏎)
            </Button>
          </div>

          {/* Reject column */}
          <div
            className="col flex-1"
            style={{ padding: 24, gap: 16, cursor: 'pointer' }}
            onClick={() => setMode('reject')}
          >
            <div className="row gap-3">
              <div style={{ width: 40, height: 40, background: 'var(--color-rose-glow)', border: '1px solid var(--color-rose)', display: 'grid', placeItems: 'center', color: 'var(--color-rose)' }}>
                {Icons.branch}
              </div>
              <div className="col" style={{ gap: 2 }}>
                <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--color-rose)' }}>Відхилити та створити гілку</div>
                <div style={{ fontSize: 11.5, color: 'var(--color-fg-secondary)' }}>Reject &amp; Branch · COW Snapshot Protocol</div>
              </div>
            </div>
            <div className="col gap-2">
              <div className="text-eyebrow">COW SNAPSHOT PROTOCOL</div>
              <ol className="col gap-1" style={{ fontSize: 11, color: 'var(--color-fg-secondary)', lineHeight: 1.5 }}>
                <li>1. Immutable copy-on-write branch created from current sprint state</li>
                <li>2. Rationale committed to ΔC negative-invariant ledger</li>
                <li>3. Rollback depth={rollbackDepth} sprint(s) restored to Φ1</li>
                <li>4. Handoff engine emits new next_sprint.md with ΔC constraints</li>
                <li>5. Next sprint auto-launches with updated invariant set</li>
              </ol>
              <Banner tone="warn">
                <span className="mono" style={{ fontSize: 10 }}>ADR-008-INV-03 · ADR-007-INV-01</span> — this action creates an immutable audit record.
              </Banner>
            </div>
            <Button variant="destructive" size="lg" onClick={() => setMode('reject')} icon={Icons.branch} style={{ justifyContent: 'center' }}>
              Продовжити (⇧R)
            </Button>
          </div>
        </div>
      )}

      {mode === 'reject' && (
        <div className="col" style={{ padding: 24, gap: 12, height: '100%' }}>
          <div className="row gap-3">
            <button className="btn btn--ghost btn--sm" onClick={() => setMode('choose')}>← Back</button>
            <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--color-rose)' }}>Reject &amp; Branch · Configure COW Snapshot</div>
          </div>
          <div className="col gap-1">
            <label className="text-eyebrow">Branch Name</label>
            <input type="text" value={branchName} onChange={(e) => setBranchName(e.target.value)} className="input mono" />
          </div>
          <div className="col gap-1">
            <label className="text-eyebrow">Rollback Depth (sprints)</label>
            <Selector
              value={String(rollbackDepth)}
              onChange={(v) => setRollbackDepth(parseInt(v, 10))}
              options={[{ value: '1', label: '1 sprint (this one)' }, { value: '2', label: '2 sprints' }, { value: '3', label: '3 sprints' }]}
            />
          </div>
          <div className="col gap-1 flex-1" style={{ minHeight: 0 }}>
            <label className="text-eyebrow">Rejection Rationale (ΔC ledger)</label>
            <textarea
              value={reason} onChange={(e) => setReason(e.target.value)}
              placeholder="Explain why this sprint's output must be rejected. This text is committed immutably to the ΔC negative-invariant ledger and will constrain future sprints."
              className="textarea flex-1"
              style={{ resize: 'none', minHeight: 120 }}
            />
            <div className="mono" style={{ fontSize: 10, color: reason.length < 10 ? 'var(--color-rose)' : 'var(--color-fg-muted)' }}>
              {reason.length}/10 minimum characters
            </div>
          </div>
          <div className="row gap-2" style={{ justifyContent: 'flex-end' }}>
            <Button onClick={() => setMode('choose')}>Cancel</Button>
            <Button variant="destructive" onClick={handleReject} icon={Icons.branch}>
              Confirm Reject &amp; Branch
            </Button>
          </div>
        </div>
      )}
    </Dialog>
  );
}

function FitnessRow({ label, value, pass }) {
  return (
    <div className="row" style={{ justifyContent: 'space-between', padding: '4px 8px', background: 'var(--color-bg-canvas)', borderLeft: `2px solid var(--color-${pass ? 'emerald' : 'rose'})` }}>
      <span style={{ fontSize: 11, color: 'var(--color-fg-secondary)' }}>{label}</span>
      <span className="mono tabnum" style={{ fontSize: 11, fontWeight: 600, color: `var(--color-${pass ? 'emerald' : 'rose'})` }}>{value} {pass ? '✓' : '✗'}</span>
    </div>
  );
}

window.ReviewGateModal = ReviewGateModal;
