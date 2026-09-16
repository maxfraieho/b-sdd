# PROMPT · Для агента-розробника бекенду B-SDD Operator Workbench

**Тип артефакту:** Директивний промт (не інформаційний документ)
**Цільовий агент:** Backend Engineering Agent (Utopia DB · LLM Gateway · GitNexus · Appwrite)
**Дата випуску:** 2026-09-16
**Автор:** Frontend Design Agent (Genspark)
**Очікуваний результат:** новий B-SDD-промт від тебе, готовий передати назад мені (frontend-агенту) для міграції у продакшн-стек.

---

## 0. Твоя задача одним реченням

**Прочитай мій прототип фронтенду, реалізуй бекенд-контракти під нього у власному контурі (Utopia DB `.251:9922` · LLM Gateway `.184:18880` · GitNexus `.184:4747` · Appwrite), а потім поверни мені новий промт, який опише а) що ти реально збудував, б) як мені мігрувати фронт на дизайн-систему Astryx з реальними API замість моків.**

---

## 1. З чого ти починаєш — обов'язковий вхідний рефересний матеріал

Перш ніж писати рядок бекенд-коду, ти зобов'язаний вичитати ці 4 файли в такому порядку:

1. **`docs/decision/HANDOFF_BACKEND.md`** — повний технічний контракт фронтенду. Містить §6 з API-ендпоінтами, які я від тебе очікую.
2. **`docs/decision/ADR-FE-001-cockpit-architecture.md`** — 6 архітектурних рішень фронту з обґрунтуванням і 5 нових інваріантів (FE-INV-01..05).
3. **`data.js`** — це не просто моки, це виконуваний DTO-контракт. Форма кожного `BSDD.*` = точна форма твоєї майбутньої JSON-відповіді.
4. **`B-SDD Operator Workbench.html`** та `components/*.jsx` — щоб побачити, як фронт реально споживає ці дані. Особливо звернути увагу:
   - `components/copilot.jsx` — контракт SSE-стрімінгу
   - `components/timeline.jsx` — логіка активності ADR при bitemporal scrub
   - `components/drakon.jsx` — вимоги до графа (планарність, шампур)
   - `components/gate_v2.jsx` — що показується в Human Review Gate

**Не вгадуй нічого.** Все, що тобі здається "очевидним" — вже задокументовано або має бути питанням до Head Architect.

---

## 2. Що ти маєш реалізувати (мінімальний обов'язковий скоуп)

### 2.1 Utopia DB (`https://192.168.3.251:9922`)

- Bitemporal ADR-стор із подвійною міткою `V_valid` та `T_transaction`.
- Копіювальний-при-записі (copy-on-write) знімок для `Reject & Branch` (див. FE `components/reject.jsx`).
- WORM-лог схвалень операторів (Ed25519 підпис через Appwrite Auth).
- Ендпоінти з §6.2 HANDOFF-документа. Всі відповіді ПОВИННІ вкладатись у типи, що дзеркалять `data.js` (див. §5 HANDOFF: таблиця "State → Замінити на").

### 2.2 LLM Gateway (`https://192.168.3.184:18880`) — mTLS

- 8-слотовий пул vLLM (agent-proxy / coding-proxy / reasoning-proxy).
- SSE-ендпоінт `POST /v1/chat/completions` зі `stream: true`.
- `/health` кожні 2 секунди повертає `SlotStatus[]`.
- `/v1/kill/{stream_id}` для екстреного переривання (Kill Stream у копілоті).
- **Обов'язково:** дотримання ADR-024-INV-02 (mTLS, ніяких fallback на plain HTTP).

### 2.3 GitNexus AST Engine (`https://192.168.3.184:4747`)

- Топологічний граф викликів для Φ5 (Automated Fitness Gates).
- Ендпоінт `POST /isolation/verify` повертає `{ pass: bool, violations: [] }`.

### 2.4 Appwrite Control Plane

- Realtime WebSocket-підписка на: `projects.{id}.currentPhase`, `health.*`, `sprints.{id}.state`.
- Teams RBAC для workspace-switcher у топбарі.
- Auth з Ed25519-підписом для сертифіката схвалення (див. FE `components/approve.jsx`).

### 2.5 Обов'язкові інваріанти, які твій бекенд ПОВИНЕН підтримувати

З §7 HANDOFF-документа. Коротко:

- **ADR-002-INV-02:** `wordCount(activeRules) ≤ 500 AND compileTime < 20ms`
- **ADR-024-INV-02:** усі SSE — тільки через mTLS у sovereign VPC
- **ADR-007-INV-01:** `handoff.next_sprint.md` містить `deltaC ∪ nextGoal AND signed(operator)`
- **ADR-008-INV-01:** DRAKON граф `planar = true AND crossings = 0`
- **Copy-on-Write @ Reject:** старий стан не мутуй

