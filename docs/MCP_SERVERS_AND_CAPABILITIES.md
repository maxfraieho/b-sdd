# B-SDD AGI Agent: MCP Servers & Capabilities Inventory

**Версія:** 1.0.0  
**Дата формування:** 2026-09-21  
**Хост координації:** 192.168.3.161 (debian)  
**Архітектурний стандарт:** B-SDD Methodology v1.2 (ADR-001 — ADR-020, Invariant FL-01)  
**Цільовий репозиторій:** `/home/vokov/projects/b-sdd`

---

## 1. Загальний огляд інфраструктури MCP

Для усунення «сліпих зон» Планувальника (Gemini Spark) та забезпечення повної синергії між оркестратором та агентом виконання нижче наведено повний реєстр Model Context Protocol (MCP) серверів, інструментів та протоколів взаємодії, розгорнутих у кластері B-SDD.

### 1.1. Зведена таблиця підключених MCP-серверів

| Назва MCP-сервера | Транспорт | Адреса / Endpoint | Порт | Авторизація / Права | Статус | Призначення |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`n8n`** | Streamable HTTP | `https://n8n.exodus.pp.ua/mcp-server/http` | 443 (Cloudflare) / 5678 (Oracle VM `100.66.97.93`) | Bearer JWT (Owner/Admin) | **ACTIVE (UP)** | Повний життєвий цикл воркфлоу n8n, моніторинг тригерів, вебхуки супервайзера |
| **`notebooklm`** | Streamable HTTP | `http://192.168.3.184:8002/mcp` *(резерв: .234)* | 8002 | Headless Session / Local LAN | **ACTIVE (UP)** | Доставка та читання артефактів FL-01, створення джерел, чат, аудіо-огляди, дослідження |
| **`gitnexus`** | Streamable HTTP | `http://192.168.3.184:4747/api/mcp` | 4747 | Local LAN | **ACTIVE (UP)** | Граф знань кодової бази (KùzuDB), Cypher-запити, impact analysis, виявлення змін |
| **`ai-memory`** | Streamable HTTP | `http://192.168.3.184:49374/mcp` | 49374 | Local LAN | **ACTIVE (UP)** | Довготривала пам'ять агентів, handoff-сесії, консолідація контексту |
| **`drakon`** | Streamable HTTP | `https://drakon-antigravity-worker.maxfraieho.workers.dev/mcp` | 443 (Cloudflare Workers) | Bearer Token (`drakon-mcp-2026`) | **ACTIVE (UP)** | ДРАКОН-схеми як алгоритмічний препроцесор, валідація візуальних правил |
| **`agent-workspace`** | stdio (через SSH) | `ssh vokov@192.168.3.234 agent-workspace mcp --headless` | 22 (SSH) | SSH Key (`id_agent_cluster`) | **ACTIVE (UP)** | Дистанційне керування виділеним вузлом розробки .234, виконання ізольованих задач |
| **`mempalace`** | stdio | `/home/vokov/.local/share/pipx/venvs/mempalace/bin/python -m mempalace.mcp_server` | Local Process | Local user permissions | **ACTIVE (UP)** | Структуроване сховище персональних та архітектурних спогадів |
| **`sequential-thinking`**| stdio (npx) | `npx -y @modelcontextprotocol/server-sequential-thinking` | Local Process | Node.js runtime | **ACTIVE (UP)** | Багатокрокове динамічне міркування, корекція гіпотез, декомпозиція задач |
| **`chrome-win`** | stdio (npx / CDP) | `npx -y chrome-devtools-mcp@latest --browser-url=http://192.168.3.234:19222` | 19222 | Remote CDP | **ACTIVE (UP)** | Тестування вебінтерфейсів (Playwright / CDP) на виділеному вузлі |
| **`comet-win`** | SSE | `http://192.168.3.234:18765/sse` | 18765 | Local LAN | **IDLE** | Телеметрія та системний моніторинг робочої станції |
| **`browser-harness-win`**| SSE | `http://192.168.3.234:18766/sse` | 18766 | Local LAN | **IDLE** | Автоматизація браузерних сесій HITL |

---

## 2. Каталог доступних MCP-інструментів

### 2.1. MCP Server `n8n` (Оркестрація воркфлоу та комунікація)
Сервер реалізує протокол n8n Workflow SDK для programmatic керування воркфлоу n8n без потреби у веб-інтерфейсі.

