"""
B-SDD (Bitemporal Spec-Driven Development) Utopia DB Adapter
Universal bitemporal store and knowledge graph adapter for managing
architectural intents, DAG supersessions, and ontology relations in Utopia DB.
Operates using 100% Pure Python Standard Library.
"""
import os
import json
import uuid
import hashlib
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger("BSDD_UtopiaDBAdapter")

# Default connection parameters
UTOPIA_HOST = os.getenv("UTOPIA_DB_HOST", "192.168.3.251")
UTOPIA_SSH_PORT = int(os.getenv("UTOPIA_SSH_PORT", "9922"))
UTOPIA_SSH_USER = os.getenv("UTOPIA_SSH_USER", "root")
UTOPIA_SSH_PASS = os.getenv("UTOPIA_SSH_PASS", "podroid")
UTOPIA_CONTAINER = os.getenv("UTOPIA_CONTAINER", "utopia-db")
UTOPIA_DB_NAME = os.getenv("UTOPIA_DB_NAME", "utopia")
UTOPIA_DB_USER = os.getenv("UTOPIA_DB_USER", "utopia")
# Dedicated B-SDD Knowledge Base ID
UTOPIA_KB_ID = os.getenv("UTOPIA_KB_ID", "01a08474-0000-7000-8000-000000000001")

NS_BSDD = uuid.UUID("b17e4040-0000-7000-8000-000000000001")


