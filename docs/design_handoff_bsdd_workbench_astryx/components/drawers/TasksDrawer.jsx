/* =========================================================
   TasksDrawer · spec checklist with interactive toggle
   ========================================================= */
function TasksDrawer({ open, onClose, specs, selectedSpecId, onSelectSpec, onToggleTask }) {
  const spec = specs.find((s) => s.id === selectedSpecId) || specs[0];
  if (!spec) return null;

  return (
    <Drawer open={open} onClose={onClose} title="Завдання спринту · Sprint Tasks" width={480}
      headerRight={
        <Badge tone={spec.percent === 100 ? 'emerald' : 'amber'}>{spec.completed_count}/{spec.tasks_count} · {spec.percent}%</Badge>
      }
    >
      <div className="col" style={{ padding: 12, gap: 10, overflow: 'auto' }}>
        {/* Spec picker */}
        <Selector
          value={selectedSpecId}
          onChange={onSelectSpec}
          options={specs.map((s) => ({ value: s.id, label: `${s.id.split('-')[0]} · ${s.title.replace(/^Spec \d+ · /, '')}` }))}
        />

        <div style={{ padding: 10, background: 'var(--color-bg-card)', border: '1px solid var(--color-border-hair)' }}>
          <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 4 }}>{spec.title}</div>
          <div className="mono" style={{ fontSize: 10, color: 'var(--color-fg-muted)' }}>{spec.path}</div>
        </div>

        {/* Task rows */}
        <div className="col" style={{ gap: 4 }}>
          {(spec.tasks || []).map((t) => (
            <TaskRow key={t.id} task={t} onToggle={(c) => onToggleTask(spec.id, t.id, c)} />
          ))}
          {(!spec.tasks || spec.tasks.length === 0) && (
            <div className="mono" style={{ fontSize: 11, color: 'var(--color-fg-muted)', padding: 12 }}>
              No task list available for this spec.
            </div>
          )}
        </div>
      </div>
    </Drawer>
  );
}

function TaskRow({ task, onToggle }) {
  const [checked, setChecked] = useState(task.completed);
  return (
    <label
      className="row gap-3"
      style={{
        padding: '8px 10px',
        background: checked ? 'var(--color-emerald-glow)' : 'var(--color-bg-card)',
        border: '1px solid var(--color-border-hair)',
        borderLeft: `3px solid ${checked ? 'var(--color-emerald)' : 'var(--color-fg-faint)'}`,
        cursor: 'pointer',
      }}
    >
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => { setChecked(e.target.checked); onToggle(e.target.checked); }}
        style={{ marginTop: 2, accentColor: 'var(--color-emerald)' }}
      />
      <div className="col" style={{ gap: 2, flex: 1, minWidth: 0 }}>
        <div className="row gap-2">
          <span className="mono" style={{ fontSize: 10, color: 'var(--color-fg-muted)' }}>{task.id}</span>
          {checked && <Badge tone="emerald">done</Badge>}
        </div>
        <div style={{ fontSize: 11.5, textDecoration: checked ? 'line-through' : 'none', color: checked ? 'var(--color-fg-muted)' : 'var(--color-fg-primary)' }}>
          {task.title}
        </div>
      </div>
    </label>
  );
}

window.TasksDrawer = TasksDrawer;
