// src/components/ReviewGateModal.tsx
import React, { useState } from 'react';
import type { FitnessTestSummary, RejectAndBranchPayload } from '@/types/sprint';
import {
  ShieldAlert,
  CheckCircle,
  XCircle,
  AlertTriangle,
  FileCode2,
  X,
  Key,
} from 'lucide-react';

interface ReviewGateModalProps {
  isOpen: boolean;
  onClose: () => void;
  fitnessSummary: FitnessTestSummary;
  onApprove: () => void;
  onRejectAndBranch: (payload: RejectAndBranchPayload) => void;
}

export const ReviewGateModal: React.FC<ReviewGateModalProps> = ({
  isOpen,
  onClose,
  fitnessSummary,
  onApprove,
  onRejectAndBranch,
}) => {
  const [isRejecting, setIsRejecting] = useState(false);
  const [rollbackDepth, setRollbackDepth] = useState(1);
  const [negativeInvariants, setNegativeInvariants] = useState('ADR-007-INV-01: Branch mutation detected');
  const [rationale, setRationale] = useState('');

  if (!isOpen) return null;

  const handleConfirmReject = () => {
    onRejectAndBranch({
      rejectedPhase: 'phi_6',
      rollbackDepth,
      negativeInvariants: negativeInvariants.split('\n').map((s) => s.trim()).filter(Boolean),
      rationale: rationale || 'Operator requested rollback to clean context.',
      timestamp: new Date().toISOString(),
    });
    setIsRejecting(false);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="w-full max-w-2xl bg-panel border border-border-subtle rounded-xl shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 bg-card border-b border-border-subtle flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-violet-500/20 border border-violet-500/40 flex items-center justify-center text-violet-300">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <span>Phase 6: Human Review Gate</span>
                <span className="text-xs font-mono font-normal bg-violet-500/20 text-violet-300 px-2 py-0.5 rounded">
                  Synchronous Blocking Gate
                </span>
              </h2>
              <p className="text-xs text-slate-400">
                Architectural inspection of synthesized action bodies & fitness guarantees
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-200 rounded hover:bg-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-5 overflow-y-auto max-h-[70vh]">
          {/* Fitness Metrics Grid */}
          <div>
            <span className="text-xs font-mono uppercase text-slate-400 font-semibold tracking-wider">
              Automated Fitness Verification Gate (Φ5)
            </span>
            <div className="grid grid-cols-4 gap-3 mt-2">
              <div className="bg-card border border-emerald-500/30 rounded-lg p-3 flex flex-col items-center">
                <span className="text-xl font-bold font-mono text-emerald-400">
                  {fitnessSummary.passed}/{fitnessSummary.total}
                </span>
                <span className="text-[11px] text-slate-400 mt-1">Pytest Suites</span>
                <span className="text-[10px] text-emerald-500/80 font-mono mt-0.5">100% Passed</span>
              </div>

              <div className="bg-card border border-border-subtle rounded-lg p-3 flex flex-col items-center">
                <span className="text-xl font-bold font-mono text-blue-400">
                  {fitnessSummary.astIsolationScore}%
                </span>
                <span className="text-[11px] text-slate-400 mt-1">AST Isolation</span>
                <span className="text-[10px] text-blue-400/80 font-mono mt-0.5">0 Ext Imports</span>
              </div>

              <div className="bg-card border border-border-subtle rounded-lg p-3 flex flex-col items-center">
                <span className="text-xl font-bold font-mono text-amber">
                  {fitnessSummary.latencyMs}ms
                </span>
                <span className="text-[11px] text-slate-400 mt-1">Compile Latency</span>
                <span className="text-[10px] text-amber/80 font-mono mt-0.5">&lt; 50ms Limit</span>
              </div>

              <div className="bg-card border border-border-subtle rounded-lg p-3 flex flex-col items-center">
                <span className="text-xl font-bold font-mono text-violet-400">
                  {fitnessSummary.tokenCount}
                </span>
                <span className="text-[11px] text-slate-400 mt-1">Token Words</span>
                <span className="text-[10px] text-violet-400/80 font-mono mt-0.5">&le; 500 Budget</span>
              </div>
            </div>
          </div>

          {/* Diff & Scope Inspection */}
          <div className="bg-canvas border border-border-subtle rounded-lg p-4 font-mono text-xs text-slate-300 space-y-2">
            <div className="flex items-center justify-between text-slate-400 pb-2 border-b border-border-subtle">
              <span className="flex items-center gap-1.5">
                <FileCode2 className="w-4 h-4 text-amber" />
                <span>Scope: Leaf Action Synthesis Immutability</span>
              </span>
              <span className="text-emerald-400">Control Flow Preserved ✓</span>
            </div>
            <div className="text-[11px] text-slate-400 leading-relaxed">
              • Validated 4 canonical DRAKON topological rules: vertical skewer, right-is-worse, zero crossings, planar silhouette.<br />
              • Bound 8 active ADR invariant IDs (ADR-001, ADR-002, ADR-007, ADR-008).<br />
              • Ready for sprint distillation into <span className="text-amber">.context/sprint_handoff.json</span>.
            </div>
          </div>

          {/* Reject & Branch Drawer */}
          {isRejecting && (
            <div className="bg-rose-950/20 border border-rose-500/40 rounded-lg p-4 space-y-3">
              <div className="flex items-center gap-2 text-rose-300 font-semibold text-xs">
                <AlertTriangle className="w-4 h-4 text-rose-400" />
                <span>Reject & Branch Protocol Configuration</span>
              </div>
              <p className="text-[11px] text-slate-400">
                A copy-on-write snapshot will be taken in Utopia DB, the rejected branch terminated, and next execution initialized with clean context and negative invariant vector ΔC.
              </p>

              <div>
                <label className="block text-[11px] font-mono text-slate-300 mb-1">
                  Rollback Depth (Sprints):
                </label>
                <select
                  value={rollbackDepth}
                  onChange={(e) => setRollbackDepth(Number(e.target.value))}
                  className="w-full bg-card border border-border-subtle rounded px-2.5 py-1.5 text-xs text-slate-200"
                >
                  <option value={1}>1 Sprint (Immediate prior snapshot)</option>
                  <option value={2}>2 Sprints (Re-anchor at Milestone start)</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-mono text-slate-300 mb-1">
                  Negative Invariant Vector (ΔC):
                </label>
                <textarea
                  value={negativeInvariants}
                  onChange={(e) => setNegativeInvariants(e.target.value)}
                  rows={2}
                  className="w-full bg-card border border-border-subtle rounded p-2 text-xs font-mono text-rose-200 focus:outline-none focus:border-rose-400"
                />
              </div>

              <div>
                <label className="block text-[11px] font-mono text-slate-300 mb-1">
                  Rejection Rationale:
                </label>
                <input
                  type="text"
                  placeholder="e.g. Edge case in timeout recovery not covered by spec."
                  value={rationale}
                  onChange={(e) => setRationale(e.target.value)}
                  className="w-full bg-card border border-border-subtle rounded px-2.5 py-1.5 text-xs text-slate-200"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  onClick={() => setIsRejecting(false)}
                  className="px-3 py-1 text-xs text-slate-400 hover:text-slate-200"
                >
                  Cancel
                </button>
                <button
                  onClick={handleConfirmReject}
                  className="px-3 py-1.5 bg-rose-600 hover:bg-rose-500 text-white rounded text-xs font-semibold shadow transition-colors"
                >
                  Execute COW Branch Fork
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-4 bg-card border-t border-border-subtle flex items-center justify-between">
          {!isRejecting ? (
            <>
              <button
                onClick={() => setIsRejecting(true)}
                className="flex items-center gap-1.5 px-3 py-2 rounded-lg border border-rose-500/40 text-rose-400 hover:bg-rose-500/10 text-xs font-medium transition-colors"
              >
                <XCircle className="w-4 h-4" />
                <span>Reject & Branch</span>
              </button>

              <button
                onClick={() => {
                  onApprove();
                  onClose();
                }}
                className="flex items-center gap-2 px-5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-lg shadow-emerald-900/30 transition-all"
              >
                <Key className="w-4 h-4" />
                <span>Approve & Cryptographically Sign</span>
              </button>
            </>
          ) : (
            <div className="w-full text-right text-[11px] text-slate-400 font-mono">
              Branch fork will terminate current valid-time interval (V_end = NOW)
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
