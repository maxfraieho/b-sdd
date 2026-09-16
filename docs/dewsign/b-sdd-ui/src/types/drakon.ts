// src/types/drakon.ts

export type DrakonNodeType =
  | 'headline'
  | 'header'
  | 'branch'
  | 'action'
  | 'question'
  | 'choice'
  | 'select'
  | 'silhouette_route'
  | 'address'
  | 'loopbegin'
  | 'loopend'
  | 'insertion'
  | 'end';

export type DrakonSeverity = 'normal' | 'mild' | 'degraded' | 'severe' | 'fatal';

export interface DrakonSemanticBinding {
  adr_invariant_id?: string;
  utopia_entity_id?: string;
  temporal_scope?: {
    valid_from?: string;
    valid_to?: string;
  };
  severity?: DrakonSeverity;
}

export interface DrakonEdgesIR {
  down: string | null;
  right: string | null;
  extra?: Record<string, string>;
}

export interface DrakonNodeIR {
  node_id: string;
  node_type: DrakonNodeType;
  label: string;
  edges: DrakonEdgesIR;
  semantic_binding?: DrakonSemanticBinding;
  x?: number;
  y?: number;
  branch_id?: number;
}

export interface DrakonSchemaIR {
  schema_version: string;
  name: string;
  params?: string;
  nodes: DrakonNodeIR[];
  branch_order?: string[];
  meta?: Record<string, unknown>;
}
