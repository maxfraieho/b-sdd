---
name: b-sdd-sprint-distiller
description: Автономна дистиляція звітів закриття спринту, оновлення кумулятивного Mega-ADR, реєстрація WORM-запису в Utopia DB та збереження в нестираємий архів Google Drive.
type: SYSTEM_SKILL
category: bssd-system-skill
immutable: true
invoked_skills: [test-driven-development, b-sdd-notebooklm-sync, safe-refactor]
---

# b-sdd-sprint-distiller

Автономна дистиляція звітів закриття спринту, оновлення кумулятивного Mega-ADR, реєстрація WORM-запису в Utopia DB та збереження в нестираємий архів Google Drive.

---

## 1. Architectural Context & Negative Invariants
- **ADR Compliance**: Відповідає ADR-001 (Bitemporal WORM Ledger), ADR-005 (Active Rules Budget < 500 words), ADR-010 (Tripartite ADR Ontology), ADR-015 (System Skill Taxonomy) та ADR-016 (Tripartite Skill Architecture & Pseudocode Standard).
- **Negative Invariants**:
  - **NEVER** видаляти або перезаписувати історичні бітемпоральні WORM-записи.
  - **NEVER** перевищувати ліміт активних правил у 500 слів у `.context/active_rules.md`.
  - **NEVER** додавати поодинокі сирі звіти як постійні джерела в NotebookLM (уникати ліміту 50 джерел).
  - **NEVER** спрямовувати обробники деградації або помилок ліворуч від шампура (дозволено строго X = 4.0).

---

## 2. Algorithmic Workflow (ADR-016 Standard)

<!-- ALGORITHMIC_PSEUDOCODE_START -->
ALGORITHM DistillSprintKnowledge
INPUT:
    sprint_id: str
    raw_report_path: str
OUTPUT:
    status: str ("SUCCESS" | "FAILED" | "DEGRADED")
BEGIN
    TRY
        ASSERT FileExists(raw_report_path)
        
        // STEP 1: Semantic extraction from raw report (X=0.0, Y=2.0)
        EXECUTE raw_data := ExtractMetricsAndDecisions(raw_report_path)
        
        // STEP 2: Tripartite classification according to ADR-010 (X=0.0, Y=4.0)
        EXECUTE data_adr := ClusterDecisions(raw_data, "DataADR")
        EXECUTE skill_adr := ClusterDecisions(raw_data, "SkillADR")
        EXECUTE spec_adr := ClusterDecisions(raw_data, "SpecADR")
        
        // STEP 3: Question Node - Invariant superseding verification (X=0.0, Y=6.0)
        IF DetectSupersededInvariants(raw_data) THEN
            EXECUTE ApplyBitemporalSuperseding("docs/ADR/B_SDD_MEGA_ADR_MASTER.md")
        ELSE
            CONTINUE along Vertical Skewer (X=0.0)
        FI
        
        // STEP 4: Append distilled quantum to Mega-ADR (X=0.0, Y=8.0)
        EXECUTE AppendDistilledSprintNode("docs/ADR/B_SDD_MEGA_ADR_MASTER.md", sprint_id, raw_data)
        
        // STEP 5: Commit immutable WORM record (X=0.0, Y=10.0)
        EXECUTE worm_id := CommitToUtopiaWORM(sprint_id, raw_data)
        ASSERT worm_id != null
        
        // STEP 6: Replicate to permanent archive (X=0.0, Y=12.0)
        EXECUTE ReplicateArchive(raw_report_path, sprint_id)
        
        // STEP 7: Question Node - Rule budget verification (X=0.0, Y=14.0)
        IF WordCount(".context/active_rules.md") >= 500 THEN
            BRANCH_RIGHT(X=4.0, Y=14.0): Budget Overflow
            CALL_SKILL(safe-refactor, {target: ".context/active_rules.md", max_words: 490})
        ELSE
            CONTINUE along Vertical Skewer (X=0.0)
        FI
        
        // STEP 8: Synchronize SSoT in NotebookLM (X=0.0, Y=16.0)
        CALL_SKILL(b-sdd-notebooklm-sync, {source: "docs/ADR/B_SDD_MEGA_ADR_MASTER.md"})
        
        EMIT_TELEMETRY(status="SUCCESS", skill="b-sdd-sprint-distiller")
        RETURN "SUCCESS"
        
    CATCH Error AS e
        BRANCH_RIGHT(X=4.0): Failure Handling
        LOG_CRITICAL("Sprint distillation failed: " + e.Message)
        HALT_AND_DEGRADE(e.Message)
    END
END
<!-- ALGORITHMIC_PSEUDOCODE_END -->

---

## 3. DRAKON Visual Workflow (Planar Skewer X=0)

<!-- DRAKON_VISUAL_FLOW_START -->
- Schema File: b-sdd-sprint-distiller.drakon.json
- Total Algorithmic Nodes: 9
- Spine Topology: Vertical Skewer (X=0, C=0) verified with rightward degradation branches (X=4.0).
  1. [HEADLINE] Початок: Виконання b-sdd-sprint-distiller (X=0, Y=0)
  2. [ACTION] Крок 1: Семантична екстракція метрик та рішень (X=0, Y=2)
  3. [ACTION] Крок 2: Класифікація за тріадою ADR-010 (X=0, Y=4)
  4. [QUESTION] Крок 3: Виявлено заміщені інваріанти? (X=0, Y=6)
  5. [ACTION] Крок 4: Дописування кванту знань у Mega-ADR (X=0, Y=8)
  6. [ACTION] Крок 5: Реєстрація бітемпорального WORM-запису (X=0, Y=10)
  7. [QUESTION] Крок 6: Бюджет active_rules < 500 слів? (X=0, Y=12)
  8. [INSERTION] CALL_SKILL(b-sdd-notebooklm-sync): Оновлення SSoT (X=0, Y=14)
  9. [END] Успішне завершення: Дистиляцію спринту завершено (X=0, Y=16)
<!-- DRAKON_VISUAL_FLOW_END -->

---

## 4. Operational Guide & CLI Execution

### Типовий запуск процедури:
```bash
python3 scripts/distill_sprint.py --sprint-id sprint_031 --raw reports/sprint_031_closure_raw.md
```

### Верифікація результатів:
```bash
pytest tests/test_sprint_distiller.py -v
```
