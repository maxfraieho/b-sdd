/* =========================================================
   Astryx primitives (facebook/astryx shape)
   Button, IconButton, Badge, Dot, Banner, Selector, Tag,
   Toast, Segmented, ClientOnly
   ========================================================= */
const { useState, useEffect, useRef, useCallback, useMemo } = React;

function cx(...args) {
  return args.filter(Boolean).join(' ');
}

// --- Astryx <Button> ---
function Button({ variant = 'secondary', size = 'md', icon, iconRight, children, className, ...rest }) {
  const cls = cx(
    'btn',
    variant === 'primary' && 'btn--primary',
    variant === 'success' && 'btn--success',
    variant === 'destructive' && 'btn--destructive',
    variant === 'ghost' && 'btn--ghost',
    size === 'sm' && 'btn--sm',
    size === 'lg' && 'btn--lg',
    size === 'xl' && 'btn--xl',
    className
  );
  return (
    <button className={cls} {...rest}>
      {icon && <span className="btn__icon" aria-hidden>{icon}</span>}
      {children && <span>{children}</span>}
      {iconRight && <span className="btn__icon" aria-hidden>{iconRight}</span>}
    </button>
  );
}

// --- Astryx <IconButton> ---
function IconButton({ variant = 'ghost', size = 'md', title, children, className, ...rest }) {
  return (
    <button
      title={title}
      aria-label={title}
      className={cx('btn btn--icon', variant === 'ghost' && 'btn--ghost', size === 'sm' && 'btn--sm', className)}
      {...rest}
    >
      {children}
    </button>
  );
}

// --- Astryx <Badge> ---
function Badge({ tone = 'neutral', outline, children, className, ...rest }) {
  const cls = cx('badge', `badge--${tone}`, outline && 'badge--outline', className);
  return <span className={cls} {...rest}>{children}</span>;
}

// --- Status dot ---
function Dot({ tone = 'emerald', pulse, className }) {
  return <span className={cx('dot', `dot--${tone}`, pulse && 'dot--pulse', className)} />;
}

// --- Astryx <Banner> ---
function Banner({ tone = 'info', icon, children, action }) {
  return (
    <div className={cx('banner', `banner--${tone}`)}>
      {icon && <span aria-hidden>{icon}</span>}
      <div className="flex-1">{children}</div>
      {action}
    </div>
  );
}

// --- Astryx <Selector> (styled native select) ---
function Selector({ value, onChange, options, className, ...rest }) {
  return (
    <select
      value={value}
      onChange={(e) => onChange && onChange(e.target.value)}
      className={cx('selector', className)}
      {...rest}
    >
      {options.map((opt) =>
        typeof opt === 'string'
          ? <option key={opt} value={opt}>{opt}</option>
          : <option key={opt.value} value={opt.value}>{opt.label}</option>
      )}
    </select>
  );
}

