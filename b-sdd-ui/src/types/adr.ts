// src/types/adr.ts

export type AdrStatus = 'proposed' | 'accepted' | 'rejected' | 'deprecated' | 'superseded';

export interface AdrInvariant {
  id: string;
  statement: string;
  severity?: 'mandatory' | 'recommended' | 'critical';
  component?: string;
}

export interface BitemporalAdr {
  id: string; // e.g. "ADR-008"
  title: string;
  status: AdrStatus;
  component: string;
  date: string;
  valid_from: string; // ISO string for Tv_start
  valid_to: string | null; // ISO string for Tv_end, null if currently active
  tx_time: string; // ISO string for Tt (transaction time recorded in database)
  supersedes: string | null; // e.g. "ADR-001"
  superseded_by: string | null; // e.g. "ADR-013"
  invariants: AdrInvariant[];
  context: string;
  decision_outcome: string;
  content?: string;
  file_path?: string;
}

export interface BitemporalFilter {
  validTime: string; // T_v timestamp to evaluate active rules
  transactionTime: string; // T_t timestamp to snapshot database state
}
