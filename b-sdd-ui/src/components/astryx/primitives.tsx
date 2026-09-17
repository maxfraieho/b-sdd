// src/components/astryx/primitives.tsx
// Official Astryx Design System Primitives (facebook/astryx contract)
// Styled for Swiss High-Tech Dark Cockpit
import React from 'react';
import { X, ChevronRight, AlertCircle, CheckCircle, Info, AlertTriangle } from 'lucide-react';

export function cx(...args: (string | boolean | undefined | null)[]): string {
  return args.filter(Boolean).join(' ');
}

// -----------------------------------------------------------------------------
// 1. Astryx Button
// -----------------------------------------------------------------------------
export type ButtonVariant = 'primary' | 'secondary' | 'success' | 'destructive' | 'ghost';
export type ButtonSize = 'sm' | 'md' | 'lg' | 'xl';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  icon?: React.ReactNode;
  iconRight?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'secondary',
  size = 'md',
  icon,
  iconRight,
  children,
  className,
  disabled,
  ...rest
}) => {
  const baseClasses =
    'inline-flex items-center justify-center font-mono font-medium rounded transition-colors select-none focus:outline-none focus:ring-1 focus:ring-amber/50 disabled:opacity-50 disabled:cursor-not-allowed';

  const sizeClasses: Record<ButtonSize, string> = {
    sm: 'text-xs px-2.5 py-1 gap-1.5 h-7',
    md: 'text-xs px-3 py-1.5 gap-2 h-8',
    lg: 'text-sm px-4 py-2 gap-2 h-10',
    xl: 'text-base px-5 py-2.5 gap-2.5 h-12',
  };

  const variantClasses: Record<ButtonVariant, string> = {
    primary:
      'bg-amber hover:bg-amber/90 text-slate-950 font-bold border border-amber/40 shadow-sm',
    secondary:
      'bg-[#1a2233] hover:bg-[#24324d] text-slate-200 border border-[#1e293b]',
    success:
      'bg-emerald hover:bg-emerald/90 text-slate-950 font-bold border border-emerald/40 shadow-sm',
    destructive:
      'bg-rose hover:bg-rose/90 text-white font-bold border border-rose/40 shadow-sm',
    ghost:
      'bg-transparent hover:bg-[#1a2233] text-slate-300 hover:text-slate-100 border border-transparent',
  };

  return (
    <button
      className={cx(baseClasses, sizeClasses[size], variantClasses[variant], className)}
      disabled={disabled}
      {...rest}
    >
      {icon && <span className="shrink-0">{icon}</span>}
      {children && <span>{children}</span>}
      {iconRight && <span className="shrink-0">{iconRight}</span>}
    </button>
  );
};

// -----------------------------------------------------------------------------
// 2. Astryx IconButton
// -----------------------------------------------------------------------------
export interface IconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'ghost' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  title: string;
}

export const IconButton: React.FC<IconButtonProps> = ({
  variant = 'ghost',
  size = 'md',
  title,
  children,
  className,
  ...rest
}) => {
  const sizeClasses = {
    sm: 'w-7 h-7 p-1 text-xs',
    md: 'w-8 h-8 p-1.5 text-sm',
    lg: 'w-10 h-10 p-2 text-base',
  };

  const variantClasses = {
    ghost: 'bg-transparent hover:bg-[#1a2233] text-slate-400 hover:text-slate-100 border border-transparent',
    secondary: 'bg-[#1a2233] hover:bg-[#24324d] text-slate-200 border border-[#1e293b]',
  };

  return (
    <button
      title={title}
      aria-label={title}
      className={cx(
        'inline-flex items-center justify-center rounded transition-colors select-none focus:outline-none focus:ring-1 focus:ring-amber/50 disabled:opacity-40',
        sizeClasses[size],
        variantClasses[variant],
        className
      )}
      {...rest}
    >
      {children}
    </button>
  );
};

// -----------------------------------------------------------------------------
// 3. Astryx Badge & Dot
// -----------------------------------------------------------------------------
export type AstryxTone = 'emerald' | 'amber' | 'cyan' | 'rose' | 'violet' | 'neutral';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  tone?: AstryxTone;
  outline?: boolean;
}

