# PROMPT_FRONTEND_MIGRATION · Backend Engineering Agent → Frontend Design Agent

**Проєкт:** B-SDD Operator Workbench (Human-in-the-Loop Engineering Cockpit)
**Автор:** Backend Engineering Agent
**Версія:** 1.0 (Phase 3 Integration Complete & Verified)
**Дата:** 2026-09-16
**Статус:** Phase 3 інтеграція успішно проведена у гілці `master`. Всі 5 REST-контрактів + SSE-стрімінг синхронізовані. `npm run build` (tsc -b + vite) та 31/31 pytest тестів проходять бездоганно.

---

## § 1. Що реально збудовано / оновлено

Всі 5 ендпоінтів та SSE стрім повністю відповідають DTO з `b-sdd-ui/src/lib/backend-types.ts`:

### 1.1 `GET /api/health`
Повертає статус суверенних вузлів (`utopia_db`, `llm_gateway`, `gitnexus_ast`) з субсекундною TCP-перевіркою та offline fallback:
```bash
curl -s http://localhost:8765/api/health
```
```json
{
  "status": "healthy",
  "server": "online",
  "offline_parity": true,
  "checked_at": "2026-09-16T18:11:00Z",
  "utopia_db": {
    "host": "192.168.3.251",
    "port": 9922,
    "status": "offline",
    "latency_ms": null,
    "endpoint": "192.168.3.251:9922",
    "reachable": false
  },
  "llm_gateway": {
    "host": "192.168.3.184",
    "port": 18880,
    "status": "offline",
    "slots_available": 0,
    "latency_ms": null,
    "endpoint": "192.168.3.184:18880",
    "reachable": false
  }
}
```

### 1.2 `GET /api/rules/active`
Виконує детерміністичну Pre-Flight компіляцію активних правил (<20 мс, <500 слів) та повертає поля для `TokenGauge`:
```bash
curl -s http://localhost:8765/api/rules/active
```
```json
{
  "compiled_snapshot": "...",
  "word_count": 476,
  "max_budget": 500,
  "is_budget_exceeded": false,
  "compile_latency_ms": 14.5,
  "latency_ms": 14.5,
  "compiled_at": "2026-09-16T18:11:00Z",
  "is_latency_compliant": true,
  "recommended_skills": ["b-sdd", "architecture-designer", "find-skills", "safe-refactor", "skill-creator"]
}
```

### 1.3 `GET /api/adrs`
Бітемпоральні ADR з фільтрацією за часовими горизонтами:
```bash
curl -s "http://localhost:8765/api/adrs?valid_time=2026-09-16&transaction_time=2026-09-16"
```
```json
{
  "total": 4,
  "adrs": [
    {
      "id": "ADR-001",
      "title": "ADR-001: Bitemporal Invariant Architecture",
      "status": "accepted",
      "invariants": [...]
    }
  ]
}
```

### 1.4 `GET /api/drakon/schema` та `POST /api/drakon/schema`
Підтримує передачу `schema_ir` як у верхньому рівні, так і у вкладеному об'єкті `{ schema_ir, diagram }`, валідує планарність (crossings=0) через `DrakonValidator` та записує зміни у `specs/004-multi-session-handoff-and-drakon/logic.drakon.json`:
```bash
curl -s -X POST http://localhost:8765/api/drakon/schema \
  -H "Content-Type: application/json" \
  -d '{"schema_ir": {"schema_version": "1.0", "name": "HITL Protocol", "nodes": {}}}'
```
```json
{
  "status": "saved",
  "saved": true,
  "target_path": "specs/004-multi-session-handoff-and-drakon/logic.drakon.json",
  "path": "specs/004-multi-session-handoff-and-drakon/logic.drakon.json",
  "bytes_written": 2410,
  "validation": {
    "is_valid": true,
    "violations": [],
    "crossings": 0,
    "planar": true
  },
  "name": "HITL Protocol"
}
```

### 1.5 `POST /api/sprint/review`
Реалізує перехід Φ6 -> Φ7 (Approve) з атомарним синтезом `sprint_handoff.json` або COW-гілкуванням (Reject & Branch):
```bash
curl -s -X POST http://localhost:8765/api/sprint/review \
  -H "Content-Type: application/json" \
  -d '{"action": "approve"}'
```
```json
{
  "status": "approved",
  "action": "approve",
  "sprint_id": "handoff-f8da1c0c-1789577151",
  "cycle_id": "cycle-1789578600",
  "worm_locked": true,
  "launch_command": "./run_b_sdd.sh --auto-chain",
  "handoff_path": ".context/sprint_handoff.json",
  "next_phase": "phi_7",
  "message": "Sprint approved by human architect. Handoff generated atomically."
}
```

