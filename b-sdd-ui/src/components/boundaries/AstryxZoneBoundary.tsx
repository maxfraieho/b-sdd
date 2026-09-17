import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface Props {
  zoneName: string;
  children: ReactNode;
  fallbackMessage?: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

/**
 * AstryxZoneBoundary: Fault-isolation boundary for workbench zones (INV-FE3).
 * Prevents errors in visual canvas or sidebars from crashing the entire workbench.
 */
export class AstryxZoneBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error(`[AstryxZoneBoundary: ${this.props.zoneName}] error caught:`, error, errorInfo);
  }

  private handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="h-full w-full flex flex-col items-center justify-center p-6 bg-canvas border border-red-500/20 text-center rounded-lg">
          <div className="p-3 bg-red-500/10 rounded-full text-red-400 mb-3">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <h3 className="text-sm font-semibold text-white font-mono mb-1">
            Zone Error: {this.props.zoneName}
          </h3>
          <p className="text-xs text-slate-400 max-w-sm mb-4">
            {this.props.fallbackMessage || this.state.error?.message || 'An unexpected rendering error occurred in this zone.'}
          </p>
          <button
            onClick={this.handleRetry}
            className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-xs font-mono text-slate-200 border border-border-subtle rounded transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Recover Zone</span>
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