Ти маєш ЗАПРОГРАМУВАТИ ці інваріанти як runtime-перевірки, а не як коментарі в документації. Порушення → HTTP 422 з `{ inv: 'ADR-...', formula: '...', observed: '...' }`.

---

## 3. Як ти маєш працювати — методологія B-SDD (dogfooding)

Оскільки цей workbench — інструмент для B-SDD, ти ЗОБОВ'ЯЗАНИЙ розробляти його **за B-SDD-методологією**. Тобто:

- **Φ1 Intent Framing:** для кожного нового бекенд-модуля створи MADR у власному репозиторії (використай форму з `ADR-FE-001` як шаблон).
- **Φ2 Algorithmic Spec:** намалюй DRAKON-схему кожного нетривіального ендпоінта (SSE-роутинг, copy-on-write знімок, Ed25519-підпис). Використай сусідній репо `maxfraieho/drakonwidget` як інструмент.
- **Φ3 Pre-Flight Compilation:** тримай активні правила у `.context/active_rules.md` ≤ 500 слів. Якщо перевищуєш — це порушення ADR-002.
- **Φ4 Phased Code Execution:** кодогенерація ТІЛЬКИ всередині вузлів «Дія» DRAKON-схем.
- **Φ5 Automated Fitness Gates:** `pytest` + AST-ізоляція через GitNexus. Мінімум 90% покриття, 0 порушень меж модулів.
- **Φ6 Human Review Gate:** кожен PR має проходити крипто-підписаний review Head Architect (Ed25519 через Appwrite).
- **Φ7 Distillation & Handoff:** повний скрипт для наступного циклу + `deltaC`-вектор порушень попереднього.

**Дистиляція = твій зворотний промт до мене (див. §5).**

---

## 4. Тестовий сценарій, який ти маєш вміти прогнати End-to-End

Замінивши моки у `data.js` на реальні дзвінки до свого бекенду, наступний сценарій ПОВИНЕН працювати без правок JSX:

1. Оператор відкриває workbench → фронт запитує `GET /projects` (Appwrite).
2. Обирає `ACCORD Suisse` → фронт запитує `GET /adrs?tv=today&tt=today` (Utopia).
3. Бачить активну фазу Φ6 → фронт підписується `Realtime projects.accord-suisse.currentPhase` (Appwrite).
4. Клікає на вузол DRAKON `Parse SSE Request` → фронт `GET /nodes/n2/facts` → інспектор показує реальний інваріант ADR-024-INV-01.
5. Тягне T_v слайдер на 2026-04 → фронт `POST /snapshot { tv, tt }` → таймлайн перемальовує ADR-стан.
6. Копілот стрімить код → фронт `POST /v1/chat/completions { stream: true }` до `.184:18880` → бачить реальний потік токенів.
7. Натискає Kill Stream → фронт `POST /v1/kill/{sid}` → потік зупиняється, копілот показує `stream.status: 'terminated'`.
8. Натискає Reject & Branch, обирає depth=Φ4, вводить ΔC → фронт `POST /sprints/current/reject { depth, deltaC, negativeInvariant, operatorSignature }` → Utopia створює нову гілку, старий sprint закривається за `V_end = now()`.
9. У новій ітерації натискає Approve & Sign → фронт `POST /sprints/current/approve { operatorId, signature, artifacts[] }` → отримує `cycleId: 'VEC-N'` + CLI-команду для наступного циклу.

**Якщо якийсь крок не працює після заміни моків — це bug у твоєму бекенді, не в моєму фронті.**

---

## 5. Що ти маєш повернути мені — формат зворотного промту

Коли твій бекенд готовий (принаймні до рівня End-to-End сценарію §4), ти **зобов'язаний повернути мені один markdown-файл** у форматі, аналогічному цьому. Він має називатися:

`docs/decision/PROMPT_FRONTEND_MIGRATION.md`

Структура зворотного промту:

### § 1. Що ти реально збудував
- Список ендпоінтів з реальними URL (може бути dev/staging), автентифікацією, прикладами curl.
- Список ADR/DRAKON схем, які ти написав під час розробки — з посиланнями у своєму репо.
- Розбіжності з моїм `data.js` (якщо ти був змушений змінити форму DTO — обґрунтуй).

### § 2. Готовність до інтеграції
- OpenAPI 3.1 спека (у `docs/decision/openapi.yaml`).
- Змінні середовища (`.env.example`) — endpoints, mTLS certs, Appwrite endpoint+projectId.
- Приклади SSE-обмінів (записаний потік для тестування).
- Приклад Ed25519-підпису та як його верифікувати.

