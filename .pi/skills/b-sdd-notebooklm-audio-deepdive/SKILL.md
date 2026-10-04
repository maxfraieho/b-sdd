---
name: b-sdd-notebooklm-audio-deepdive
description: Автономна генерація максимального україномовного аудіоогляду (Deep Dive Podcast, AudioLength.LONG) з матеріалів записника Google NotebookLM через сервіс MCP NotebookLM.
type: SYSTEM_SKILL
category: bssd-system-skill
immutable: true
invoked_skills: [b-sdd, notebooklm, sequential-thinking]
---

# B-SDD NotebookLM Audio Deep Dive Generator (Maximal Ukrainian Podcast)

> **B-SDD Invariant (ADR-003 Rule of 2):** Кристалізовано в системний скіл після 2 повторних успішних застосувань та перевірки на інженерному контурі `192.168.3.184:8002`.

---

## 1. Архітектурні інваріанти та обмеження (Architectural Anchors & Strict Invariants)

- **Параметри аудіопереказу (NotebookLM Synthesis Invariants):**
  - **Розмір аудіо (`audio_length`):** Суворо **`LONG`** (великий розмір із трьох існуючих: `SHORT`, `DEFAULT`, `LONG`). Забезпечує максимальну тривалість, повноту викладу та глибину аналітики.
  - **Формат (`audio_format`):** Суворо **`DEEP_DIVE`** (інтелектуальний діалог двох фахових експертів-аналітиків).
  - **Мова (`language`):** За замовчуванням **`uk`** (чиста літературна українська мова з коректною інженерною термінологією).
- **Канонічний український промпт (AI Instruction Anchor):**
  ```text
  Проведіть глибокий, детальний та вичерпний експертний аналіз матеріалів цього записника українською мовою.
  Формат: інтелектуальний, динамічний діалог двох фахових аналітиків (Deep Dive Podcast).
  1. Автоматично виділіть та ретельно розберіть усі ключові концептуальні, інженерні та практичні тези з першоджерел.
  2. Детально розкрийте реальні кейси, виклики впровадження, цифри, методології та причинно-наслідкові зв'язки.
  3. Мова розмови — виключно якісна українська мова з коректною професійною термінологією.
  4. Забезпечте максимальну повноту викладу матеріалу, утримуючи фокус на практичній цінності для інженера та архітектора.
  ```
- **Negative Invariants (Суворі заборони):**
  - **NEVER** використовувати параметри `SHORT` або `DEFAULT`, якщо завданням визначено максимальний переказ.
  - **NEVER** використовувати мову, відмінну від української (`uk`), без прямої вказівки оператора.
  - **NEVER** запускати синтез у порожньому блокноті (`sources_count == 0`).
  - **NEVER** використовувати зовнішні неперевірені залежності — клієнтський раннер повинен бути 100% Pure Python Standard Library (ADR-002).
  - **NEVER** завершувати конвеєр без сповіщення оператора в Telegram (`chat_id: 6412868393`) та відправки телеметрії в n8n Supervisor Webhook.

---

## 2. Sequential Thinking: Фазова декомпозиція процесу

1. **Фаза 1: Валідація джерел записника (Notebook & Source Validation)**
   - З'єднання з сервісом NotebookLM MCP на `192.168.3.184:8002`.
   - Запит `sources_list` для цільового `notebook_id`.
   - Перевірка: `len(sources) > 0`. Якщо 0 — аварійна деградація (X=4.0).
2. **Фаза 2: Конфігурація синтезу (Parameter Enforcement)**
   - Фіксація `audio_length = "LONG"`, `audio_format = "DEEP_DIVE"`, `language = "uk"`.
   - Ін'єкція канонічного українського промпту для автоматичного виділення головних тез.
3. **Фаза 3: Диспетчеризація через FastMCP JSON-RPC**
   - Виклик методу `tools/call` з `name: generate_audio`.
   - Фіксація унікального асинхронного ідентифікатора задачі (`task_id`).
4. **Фаза 4: Асинхронний моніторинг (Task Polling & State Tracking)**
   - Періодичний запит `artifacts_poll_status` з передачею `task_id` та `notebook_id`.
   - Стан `pending` / `status='2'` свідчить про активний хмарний рендеринг аудіодорожки.
5. **Фаза 5: Телеметрія та WORM-аудит (Dual-Loop Telemetry & Ledger)**
   - Відправка картки запуску в Telegram (`6412868393`).
   - Відправка телеметрії в Supervisor Webhook (`https://n8n.exodus.pp.ua/webhook/bsdd-supervisor-result`).
   - Фіксація WORM-транзакції в Utopia DB (`192.168.3.251:5432`).

---

## 3. Алгоритмічний псевдокод (ADR-016 Standard)

