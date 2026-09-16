// src/types/sprint.ts

export type HitlPhaseId =
  | 'phi_1'
  | 'phi_2'
  | 'phi_3'
  | 'phi_4'
  | 'phi_5'
  | 'phi_6'
  | 'phi_7';

export type PhaseStatus = 'pending' | 'running' | 'completed' | 'blocked' | 'rejected';

export interface HitlPhase {
  id: HitlPhaseId;
  index: number;
  symbol: string; // e.g. "Φ1"
  name: string; // e.g. "Intent Framing"
  description: string;
  hitlLevel: string; // e.g. "100% Operator", "0% Automated"
  status: PhaseStatus;
  validationGate: string;
}

export interface FitnessTestSummary {
  total: number;
  passed: number;
  failed: number;
  durationSeconds: number;
  astIsolationScore: number; // 0 to 100%
  latencyMs: number;
  tokenCount: number;
}

export interface RejectAndBranchPayload {
  rejectedPhase: HitlPhaseId;
  rollbackDepth: number; // sprints to roll back
  negativeInvariants: string[]; // ΔC vector
  rationale: string;
  timestamp: string;
}

export interface SprintState {
  sprintId: string;
  projectName: string;
  currentPhase: HitlPhaseId;
  phases: HitlPhase[];
  fitnessSummary: FitnessTestSummary;
  isReviewGateOpen: boolean;
  deltaC: string[];
  handoffPayload?: {
    sprint_id: string;
    next_tasks: string[];
    launch_command: string;
    markdown_preview: string;
  };
}
