import React, { useState, useEffect } from 'react';
import { Activity, Server, ShieldCheck, AlertTriangle, RefreshCw, Cpu, Database, Workflow } from 'lucide-react';
import { ClusterHealthReport, ServiceHealth } from '../../types/cluster-health';

const INITIAL_REPORT: ClusterHealthReport = {
  timestamp: new Date().toISOString(),
  overall_status: 'DEGRADED',
  services: [
    {
      service_id: 'local_supervisor',
      host: '127.0.0.1',
      port: 8161,
      is_up: true,
      latency_ms: 1.2,
      error_message: null
    },
    {
      service_id: 'laya_decision_engine',
      host: '192.168.3.251',
      port: 9623,
      is_up: true,
      latency_ms: 38.5,
      error_message: null
    },
    {
      service_id: 'utopia_db_worm',
      host: '192.168.3.251',
      port: 9622,
      is_up: false,
      latency_ms: 2.1,
      error_message: 'Connection refused (Daemon offline)'
    },
    {
      service_id: 'n8n_orchestrator',
      host: 'n8n.exodus.pp.ua',
      port: 443,
      is_up: true,
      latency_ms: 84.0,
      error_message: null
    }
  ]
};

const SERVICE_META: Record<string, { name: string; node: string; icon: React.ComponentType<{ className?: string }> }> = {
  local_supervisor: { name: 'B-SDD Supervisor', node: 'Node .161', icon: Server },
  laya_decision_engine: { name: 'Laya System 1', node: 'Pixel 7 (.251)', icon: Cpu },
  utopia_db_worm: { name: 'Utopia DB WORM', node: 'Pixel 7 (.251)', icon: Database },
  n8n_orchestrator: { name: 'n8n Orchestrator', node: 'Edge Cloud', icon: Workflow }
};

export const ClusterHealthRadar: React.FC = () => {
  const [report, setReport] = useState<ClusterHealthReport>(INITIAL_REPORT);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);

  const fetchHealth = async () => {
    setIsRefreshing(true);
    try {
      // In production, poll health gateway or supervisor endpoint
      const res = await fetch('/api/cluster/health').catch(() => null);
      if (res && res.ok) {
        const data = await res.json();
        setReport(data);
      } else {
        // Fallback live timestamp update
        setReport(prev => ({
          ...prev,
          timestamp: new Date().toISOString()
        }));
      }
    } catch {
      // Retain state gracefully
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 shadow-xl backdrop-blur-md">
      <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-800">
        <div className="flex items-center space-x-2.5">
          <div className="p-1.5 bg-blue-500/10 rounded-lg text-blue-400">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
              Astryx Cluster Health Radar
              <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full border ${
                report.overall_status === 'UP'
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                  : report.overall_status === 'DEGRADED'
                  ? 'bg-amber-500/10 border-amber-500/30 text-amber-400'
                  : 'bg-rose-500/10 border-rose-500/30 text-rose-400'
              }`}>
                {report.overall_status}
              </span>
            </h3>
            <p className="text-xs text-slate-400">
              Proactive telemetry heartbeat • SLA 1.5s • Last poll: {new Date(report.timestamp).toLocaleTimeString()}
            </p>
          </div>
        </div>

        <button
          onClick={fetchHealth}
          disabled={isRefreshing}
          className="p-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 text-slate-400 hover:text-slate-200 transition-colors"
          title="Refresh cluster telemetry"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-blue-400' : ''}`} />
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {report.services.map((svc: ServiceHealth) => {
          const meta = SERVICE_META[svc.service_id] || {
            name: svc.service_id,
            node: `${svc.host}:${svc.port}`,
            icon: Server
          };
          const Icon = meta.icon;

          return (
            <div
              key={svc.service_id}
              className={`relative overflow-hidden rounded-lg p-3 border transition-all ${
                svc.is_up
                  ? 'bg-slate-800/40 border-slate-700/60 hover:border-emerald-500/40'
                  : 'bg-rose-950/20 border-rose-800/40 hover:border-rose-700/60'
              }`}
            >
              {/* Pulsing indicator */}
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <div className="p-1.5 rounded-md bg-slate-800 text-slate-300">
                    <Icon className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="text-xs font-medium text-slate-200">{meta.name}</div>
                    <div className="text-[10px] text-slate-400">{meta.node}</div>
                  </div>
                </div>

                <div className="flex items-center space-x-1.5">
                  <span className="relative flex h-2.5 w-2.5">
                    {svc.is_up ? (
                      <>
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                      </>
                    ) : (
                      <>
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-rose-500"></span>
                      </>
                    )}
                  </span>
                </div>
              </div>

              {/* Telemetry info */}
              <div className="flex items-center justify-between text-[11px] pt-1 border-t border-slate-800/60">
                <span className="text-slate-400">Latency</span>
                <span className={`font-mono font-medium ${
                  svc.is_up ? (svc.latency_ms < 50 ? 'text-emerald-400' : 'text-amber-400') : 'text-slate-500'
                }`}>
                  {svc.is_up ? `${svc.latency_ms} ms` : 'TIMEOUT'}
                </span>
              </div>

              {svc.error_message && (
                <div className="mt-1 text-[10px] text-rose-400 truncate" title={svc.error_message}>
                  {svc.error_message}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