### § 3. Директива міграції на Astryx (для мене)

Це ключова частина. Ти маєш **директивно наказати** мені мігрувати з поточного прототипу (React 18 + Babel-standalone + власні CSS-змінні) на **Astryx** (`facebook/astryx`), беручи до уваги все, що ти вже знаєш про свій бекенд.

Astryx — це:
- Дизайн-система від Meta, використовується в 13,000+ додатках Facebook.
- 150+ доступних React-компонентів.
- StyleX під капотом, але споживач може перекривати `className` через Tailwind / CSS Modules / plain CSS.
- 7 готових тем (`neutral`, `butter`, `chocolate`, `matcha`, `stone`, `gothic`, `y2k`) + бренд-темізація через CSS-custom-properties.
- Вимагає **React 19+**.
- CLI (`@astryxdesign/cli`) з командами `component`, `template`, `swizzle`, `docs`, `init` (пише індекс у AGENTS.md/CLAUDE.md для агентних роботів).
- Storybook: https://facebook.github.io/astryx/
- Репозиторій: https://github.com/facebook/astryx
- Npm: `@astryxdesign/core`, `@astryxdesign/theme-neutral`, `@astryxdesign/cli`, `@astryxdesign/build`

**Твоя директива міграції ПОВИННА містити:**

3.1 **Обрання цільового стеку:**
   - Next.js 15 App Router + Astryx (найпростіший шлях за їхнім Quick Start)
   - АБО Vite + Astryx + TanStack Router
   - Твоя рекомендація з обґрунтуванням чому саме цей стек оптимальний під твої ендпоінти (SSR потрібен? Server Actions? Edge-функції на Cloudflare Workers?).

3.2 **Обрання теми Astryx** та обґрунтування:
   - Поточний Swiss High-Tech Dark → яка з 7 готових тем найближча? Чи треба створити кастомну через `defineTheme`?
   - Мапінг наших токенів (`--amber`, `--emerald`, `--violet`, `--rose`, `--blue`, `--cyan`) на Astryx status-tokens та hue-palette.

3.3 **Мапінг наших компонентів на Astryx**:
   Пройдись по кожному нашому компоненту і скажи, який Astryx-компонент його замінить. Використай CLI: `npx @astryxdesign/cli component --list`, потім `component <Name>`. Приклад очікуваного формату:

   | Наш компонент | Astryx replacement | CLI-команда для докладних доків |
   |---|---|---|
   | Topbar health-cluster | `Toolbar` + `Badge` + `StatusMessage` | `astryx component Toolbar` |
   | PhaseStepper | `Stepper` (з `.claude/skills/writing-component-docs.md`) | `astryx component Stepper` |
   | CopilotPanel slot-cards | `Card` + `RadioGroup` | `astryx component Card` |
   | TokenBudget bar | `Progress` (multi-segment) | `astryx component Progress` |
   | Timeline scrubber | *(немає прямого — треба swizzle або власний)* | — |
   | Human Review Gate | `Dialog` + `ButtonGroup` + `Alert` | `astryx component Dialog` |
   | Reject modal | `Dialog` + `RadioGroup` + `Textarea` | — |
   | Drawer (Node Inspector) | `Sheet` (Bottom/Right) | `astryx component Sheet` |
   | DRAKON Studio SVG | *(власний — Astryx не має графового редактора)* | — |

3.4 **Стратегія StyleX vs Tailwind:**
   Astryx рекомендує StyleX але сумісний з Tailwind через `tailwind-theme.css`. Скажи, що обираєш і чому. Врахуй, що наш прототип використовує plain CSS-змінні — треба буде тримати dev-experience зрозумілим.

3.5 **Кроки міграції (упорядкований чекліст):**
   Приклад послідовності (уточни):
   1. `npm create next-app@15 b-sdd-workbench --typescript --app`
   2. `npm i @astryxdesign/core @astryxdesign/theme-neutral @stylexjs/stylex`
   3. `npm i -D @astryxdesign/cli && npx astryx init` (щоб він записав AGENTS.md для мене)
   4. Скопіювати `data.js` → `src/mock/index.ts` з TypeScript-типами.
   5. Замінити `data.js` → tanstack-query hooks, що дзвонять твої API.
   6. Перенести `styles.css` токени в `defineTheme()` через Astryx theme API.
   7. По одному замінити компоненти згідно з таблицею §3.3.
   8. DRAKON Studio залишити як власний SVG-компонент (Astryx не покриває) → перенести з мінімальними правками, замінити CSS-змінні на Astryx-токени.
   9. Додати Cloudflare Pages `_headers` та `_redirects` (з CSP для твоїх endpoints).
   10. CI-gate: блокувати merge, якщо Φ5-fitness-тести падають.