### 1.6 `POST /api/copilot/proxy` (SSE Stream)
Генерує сумісні SSE-фрейми формату `CopilotSseEvent` (`type: token`, `type: meta`, `type: done`, `[DONE]`):
```bash
curl -N -X POST http://localhost:8765/api/copilot/proxy \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"prompt": "Generate leaf action for cond_phi3", "slot": "coding-proxy", "stream": true}'
```
Потік фреймів:
```text
data: {"type": "token", "delta": "[coding-proxy] Synthesizing sovereign action body...\n", "token": "[coding-proxy] ...", "timestamp": 1789578601.12}

data: {"type": "meta", "slot": "coding-proxy", "latency_ms": 420}

data: {"type": "done", "total_tokens": 28, "reason": "stop"}

data: [DONE]
```

### Розбіжності з DTO (`backend-types.ts`)
**Розбіжностей немає.** Сервер тепер повертає 100% очікуваних полів DTO і одночасно підтримує сумісність із попередніми викликами.

---

## § 2. CORS & Auth статус

- **CORS:** Налаштовано повну підтримку `http://localhost:5173` (та wildcards для локальної розробки).
- **Заголовки:**
  ```http
  Access-Control-Allow-Origin: *
  Access-Control-Allow-Methods: GET, POST, OPTIONS
  Access-Control-Allow-Headers: Content-Type, Authorization, Accept
  ```
- **Ed25519-підпис оператора:** Заплановано на Sprint N+3 (після підключення Appwrite Auth). Поле `operator_signature` у `SprintReviewPayload` резервується бекендом без помилок валідації.

---

## § 3. Astryx Adherence Confirmation

- [x] Я прочитав §11 HANDOFF та `DELTA_C_ASTRYX_OMISSION.md`.
- [x] Мої UI-артефакти (адмінка / email-шаблони / dashboards): **немає** (бекенд — це 100% Pure Python Standard Library CLI & headless REST/SSE сервер без сторонніх UI, весь візуальний шар концентрується виключно в `b-sdd-ui/`).
- [x] Мої API-контракти повністю сумісні з очікуваннями Astryx-компонентів:
  - Пагінація: `{ items[], total, cursor? }` (підтримується в `/api/adrs`).
  - Помилки: `{ error, status }` та `{ code, message, details? }`.
  - Realtime events: `{ type, delta, meta, done }` shape у SSE потоці.

---

## § 4. Каталог питань до Frontend-агента

- **[Q1]** У `ReviewGateModal.tsx` поле `launch_command` береться з `reviewResponse.launch_command`. Чи планується відображення прогресу виконання команди безпосередньо у вікні workbench (наприклад, через WebSocket/SSE потік терміналу)?
- **[Q2]** Для збереження схеми DRAKON (`POST /api/drakon/schema`): зараз фронтенд надсилає `schema_ir: CANONICAL_HITL_DRAKON_IR` та `diagram: widgetDiagram`. Чи планується в Sprint N+3 підтримка динамічного drag-and-drop редагування топології вузлів у `DrakonCanvas.tsx`, чи генерація залишиться обмеженою виключно leaf action-вузлами згідно з ADR-008-INV-03?

---

## § 5. ΔC-вектор порушень прототипу (виправлено)

Під час інтеграції виявлено та усунено два дефекти компіляції:

1. **`DrakonToolbar.tsx` — подвійний `return (`:**
   - *Виявлено:* У рядках 65-66 містився дублікат інструкції `return (`, що ламало компілятор TypeScript.
   - *Виправлено:* Усунуто дублікат, відновлено повну тернарну форму `saveLabel`.
2. **`import.meta.env` — відсутність декларацій Vite:**
   - *Виявлено:* `src/lib/api.ts:29:16 - error TS2339: Property 'env' does not exist on type 'ImportMeta'`.
   - *Виправлено:* Створено `b-sdd-ui/src/vite-env.d.ts` з `/// <reference types="vite/client" />`.

Після цих виправлень:
- `npm run build` успішно збирає клієнтський бандл.
- `pytest` проходить усі 31 тест (включаючи архітектурні фітнес-тести на нульові сторонні залежності та суб-50мс затримку компіляції).

---

## § 6. Handoff CLI-команда

Для запуску наступного кроку розробки:
```bash
./run_b_sdd.sh --new-session "Sprint N+3: Astryx Design System migration for b-sdd-ui components & Appwrite Realtime phase sync"
```
