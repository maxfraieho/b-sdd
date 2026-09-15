# Spec 002: Utopia DB Bitemporal Store & Knowledge Graph Adapter

## Objective
Connect B-SDD to Utopia DB over SSH/Docker, manage the `intent_store` bitemporal schema, and synchronize architectural entities and facts into dedicated Knowledge Bases.

## Invariants
- Bitemporal DAG: all intent nodes must have `valid_from`, `valid_to`, `system_from`, `system_to`.
- Atomic supersession: stored procedure `register_and_supersede_intent` must atomically terminate superseded records (`valid_to = NOW`).
- Schema compliance: strict adherence to Utopia Knowledge Graph schema (`canonical_name`, `specific_type`, `type_id`, `attrs`, `valid_from_precision`).
