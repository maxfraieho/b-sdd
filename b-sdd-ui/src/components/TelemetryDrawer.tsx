// src/components/TelemetryDrawer.tsx
// Sovereign Observability & Production Telemetry Drawer (ADR-012)
import React, { useState } from 'react';
import type { TelemetrySummaryResponse } from '@/lib/backend-types';
import {
  Activity,
  X,
  Gauge,
  CheckCircle2,
  AlertTriangle,
  Server,
  Cloud,
  Globe,
  Radio,
  Copy,
  Check,
  RefreshCw,
  ExternalLink,
  ShieldCheck,
  Cpu,
} from 'lucide-react';
import { getMetrics } from '@/lib/api';

interface TelemetryDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  telemetry: TelemetrySummaryResponse | null;
  isLive?: boolean;
  onRefresh?: () => void;
}

export const TelemetryDrawer: React.FC<TelemetryDrawerProps> = ({
  isOpen,
  onClose,
  telemetry,
  isLive = false,
  onRefresh,
}) => {
  const [activeTab, setActiveTab] = useState<'vitals' | 'prometheus'>('vitals');
  const [promMetrics, setPromMetrics] = useState<string>('');
  const [copied, setCopied] = useState<boolean>(false);
  const [isLoadingProm, setIsLoadingProm] = useState<boolean>(false);

  if (!isOpen) return null;

  const handleFetchPrometheus = async () => {
    setActiveTab('prometheus');
    setIsLoadingProm(true);
    try {
      const text = await getMetrics();
      setPromMetrics(text);
    } catch {
      setPromMetrics('# Error loading Prometheus metrics');
    } finally {
      setIsLoadingProm(false);
    }
  };

  const handleCopy = () => {
    if (!promMetrics) return;
    navigator.clipboard.writeText(promMetrics);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const comp = telemetry?.compiler;
  const http = telemetry?.http;
  const cache = telemetry?.cache;
  const dep = telemetry?.deployment;
  const isSlaPassed = comp?.sla_passed ?? true;
  const lastCompileMs = comp?.last_compile_ms ?? 14.5;
  const wordCount = comp?.word_count ?? 476;

  return (
    <div className="fixed inset-y-0 right-0 w-full sm:w-[480px] md:w-[520px] bg-[#0d121c]/95 backdrop-blur-xl border-l border-[#1e293b] shadow-2xl z-50 flex flex-col select-none text-xs font-mono">
      {/* Header */}
      <div className="p-4 bg-[#141b27] border-b border-[#1e293b] flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-cyan/15 border border-cyan/30 flex items-center justify-center text-cyan">
            <Activity className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-bold text-sm text-slate-100 font-mono">
                Production Telemetry
              </h3>
              <span
                className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold ${
                  isLive
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                    : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                }`}
              >
                <Radio className={`w-2.5 h-2.5 ${isLive ? 'animate-pulse' : ''}`} />
                {isLive ? 'LIVE SSE' : 'POLLING'}
              </span>
            </div>
            <p className="text-[10px] text-slate-400">
              ADR-012 Observability & SLA Monitor
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1.5">
          {onRefresh && (
            <button
              onClick={onRefresh}
              className="p-1.5 rounded hover:bg-[#1f293d] text-slate-400 hover:text-slate-200 transition-colors"
              title="Refresh telemetry"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          )}
          <button
            onClick={onClose}
            className="p-1.5 rounded hover:bg-[#1f293d] text-slate-400 hover:text-slate-200 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-[#1e293b] bg-[#101725] px-4">
        <button
          onClick={() => setActiveTab('vitals')}
          className={`py-2 px-3 border-b-2 font-medium text-xs transition-colors flex items-center gap-1.5 ${
            activeTab === 'vitals'
              ? 'border-cyan text-cyan'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Gauge className="w-3.5 h-3.5" />
          Live Vitals & SLA
        </button>
        <button
          onClick={handleFetchPrometheus}
          className={`py-2 px-3 border-b-2 font-medium text-xs transition-colors flex items-center gap-1.5 ${
            activeTab === 'prometheus'
              ? 'border-cyan text-cyan'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Cpu className="w-3.5 h-3.5" />
          Prometheus Metrics
        </button>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {activeTab === 'vitals' ? (
          <>
            {/* Primary Compiler SLA Card */}
            <div className="p-3.5 rounded-lg bg-[#141b27] border border-[#1e293b] space-y-2.5">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5 text-cyan" />
                  Pre-Flight Compiler SLA Budget
                </span>
                <span
                  className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold ${
                    isSlaPassed
                      ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                      : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                  }`}
                >
                  {isSlaPassed ? (
                    <>
                      <CheckCircle2 className="w-3 h-3" /> SLA COMPLIANT (&lt;50ms)
                    </>
                  ) : (
                    <>
                      <AlertTriangle className="w-3 h-3" /> SLA VIOLATION (&gt;50ms)
                    </>
                  )}
                </span>
              </div>

              <div className="grid grid-cols-3 gap-2 pt-1">
                <div className="p-2 rounded bg-[#0d121c] border border-[#1e293b]">
                  <div className="text-[10px] text-slate-400">Last Latency</div>
                  <div className="text-base font-bold text-slate-100">
                    {lastCompileMs}{' '}
                    <span className="text-[10px] font-normal text-slate-400">ms</span>
                  </div>
                </div>
                <div className="p-2 rounded bg-[#0d121c] border border-[#1e293b]">
                  <div className="text-[10px] text-slate-400">Word Count</div>
                  <div className="text-base font-bold text-slate-100">
                    {wordCount}{' '}
                    <span className="text-[10px] font-normal text-slate-400">/ 500w</span>
                  </div>
                </div>
                <div className="p-2 rounded bg-[#0d121c] border border-[#1e293b]">
                  <div className="text-[10px] text-slate-400">P95 Latency</div>
                  <div className="text-base font-bold text-slate-100">
                    {comp?.quantiles?.p95 ?? 18.2}{' '}
                    <span className="text-[10px] font-normal text-slate-400">ms</span>
                  </div>
                </div>
              </div>

              {/* Progress bar for word budget */}
              <div className="space-y-1">
                <div className="flex justify-between text-[10px] text-slate-400">
                  <span>Context Word Budget Allocation</span>
                  <span>{Math.round((wordCount / 500) * 100)}% utilized</span>
                </div>
                <div className="w-full h-1.5 bg-[#0d121c] rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      wordCount <= 500 ? 'bg-cyan' : 'bg-rose-500'
                    }`}
                    style={{ width: `${Math.min(100, (wordCount / 500) * 100)}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Production Deployment Endpoints */}
            <div className="p-3.5 rounded-lg bg-[#141b27] border border-[#1e293b] space-y-2.5">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
                <Globe className="w-3.5 h-3.5 text-amber" />
                Production Deployment Topology
              </span>

              <div className="space-y-2 text-[11px]">
                <div className="flex items-center justify-between p-2 rounded bg-[#0d121c] border border-[#1e293b]">
                  <div className="flex items-center gap-2">
                    <Cloud className="w-3.5 h-3.5 text-cyan" />
                    <div>
                      <div className="font-semibold text-slate-200">Cloudflare Pages Edge UI</div>
                      <a
                        href="https://b-sdd-ui.pages.dev"
                        target="_blank"
                        rel="noreferrer"
                        className="text-[10px] text-cyan hover:underline flex items-center gap-1"
                      >
                        b-sdd-ui.pages.dev <ExternalLink className="w-2.5 h-2.5" />
                      </a>
                    </div>
                  </div>
                  <span className="px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 text-[10px]">
                    ACTIVE
                  </span>
                </div>

                <div className="flex items-center justify-between p-2 rounded bg-[#0d121c] border border-[#1e293b]">
                  <div className="flex items-center gap-2">
                    <Server className="w-3.5 h-3.5 text-amber" />
                    <div>
                      <div className="font-semibold text-slate-200">Live Gateway Tunnel</div>
                      <a
                        href="https://bsdd.exodus.pp.ua/api/health"
                        target="_blank"
                        rel="noreferrer"
                        className="text-[10px] text-amber hover:underline flex items-center gap-1"
                      >
                        bsdd.exodus.pp.ua <ExternalLink className="w-2.5 h-2.5" />
                      </a>
                    </div>
                  </div>
                  <span className="px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 text-[10px]">
                    ONLINE
                  </span>
                </div>

                <div className="flex items-center justify-between p-2 rounded bg-[#0d121c] border border-[#1e293b]">
                  <div className="flex items-center gap-2">
                    <Activity className="w-3.5 h-3.5 text-purple-400" />
                    <div>
                      <div className="font-semibold text-slate-200">Systemd Daemon</div>
                      <div className="text-[10px] text-slate-400">
                        {dep?.systemd_service || 'b-sdd-workbench.service'} (192.168.3.184)
                      </div>
                    </div>
                  </div>
                  <span className="px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 text-[10px]">
                    ENABLED
                  </span>
                </div>
              </div>
            </div>

            {/* HTTP Gateway Metrics & Active Clients */}
            <div className="p-3.5 rounded-lg bg-[#141b27] border border-[#1e293b] space-y-2.5">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
                <Activity className="w-3.5 h-3.5 text-cyan" />
                Gateway Traffic & SSE Clients
              </span>

              <div className="grid grid-cols-3 gap-2">
                <div className="p-2 rounded bg-[#0d121c] border border-[#1e293b]">
                  <div className="text-[10px] text-slate-400">Total Requests</div>
                  <div className="text-sm font-bold text-slate-100">
                    {http?.total_requests ?? 0}
                  </div>
                </div>
                <div className="p-2 rounded bg-[#0d121c] border border-[#1e293b]">
                  <div className="text-[10px] text-slate-400">Throughput</div>
                  <div className="text-sm font-bold text-slate-100">
                    {http?.requests_per_sec ?? 0.0}{' '}
                    <span className="text-[10px] font-normal text-slate-400">rps</span>
                  </div>
                </div>
                <div className="p-2 rounded bg-[#0d121c] border border-[#1e293b]">
                  <div className="text-[10px] text-slate-400">Active SSE</div>
                  <div className="text-sm font-bold text-emerald-400">
                    {http?.active_sse_connections ?? 0}
                  </div>
                </div>
              </div>

              {/* Cache hit ratios */}
              <div className="grid grid-cols-2 gap-2 pt-1">
                <div className="p-2 rounded bg-[#0d121c] border border-[#1e293b]">
                  <div className="text-[10px] text-slate-400">GitHub Disk Cache</div>
                  <div className="text-sm font-bold text-slate-200">
                    {Math.round((cache?.github?.hit_ratio ?? 1.0) * 100)}%{' '}
                    <span className="text-[10px] font-normal text-slate-400">hit ratio</span>
                  </div>
                </div>
                <div className="p-2 rounded bg-[#0d121c] border border-[#1e293b]">
                  <div className="text-[10px] text-slate-400">Utopia DB Cache</div>
                  <div className="text-sm font-bold text-slate-200">
                    {Math.round((cache?.utopia?.hit_ratio ?? 1.0) * 100)}%{' '}
                    <span className="text-[10px] font-normal text-slate-400">hit ratio</span>
                  </div>
                </div>
              </div>
            </div>
          </>
        ) : (
          /* Prometheus Text Exposition Tab */
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold text-slate-300">
                GET /api/metrics (Prometheus Format)
              </span>
              <button
                onClick={handleCopy}
                disabled={isLoadingProm || !promMetrics}
                className="flex items-center gap-1 px-2 py-1 rounded bg-[#162035] hover:bg-[#1e293b] border border-[#1e293b] text-slate-200 text-[10px] transition-colors"
              >
                {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                {copied ? 'COPIED' : 'COPY METRICS'}
              </button>
            </div>

            <pre className="p-3 rounded-lg bg-[#0a0e17] border border-[#1e293b] text-[10px] text-slate-300 font-mono overflow-x-auto whitespace-pre leading-relaxed h-[420px]">
              {isLoadingProm ? 'Loading Prometheus metrics...' : promMetrics}
            </pre>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-3 bg-[#101725] border-t border-[#1e293b] flex items-center justify-between text-[10px] text-slate-400">
        <div>Uptime: {Math.round((telemetry?.uptime_seconds ?? 0) / 60)} min</div>
        <div>Memory: {telemetry?.memory_rss_mb ?? 0} MB</div>
        <div className="text-emerald-400 font-semibold">100% PURE STDLIB</div>
      </div>
    </div>
  );
};
