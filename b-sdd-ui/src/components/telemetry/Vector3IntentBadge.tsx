import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, ShieldCheck } from 'lucide-react';
import { Vector3IntentState } from '../../types/cluster-health';

interface Vector3IntentBadgeProps {
  state?: Partial<Vector3IntentState>;
}

const DEFAULT_STATE: Vector3IntentState = {
  cosine_alignment: 0.98,
  threshold: 0.82,
  verdict: 'VERDICT_INTENT_ALIGNED',
  allow_commit: true,
  latency_ms: 38.4,
  missing_invariants: []
};

export const Vector3IntentBadge: React.FC<Vector3IntentBadgeProps> = ({ state = {} }) => {
  const current: Vector3IntentState = { ...DEFAULT_STATE, ...state };
  const isAligned = current.verdict === 'VERDICT_INTENT_ALIGNED';
  const isWarning = current.verdict === 'VERDICT_INTENT_DRIFT_WARNING';

  const badgeColor = isAligned
    ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
    : isWarning
    ? 'bg-amber-500/10 border-amber-500/30 text-amber-400'
    : 'bg-rose-500/10 border-rose-500/30 text-rose-400';

  const Icon = isAligned ? CheckCircle2 : isWarning ? AlertTriangle : XCircle;

  return (
    <div className={`inline-flex items-center space-x-2 px-2.5 py-1 rounded-lg border text-xs font-medium ${badgeColor}`}>
      <ShieldCheck className="w-3.5 h-3.5" />
      <div className="flex items-center space-x-1.5">
        <span className="font-semibold">Dual-Gate Vector 3:</span>
        <span className="font-mono">S_intent = {current.cosine_alignment.toFixed(2)}</span>
      </div>
      <Icon className="w-3.5 h-3.5" />
    </div>
  );
};
