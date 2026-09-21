# Спринт 027: Відновлення скілів B-SDD, компіляція книги Vol. 2 та доставка на Kindle

**Sprint ID:** `sprint_027_restore`  
**Статус:** Успішно завершено  
**Основні інваріанти:** ADR-002, ADR-003, Amazon Send-to-Kindle Invariant, Invariant FL-01

---

## 1. Мета та архітектурний фокус
Повернення в активний каталог ядра чотирьох фундаментальних навичок фреймворку B-SDD: `kindle-release-pipeline`, `drakon-compiler`, `utopia-intent-ledger`, `astryx-scaffolder`. Формування другого тому архітектурної книги `b_sdd_architecture_vol2.epub`, що поєднує практичний посібник (розділи 01–10), реєстр архітектурних рішень (ADR-001–ADR-012) та історію спринтів (sprint_020–sprint_027), з наступною автономною передачею на Amazon Kindle (`tukroschu@kindle.com`).

## 2. Ключові досягнення
- **Відновлення 4 скілів фреймворку:**
  - `kindle-release-pipeline`: автономна збірка та відправка EPUB на пристрої Kindle та Gmail backup.
  - `drakon-compiler`: компілятор планарних візуальних схем ($C=0, X=0$) в IR та макропромпти.
  - `utopia-intent-ledger`: bitemporal WORM транзакції та синхронізація з графом знань Utopia DB (.251).
  - `astryx-scaffolder`: генератор інтерфейсних зон та компонентів кокпіта Astryx.
- **Оновлення каталогу активних скілів:** Зареєстровано 53 активні скіли ядра у `docs/skills_dump/ACTIVE_SKILLS_CATALOG.md` та згенеровано повний дамп `SKILLS_INVENTORY_DUMP.md` (1.16 МБ).
- **Компіляція другого тому (Vol. 2):** Створено структуру `docs/user_guide_vol2/` із 30 впорядкованих розділів та скомпільовано валідний електронний документ `docs/b_sdd_architecture_vol2.epub`.
- **Kindle & Gmail Dispatch:** Скрипт `scripts/bsdd_to_kindle.py` виконав підготовку, пакування та ініціалізацію поштового транспорту на Kindle (`tukroschu@kindle.com`) з резервною копією оператору.
