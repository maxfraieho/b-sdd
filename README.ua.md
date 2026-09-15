# B-SDD: Bitemporal Spec-Driven Development (Українська версія)

[![Фітнес-тести](https://img.shields.io/badge/Архітектурні%20тести-5%2F5%20Пройдено-brightgreen)](tests/test_architecture_fitness.py)
[![Ліцензія](https://img.shields.io/badge/Ліцензія-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Без сторонніх залежностей](https://img.shields.io/badge/Залежності-100%25%20Python%20Stdlib-blue)](src/)
[![Швидкість компіляції](https://img.shields.io/badge/Затримка-%3C20%20мс-orange)](src/core/compiler.py)
[![Щільність правил](https://img.shields.io/badge/Ліміт%20промпту-%3C500%20слів-purple)](.context/active_rules.md)

> **Безперервні архітектурні інваріанти без втрати контексту.**  
> Детермінована референсна архітектура та pre-flight компілятор правил для автономних AI-агентів розробки (Claude Code, OpenAI Codex CLI, Google Antigravity CLI).

---

## 🌐 Документація
- 📖 [Повна специфікація та маніфест методології (Українська)](docs/B_SDD_METHODOLOGY.ua.md)
- 📖 [Full Methodology Specification & Manifesto (English)](docs/B_SDD_METHODOLOGY.md)
- 🇬🇧 [English README](README.md)

---

## 💡 Що таке B-SDD?

Під час тривалої розробки програмного забезпечення за допомогою AI-агентів виникає **Архітектурна деградація (Architecture Drift)**: моделі «воскрешають» старий застарілий код, порушують межі модулів та галюцинують вимоги, які вже давно було замінено.

**B-SDD (Bitemporal Spec-Driven Development)** вирішує цю проблему через детермінований синтез 5 складових:

$$\text{B-SDD} = \underbrace{\text{Бітемпоральні інваріанти (Utopia DB)}}_{\text{ЩО (Межі та Заборони)}} + \underbrace{\text{AST Граф коду (GitNexus)}}_{\text{ДЕ (Топологія компонентів)}} + \underbrace{\text{Процедурні скіли (MCP)}}_{\text{ЯК (Плейбуки та Інструменти)}} + \underbrace{\text{Детермінований компілятор}}_{\text{КОЛИ (Pre-Flight <20мс)}} + \underbrace{\text{Фітнес-шлюзи}}_{\text{ПЕРЕВІРКА (pytest 5/5)}}$$

---

## ⚡ Швидкий старт (30 секунд)

### 1. Pre-Flight компіляція правил
Перед початком роботи або перед запуском агента скомпілюйте зріз активних архітектурних правил:
```bash
./run_agy.sh
# або вручну:
python3 -m src.cli.main compile
```
Результат формується у файлі [`.context/active_rules.md`](.context/active_rules.md) за **< 20 мс** з жорстким лімітом до **500 слів**.

### 2. Запуск архітектурних фітнес-тестів
Переконайтеся, що всі 5 критеріїв придатності пройдено:
```bash
pytest -v tests/test_architecture_fitness.py
```

### 3. Синхронізація з базою Utopia DB
Передайте діючі інваріанти та граф зв'язків у виділену базу знань Utopia Knowledge Graph:
```bash
python3 scripts/sync_utopia.py
```

---

## 📊 Порівняльна таблиця з інструментами індустрії

| Критерій | Cursor / Windsurf Rules | Vector RAG / MemGPT | Оптимізація DSPy | Звичайні Agent Skills | **B-SDD Framework** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Детерміноване заміщення** | ❌ Відсутнє | ❌ Ймовірнісна помилка | ❌ Відсутнє | ❌ Відсутнє | ✅ **Математичний DAG (`valid_to = NOW`)** |
| **Розмір промпту** | ⚠️ Необмежений (>2000 слів) | ⚠️ Довільні шматки RAG | ⚠️ Змінний | ⚠️ Лише розмір скіла | ✅ **Суворий ліміт (<500 слів)** |
| **Швидкість компіляції** | 0 мс (Статичний файл) | 300–1200 мс (Ембеддинг/БД) | 500–2500 мс (LLM-виклик) | 0 мс (Статичний файл) | ✅ **<20 мс (Кешований компілятор)** |
| **Граф впливу коду** | ❌ Немає | ❌ Немає | ❌ Немає | ❌ Немає | ✅ **GitNexus AST-маршрутизація** |
| **Процедурна майстерність** | ❌ Тільки текст промпту | ❌ Тільки текст промпту | ❌ Тільки промпт | ✅ Висока (Плейбуки інструментів) | ✅ **Інтегровані скіли + Rule of 2** |
| **Автоматичні фітнес-тести** | ❌ Немає | ❌ Немає | ⚠️ Оцінка метрик | ❌ Немає | ✅ **Архітектурні тести Pytest (5/5)** |
| **Зовнішні залежності** | 0 | Важкі (Torch/Chroma/LangChain) | Важкі (PyTorch/DSPy) | Низькі | ✅ **Нуль (Чиста stdlib Python у `src/`)** |

---

## 🔄 6-фазний життєвий цикл розробки

```
[ Фаза 0: Pre-Flight Hook ] ──────────> run_agy.sh / b-sdd compile
                                          │
                                          ▼
[ Фаза 1: Компіляція правил та скілів ] > .context/active_rules.md (<20 мс, <500 слів)
                                          - ОБОВ'ЯЗКОВІ ІНВАРІАНТИ
                                          - РЕКОМЕНДОВАНІ ПРОЦЕДУРНІ СКІЛИ
                                          │
                                          ▼
[ Фаза 2: Вибір та пошук скілів ] ────> Агент обирає скіл (або викликає find-skills)
                                          │
                                          ▼
[ Фаза 3: Оформлення спеки ] ─────────> specs/<NNN>/ (spec.md, plan.md, tasks.md)
                                          │
                                          ▼
[ Фаза 4: Реалізація у коді ] ────────> Код пишеться суворо за активними інваріантами
                                          │
                                          ▼
[ Фаза 5: Фітнес-шлюз ] ──────────────> pytest tests/test_architecture_fitness.py (5/5 OK)
                                          │
                                          ▼
[ Фаза 6: Еволюція скілів (Rule of 2)]> Якщо процес повторився >= 2 разів: skill-creator!
```

---

## 🛠️ Шпаргалка команд CLI

```bash
# Компіляція правил для поточного репозиторію
python3 -m src.cli.main compile

# Компіляція під конкретні змінені файли
python3 -m src.cli.main compile --files src/core/compiler.py

# Синхронізація з центральною базою Utopia DB
python3 -m src.cli.main sync

# Запуск архітектурних фітнес-тестів
python3 -m src.cli.main fitness

# Ініціалізація структури B-SDD у новому проекті
python3 -m src.cli.main init --name "Мій проект"

# Створення нового архітектурного рішення (ADR)
python3 -m src.cli.main adr new "WebSocket Protocol" --component core --supersedes ADR-002
```

---

## 📜 Ліцензія та авторські права
- **Виконуваний код та інструменти:** Розповсюджуються за ліцензією [Apache License, Version 2.0](LICENSE).  
  Авторські права (c) 2026 **Арсен Коваленко** ([@maxfraieho](https://github.com/maxfraieho)).
- **Специфікація та методологія:** Захищені ліцензією [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