class UtopiaDBAdapter:
    """Universal client adapter for communicating with Utopia DB bitemporal store and knowledge graph."""

    def __init__(
        self,
        host: str = UTOPIA_HOST,
        ssh_port: int = UTOPIA_SSH_PORT,
        ssh_user: str = UTOPIA_SSH_USER,
        ssh_pass: str = UTOPIA_SSH_PASS,
        container: str = UTOPIA_CONTAINER,
        db_name: str = UTOPIA_DB_NAME,
        db_user: str = UTOPIA_DB_USER,
        kb_id: str = UTOPIA_KB_ID,
    ):
        self.host = host
        self.ssh_port = ssh_port
        self.ssh_user = ssh_user
        self.ssh_pass = ssh_pass
        self.container = container
        self.db_name = db_name
        self.db_user = db_user
        self.kb_id = kb_id

    @staticmethod
    def _sql_esc(v: Optional[str]) -> str:
        """Escapes string literal for single-quoted SQL query."""
        if v is None:
            return "NULL"
        return "'" + v.replace("'", "''") + "'"

    def execute_sql(self, sql: str, timeout: float = 30.0) -> str:
        """
        Executes SQL script inside Docker container utopia-db via sshpass.
        Returns stdout if successful, raises RuntimeError otherwise.
        """
        cmd = [
            "sshpass", "-p", self.ssh_pass,
            "ssh", "-p", str(self.ssh_port),
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=5",
            f"{self.ssh_user}@{self.host}",
            f"docker exec -i {self.container} psql -U {self.db_user} -d {self.db_name} -t -A"
        ]
        try:
            res = subprocess.run(
                cmd,
                input=sql,
                text=True,
                capture_output=True,
                timeout=timeout,
                check=False
            )
            if res.returncode != 0:
                err_msg = res.stderr.strip() or res.stdout.strip()
                raise RuntimeError(f"Utopia DB execution failed (code {res.returncode}): {err_msg}")
            return res.stdout
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Connection to Utopia DB host {self.host}:{self.ssh_port} timed out after {timeout}s.")
        except FileNotFoundError:
            raise RuntimeError("sshpass or ssh client not found on local host.")

    def test_connection(self) -> bool:
        """Verifies connection to Utopia DB."""
        try:
            out = self.execute_sql("SELECT 1;")
            return "1" in out
        except Exception as ex:
            logger.warning(f"Utopia DB offline or unreachable: {ex}")
            return False

    def init_schema(self) -> bool:
        """
        Idempotently provisions schema intent_store, tables, indexes,
        and stored procedures for bitemporal DAG operations.
        """
        sql = """
        CREATE SCHEMA IF NOT EXISTS intent_store;

        CREATE TABLE IF NOT EXISTS intent_store.intent_nodes (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            intent_key TEXT NOT NULL,
            component TEXT NOT NULL,
            rule_type TEXT NOT NULL,
            scope TEXT NOT NULL,
            target_key TEXT NOT NULL,
            target_value TEXT NOT NULL,
            source_file TEXT NOT NULL,
            source_hash TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'accepted',
            valid_from TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            valid_to TIMESTAMPTZ NOT NULL DEFAULT 'infinity'::timestamptz,
            system_from TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            system_to TIMESTAMPTZ NOT NULL DEFAULT 'infinity'::timestamptz,
            metadata JSONB DEFAULT '{}'::jsonb
        );

        CREATE INDEX IF NOT EXISTS idx_intent_nodes_lookup
            ON intent_store.intent_nodes (intent_key, status, valid_to);

        CREATE TABLE IF NOT EXISTS intent_store.intent_supersessions (
            superseding_id UUID NOT NULL REFERENCES intent_store.intent_nodes(id) ON DELETE CASCADE,
            superseded_id UUID NOT NULL REFERENCES intent_store.intent_nodes(id) ON DELETE CASCADE,
            superseded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            reason TEXT,
            PRIMARY KEY (superseding_id, superseded_id)
        );

        CREATE OR REPLACE FUNCTION intent_store.register_and_supersede_intent(
            p_intent_key TEXT,
            p_component TEXT,
            p_rule_type TEXT,
            p_scope TEXT,
            p_target_key TEXT,
            p_target_value TEXT,
            p_source_file TEXT,
            p_source_hash TEXT,
            p_supersedes_key TEXT DEFAULT NULL,
            p_reason TEXT DEFAULT 'Superseded via B-SDD Compiler'
        ) RETURNS UUID AS $$
        DECLARE
            v_new_id UUID;
            v_old_rec RECORD;
        BEGIN
            INSERT INTO intent_store.intent_nodes (
                intent_key, component, rule_type, scope,
                target_key, target_value, source_file, source_hash
            ) VALUES (
                p_intent_key, p_component, p_rule_type, p_scope,
                p_target_key, p_target_value, p_source_file, p_source_hash
            ) RETURNING id INTO v_new_id;

            IF p_supersedes_key IS NOT NULL AND p_supersedes_key <> '' THEN
                FOR v_old_rec IN
                    SELECT id FROM intent_store.intent_nodes
                    WHERE intent_key = p_supersedes_key
                      AND status = 'accepted'
                      AND valid_to = 'infinity'::timestamptz
                LOOP
                    UPDATE intent_store.intent_nodes
                    SET status = 'superseded',
                        valid_to = CURRENT_TIMESTAMP,
                        system_to = CURRENT_TIMESTAMP
                    WHERE id = v_old_rec.id;

                    INSERT INTO intent_store.intent_supersessions (
                        superseding_id, superseded_id, superseded_at, reason
                    ) VALUES (
                        v_new_id, v_old_rec.id, CURRENT_TIMESTAMP, p_reason
                    ) ON CONFLICT DO NOTHING;
                END LOOP;
            END IF;

            RETURN v_new_id;
        END;
        $$ LANGUAGE plpgsql;
        """
        try:
            self.execute_sql(sql)
            return True
        except Exception as ex:
            logger.error(f"Failed to initialize intent_store schema: {ex}")
            return False

    def register_intent(
        self,
        intent_key: str,
        component: str,
        rule_type: str,
        scope: str,
        target_key: str,
        target_value: str,
        source_file: str,
        source_hash: str,
        supersedes_adr: Optional[str] = None,
        reason: str = "Registered via B-SDD Engine"
    ) -> Optional[str]:
        """Registers intent into intent_store.intent_nodes via stored procedure."""
        sql = f"""
        SELECT intent_store.register_and_supersede_intent(
            {self._sql_esc(intent_key)},
            {self._sql_esc(component)},
            {self._sql_esc(rule_type)},
            {self._sql_esc(scope)},
            {self._sql_esc(target_key)},
            {self._sql_esc(target_value)},
            {self._sql_esc(source_file)},
            {self._sql_esc(source_hash)},
            {self._sql_esc(supersedes_adr)},
            {self._sql_esc(reason)}
        );
        """
        try:
            out = self.execute_sql(sql)
            return out.strip()
        except Exception as ex:
            logger.error(f"Failed to register intent {intent_key}: {ex}")
            return None

    def sync_all_intents(self, intents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Synchronizes a list of intent records into intent_store on Utopia DB
        in a single batched transaction for high speed and network resilience.
        """
        statements: List[str] = ["BEGIN;"]
        supersessions_count = 0

        sorted_intents = sorted(
            intents,
            key=lambda x: (len(x.get("supersedes", [])), x["id"])
        )

        for it in sorted_intents:
            intent_key = it["id"]
            component = it.get("component", "core")
            source_file = it.get("source_file", "docs/adr")
            invariants = it.get("invariants", [])
            supersedes = it.get("supersedes", [])

            content_str = json.dumps(invariants, sort_keys=True, ensure_ascii=False)
            source_hash = hashlib.sha256(content_str.encode("utf-8")).hexdigest()

            target_val = json.dumps({
                "title": it.get("title", intent_key),
                "invariants": invariants
            }, ensure_ascii=False)

            sup_adr = supersedes[0] if supersedes else None
            if sup_adr:
                supersessions_count += 1
            reason = f"Supersedes {sup_adr}" if sup_adr else "Registered via B-SDD Intent Sync"

            statements.append(f"""
            SELECT intent_store.register_and_supersede_intent(
                {self._sql_esc(intent_key)},
                {self._sql_esc(component)},
                {self._sql_esc("architectural_decision" if "ADR" in intent_key else "specification")},
                {self._sql_esc("global" if component in ("global", "core") else component)},
                {self._sql_esc(intent_key)},
                {self._sql_esc(target_val)},
                {self._sql_esc(source_file)},
                {self._sql_esc(source_hash)},
                {self._sql_esc(sup_adr)},
                {self._sql_esc(reason)}
            );
            """)

        statements.append("COMMIT;")
        sql_batch = "\n".join(statements)

        try:
            self.execute_sql(sql_batch, timeout=60.0)
            return {
                "total": len(intents),
                "registered": len(intents),
                "supersessions": supersessions_count,
                "errors": 0
            }
        except Exception as ex:
            logger.error(f"Batch intent synchronization failed: {ex}")
            return {
                "total": len(intents),
                "registered": 0,
                "supersessions": 0,
                "errors": len(intents)
            }

    def fetch_active_intents(self, component: Optional[str] = None) -> List[Dict[str, Any]]:
        """Queries all active, non-superseded intents from intent_store."""
        where = "WHERE status = 'accepted' AND valid_to = 'infinity'::timestamptz"
        if component:
            where += f" AND component = {self._sql_esc(component)}"

        sql = f"""
        SELECT json_agg(t) FROM (
            SELECT id, intent_key, component, rule_type, scope, target_key, target_value, source_file
            FROM intent_store.intent_nodes
            {where}
            ORDER BY valid_from ASC
        ) t;
        """
        out = self.execute_sql(sql)
        if not out.strip() or out.strip() == "NULL":
            return []
        try:
            return json.loads(out)
        except Exception:
            return []

    def sync_to_knowledge_graph(self, intents: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Synchronizes ADR entities, system components, skills, and facts
        into the specified Utopia Knowledge Graph (KB ID).
        Conforms strictly to Utopia Knowledge Graph schema.
        """
        statements: List[str] = [
            "BEGIN;",
            f"-- B-SDD Utopia Knowledge Graph Synchronization for KB: {self.kb_id}"
        ]

        # Ensure required entity_types exist
        skill_type_uuid = str(uuid.uuid5(NS_BSDD, "entity_type:agent_skill"))
        adr_type_uuid = "ce1c9748-e163-5a41-86f0-fe6daaf53d6a"
        comp_type_uuid = "88b63c02-dfae-5609-9341-eaac1f210c52"

        statements.append(f"""
        INSERT INTO entity_types (id, kb_id, key, label, description)
        VALUES ('{skill_type_uuid}', '{self.kb_id}', 'agent_skill', 'Agent Procedural Skill', 'Specialized procedural agent skill or playbook')
        ON CONFLICT (kb_id, key) DO UPDATE SET label = EXCLUDED.label;
        """)

        # Ensure required relation_types exist
        impl_rel_uuid = "85dc78bb-95fc-5d9b-8293-eac5a8ce209e"  # implemented_by
        sup_rel_uuid = str(uuid.uuid5(NS_BSDD, "relation_type:supersedes"))
        req_rel_uuid = str(uuid.uuid5(NS_BSDD, "relation_type:requires_skill"))

        statements.append(f"""
        INSERT INTO relation_types (id, kb_id, key, label, temporal, kind, description)
        VALUES ('{sup_rel_uuid}', '{self.kb_id}', 'supersedes', 'supersedes', 'state', 'relation', 'Architectural decision supersession')
        ON CONFLICT (kb_id, key) DO UPDATE SET label = EXCLUDED.label;

        INSERT INTO relation_types (id, kb_id, key, label, temporal, kind, description)
        VALUES ('{req_rel_uuid}', '{self.kb_id}', 'requires_skill', 'requires skill', 'state', 'relation', 'Domain or ADR requires procedural skill')
        ON CONFLICT (kb_id, key) DO UPDATE SET label = EXCLUDED.label;
        """)

        adr_count = 0
        facts_count = 0

        for it in intents:
            doc_id = it["id"]
            adr_count += 1
            a_uuid = str(uuid.uuid5(NS_BSDD, doc_id))
            name = f"{doc_id}: {it.get('title', doc_id)}"
            summary = ("; ".join(it.get("invariants", []))[:300] or "Architecture decision")
            component = it.get("component", "core")
            adr_attrs = json.dumps({
                "code": doc_id,
                "title": it.get("title", doc_id),
                "summary": summary,
                "status": it.get("status", "ACTIVE")
            })

            statements.append(f"""
            INSERT INTO entities (id, kb_id, canonical_name, specific_type, type_id, attrs, type_source)
            VALUES ('{a_uuid}', '{self.kb_id}', {self._sql_esc(name)}, 'architecture_decision', '{adr_type_uuid}', {self._sql_esc(adr_attrs)}::jsonb, 'human')
            ON CONFLICT (id) DO UPDATE SET canonical_name = EXCLUDED.canonical_name, attrs = EXCLUDED.attrs;
            """)

            comp_uuid = str(uuid.uuid5(NS_BSDD, component))
            comp_attrs = json.dumps({"name": component, "summary": f"System component: {component}"})
            statements.append(f"""
            INSERT INTO entities (id, kb_id, canonical_name, specific_type, type_id, attrs, type_source)
            VALUES ('{comp_uuid}', '{self.kb_id}', {self._sql_esc(component)}, 'system_component', '{comp_type_uuid}', {self._sql_esc(comp_attrs)}::jsonb, 'extracted')
            ON CONFLICT (id) DO UPDATE SET attrs = EXCLUDED.attrs;
            """)

            fact_impl_id = str(uuid.uuid5(NS_BSDD, f"fact:{a_uuid}:{impl_rel_uuid}:{comp_uuid}"))
            statements.append(f"""
            INSERT INTO facts (id, kb_id, subject_id, predicate_id, object_id, valid_from, valid_from_precision)
            VALUES ('{fact_impl_id}', '{self.kb_id}', '{a_uuid}', '{impl_rel_uuid}', '{comp_uuid}', date_trunc('day', CURRENT_TIMESTAMP AT TIME ZONE 'UTC'), 'day')
            ON CONFLICT (id) DO NOTHING;
            """)
            facts_count += 1

            for sup in it.get("supersedes", []):
                sup_uuid = str(uuid.uuid5(NS_BSDD, sup))
                fact_sup_id = str(uuid.uuid5(NS_BSDD, f"fact:{a_uuid}:{sup_rel_uuid}:{sup_uuid}"))
                statements.append(f"""
                INSERT INTO facts (id, kb_id, subject_id, predicate_id, object_id, valid_from, valid_from_precision)
                VALUES ('{fact_sup_id}', '{self.kb_id}', '{a_uuid}', '{sup_rel_uuid}', '{sup_uuid}', date_trunc('day', CURRENT_TIMESTAMP AT TIME ZONE 'UTC'), 'day')
                ON CONFLICT (id) DO NOTHING;
                """)
                facts_count += 1

        # Register Core B-SDD Procedural Skills
        skills_meta = [
            ("skill:b-sdd", "B-SDD Architecture Skill", "Enforces bitemporal architectural invariants, ADR compliance, and pre-flight compilation."),
            ("skill:architecture-designer", "Architecture Designer Skill", "System design, ADR authoring, trade-off evaluation, and scalability planning."),
            ("skill:safe-refactor", "Safe Refactor Skill", "Restructures code while strictly preserving verified behavior and invariants."),
            ("skill:skill-creator", "Skill Creator Wizard", "Self-authoring wizard for crystallizing repeatable processes into agent skills."),
            ("skill:find-skills", "Skill Discovery Skill", "Discovery engine for locating and connecting installable agent capabilities.")
        ]
        for s_id, s_name, s_summary in skills_meta:
            s_uuid = str(uuid.uuid5(NS_BSDD, s_id))
            s_attrs = json.dumps({"skill_id": s_id, "summary": s_summary})
            statements.append(f"""
            INSERT INTO entities (id, kb_id, canonical_name, specific_type, type_id, attrs, type_source)
            VALUES ('{s_uuid}', '{self.kb_id}', {self._sql_esc(s_name)}, 'agent_skill', '{skill_type_uuid}', {self._sql_esc(s_attrs)}::jsonb, 'human')
            ON CONFLICT (id) DO UPDATE SET canonical_name = EXCLUDED.canonical_name, attrs = EXCLUDED.attrs;
            """)

        statements.append("COMMIT;")
        sql_batch = "\n".join(statements)
        self.execute_sql(sql_batch, timeout=30.0)

        return {
            "entities": adr_count + len(skills_meta),
            "facts": facts_count
        }