```text
ALGORITHM ExecuteBSddNotebooklmAudioDeepdive
INPUT:
    notebook_id: str
    audio_length: str := "LONG"
    audio_format: str := "DEEP_DIVE"
    language: str := "uk"
    instructions: str := DEFAULT_UKRAINIAN_INSTRUCTIONS
OUTPUT:
    result: dict

BEGIN
    TRY
        ASSERT notebook_id != null AND notebook_id != ""

        // КРОК 1: Запит джерел блокнота через MCP (X=0.0, Y=2.0)
        client := InitializeNotebookLmMcpClient("http://192.168.3.184:8002/mcp")
        sources := client.CallTool("sources_list", {"notebook_id": notebook_id})

        // КРОК 2: Валідація наявності джерел (X=0.0, Y=4.0)
        IF sources != null AND Length(sources) > 0 THEN
            CONTINUE along Vertical Skewer (X=0.0)
        ELSE
            BRANCH_RIGHT(X=4.0, Y=4.0): Failure/Degradation
            LOG_CRITICAL("No sources found in notebook: " + notebook_id)
            HALT_AND_DEGRADE("SOURCES_UNAVAILABLE")
        FI

        // КРОК 3: Фіксація параметрів синтезу (X=0.0, Y=6.0)
        params := {
            "notebook_id": notebook_id,
            "audio_length": audio_length,
            "audio_format": audio_format,
            "language": language,
            "instructions": instructions
        }

        // КРОК 4: Виклик generate_audio в NotebookLM MCP (X=0.0, Y=8.0)
        resp := client.CallTool("generate_audio", params)
        task_id := resp.task_id

        IF task_id == null THEN
            BRANCH_RIGHT(X=4.0, Y=8.0): Failure
            HALT_AND_DEGRADE("TASK_DISPATCH_FAILED")
        FI

        // КРОК 5: Відправка телеметрії оператору та WORM запис (X=0.0, Y=10.0)
        SendTelegramNotification(notebook_id, task_id, audio_length, language)
        SendSupervisorTelemetry("B-SDD-AUDIO-DEEPDIVE", "SUCCESS", task_id)
        RecordUtopiaWormLedger("AUDIO_DEEPDIVE_DISPATCH", notebook_id, task_id)

        RETURN {"status": "SUCCESS", "task_id": task_id, "notebook_id": notebook_id}

    CATCH Error AS e
        LOG_CRITICAL("Execution failed in b-sdd-notebooklm-audio-deepdive: " + e.Message)
        HALT_AND_DEGRADE(e.Message)
    END
END
```

---

## 4. DRAKON Visual Workflow (Planar Skewer X=0.0, C=0)

<!-- DRAKON_VISUAL_FLOW_START -->
## DRAKON Visual Workflow (Planar Skewer X=0)
- Schema File: `b-sdd-notebooklm-audio-deepdive.drakon.json`
- Total Algorithmic Nodes: 9
- Invariant: Planar vertical spine (X=0.0, C=0) verified with rightward degradation branch (X=4.0).
  1. `[HEADLINE]` Початок: Виконання b-sdd-notebooklm-audio-deepdive (X=0.0, Y=0.0)
  2. `[ACTION]` Крок 1: Запит списку джерел блокнота через NotebookLM MCP (X=0.0, Y=2.0)
  3. `[QUESTION]` Крок 2: Джерела присутні (count > 0) та блокнот валідний? (X=0.0, Y=4.0)
  4. `[ACTION]` Аварійна зупинка: Джерела відсутні або блокнот недоступний (X=4.0, Y=4.0)
  5. `[END]` Аварійне завершення (X=4.0, Y=6.0)
  6. `[ACTION]` Крок 3: Фіксація інваріантів: AudioLength=LONG, Format=DEEP_DIVE, Lang=uk (X=0.0, Y=6.0)
  7. `[ACTION]` Крок 4: Виклик generate_audio в NotebookLM MCP та отримання task_id (X=0.0, Y=8.0)
  8. `[ACTION]` Крок 5: Відправка телеметрії в Telegram та n8n Supervisor Webhook (X=0.0, Y=10.0)
  9. `[END]` Успішне завершення: Генерацію максимального аудіопереказу ініційовано (X=0.0, Y=12.0)
<!-- DRAKON_VISUAL_FLOW_END -->

---

## 5. Швидкий виконуваний раннер (CLI Execution)

Запуск генерації максимального україномовного аудіоогляду для будь-якого блокнота:

```bash
python3 scripts/generate_audio_deepdive.py \
  --notebook b371bcda-77c6-4803-84e7-8aed42817454 \
  --length LONG \
  --format DEEP_DIVE \
  --language uk
```

### Перевірка статусу виконання генерації:
```bash
python3 -c "
from scripts.generate_audio_deepdive import NotebookLmMcpClient
client = NotebookLmMcpClient()
status = client.call_tool('artifacts_poll_status', {
    'notebook_id': 'b371bcda-77c6-4803-84e7-8aed42817454',
    'task_id': '<TASK_ID>'
})
print(status)
"
```

### Завантаження готового аудіофайлу після завершення:
```bash
python3 -c "
from scripts.generate_audio_deepdive import NotebookLmMcpClient
client = NotebookLmMcpClient()
client.call_tool('download_audio', {
    'notebook_id': 'b371bcda-77c6-4803-84e7-8aed42817454',
    'output_path': 'dist/audio_deepdive_fde_ukrainian.mp3'
})
"
```
