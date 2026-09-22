---

name: laya-decision-router

description: Суб-40мс не-авторегресивна System 1 класифікація задач, оцінка ризиків порушення ADR та маршрутизація скілів на Pixel 7.

type: SYSTEM_SKILL

category: bssd-system-skill

immutable: true

invoked_skills: [b-sdd, intent-continuity]

---



# LayaDecisionRouter



Суб-40мс не-авторегресивна System 1 класифікація задач, оцінка ризиків порушення ADR та маршрутизація скілів на Pixel 7.



---



## 1. Architectural Context & Negative Invariants

- **ADR Compliance**: Відповідає ADR-015 (Taxonomy & Immutability) та ADR-016 (Algorithmic Pseudocode & Visual DRAKON Round-Trip).

- **Negative Invariants**:

  - **NEVER** порушувати топологічні обмеження головного шампура (X = 0.0, C = 0).

  - **NEVER** спрямовувати обробники деградації або помилок ліворуч від шампура (дозволено строго X = 4.0).

  - **NEVER** завершувати виконання без емісії телеметрії та реєстрації статусу.



---



## 2. Algorithmic Workflow (ADR-016 Standard)



```text

ALGORITHM ExecuteLayaDecisionRouter

INPUT:

    context: dict

    options: dict

OUTPUT:

    status: str ("SUCCESS" | "FAILED" | "DEGRADED")



BEGIN

    TRY

        ASSERT context != null



        // STEP 1: Pre-execution validation along Vertical Skewer (X=0.0, Y=2.0)

        EXECUTE ValidateEnvironmentPreconditions(context)



        // STEP 2: Main vertical spine execution (X=0.0, Y=4.0)

        EXECUTE PerformCoreOperation(options)



        // STEP 3: Question Node - Invariant verification (X=0.0, Y=6.0)

        IF VerifyOperationIntegrity() THEN

            CONTINUE along Vertical Skewer (X=0.0)

        ELSE

            BRANCH_RIGHT(X=4.0, Y=6.0): Failure/Degradation

            LOG_ERROR("Operation verification failed in laya-decision-router")

            HALT_AND_DEGRADE("INTEGRITY_CHECK_FAILED")

        FI

        CALL_SKILL(b-sdd, {context: context})



        // STEP 4: Verification Gate & Telemetry emission (X=0.0, Y=8.0)

        ASSERT VerifyFinalArtifacts()

        EMIT_TELEMETRY(status="SUCCESS", skill="laya-decision-router")

        RETURN Status="SUCCESS"



    CATCH Error AS e

        LOG_CRITICAL("Execution failed in laya-decision-router: " + e.Message)

        HALT_AND_DEGRADE(e.Message)

    END

END

```



---



## 3. DRAKON Visual Workflow (Planar Skewer X=0)

<!-- DRAKON_VISUAL_FLOW_START -->

## DRAKON Visual Workflow (Planar Skewer X=0)

- Schema File: laya-decision-router.drakon.json

- Total Algorithmic Nodes: 8

- Spine Topology: Vertical Skewer (X=0, C=0) verified with rightward degradation branches (X=4.0).

  1. [HEADLINE] Початок: Виконання laya-decision-router

  2. [ACTION] Крок 1: Перевірка вхідного контексту та середовища

  3. [QUESTION] Крок 2: Передумови успішно перевірені?

  4. [INSERTION] CALL_SKILL(b-sdd): Делегування підзадачі

  5. [ACTION] Крок 4: Фінальна верифікація та телеметрія

  6. [END] Успішне завершення: Процедуру laya-decision-router виконано

  7. [ACTION] Обробка помилки перевірки (X=4.0)

  8. [END] Аварійне завершення: Зупинка виконання (X=4.0)

<!-- DRAKON_VISUAL_FLOW_END -->



---



## 4. Operational Guide & CLI Execution

### Типовий запуск процедури:

```bash

python3 -m src.cli.main run-skill --name laya-decision-router --context default

```



### Верифікація результатів:

```bash

pytest tests/test_laya_decision_router.py -v || true

```

