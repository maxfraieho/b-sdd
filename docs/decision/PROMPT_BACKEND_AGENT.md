# Architectural Instruction: B-SDD Backend Integration Agent (Task-007)
## Контракт інтеграції бекенду B-SDD з веб-панеллю розробника `b-sdd-ui` та Utopia DB

---

### 1. Мета та Контекст
У межах задачі `task-006` завершено портування фронтенд-кокпіта `b-sdd-ui` (Vite + React 19 + TypeScript + Tailwind CSS) з використанням канонічного рушія `stepan-mitkin/drakonwidget`.
Мета поточної задачі (`task-007`) — з'єднати `b-sdd-ui` з локальним файловим сховищем `.context/`, кешем `intents_cache.sqlite` та суверенними вузлами VPC:
1. **Utopia DB** на хості `192.168.3.251:9922` (PostgreSQL 16 + pgvector + Tantivy).
2. **LLM Gateway** на хості `192.168.3.184:18880 / 8082` (слоти `agent-proxy`, `coding-proxy`, `reasoning-proxy`).
3. **GitNexus AST Engine** на хості `192.168.3.184:4747`.

---

### 2. Обов'язкові Архітектурні Інваріанти (MANDATORY INVARIANTS)
Будь-який створюваний бекенд-код повинен бездоганно проходити тести `tests/test_architecture_fitness.py`:
1. **Zero External Dependencies in `src/`:** Увесь код у папці `src/server/` та `src/drakon/` зобов'язаний бути **100% чистим Python Standard Library** (`http.server`, `urllib.request`, `sqlite3`, `json`, `subprocess`, `pathlib`). Заборонено встановлювати `fastapi`, `flask`, `aiohttp`, `requests` тощо.
2. **Deterministic Pre-Flight Compilation:** Компіляція правил повинна виконуватися за $<50$ мс, а знімок активних правил — строго $\le 500$ слів.
3. **Bitemporal Isolation:** Правила із `valid_to < NOW` не повинні віддаватися в активний контекст агента.
4. **Offline Local Parity:** Сервер повинен коректно обслуговувати панель навіть без доступу до зовнішнього інтернету, транслюючи стан з локального SQLite-кешу.

---

### 3. Специфікація REST/SSE API Шлюзу (`src/server/workbench_server.py`)

Сервер запускається командою:
```bash
python3 -m src.server.workbench_server --port 8765 --root .
```

#### Ендпоінти:
1. `GET /api/health`
   - Перевіряє доступність локального середовища, `.context/active_rules.md`, `intents_cache.sqlite` та пінг до `.251:9922` і `.184:18880`.
   - Повертає JSON зі статусами здоров'я вузлів.
2. `GET /api/rules/active`
   - Викликає `BSDDCompiler.compile()` у пам'яті.
   - Повертає знімок активних правил, час компіляції (мс), лічильник слів та список рекомендованих скілів.
3. `GET /api/adrs?tv={timestamp}&tt={timestamp}`
   - Зчитує бітемпоральні ADR з `intents_cache.sqlite` або парсить файли `docs/adr/*.md`.
   - Фільтрує записи за горизонтами $T_v$ (дійсний час) та $T_t$ (транзакційний час).
4. `GET /api/drakon/schema?path=specs/004-multi-session-handoff-and-drakon/logic.drakon.json`
   - Парсить ДРАКОН-схему через `src/drakon/parser.py`.
   - Валідує інваріанти через `src/drakon/validator.py`.
   - Повертає канонічний `DRAKON-IR` та перетворений формат `items` для `drakonwidget.js`.
5. `GET /api/sprint/state`
   - Повертає стан поточного спринту, статус 7 фаз ($\Phi_1 - \Phi_7$) та вміст `.context/sprint_handoff.json`.
6. `POST /api/sprint/review`
   - Приймає рішення оператора на фазі $\Phi_6$:
     - `action: "approve"` -> просуває спринт до $\Phi_7$ та викликає синтез естафети.
     - `action: "reject"` -> ініціює протокол Reject & Branch з негативним вектором $\Delta C$.
7. `POST /api/copilot/proxy`
   - Проксіює запити оператора до локального LLM Gateway (`http://192.168.3.184:18880/v1/chat/completions`) з підтримкою Server-Sent Events (SSE).

---

### 4. План Виконання та Критерії Прийомки
1. Створити модуль `src/server/workbench_server.py` на чистому `http.server.ThreadingHTTPServer`.
2. Додати CLI-команду `python3 -m src.cli.main serve --port 8765`.
3. Написати модульні тести `tests/test_workbench_server.py` для перевірки всіх REST-маршрутів.
4. Переконатися, що `pytest -v tests/test_architecture_fitness.py` виконується без жодних зауважень (0 зовнішніх імпортів).