export const Badge: React.FC<BadgeProps> = ({
  tone = 'neutral',
  outline = false,
  children,
  className,
  ...rest
}) => {
  const toneClasses: Record<AstryxTone, string> = outline
    ? {
        emerald: 'border border-emerald/40 text-emerald bg-emerald/10',
        amber: 'border border-amber/40 text-amber bg-amber/10',
        cyan: 'border border-cyan/40 text-cyan bg-cyan/10',
        rose: 'border border-rose/40 text-rose bg-rose/10',
        violet: 'border border-violet/40 text-violet bg-violet/10',
        neutral: 'border border-[#1e293b] text-slate-400 bg-slate-900/40',
      }
    : {
        emerald: 'bg-emerald/20 text-emerald',
        amber: 'bg-amber/20 text-amber',
        cyan: 'bg-cyan/20 text-cyan',
        rose: 'bg-rose/20 text-rose',
        violet: 'bg-violet/20 text-violet',
        neutral: 'bg-[#1a2233] text-slate-300',
      };

  return (
    <span
      className={cx(
        'inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-mono font-medium tracking-tight',
        toneClasses[tone],
        className
      )}
      {...rest}
    >
      {children}
    </span>
  );
};

export interface DotProps {
  tone?: AstryxTone;
  pulse?: boolean;
  className?: string;
}

export const Dot: React.FC<DotProps> = ({ tone = 'emerald', pulse = false, className }) => {
  const dotColor: Record<AstryxTone, string> = {
    emerald: 'bg-emerald',
    amber: 'bg-amber',
    cyan: 'bg-cyan',
    rose: 'bg-rose',
    violet: 'bg-violet',
    neutral: 'bg-slate-500',
  };

  return (
    <span className={cx('relative inline-flex w-2 h-2 shrink-0', className)}>
      {pulse && (
        <span
          className={cx(
            'absolute inset-0 rounded-full opacity-75 animate-ping',
            dotColor[tone]
          )}
        />
      )}
      <span className={cx('relative inline-flex rounded-full w-2 h-2', dotColor[tone])} />
    </span>
  );
};

// -----------------------------------------------------------------------------
// 4. Astryx Banner
// -----------------------------------------------------------------------------
export interface BannerProps {
  tone?: 'info' | 'warning' | 'error' | 'success';
  icon?: React.ReactNode;
  children: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
}

export const Banner: React.FC<BannerProps> = ({
  tone = 'info',
  icon,
  children,
  action,
  className,
}) => {
  const toneMap = {
    info: 'border-cyan/30 bg-cyan/5 text-cyan',
    warning: 'border-amber/30 bg-amber/5 text-amber',
    error: 'border-rose/30 bg-rose/5 text-rose',
    success: 'border-emerald/30 bg-emerald/5 text-emerald',
  };

  const defaultIcon = {
    info: <Info className="w-4 h-4 text-cyan shrink-0" />,
    warning: <AlertTriangle className="w-4 h-4 text-amber shrink-0" />,
    error: <AlertCircle className="w-4 h-4 text-rose shrink-0" />,
    success: <CheckCircle className="w-4 h-4 text-emerald shrink-0" />,
  };

  return (
    <div
      className={cx(
        'flex items-start gap-2.5 p-3 rounded border text-xs font-mono leading-relaxed',
        toneMap[tone],
        className
      )}
    >
      {icon || defaultIcon[tone]}
      <div className="flex-1 text-slate-200">{children}</div>
      {action && <div className="shrink-0">{action}</div>}
    </div>
  );
};

// -----------------------------------------------------------------------------
// 5. Astryx Selector
// -----------------------------------------------------------------------------
export interface SelectorOption {
  value: string;
  label: string;
  hint?: string;
}

export interface SelectorProps extends Omit<React.SelectHTMLAttributes<HTMLSelectElement>, 'onChange'> {
  value: string;
  onChange: (val: string) => void;
  options: (string | SelectorOption)[];
}

export const Selector: React.FC<SelectorProps> = ({
  value,
  onChange,
  options,
  className,
  ...rest
}) => {
  return (
    <div className="relative inline-block">
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={cx(
          'appearance-none bg-[#141b27] border border-[#1e293b] hover:border-amber/50 rounded px-2.5 py-1.5 pr-7 text-xs font-mono text-slate-200 focus:outline-none focus:ring-1 focus:ring-amber transition-colors cursor-pointer',
          className
        )}
        {...rest}
      >
        {options.map((opt) => {
          const val = typeof opt === 'string' ? opt : opt.value;
          const lbl = typeof opt === 'string' ? opt : opt.label;
          return (
            <option key={val} value={val} className="bg-[#141b27] text-slate-200">
              {lbl}
            </option>
          );
        })}
      </select>
      <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-slate-400">
        <ChevronRight className="w-3 h-3 rotate-90" />
      </div>
    </div>
  );
};

