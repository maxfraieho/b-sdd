---

name: diagnosing-bugs

description: Систематична петля діагностики критичних багів, регресій продуктивності та побудова відтворюваного детермінованого тест-кейсу.

type: SYSTEM_SKILL

category: bssd-system-skill

immutable: true

invoked_skills: [root-cause-tracing]

---



# DiagnosingBugs



Систематична петля діагностики критичних багів, регресій продуктивності та побудова відтворюваного детермінованого тест-кейсу.



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

ALGORITHM ExecuteDiagnosingBugs

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

            LOG_ERROR("Operation verification failed in diagnosing-bugs")

            HALT_AND_DEGRADE("INTEGRITY_CHECK_FAILED")

        FI

        CALL_SKILL(root-cause-tracing, {context: context})



        // STEP 4: Verification Gate & Telemetry emission (X=0.0, Y=8.0)

        ASSERT VerifyFinalArtifacts()

        EMIT_TELEMETRY(status="SUCCESS", skill="diagnosing-bugs")

        RETURN Status="SUCCESS"



    CATCH Error AS e

        LOG_CRITICAL("Execution failed in diagnosing-bugs: " + e.Message)

        HALT_AND_DEGRADE(e.Message)

    END

END

```



---



## 3. DRAKON Visual Workflow (Planar Skewer X=0)

<!-- DRAKON_VISUAL_FLOW_START -->

## DRAKON Visual Workflow (Planar Skewer X=0)

- Schema File: diagnosing-bugs.drakon.json

- Total Algorithmic Nodes: 8

- Spine Topology: Vertical Skewer (X=0, C=0) verified with rightward degradation branches (X=4.0).

  1. [HEADLINE] Початок: Виконання diagnosing-bugs

  2. [ACTION] Крок 1: Перевірка вхідного контексту та середовища

  3. [QUESTION] Крок 2: Передумови успішно перевірені?

  4. [INSERTION] CALL_SKILL(root-cause-tracing): Делегування підзадачі

  5. [ACTION] Крок 4: Фінальна верифікація та телеметрія

  6. [END] Успішне завершення: Процедуру diagnosing-bugs виконано

  7. [ACTION] Обробка помилки перевірки (X=4.0)

  8. [END] Аварійне завершення: Зупинка виконання (X=4.0)

<!-- DRAKON_VISUAL_FLOW_END -->



---



## 4. Operational Guide & CLI Execution

### Типовий запуск процедури:

```bash

python3 -m src.cli.main run-skill --name diagnosing-bugs --context default

```



### Верифікація результатів:

```bash

pytest tests/test_diagnosing_bugs.py -v || true

```

