---
name: b-sdd-kindle-docs
description: Автономний конвеєр компіляції документації B-SDD в EPUB 3.0 та відправка на Amazon Kindle та резервний email через хост 192.168.3.184.
type: SYSTEM_SKILL
category: bssd-system-skill
immutable: true
invoked_skills: [b-sdd]
---

# B-SDD Kindle Docs Pipeline
Системний скіл для автоматизованого збирання 10 розділів посібника оператора B-SDD (
docs/user_guide/
) у валідний формат електронної книги EPUB 3.0 та її доставки на Amazon Kindle (
tukroschu@kindle.com
) з дублюванням на Gmail через сервіс 
send-to-kindle
 на вузлі 
192.168.3.184
.

--------------------------------------------------------------------------------

1. Architectural Context & Negative Invariants
ADR Compliance
: ADR-015 (системний скіл), ADR-016 (алгоритмічний псевдокод), ADR-002 (Pure Stdlib).
Negative Invariants
:
NEVER
 виконувати компіляцію на несинхронізованому стані git між хостами 
.161
 та 
.184
.
NEVER
 надсилати пошкоджені або неповні EPUB-файли (менше 10 розділів або відсутність TOC).
NEVER
 зберігати вхідні облікові дані пошти у відкритому вигляді всередині коду (використовувати pre-authorized OAuth2 або токени оточення).

--------------------------------------------------------------------------------

2. Algorithmic Workflow (ADR-016 Standard)
ALGORITHM ExecuteBSddKindleDocs
INPUT:
    recipient_email: str ("tukroschu@kindle.com")
    dry_run: bool
OUTPUT:
    status: str ("SUCCESS" | "FAILED" | "DEGRADED")
    epub_path: str

BEGIN
    TRY
        ASSERT recipient_email != ""

        // STEP 1: Sub-skill composition - Verify B-SDD state (X=0.0, Y=2.0)
        CALL_SKILL(b-sdd, {action: "verify_cluster_git_sync"})

        // STEP 2: Main vertical spine - Sync Git State to .184 (X=0.0, Y=4.0)
        EXECUTE SyncCodebaseToAggregatorHost("192.168.3.184")

        // STEP 3: Question Node - Remote Codebase Readiness (X=0.0, Y=6.0)
        IF VerifyRemoteClusterSync("192.168.3.184") THEN
            CONTINUE along Vertical Skewer (X=0.0)
        ELSE
            BRANCH_RIGHT(X=4.0, Y=6.0): Failure/Degradation
            LOG_ERROR("Git state sync between .161 and .184 failed")
            HALT_AND_DEGRADE("CLUSTER_SYNC_FAILED")
        FI

        // STEP 4: Main vertical spine - Compile EPUB 3.0 (X=0.0, Y=8.0)
        EXECUTE CompileEpubHandbook("docs/user_guide/")

        // STEP 5: Question Node - EPUB Validation Check (X=0.0, Y=10.0)
        IF ValidateEpubIntegrity(min_chapters=10) THEN
            CONTINUE along Vertical Skewer (X=0.0)
        ELSE
            BRANCH_RIGHT(X=4.0, Y=10.0): Failure/Degradation
            LOG_ERROR("EPUB compilation failed integrity or completeness check")
            HALT_AND_DEGRADE("INVALID_EPUB_ARTIFACT")
        FI

        // STEP 6: Main vertical spine - Dispatch to Kindle (X=0.0, Y=12.0)
        IF NOT dry_run THEN
            EXECUTE DispatchEmailViaOauth(recipient_email)
        FI

        // STEP 7: Verification & Telemetry (X=0.0, Y=14.0)
        EMIT_TELEMETRY(status="SUCCESS", recipient=recipient_email)
        RETURN Status="SUCCESS"

    CATCH Error AS e
        LOG_CRITICAL("Kindle docs pipeline failed: " + e.Message)
        HALT_AND_DEGRADE(e.Message)
    END
END

text

--------------------------------------------------------------------------------

<!-- DRAKON_VISUAL_FLOW_START -->
## 3. DRAKON Visual Workflow (Planar Skewer X=0)
Schema File:
 b-sdd-kindle-docs.drakon.json
Total Algorithmic Nodes:
 9
Spine Topology:
 Vertical Skewer (X=0, C=0) verified with rightward degradation branches (X=4.0).
[HEADLINE] Початок: Компіляція та доставка документації на Kindle
[INSERTION] CALL_SKILL(b-sdd): Крок 1: Верифікація стану кластера та синхронізації
[ACTION] Крок 2: Синхронізація git-репозиторію на вузол 192.168.3.184
[QUESTION] Крок 3: Синхронізація з віддаленим вузлом успішна?
[ACTION] Крок 4: Збирання 10 розділів посібника у формат EPUB 3.0
[QUESTION] Крок 5: EPUB-файл валідний та містить 10 розділів?
[ACTION] Крок 6: Відправка на Kindle через send_digest.py
[END] Успішне завершення: Документацію доставлено на Kindle
[END] Аварійне завершення: Помилка компіляції або доставки (X=4.0)
<!-- DRAKON_VISUAL_FLOW_END -->

---

4. Operational Guide & CLI Execution
Автономний запуск збірки та відправки з хоста .161:
bash /home/vokov/.agents/skills/b-sdd-kindle-docs/scripts/dispatch_on_184.sh

bash
Виконання прямої команди через SSH на вузлі .184:
ssh 192.168.3.184 "cd /home/vokov/projects/send-to-kindle && \
  uv run --with ebooklib --with markdown --with google-api-python-client --with google-auth-oauthlib \
  python3 bsdd_to_kindle.py"

bash
Запуск у режимі Dry-Run (без відправки email):
ssh 192.168.3.184 "cd /home/vokov/projects/send-to-kindle && \
  uv run --with ebooklib --with markdown python3 bsdd_to_kindle.py --dry-run"

bash