// -----------------------------------------------------------------------------
// 6. Astryx Segmented
// -----------------------------------------------------------------------------
export interface SegmentedOption {
  value: string;
  label: React.ReactNode;
}

export interface SegmentedProps {
  value: string;
  onChange: (value: string) => void;
  options: SegmentedOption[];
  className?: string;
}

export const Segmented: React.FC<SegmentedProps> = ({
  value,
  onChange,
  options,
  className,
}) => {
  return (
    <div
      role="tablist"
      className={cx(
        'inline-flex items-center bg-[#0d121c] border border-[#1e293b] rounded p-0.5 text-xs font-mono select-none',
        className
      )}
    >
      {options.map((opt) => {
        const isSelected = value === opt.value;
        return (
          <button
            key={opt.value}
            role="tab"
            aria-selected={isSelected}
            onClick={() => onChange(opt.value)}
            className={cx(
              'px-2.5 py-1 rounded transition-all flex items-center gap-1.5',
              isSelected
                ? 'bg-[#1a2233] text-amber font-bold shadow-xs border border-amber/30'
                : 'text-slate-400 hover:text-slate-200'
            )}
          >
            {opt.label}
          </button>
        );
      })}
    </div>
  );
};

// -----------------------------------------------------------------------------
// 7. Astryx Dialog (Modal)
// -----------------------------------------------------------------------------
export interface DialogProps {
  isOpen: boolean;
  onClose: () => void;
  title: React.ReactNode;
  children: React.ReactNode;
  footer?: React.ReactNode;
  maxWidth?: string;
}

export const Dialog: React.FC<DialogProps> = ({
  isOpen,
  onClose,
  title,
  children,
  footer,
  maxWidth = 'max-w-2xl',
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-xs select-none">
      <div
        className={cx(
          'w-full bg-[#141b27] border border-[#1e293b] rounded-lg shadow-2xl flex flex-col overflow-hidden text-slate-100 max-h-[90vh]',
          maxWidth
        )}
      >
        <div className="flex items-center justify-between px-4 py-3 border-b border-[#1e293b] bg-[#0d121c]">
          <h2 className="text-sm font-bold font-mono tracking-tight text-slate-100">{title}</h2>
          <button
            onClick={onClose}
            className="p-1 rounded text-slate-400 hover:text-slate-100 hover:bg-[#1a2233]"
            aria-label="Close"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 select-text">{children}</div>

        {footer && (
          <div className="flex items-center justify-end gap-2 px-4 py-3 border-t border-[#1e293b] bg-[#0d121c]">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
};

// -----------------------------------------------------------------------------
// 8. Astryx Drawer (Slide-in Right Panel)
// -----------------------------------------------------------------------------
export interface DrawerProps {
  isOpen: boolean;
  onClose: () => void;
  title: React.ReactNode;
  children: React.ReactNode;
  width?: string;
}

export const Drawer: React.FC<DrawerProps> = ({
  isOpen,
  onClose,
  title,
  children,
  width = 'w-[480px]',
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/60 backdrop-blur-xs select-none">
      <div className="absolute inset-y-0 right-0 flex max-w-full pl-10">
        <div
          className={cx(
            'flex flex-col bg-[#0d121c] border-l border-[#1e293b] shadow-2xl text-slate-100 h-full',
            width
          )}
        >
          <div className="flex items-center justify-between px-4 py-3 border-b border-[#1e293b] bg-[#141b27]">
            <h2 className="text-sm font-bold font-mono text-slate-100">{title}</h2>
            <button
              onClick={onClose}
              className="p-1 rounded text-slate-400 hover:text-slate-100 hover:bg-[#1a2233]"
              aria-label="Close"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 select-text">{children}</div>
        </div>
      </div>
    </div>
  );
};

// -----------------------------------------------------------------------------
// 9. Astryx AppShell
// -----------------------------------------------------------------------------
export const AppShell: React.FC<{ children: React.ReactNode; className?: string }> = ({
  children,
  className,
}) => {
  return (
    <div
      className={cx(
        'h-screen w-screen flex flex-col bg-[#090d13] text-slate-100 overflow-hidden select-none font-sans',
        className
      )}
    >
      {children}
    </div>
  );
};
