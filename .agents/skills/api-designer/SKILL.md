---
name: api-designer
description: Архітектурне проектування REST/GraphQL API, створення специфікацій OpenAPI 3.1, моделювання ресурсів та валідація мок-контрактів.
type: PROJECT_SKILL
category: api-design
immutable: false
invoked_skills: []
---

# API Designer
Скіл для проектування масштабованих, консистентних інтерфейсів прикладного програмування (REST та GraphQL) з повною специфікацією згідно зі стандартом OpenAPI 3.1. Забезпечує моделювання життєвого циклу ресурсів, стандартизацію обробки помилок за RFC 7807, стратегії пагінації та версіонування.

--------------------------------------------------------------------------------

1. Architectural Context & Negative Invariants
ADR Compliance
: Відповідає ADR-015 (таксономія скілів) та ADR-016 (алгоритмічний псевдокод та ДРАКОН-ізоморфізм).
Negative Invariants
:
NEVER
 використовувати дієслова в шляхах ресурсів URIs (заборонено 
/getUser/{id}
, дозволено 
/users/{id}
).
NEVER
 повертати нетипізовані або неузгоджені структури помилок (обов'язкове дотримання RFC 7807 Problem Details).
NEVER
 ігнорувати семантику HTTP-статусів (заборонено повертати 200 OK з тілом 
{"error": ...}
).
NEVER
 публікувати API без попередньої перевірки валідності схеми лінтером Redocly (
npx @redocly/cli lint
).
NEVER
 створювати незворотні зміни без зміни версії або плану депрекації.

--------------------------------------------------------------------------------

2. Algorithmic Workflow (ADR-016 Standard)
ALGORITHM ExecuteApiDesigner
INPUT:
    domain_requirements: dict
    api_style: str ("REST" | "GraphQL")
OUTPUT:
    status: str ("SUCCESS" | "FAILED" | "DEGRADED")
    spec_path: str

BEGIN
    TRY
        ASSERT domain_requirements != null
        ASSERT api_style IN ["REST", "GraphQL"]

        // STEP 1: Main vertical spine - Resource Modeling (X=0.0, Y=2.0)
        EXECUTE ModelDomainResources(domain_requirements)

        // STEP 2: Main vertical spine - Endpoints & Schema Design (X=0.0, Y=4.0)
        EXECUTE DesignEndpointsAndSchemas(api_style)

        // STEP 3: Question Node - Schema Linting Verification (X=0.0, Y=6.0)
        IF ValidateOpenApiSpec() THEN
            CONTINUE along Vertical Skewer (X=0.0)
        ELSE
            BRANCH_RIGHT(X=4.0, Y=6.0): Failure/Degradation
            LOG_ERROR("OpenAPI 3.1 specification linting failed")
            HALT_AND_DEGRADE("INVALID_SPECIFICATION_SCHEMA")
        FI

        // STEP 4: Main vertical spine - Mock Server Verification (X=0.0, Y=8.0)
        EXECUTE RunContractMockVerification()

        // STEP 5: Verification & Telemetry (X=0.0, Y=10.0)
        ASSERT VerifyBackwardCompatibility()
        EMIT_TELEMETRY(status="SUCCESS", api_style=api_style)
        RETURN Status="SUCCESS"

    CATCH Error AS e
        LOG_CRITICAL("API design process failed: " + e.Message)
        HALT_AND_DEGRADE(e.Message)
    END
END

text

--------------------------------------------------------------------------------

<!-- DRAKON_VISUAL_FLOW_START -->
## 3. DRAKON Visual Workflow (Planar Skewer X=0)
Schema File:
 api-designer.drakon.json
Total Algorithmic Nodes:
 7
Spine Topology:
 Vertical Skewer (X=0, C=0) verified with rightward degradation branches (X=4.0).
[HEADLINE] Початок: Проектування API та OpenAPI специфікації
[ACTION] Крок 1: Аналіз домену та моделювання сутностей
[ACTION] Крок 2: Опис ендпоінтів та схем запитів/відповідей
[QUESTION] Крок 3: Специфікація OpenAPI валідна (linting pass)?
[ACTION] Крок 4: Запуск мок-сервера та валідація контрактів
[END] Успішне завершення: Специфікацію API узгоджено та верифіковано
[END] Аварійне завершення: Помилка валідації схеми API (X=4.0)
<!-- DRAKON_VISUAL_FLOW_END -->

---

4. Operational Guide & CLI Execution
Валідація OpenAPI 3.1 специфікації:
npx @redocly/cli lint openapi.yaml

bash
Запуск локального мок-сервера контрактів:
npx @stoplight/prism-cli mock openapi.yaml --port 4010

bash
Еталонний шаблон помилки RFC 7807 (JSON):
{
  "type": "https://api.b-sdd.local/errors/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "Field 'identifier' violates format constraints.",
  "instance": "/errors/req_10827"
}

json