// --- Astryx <Segmented> ---
function Segmented({ value, onChange, options }) {
  return (
    <div className="segmented" role="tablist">
      {options.map((opt) => (
        <button
          key={opt.value}
          role="tab"
          aria-pressed={value === opt.value}
          onClick={() => onChange(opt.value)}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}

// --- <ClientOnly> (SSR-safe boundary — mirrors real app contract) ---
function ClientOnly({ children, fallback = null }) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  return mounted ? children : fallback;
}

// --- Astryx <Dialog> ---
function Dialog({ open, onClose, title, width = 720, height, footer, children, headerRight }) {
  useEffect(() => {
    if (!open) return;
    const h = (e) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', h);
    return () => window.removeEventListener('keydown', h);
  }, [open, onClose]);
  if (!open) return null;
  return (
    <div className="modal-backdrop" onMouseDown={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div className="modal" style={{ width, height, maxWidth: '96vw', maxHeight: '92vh' }}>
        <div className="modal-header">
          <h2>{title}</h2>
          <div className="row gap-2">
            {headerRight}
            <IconButton title="Закрити" onClick={onClose}>
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M3 3l8 8M11 3l-8 8" stroke="currentColor" strokeWidth="1.5"/></svg>
            </IconButton>
          </div>
        </div>
        <div className="modal-body">{children}</div>
        {footer && <div className="modal-footer">{footer}</div>}
      </div>
    </div>
  );
}

// --- Drawer (right slide-in) ---
function Drawer({ open, onClose, title, headerRight, children, width = 420 }) {
  useEffect(() => {
    if (!open) return;
    const h = (e) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', h);
    return () => window.removeEventListener('keydown', h);
  }, [open, onClose]);
  if (!open) return null;
  return (
    <>
      <div className="drawer-backdrop" onClick={onClose} />
      <div className="drawer" style={{ width }}>
        <div className="drawer-header">
          <h2 style={{ fontSize: 13, fontWeight: 600, letterSpacing: '0.01em' }}>{title}</h2>
          <div className="row gap-2">
            {headerRight}
            <IconButton title="Закрити" onClick={onClose}>
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M3 3l8 8M11 3l-8 8" stroke="currentColor" strokeWidth="1.5"/></svg>
            </IconButton>
          </div>
        </div>
        {children}
      </div>
    </>
  );
}

// --- Toast host + hook ---
const ToastContext = React.createContext({ push: () => {} });
function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const push = useCallback((toast) => {
    const id = Math.random().toString(36).slice(2);
    setToasts((t) => [...t, { id, ...toast }]);
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), toast.duration || 2600);
  }, []);
  return (
    <ToastContext.Provider value={{ push }}>
      {children}
      <div className="toast-container">
        {toasts.map((t) => (
          <div key={t.id} className={cx('toast', t.tone === 'success' && 'toast--success', t.tone === 'error' && 'toast--error')}>
            <Dot tone={t.tone === 'error' ? 'rose' : t.tone === 'success' ? 'emerald' : 'cyan'} />
            <div className="flex-1">
              {t.title && <div style={{ fontWeight: 600, fontSize: 12 }}>{t.title}</div>}
              {t.message && <div style={{ fontSize: 11, color: 'var(--color-fg-secondary)' }}>{t.message}</div>}
            </div>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
function useToast() { return React.useContext(ToastContext); }

// Common Ic icons (single-purpose SVG factory to avoid emoji AI-slop)
const Icons = {
  chevronDown: <svg width="10" height="10" viewBox="0 0 10 10" fill="none"><path d="M2 3.5L5 6.5L8 3.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="square"/></svg>,
  chevronRight: <svg width="10" height="10" viewBox="0 0 10 10" fill="none"><path d="M3.5 2L6.5 5L3.5 8" stroke="currentColor" strokeWidth="1.4" strokeLinecap="square"/></svg>,
  check: <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M2 6.5L4.5 9L10 3" stroke="currentColor" strokeWidth="1.6" strokeLinecap="square"/></svg>,
  x: <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M2.5 2.5l7 7M9.5 2.5l-7 7" stroke="currentColor" strokeWidth="1.4"/></svg>,
  sync: <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M9 3a4 4 0 1 0 1 4M9 1v3H6" stroke="currentColor" strokeWidth="1.4" strokeLinecap="square" fill="none"/></svg>,
  save: <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M2 2h7l2 2v7H2V2z M4 2v3h4V2 M4 11V7h4v4" stroke="currentColor" strokeWidth="1.2" fill="none"/></svg>,
  play: <svg width="10" height="10" viewBox="0 0 10 10" fill="currentColor"><polygon points="2,1 9,5 2,9"/></svg>,
  pause: <svg width="10" height="10" viewBox="0 0 10 10" fill="currentColor"><rect x="2" y="1" width="2" height="8"/><rect x="6" y="1" width="2" height="8"/></svg>,
  copy: <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><rect x="3" y="3" width="7" height="7" stroke="currentColor" strokeWidth="1.2"/><path d="M2 8V2h6" stroke="currentColor" strokeWidth="1.2"/></svg>,
  download: <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M6 1v7M3 5.5l3 3 3-3M2 10.5h8" stroke="currentColor" strokeWidth="1.4" fill="none" strokeLinecap="square"/></svg>,
  plus: <svg width="10" height="10" viewBox="0 0 10 10" fill="none"><path d="M5 1v8M1 5h8" stroke="currentColor" strokeWidth="1.4"/></svg>,
  minus: <svg width="10" height="10" viewBox="0 0 10 10" fill="none"><path d="M1 5h8" stroke="currentColor" strokeWidth="1.4"/></svg>,
  home: <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M2 6l4-4 4 4v5H2V6z" stroke="currentColor" strokeWidth="1.2" fill="none"/></svg>,
  undo: <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M2 5h6a2 2 0 1 1 0 4H5M2 5l2-2M2 5l2 2" stroke="currentColor" strokeWidth="1.2" fill="none" strokeLinecap="square"/></svg>,
  redo: <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M10 5H4a2 2 0 1 0 0 4h3M10 5L8 3M10 5L8 7" stroke="currentColor" strokeWidth="1.2" fill="none" strokeLinecap="square"/></svg>,
  code: <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M4 3L1 6l3 3M8 3l3 3-3 3" stroke="currentColor" strokeWidth="1.4" fill="none" strokeLinecap="square"/></svg>,
  filter: <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M1 2h10L7 7v4L5 10V7L1 2z" stroke="currentColor" strokeWidth="1.2" fill="none"/></svg>,
  search: <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><circle cx="5" cy="5" r="3.5" stroke="currentColor" strokeWidth="1.4"/><path d="M8 8l3 3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="square"/></svg>,
  eye: <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M1 6c1.5-3 3.5-4 5-4s3.5 1 5 4c-1.5 3-3.5 4-5 4S2.5 9 1 6z" stroke="currentColor" strokeWidth="1.2" fill="none"/><circle cx="6" cy="6" r="1.5" stroke="currentColor" strokeWidth="1.2"/></svg>,
  edit: <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M2 10l1-3 6-6 2 2-6 6-3 1z" stroke="currentColor" strokeWidth="1.2" fill="none"/></svg>,
  branch: <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><circle cx="3" cy="2.5" r="1.2" stroke="currentColor" strokeWidth="1.2"/><circle cx="3" cy="9.5" r="1.2" stroke="currentColor" strokeWidth="1.2"/><circle cx="9" cy="2.5" r="1.2" stroke="currentColor" strokeWidth="1.2"/><path d="M3 4v4M3 8c0-3 6-3 6-4" stroke="currentColor" strokeWidth="1.2" fill="none"/></svg>,
  alert: <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M6 1L11 10H1L6 1z" stroke="currentColor" strokeWidth="1.2" fill="none"/><path d="M6 5v2M6 8.5v0.5" stroke="currentColor" strokeWidth="1.4"/></svg>,
  book: <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M2 2h4a2 2 0 0 1 2 2v6a2 2 0 0 0-2-2H2V2zM10 2H8v6h2a1 1 0 0 0 0-2M8 4a2 2 0 0 1 2-2" stroke="currentColor" strokeWidth="1.1" fill="none"/></svg>,
  shield: <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M6 1l4 2v3c0 3-2 4.5-4 5-2-0.5-4-2-4-5V3l4-2z" stroke="currentColor" strokeWidth="1.2" fill="none"/></svg>,
  list: <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M4 3h7M4 6h7M4 9h7M1 3h1M1 6h1M1 9h1" stroke="currentColor" strokeWidth="1.4"/></svg>,
  spin: <svg width="12" height="12" viewBox="0 0 12 12" fill="none" style={{ animation: 'spin 900ms linear infinite' }}><circle cx="6" cy="6" r="4.5" stroke="currentColor" strokeWidth="1.4" strokeDasharray="14 8" fill="none"/></svg>,
};

// Global keyframes for icon spin
if (typeof document !== 'undefined' && !document.getElementById('__bsdd_kf__')) {
  const s = document.createElement('style');
  s.id = '__bsdd_kf__';
  s.textContent = '@keyframes spin { to { transform: rotate(360deg); } }';
  document.head.appendChild(s);
}

// Expose to global scope for sibling babel scripts
Object.assign(window, {
  cx, Button, IconButton, Badge, Dot, Banner, Selector, Segmented,
  ClientOnly, Dialog, Drawer, ToastProvider, useToast, Icons,
});