1. **`get_sdk_reference(section)`** — повертає документацію та патерни n8n Workflow SDK (розділи: `overview`, `nodes`, `triggers`, `routing`, `credentials`, `expressions`, `guidelines`, `design`).
2. **`search_nodes(query, category)`** — структурний пошук нод за функціоналом (наприклад `gmail`, `slack`, `httpRequest`, `set`, `if`).
3. **`get_suggested_nodes(category)`** — рекомендації нод за шаблонами сценаріїв.
4. **`get_node_types(nodeIds)`** — витягує точні TypeScript типи та параметри для нод n8n (виключає помилки конфігурації).
5. **`validate_workflow(code)`** — статична валідація TypeScript-коду воркфлоу перед деплоєм. Перевіряє синтаксис, зв'язки та вирази `$json`.
6. **`create_workflow_from_code(code, description)`** — створення нового воркфлоу з валідованого SDK коду.
7. **`update_workflow(workflowId, code)`** — оновлення існуючого воркфлоу новим кодом зі збереженням зв'язків та активних credentials.
8. **`publish_workflow(workflowId)`** — активація воркфлоу у production середовищі n8n (`active: true`).
9. **`unpublish_workflow(workflowId)`** — деактивація воркфлоу.
10. **`archive_workflow(workflowId)`** — архівування воркфлоу.
11. **`get_workflow_details(workflowId)`** — отримання повної структури нод, параметрів, credentials та версії воркфлоу.
12. **`search_workflows(query)`** — пошук існуючих воркфлоу за назвою чи тегами.
13. **`get_execution(workflowId, executionId, includeData)`** — глибока телеметрія виконання воркфлоу: перевірка вхідних/вихідних JSON кожного вузла, стектрейси помилок, час виконання.
14. **`execute_workflow(workflowId, data)`** — примусовий запуск виконання воркфлоу з тестовим або бойовим набором даних.

---

### 2.2. MCP Server `notebooklm` (Суверенне сховище знань та зворотний зв'язок)
Надає повний програмний API для взаємодії з блокнотами Google NotebookLM (включаючи функції, недоступні у Web UI).

1. **Керування блокнотами:**
   - `notebooks_list()` — список доступних блокнотів та їхні ID.
   - `notebooks_create(title)` — створення нового блокнота.
   - `notebooks_get(notebook_id)` / `notebooks_get_summary(notebook_id)` — метадані та зведення блокнота.
   - `notebooks_rename(notebook_id, title)` / `notebooks_delete(notebook_id)`.
2. **Керування джерелами знань (Sources):**
   - `sources_list(notebook_id)` — список усіх джерел у блокноті з їхніми ID.
   - `sources_add_text(notebook_id, title, content)` — **критичний для Invariant FL-01 інструмент**. Додає структурований Markdown/JSON звіт як джерело.
   - `sources_add_url(notebook_id, url)` / `sources_add_file(notebook_id, file_path)`.
   - `sources_get_fulltext(notebook_id, source_id)` — отримання повного тексту джерела (зчитування вхідних завдань від Gemini Spark).
   - `sources_rename(notebook_id, source_id, title)` / `sources_delete(notebook_id, source_id)`.
3. **Аналітика та семантичний чат:**
   - `chat_ask(notebook_id, query)` — синтез відповіді на основі 100% завантажених джерел блокнота без галюцинацій.
   - `chat_get_history(notebook_id)` / `chat_configure(notebook_id, instructions)`.
4. **Генерація мультимодальних артефактів:**
   - `generate_audio(notebook_id)` — генерація подкасту/аудіо-огляду (Deep Dive).
   - `generate_report(notebook_id, report_type)` — побудова зведеного аналітичного звіту або Briefing Doc.
   - `generate_study_guide(notebook_id)` / `generate_mind_map(notebook_id)` / `generate_data_table(notebook_id)`.
   - `download_audio(notebook_id, artifact_id, output_path)` / `download_report(...)`.

---

### 2.3. MCP Server `gitnexus` (Граф кодової бази та Impact-аналіз)
Працює на базі високоефективної графової БД KùzuDB на вузлі 192.168.3.184:4747.

1. **`list_repos()`** — перелік проіндексованих репозиторіїв у GitNexus.
2. **`query(repo, query)`** — природномовний та семантичний пошук по кодовому графу.
3. **`cypher(repo, query)`** — виконання прямих Cypher-запитів до бази зв'язків компонентів, викликів та залежностей.
4. **`context(repo, symbol)`** — повний семантичний контекст навколо класу/методу/функції.
5. **`detect_changes(repo)`** — виявлення несинхронізованих з графом змін коду.
6. **`check(repo, symbol)`** — архітектурна верифікація символу на цілісність.
7. **`rename(repo, old_symbol, new_symbol)`** — безпечний транзитивний рефакторинг символів з перевіркою всіх референсів.
8. **`impact(repo, symbol)`** — аналіз радіуса ураження змін (blast radius) перед внесенням правок у ядро B-SDD.
9. **`explain(repo, symbol)`** — пояснення логіки та потоку даних компонента.
10. **`pdg_query(repo, symbol)`** — Program Dependence Graph для точного відстеження контрольних та інформаційних зв'язків.
11. **`route_map(repo)`** / **`tool_map(repo)`** — мапа маршрутизації та інструментального покриття системи.
12. **`shape_check(repo)`** / **`api_impact(repo, endpoint)`** — перевірка контрактів API на breaking changes.
13. **`trace(repo, from_symbol, to_symbol)`** — пошук шляху виклику між двома компонентами.