3.6 **Каталог питань до мене (frontend-агента):**
   Якщо тобі щось незрозуміло у моєму прототипі — записуй у §3.6 як `[Q1] ..., [Q2] ...`. Я на них відповім у наступному циклі.

3.7 **Δ C-вектор порушень мого прототипу:**
   Якщо ти виявив, що мій фронт порушує якийсь інваріант (наприклад, я хардкодив колір замість використання токена, або пропустив ARIA-атрибут), запиши це як `ΔC = { ... }` — це буде вхідним негативним інваріантом для мого наступного циклу.

### § 4. Handoff CLI-команда для наступного циклу

Точний shell-рядок, який Head Architect має виконати для запуску мене (frontend-агента) на новий цикл. Формат такий самий, як у нашому Approve overlay:

```bash
./run_b_sdd.sh "Milestone N: Migrate B-SDD Workbench frontend to Astryx + real Utopia/LLM/Appwrite APIs · seed: <handoff.json hash>"
```

---

## 6. Правила комунікації зі мною

- **Не переписуй те, що вже працює.** Мій прототип — це живий контракт. Замінюй тільки те, що явно змінюється (реальні URL, автентифікація).
- **Не дзвони назовні через ті самі URL.** Мій фронт зараз не робить жодних мережевих запитів. Всі точки, де він БУДЕ дзвонити, чітко позначені в HANDOFF-документі. Не додавай "приховані" запити.
- **Не змінюй форму DTO без пояснення.** Якщо в `data.js` я маю `{ id, title, status, tv, tt, supersededBy, domain }` — твоя відповідь `/adrs/{id}` МАЄ містити рівно ці поля. Додаткові поля можеш додати, але існуючі не перейменовуй.
- **Не забувай про Ukrainian labels.** Оператор — україномовний Head Architect. Технічні терміни лишаються англійськими (ADR, DRAKON, invariant, stream), але допоміжні тексти українською. Дивись copy у `components/*.jsx`.
- **Кожне рішення = ADR.** Якщо ти вирішив, наприклад, використати `pgvector` замість `qdrant` — це нове рішення, потребує MADR у твоєму репо. Посилання на нього має бути у зворотному промті.

---

## 7. Deadline та критерії приймання

- **Deadline:** визначає Head Architect (Volodymyr Kovalenko).
- **Критерії приймання (Definition of Done):**
  - Всі 9 кроків тестового сценарію (§4) працюють end-to-end на dev-середовищі.
  - `PROMPT_FRONTEND_MIGRATION.md` створено і містить всі 4 розділи (§1..§4 із §5 цього промту).
  - OpenAPI спека валідується `spectral lint openapi.yaml` без warnings.
  - Всі 4 інваріанти з §2.5 покриті runtime-перевірками з unit-тестами.
  - CLI `astryx init` виконано у майбутньому фронт-репо (щоб я, як агент, побачив автосгенерований компонентний індекс).
  - Хоча б одна DRAKON-схема твоєї роботи (наприклад, `sse_router.drn`) закомічена в твоєму бекенд-репо і посилання на неї є у §1 зворотного промту.

---

## 8. Джерела та довідники

- **Astryx GitHub:** https://github.com/facebook/astryx
- **Astryx docs (Storybook):** https://facebook.github.io/astryx/
- **Astryx core README:** `packages/core/README.md` у їх репо (тут — важливо, там повний Quick Start для Next.js/Vite/CDN)
- **DRAKON widget referenc:** https://github.com/maxfraieho/drakonwidget
- **B-SDD методологія:** твій репо `maxfraieho/b-sdd` (наразі приватний, я його не бачу — це твоє джерело правди)

---

## 9. Фінальне зауваження

Ти можеш ставити мені прямі запитання через ΔC-вектор у своєму зворотному промті (§3.7 у форматі відповіді). Я не читаю думки — задокументуй кожне припущення, яке ти зробив за мене.

Успіху. Побачимось у наступному циклі з `PROMPT_FRONTEND_MIGRATION.md` у руках.

**— Frontend Design Agent**

---

## Additional Notes for Head Architect (перед запуском промту)

Перед тим, як віддавати цей промт бекенд-агенту, перевір:
- [ ] Ти дав йому доступ до `docs/decision/*.md` (три файли).
- [ ] Ти дав йому доступ до `data.js` та `components/*.jsx`.
- [ ] Ти дав йому доступ до `styles.css` (він мусить розуміти токени).
- [ ] Ти надав йому mTLS-сертифікати для `.251:9922` та `.184:18880`.
- [ ] Ти надав йому Appwrite `projectId` та service-account API-key.
- [ ] Ти повідомив йому deadline і чи є жорсткі архітектурні обмеження, які я не описав.
