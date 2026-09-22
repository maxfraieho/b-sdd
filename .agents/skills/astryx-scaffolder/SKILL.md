---
name: astryx-scaffolder
description: Генерація компонентів Astryx Cockpit UI, інтерактивних віджетів ДРАКОН-полотна, телеметричних панелей та мультипроєктного середовища оператора.
type: SYSTEM_SKILL
category: bssd-system-skill
immutable: true
invoked_skills: [b-sdd]
---

# Astryx Scaffolder
Системний скіл проєкту B-SDD для створення UI-компонентів робочого місця оператора (Astryx Cockpit / Copilot). Відповідає за дотримання ергономічних вимог ADR-009 (Astryx Design System) та ADR-010 (мультипроєктне перемикання), генерацію планарних віджетів полотна ДРАКОН з гарантіями 
C=0, X=0
.

--------------------------------------------------------------------------------

1. Architectural Context & Negative Invariants
ADR Compliance
: ADR-008 (планарність), ADR-009 (дизайн-система Astryx), ADR-015 (системний скіл), ADR-016.
Negative Invariants
:
NEVER
 порушувати зональну ізоляцію: Zone A (проєкти), Zone B (полотно ДРАКОН), Zone C (ADR/телеметрія).
NEVER
 генерувати компоненти без підтримки темної теми та клавіатурної ергономіки (keyboard-first).
NEVER
 підключати зовнішні важкі CSS-бібліотеки, що конфліктують з Tailwind/shadcn та CSS-змінними теми.
NEVER
 ігнорувати валідацію планарності генерованих canvas-елементів.

--------------------------------------------------------------------------------

2. Algorithmic Workflow (ADR-016 Standard)
ALGORITHM ExecuteAstryxScaffolder
INPUT:
    component_name: str
    component_zone: str ("A" | "B" | "C")
    category: str ("canvas" | "telemetry" | "workbench")
OUTPUT:
    status: str ("SUCCESS" | "FAILED" | "DEGRADED")
    output_path: str

BEGIN
    TRY
        ASSERT component_name != ""
        ASSERT component_zone IN ["A", "B", "C"]

        // STEP 1: Main vertical spine - Zone & Layout Verification (X=0.0, Y=2.0)
        EXECUTE ValidateZoneConstraints(component_zone, category)

        // STEP 2: Sub-skill composition - Enforce B-SDD Ergonomic Invariants (X=0.0, Y=4.0)
        CALL_SKILL(b-sdd, {action: "verify_design_tokens", zone: component_zone})

        // STEP 3: Question Node - Token & Theme Compliance (X=0.0, Y=6.0)
        IF VerifyAstryxDesignTokens() THEN
            CONTINUE along Vertical Skewer (X=0.0)
        ELSE
            BRANCH_RIGHT(X=4.0, Y=6.0): Failure/Degradation
            LOG_ERROR("Component violates Astryx Design System tokens")
            HALT_AND_DEGRADE("DESIGN_TOKEN_VIOLATION")
        FI

        // STEP 4: Main vertical spine - Component Scaffolding (X=0.0, Y=8.0)
        EXECUTE ScaffoldUiComponent(component_name, category)

        // STEP 5: Verification & Telemetry (X=0.0, Y=10.0)
        ASSERT VerifyComponentExport(component_name)
        EMIT_TELEMETRY(status="SUCCESS", component=component_name)
        RETURN Status="SUCCESS"

    CATCH Error AS e
        LOG_CRITICAL("Astryx scaffolding failed: " + e.Message)
        HALT_AND_DEGRADE(e.Message)
    END
END

text

--------------------------------------------------------------------------------

<!-- DRAKON_VISUAL_FLOW_START -->
## 3. DRAKON Visual Workflow (Planar Skewer X=0)
Schema File:
 astryx-scaffolder.drakon.json
Total Algorithmic Nodes:
 7
Spine Topology:
 Vertical Skewer (X=0, C=0) verified with rightward degradation branches (X=4.0).
[HEADLINE] Початок: Генерація компонента Astryx Cockpit
[ACTION] Крок 1: Перевірка зональних обмежень (Zone A/B/C)
[INSERTION] CALL_SKILL(b-sdd): Крок 2: Перевірка токенів дизайн-системи ADR-009
[QUESTION] Крок 3: Токени та темна тема відповідають стандарту?
[ACTION] Крок 4: Створення вихідного коду компонента та тестів
[END] Успішне завершення: Компонент успішно згенеровано
[END] Аварійне завершення: Порушення токенів Astryx (X=4.0)
<!-- DRAKON_VISUAL_FLOW_END -->

---

4. Operational Guide & CLI Execution
Генерація віджета візуального полотна ДРАКОН:
python3 ~/.agents/skills/astryx-scaffolder/scripts/scaffold_component.py \
  --name DrakonVisualFlow \
  --category canvas \
  --zone B \
  --output-dir b-sdd-ui/src/components

bash
Генерація панелі телеметрії оператора:
python3 ~/.agents/skills/astryx-scaffolder/scripts/scaffold_component.py \
  --name MeshTelemetryInspector \
  --category telemetry \
  --zone C \
  --output-dir b-sdd-ui/src/components

bash

