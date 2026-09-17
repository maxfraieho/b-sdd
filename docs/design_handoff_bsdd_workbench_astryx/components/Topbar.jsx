/* =========================================================
   Zone 1 · Topbar (48px)
   Astryx TopNav shape · Brand · Spec selector ·
   Sovereign node indicators · Sync button · Action triggers
   ========================================================= */
function Topbar(props) {
  const {
    project, specs, selectedSpecId, onSelectSpec,
    health, invariantCount, taskProgress,
    onOpenTasks, onOpenAdrLibrary, onOpenInvariants,
    onSyncUtopia, syncing,
  } = props;

  const utopiaOnline = health?.utopia_db?.status === 'online';
  const llmOnline    = health?.llm_gateway?.status === 'online';
  const astOnline    = health?.gitnexus_ast?.status === 'online';
  const utopiaLatency = health?.utopia_db?.latency_ms ?? 1.2;
  const llmSlots      = health?.llm_gateway?.slots_available ?? 0;

  return (
    <header
      className="row shrink-0"
      style={{
        height: 'var(--h-topbar)',
        background: 'var(--color-bg-panel)',
        borderBottom: '1px solid var(--color-border-hair)',
        paddingLeft: 12, paddingRight: 12,
        gap: 16,
      }}
    >
      {/* Brand */}
      <div className="row gap-3 shrink-0">
        <div style={{
          width: 28, height: 28, borderRadius: 3,
          background: 'linear-gradient(135deg,#f59e0b 0%,#78350f 100%)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: 13,
          color: '#0b0f16',
        }}>B</div>
        <div className="col" style={{ gap: 0, lineHeight: 1.1 }}>
          <div style={{ fontSize: 12.5, fontWeight: 700, letterSpacing: '0.02em' }}>
            B-SDD WORKBENCH <span style={{ color: 'var(--color-fg-muted)', fontWeight: 500 }}>· ASTRYX EDITION</span>
          </div>
          <div className="mono" style={{ fontSize: 9.5, color: 'var(--color-fg-muted)', letterSpacing: '0.06em' }}>
            v2.4.0 · {project?.name || 'B-SDD'} · <span style={{ color: 'var(--color-emerald)' }}>{project?.branch || 'main'}</span> @{project?.commit?.slice(0,7) || '—'}
          </div>
        </div>
      </div>

      <div className="divider-v" />

      {/* Spec selector */}
      <div className="row gap-2 shrink-0">
        <span className="text-eyebrow">SPEC</span>
        <Selector
          value={selectedSpecId}
          onChange={onSelectSpec}
          options={(specs || []).map((s) => ({ value: s.id, label: `${s.id.split('-')[0]} · ${s.title.replace(/^Spec \d+ · /,'')}` }))}
          style={{ minWidth: 240 }}
        />
      </div>

      <div className="divider-v" />

      {/* Sovereign nodes */}
      <div className="row gap-4 shrink-0">
        <span className="text-eyebrow">SOVEREIGN VPC</span>
        <NodeIndicator label="Utopia DB" host="192.168.3.251:9922" online={utopiaOnline} value={`${utopiaLatency}ms`} tone="emerald"/>
        <NodeIndicator label="LLM Gateway" host="192.168.3.184:18880" online={llmOnline} value={`${llmSlots} slots`} tone="cyan"/>
        <NodeIndicator label="GitNexus AST" host=":4747" online={astOnline} value="idx" tone="cyan"/>
        <Button size="sm" variant="secondary" icon={syncing ? Icons.spin : Icons.sync} onClick={onSyncUtopia} disabled={syncing}>
          {syncing ? 'Синхронізація…' : 'Синхронізувати'}
        </Button>
      </div>

      <div className="grow" />

      {/* Action triggers */}
      <div className="row gap-2 shrink-0">
        <Button size="sm" icon={Icons.check} onClick={onOpenTasks}>
          Завдання
          <Badge tone={taskProgress?.completed === taskProgress?.total ? 'emerald' : 'amber'} outline style={{ marginLeft: 6 }}>
            {taskProgress?.completed}/{taskProgress?.total}
          </Badge>
        </Button>
        <Button size="sm" icon={Icons.book} onClick={onOpenAdrLibrary}>
          Бібліотека ADR
        </Button>
        <Button size="sm" icon={Icons.shield} onClick={onOpenInvariants}>
          Інваріанти
          <Badge tone="amber" outline style={{ marginLeft: 6 }}>{invariantCount}</Badge>
        </Button>
      </div>

      <div className="divider-v" />

      {/* Operator badge */}
      <div className="row gap-2 shrink-0" title="Head Architect">
        <div style={{
          width: 24, height: 24, borderRadius: 2,
          background: 'var(--color-bg-elevated)',
          border: '1px solid var(--color-amber)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontFamily: 'var(--font-mono)', fontSize: 10, fontWeight: 700,
          color: 'var(--color-amber)',
        }}>VK</div>
        <div className="col" style={{ gap: 0, lineHeight: 1.1 }}>
          <div style={{ fontSize: 11, fontWeight: 600 }}>Volodymyr K.</div>
          <div className="mono" style={{ fontSize: 9, color: 'var(--color-fg-muted)' }}>Head Architect</div>
        </div>
      </div>
    </header>
  );
}

function NodeIndicator({ label, host, online, value, tone }) {
  return (
    <div className="row gap-2 shrink-0" title={host} style={{ whiteSpace: 'nowrap' }}>
      <Dot tone={online ? tone : 'rose'} pulse={online} />
      <div className="col" style={{ gap: 0, lineHeight: 1.1 }}>
        <div style={{ fontSize: 10.5, fontWeight: 600, color: 'var(--color-fg-primary)', whiteSpace: 'nowrap' }}>{label}</div>
        <div className="mono tabnum" style={{ fontSize: 9.5, color: online ? `var(--color-${tone})` : 'var(--color-rose)', whiteSpace: 'nowrap' }}>{online ? value : 'OFFLINE'}</div>
      </div>
    </div>
  );
}

window.Topbar = Topbar;
