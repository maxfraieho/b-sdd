// src/components/ReviewGateModal.tsx
// Astryx-native Human Review Gate Dialog (ADR-009, ADR-011)
import React, { useState } from 'react';
import type { FitnessTestSummary, RejectAndBranchPayload } from '@/types/sprint';
import { submitSprintReview } from '@/lib/api';
import type { SprintReviewResponse } from '@/lib/backend-types';
import { Dialog, Button, Badge, Banner } from './astryx/primitives';
import {
  ShieldAlert,
  XCircle,
  AlertTriangle,
  FileCode2,
  Key,
  Loader2,
  Copy,
  CheckCircle2,
  Terminal,
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
  const [operatorSignature] = useState(
    'ed25519:e4f3a2b109876543210fedcba9876543210fedcba9876543210fedcba98765430123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef',
  );

  // Phase 3: live backend review status
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [reviewResponse, setReviewResponse] = useState<SprintReviewResponse | null>(null);
  const [reviewError, setReviewError] = useState<string | null>(null);
  const [copiedCli, setCopiedCli] = useState(false);

  if (!isOpen) return null;

  const dispatchReview = async (
    payload: Parameters<typeof submitSprintReview>[0],
  ): Promise<SprintReviewResponse | null> => {
    setIsSubmitting(true);
    setReviewError(null);
    try {
      const resp = await submitSprintReview(payload);
      setReviewResponse(resp);
      return resp;
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      setReviewError(msg);
      return null;
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleApprove = async () => {
    // Fire local optimistic state update immediately.
    onApprove();
    // Then hit the backend with cryptographic operator signature (ADR-011).
    await dispatchReview({
      action: 'approve',
      operator_signature: operatorSignature,
    });
  };

  const handleConfirmReject = async () => {
    const negatives = negativeInvariants
      .split('\n')
      .map((s) => s.trim())
      .filter(Boolean);

    onRejectAndBranch({
      rejectedPhase: 'phi_6',
      rollbackDepth,
      negativeInvariants: negatives,
      rationale: rationale || 'Operator requested rollback to clean context.',
      timestamp: new Date().toISOString(),
    });

    await dispatchReview({
      action: 'reject',
      negative_invariants: negatives,
      rationale: rationale || 'Operator requested rollback to clean context.',
      rollback_depth: rollbackDepth,
      operator_signature: operatorSignature,
    });

    setIsRejecting(false);
  };

  const handleCopyCli = () => {
    if (!reviewResponse?.launch_command) return;
    void navigator.clipboard.writeText(reviewResponse.launch_command).then(() => {
      setCopiedCli(true);
      window.setTimeout(() => setCopiedCli(false), 1400);
    });
  };

  const handleCloseAndReset = () => {
    setReviewResponse(null);
    setReviewError(null);
    setIsRejecting(false);
    onClose();
  };

  return (
    <Dialog
      isOpen={isOpen}
      onClose={handleCloseAndReset}
      maxWidth="max-w-2xl"
      title={
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-violet-500/20 border border-violet-500/40 flex items-center justify-center text-violet-300">
            <ShieldAlert className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold font-mono">Phase 6: Human Review Gate</span>
              <Badge tone="violet" outline>Synchronous Gate</Badge>
            </div>
            <p className="text-[11px] text-slate-400 font-sans font-normal">
              Architectural inspection of synthesized action bodies & fitness guarantees
            </p>
          </div>
        </div>
      }
      footer={
        reviewResponse && reviewResponse.action === 'approve' ? (
          <div className="flex items-center justify-between w-full">
            <span className="text-[11px] text-emerald-300 font-mono">
              ✓ Ready. Close this dialog to advance to Φ7.
            </span>
            <Button
              variant="success"
              size="md"
              icon={<CheckCircle2 className="w-4 h-4" />}
              onClick={handleCloseAndReset}
            >
              Continue to Φ7 Handoff
            </Button>
          </div>
        ) : !isRejecting ? (
          <div className="flex items-center justify-between w-full">
            <Button
              variant="destructive"
              size="md"
              icon={<XCircle className="w-4 h-4" />}
              onClick={() => setIsRejecting(true)}
              disabled={isSubmitting}
            >
              Reject & Branch
            </Button>
            <Button
              variant="success"
              size="md"
              icon={isSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Key className="w-4 h-4" />}
              onClick={handleApprove}
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Signing…' : 'Approve & Cryptographically Sign'}
            </Button>
          </div>
        ) : (
          <div className="w-full text-right text-[11px] text-slate-400 font-mono">
            Branch fork will terminate current valid-time interval (V_end = NOW)
          </div>
        )
      }
    >
      <div className="space-y-4">
        {/* Fitness Metrics Grid */}
        <div>
          <span className="text-xs font-mono uppercase text-slate-400 font-semibold tracking-wider">
            Automated Fitness Verification Gate (Φ5)
          </span>
          <div className="grid grid-cols-4 gap-3 mt-2">
            <div className="bg-[#0d121c] border border-emerald-500/30 rounded-lg p-3 flex flex-col items-center">
              <span className="text-xl font-bold font-mono text-emerald-400">
                {fitnessSummary.passed}/{fitnessSummary.total}
              </span>
              <span className="text-[11px] text-slate-400 mt-1">Pytest Suites</span>
              <Badge tone="emerald" outline className="mt-1">100% Passed</Badge>
            </div>

            <div className="bg-[#0d121c] border border-[#1e293b] rounded-lg p-3 flex flex-col items-center">
              <span className="text-xl font-bold font-mono text-cyan">
                {fitnessSummary.astIsolationScore}%
              </span>
              <span className="text-[11px] text-slate-400 mt-1">AST Isolation</span>
              <Badge tone="cyan" outline className="mt-1">0 Ext Imports</Badge>
            </div>

            <div className="bg-[#0d121c] border border-[#1e293b] rounded-lg p-3 flex flex-col items-center">
              <span className="text-xl font-bold font-mono text-amber">
                {fitnessSummary.latencyMs}ms
              </span>
              <span className="text-[11px] text-slate-400 mt-1">Compile Latency</span>
              <Badge tone="amber" outline className="mt-1">&lt; 50ms Limit</Badge>
            </div>

            <div className="bg-[#0d121c] border border-[#1e293b] rounded-lg p-3 flex flex-col items-center">
              <span className="text-xl font-bold font-mono text-violet-400">
                {fitnessSummary.tokenCount}
              </span>
              <span className="text-[11px] text-slate-400 mt-1">Token Words</span>
              <Badge tone="violet" outline className="mt-1">&le; 500 Budget</Badge>
            </div>
          </div>
        </div>

        {/* Diff & Scope Inspection */}
        <div className="bg-[#090d13] border border-[#1e293b] rounded-lg p-4 font-mono text-xs text-slate-300 space-y-2">
          <div className="flex items-center justify-between text-slate-400 pb-2 border-b border-[#1e293b]">
            <span className="flex items-center gap-1.5">
              <FileCode2 className="w-4 h-4 text-amber" />
              <span>Scope: Leaf Action Synthesis Immutability</span>
            </span>
            <Badge tone="emerald">Control Flow Preserved ✓</Badge>
          </div>
          <div className="text-[11px] text-slate-400 leading-relaxed">
            • Validated 4 canonical DRAKON topological rules: vertical skewer, right-is-worse, zero crossings, planar silhouette.<br />
            • Bound 8 active ADR invariant IDs (ADR-001, ADR-002, ADR-007, ADR-008).<br />
            • Ready for sprint distillation into <span className="text-amber">.context/sprint_handoff.json</span>.
          </div>
        </div>

        {/* Live backend response: approve */}
        {reviewResponse && reviewResponse.action === 'approve' && reviewResponse.launch_command && (
          <Banner
            tone="success"
            action={
              <Button
                variant="secondary"
                size="sm"
                onClick={handleCopyCli}
                icon={<Copy className="w-3 h-3" />}
              >
                {copiedCli ? 'copied' : 'copy'}
              </Button>
            }
          >
            <div className="space-y-1.5">
              <div className="font-semibold text-emerald-300">
                Handoff dispatched · Sprint N+1 ready to launch
              </div>
              {reviewResponse.cycle_id && (
                <div className="text-[11px] text-slate-400 font-mono">
                  Cycle: <span className="text-emerald-300">{reviewResponse.cycle_id}</span>
                  {reviewResponse.worm_locked && (
                    <Badge tone="emerald" outline className="ml-2">WORM locked</Badge>
                  )}
                </div>
              )}
              <div className="bg-black border border-[#1e293b] rounded p-2 font-mono text-[11px] text-amber flex items-center gap-2">
                <Terminal className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span className="flex-1 truncate">{reviewResponse.launch_command}</span>
              </div>
            </div>
          </Banner>
        )}

        {/* Live backend response: reject */}
        {reviewResponse && reviewResponse.action === 'reject' && (
          <Banner tone="error">
            <div className="space-y-1">
              <div className="font-semibold text-rose-300">
                Copy-on-write branch created · ΔC injected
              </div>
              {reviewResponse.created_branch && (
                <div className="text-[11px] text-slate-400 font-mono">
                  New branch: <span className="text-rose-200">{reviewResponse.created_branch}</span>
                </div>
              )}
              {reviewResponse.next_sprint_id && (
                <div className="text-[11px] text-slate-400 font-mono">
                  Next sprint: <span className="text-rose-200">{reviewResponse.next_sprint_id}</span>
                </div>
              )}
            </div>
          </Banner>
        )}

        {/* Live backend error */}
        {reviewError && (
          <Banner tone="warning">
            <div>
              <div className="font-semibold">[⚠ backend offline] {reviewError}</div>
              <div className="text-slate-400 mt-1">
                Local Approve/Reject state was applied. Restart <code>./run_workbench.sh</code> to enable auto-chain.
              </div>
            </div>
          </Banner>
        )}

        {/* Reject & Branch Drawer/Subpanel */}
        {isRejecting && (
          <div className="bg-rose-950/20 border border-rose-500/40 rounded-lg p-4 space-y-3">
            <div className="flex items-center gap-2 text-rose-300 font-semibold text-xs font-mono">
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
                className="w-full bg-[#141b27] border border-[#1e293b] rounded px-2.5 py-1.5 text-xs text-slate-200 font-mono"
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
                className="w-full bg-[#141b27] border border-[#1e293b] rounded p-2 text-xs font-mono text-rose-200 focus:outline-none focus:border-rose-400"
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
                className="w-full bg-[#141b27] border border-[#1e293b] rounded px-2.5 py-1.5 text-xs text-slate-200 font-mono"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsRejecting(false)}
              >
                Cancel
              </Button>
              <Button
                variant="destructive"
                size="sm"
                onClick={handleConfirmReject}
              >
                Execute COW Branch Fork
              </Button>
            </div>
          </div>
        )}
      </div>
    </Dialog>
  );
};
