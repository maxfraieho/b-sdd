---
name: b-sdd-notebooklm-kindle-dispatch
description: Еталонний конвеєр B-SDD: витягування розділів книги через NotebookLM MCP, детермінована збірка EPUB 3.0 та гарантована доставка на Amazon Kindle через шлюз n8n без поля CC (Anti-E009).
category: bssd-system-skill
type: SYSTEM_SKILL
immutable: true
---

# Автономне витягування книг з NotebookLM MCP та доставка на Kindle

> **B-SDD Invariant (ADR-003 Rule of 2/3):** Кристалізовано після 3 повторних успішних спостережень та верифікації на хості `192.168.3.184`.

---

## 1. Архітектурні якоря (Pinned Anchors & Invariants)

- **Джерело контенту (Source Endpoint):**
  - **NotebookLM MCP Server:** `http://192.168.3.184:8002/mcp` (методи: `sources_list`, `sources_get_fulltext`).
  - **Обробник тексту на .184:** Повертає нативний `ft.content` без сирих repr-обгорток.
  - **Відомі цільові блокноти:**
    * `b371bcda-77c6-4803-84e7-8aed42817454` — *FDE: Посібник інженера передового розгортання* (13 розділів: 00..12).
    * `205ee2ec-e0d2-4ba6-badf-44f2de02c7e2` — *B-SDD Architecture Core*.
    * `6813ab1c-ac22-4c3c-9c8e-9dd67e35da99` — *B-SDD Legal Dossier*.
- **Канал доставки (Delivery Gateway):**
  - **Primary Gateway:** `https://n8n.exodus.pp.ua/webhook/dispatch-kindle-book` (воркфлоу `GC5pv2TIYbKHj2Ch` — *B-SDD Kindle Dispatcher*).
  - **Автентифікація:** Авторизований токен Google API `tukroschu@gmail.com` активний на стороні n8n.
  - **Anti-E009 Invariant:** Поле `CC` суворо відсутнє / порожнє (запобігання блокуванню Amazon Kindle).
  - **Формат файлу:** Суворо EPUB 3.0, MIME-тип `application/epub+zip` (перший нестиснений файл у ZIP-контейнері), розмір > 50 КБ.
- **Телеметрія та зворотний зв'язок (Dual-Loop Telemetry):**
  - **Supervisor Webhook:** `https://n8n.exodus.pp.ua/webhook/bsdd-supervisor-result` (надсилає сповіщення у Telegram-чат 6412868393 та резервний звіт на `tukroschu@gmail.com`).
  - **Локальний лог:** [`logs/kindle_delivery.log`](file:///home/vokov/projects/b-sdd/logs/kindle_delivery.log).
  - **Незмінний WORM-леджер:** [`docs/utopia_local_worm.jsonl`](file:///home/vokov/projects/b-sdd/docs/utopia_local_worm.jsonl) та Utopia DB (`192.168.3.251`, виклик `utopia_worm_append`).

---

## 2. Швидкий виконуваний раннер (Turnkey One-Shot Execution)

Виконання повного циклу витягування, збірки та доставки однією командою:

```bash
python3 scripts/notebooklm_to_kindle.py \
  --notebook b371bcda-77c6-4803-84e7-8aed42817454 \
  --title "FDE: Посібник інженера передового розгортання" \
  --author "Фань Бін (Fan Bing / XDash)" \
  --to tukroschu@kindle.com
```

### Dry-run режим (перевірка витягування та збірки без надсилання пошти):
```bash
python3 scripts/notebooklm_to_kindle.py --notebook <NOTEBOOK_ID> --dry-run
```

---

## 3. ДРАКОН-алгоритм (Планарний шампур X=0.0, C=0)

1. `[HEADLINE]` Початок: Виконання b-sdd-notebooklm-kindle-dispatch (X=0.0, Y=0.0)
2. `[ACTION]` Крок 1: Ініціалізація клієнта NotebookLM MCP на `192.168.3.184:8002` (X=0.0, Y=2.0)
3. `[ACTION]` Крок 2: Отримання списку розділів `sources_list` та викачування `sources_get_fulltext` (X=0.0, Y=4.0)
4. `[ACTION]` Крок 3: Детермінована компіляція EPUB 3.0 через pandoc (--toc, valid container) (X=0.0, Y=6.0)
5. `[QUESTION]` Крок 4: Шлюз n8n `dispatch-kindle-book` відповідає 200 OK? (X=0.0, Y=8.0)
   - *Праворуч (X=4.0, Y=8.0):* Буферизація у чергу на вузлі .184 -> Аварійне завершення (X=4.0, Y=10.0)
   - *Вниз (X=0.0, Y=10.0):* Успішна доставка
6. `[ACTION]` Крок 5: Відправка на Kindle через n8n без поля CC (X=0.0, Y=10.0)
7. `[ACTION]` Крок 6: Реєстрація WORM-запису, емісія телеметрії та резервний лист (X=0.0, Y=12.0)
8. `[END]` Успішне завершення: Книгу доставлено на Kindle (X=0.0, Y=14.0)

---

## 4. Верифікація результатів

```bash
# Перевірка статусу доставки
tail -n 15 logs/kindle_delivery.log

# Перевірка локального WORM-запису
tail -n 5 docs/utopia_local_worm.jsonl
```