---

### 2.4. MCP Server `ai-memory` (Довготривала семантична пам'ять)
1. **`memory_briefing()`** — швидкий брифінг щодо поточної робочої сесії та контексту проєкту.
2. **`memory_status()`** — поточний статус індексу пам'яті.
3. **`memory_query(query)`** — семантичний пошук за історичними рішеннями та діалогами.
4. **`memory_write_page(title, content, tags)`** — фіксація нового архітектурного знання або паттерну.
5. **`memory_handoff_begin(task_id)`** / **`memory_handoff_accept(handoff_id)`** — передача контексту між сесіями та агентами без втрати цілей.
6. **`memory_consolidate()`** — консолідація спогадів, дедуплікація фактів.

---

### 2.5. MCP Server `drakon` (ДРАКОН-схеми та формалізація алгоритмів)
1. Синтаксична валідація візуальних схем ДРАКОН (гілки «Шампур», маршрути помилок «Праве плече»).
2. Трансляція блок-схем ДРАКОН у строгі програмні інваріанти та тести для B-SDD.
3. Генерація ДРАКОН-схем для інтеграції в Astryx Operator Cockpit.

---

### 2.6. Локальні інструменти оркестратора AGI (Хост 161)
1. **Bash & Process Harness:** `run_command`, `manage_task` (асинхронне виконання фонових демонів, pytest, uv, git).
2. **Файлова система:** `view_file`, `replace_file_content`, `write_to_file`.
3. **Субагентний контур:** `invoke_subagent`, `define_subagent`, `manage_subagents`, `send_message` (розпаралелювання досліджень та рефакторингу).
4. **Мережа та веб:** `read_url_content`, `search_web`, `generate_image`.

---

## 3. Рольова матриця покриття задач B-SDD

| Фаза / Задача Спринту | Відповідальні MCP-сервери | Цільові інструменти | Гарантований результат |
| :--- | :--- | :--- | :--- |
| **1. Диспатч та Прийом Завдання** | `n8n` | `Gmail Trigger`, `get_workflow_details`, `get_execution` | Автоматичне зняття літер `OUTBOX_AGI_*` без застрягання в UNREAD |
| **2. Вхідний Контекст та ADR** | `notebooklm`, `gitnexus` | `sources_get_fulltext`, `cypher`, `impact`, `context` | Отримання 100% специфікації від Spark, аналіз радіуса змін у репозиторії |
| **3. Алгоритмічне моделювання** | `drakon`, `sequential-thinking` | `drakon/*`, `sequentialthinking` | Побудова неконфліктних графів рішень, розв'язання планарних перетинів |
| **4. Реалізація та Рефакторинг** | Локальні інструменти AGI, `gitnexus` | `replace_file_content`, `write_to_file`, `rename` | Суверенне кодування без сторонніх runtime-залежностей у `src/` (ADR-002) |
| **5. Перевірка Фітнес-Функцій** | Локальний супервайзер, `pytest` | `run_command` (`pytest -v tests/`) | 18/18 green тестів, латентність компіляції < 50ms (ADR-001) |
| **6. Зворотний Зв'язок (FL-01)** | `notebooklm` | `sources_add_text` | Обов'язкова публікація `INBOX_GEMINI_*_REPORT` перед закриттям спринту |
| **7. Сповіщення Оператора (HITL)** | `n8n` | `Telegram Notify (Success)`, `Send Email (Gmail)` | Сповіщення в Telegram-боті та технічний лист без витоків на Kindle |
| **8. Закриття Епіка (Kindle Pipeline)** | Local CLI (`send-to-kindle`) | `md_to_epub.py`, `send_digest.py` | Генерація чистого `.epub` та адресна доставка на Kindle без порушення поштових контурів |

---

## 4. Конфігураційні шляхи на хості 192.168.3.161

- **Antigravity CLI MCP Config:** `/home/vokov/.gemini/antigravity-cli/mcp_config.json`
- **Claude Code MCP Config:** `/home/vokov/.claude.json`
- **Локальний демон супервайзера:** `/home/vokov/projects/b-sdd/scripts/bsdd_supervisor.py` (порт `:8161`, systemd: `b-sdd-supervisor.service`)
- **n8n Workflow SDK Blueprint:** `/home/vokov/projects/b-sdd/scripts/workflow_bsdd_sdk.ts`
- **n8n MCP Deployer:** `/home/vokov/projects/b-sdd/scripts/deploy_n8n_workflow.py`
- **Kindle Delivery Pipeline:** `/home/vokov/projects/send-to-kindle/bsdd_to_kindle.py`
