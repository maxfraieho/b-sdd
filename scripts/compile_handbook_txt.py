#!/usr/bin/env python3
"""
B-SDD Monolithic Operator Handbook Compiler.
Compiles all 10 user guide chapters and architectural appendices into a single
canonical monolithic document (dist/B_SDD_OPERATOR_HANDBOOK_COMPLETE.txt and .md)
for seamless Google NotebookLM ingestion and deep dive audio overview synthesis.
100% Pure Python Standard Library (ADR-002).
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs" / "user_guide"
VOL2_DIR = ROOT / "docs" / "user_guide_vol2"
ADR_DIR = ROOT / "docs" / "ADR"
DIST_DIR = ROOT / "dist"

CHAPTER_TITLES = {
    "01": "МАНІФЕСТ, ПРИНЦИПИ ТА АРХІТЕКТУРНА ФІЛОСОФІЯ",
    "02": "СЕМИФАЗНИЙ ДИСКРЕТНИЙ ЖИТТЄВИЙ ЦИКЛ СПРИНТУ (PHI_1 - PHI_7)",
    "03": "ПЛАНАРНІ ДРАКОН-АЛГОРИТМИ ТА ВІЗУАЛЬНИЙ СТАНДАРТ C=0",
    "04": "МУЛЬТИРЕПОЗИТОРНА СТРУКТУРА ТА СЕМАНТИЧНИЙ ГРАФ GITNEXUS",
    "05": "СУВЕРЕННА MESH-АРХІТЕКТУРА ТА БІТЕМПОРАЛЬНІ ОРЕНДИ (LEASES)",
    "06": "КОНСЕНСУС АГЕНТІВ, КВОРУМ ТА СТАНДАРТ ПОСТАНОВКИ ЗАДАЧ",
    "07": "САМОЗЦІЛЕННЯ КОДУ, ДІАГНОСТИКА ТА АВТОНОМНИЙ ROLLBACK",
    "08": "ASTRYX COCKPIT UI: КЕРІВНИЦТВО ОПЕРАТОРА ТА ТЕЛЕМЕТРІЯ",
    "09": "РЕЄСТР АРХІТЕКТУРНИХ РІШЕНЬ (ADR-001 - ADR-016)",
    "10": "ПРАКТИЧНИЙ ПОСІБНИК ОПЕРАТОРА ТА CLI ІНСТРУМЕНТАРІЙ"
}


def compile_handbook() -> Path:
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    out_txt = DIST_DIR / "B_SDD_OPERATOR_HANDBOOK_COMPLETE.txt"
    out_md = DIST_DIR / "B_SDD_OPERATOR_HANDBOOK_COMPLETE.md"

    lines = []

    # Title & Metadata
    lines.append("=" * 80)
    lines.append("B-SDD: BITEMPORAL SPEC-DRIVEN DEVELOPMENT")
    lines.append("СУВЕРЕННА АРХІТЕКТУРА ТА ПОВНИЙ ПРАКТИЧНИЙ ПОСІБНИК ОПЕРАТОРА")
    lines.append("Версія 3.1 | Вересень 2026 | Автономне ядро B-SDD Core")
    lines.append("=" * 80)
    lines.append("")
    lines.append("Автор: Архітектурна команда B-SDD & Агент Agy")
    lines.append("Цільове призначення: База знань SSoT та первинне джерело для Deep Dive Audio Podcast")
    lines.append("Кластер: .161 (Core/Agy) | .184 (GitNexus/MCP) | .251 (Pixel 7 Podroid / Laya System 1)")
    lines.append("Edge: Cloudflare Pages (https://b-sdd-ui.pages.dev)")
    lines.append("")
    lines.append("=" * 80)
    lines.append("ЗМІСТ (TABLE OF CONTENTS)")
    lines.append("=" * 80)
    for ch_num, ch_title in CHAPTER_TITLES.items():
        lines.append(f"  ГЛАВА {ch_num}: {ch_title}")
    lines.append("  ДОДАТОК A: Канонічний реєстр архітектурних рішень (ADR-001 .. ADR-016)")
    lines.append("  ДОДАТОК B: Кластерна топологія та фізичний розподіл сервісів")
    lines.append("  ДОДАТОК C: Інструкція оператора з Dual-Gate Pre-Commit контролю")
    lines.append("  ДОДАТОК D: Каталог 60 системних та процедурних скілів B-SDD")
    lines.append("  ДОДАТОК E: Хроніка еволюції спринтів (Sprint 020 – Sprint 034 Ledger)")
    lines.append("")
    lines.append("=" * 80)
    lines.append("")

    # Process Chapters 01 to 10
    chapter_files = sorted([f for f in os.listdir(DOCS_DIR) if f.endswith(".md") and f[:2].isdigit()])
    for fname in chapter_files:
        ch_num = fname[:2]
        ch_title = CHAPTER_TITLES.get(ch_num, fname)
        ch_path = DOCS_DIR / fname
        with open(ch_path, "r", encoding="utf-8") as f:
            ch_content = f.read().strip()

        lines.append("")
        lines.append("=" * 80)
        lines.append(f"ГЛАВА {ch_num}: {ch_title}")
        lines.append("=" * 80)
        lines.append("")
        lines.append(ch_content)
        lines.append("")

    # APPENDIX A: Canonical ADRs
    lines.append("")
    lines.append("=" * 80)
    lines.append("ДОДАТОК A: РЕЄСТР АРХІТЕКТУРНИХ РІШЕНЬ (ADR-001 .. ADR-016)")
    lines.append("=" * 80)
    lines.append("")
    mega_adr_path = ADR_DIR / "B_SDD_MEGA_ADR_MASTER.md"
    if mega_adr_path.exists():
        with open(mega_adr_path, "r", encoding="utf-8") as f:
            lines.append(f.read().strip())
        lines.append("")

    # Individual ADR details from vol2 if available
    if VOL2_DIR.exists():
        adr_files = sorted([f for f in os.listdir(VOL2_DIR) if "adr_" in f and f.endswith(".md")])
        for af in adr_files:
            af_path = VOL2_DIR / af
            with open(af_path, "r", encoding="utf-8") as f:
                lines.append(f"\n--- {af} ---\n")
                lines.append(f.read().strip())
                lines.append("")

    # APPENDIX B: Cluster Topology & Physical Distribution
    lines.append("")
    lines.append("=" * 80)
    lines.append("ДОДАТОК B: КЛАСТЕРНА ТОПОЛОГІЯ ТА ФІЗИЧНИЙ РОЗПОДІЛ СЕРВІСІВ")
    lines.append("=" * 80)
    lines.append("")
    lines.append("""
1. ВУЗОЛ 192.168.3.161 (Primary Development Engine & Supervisor):
   - Роль: Первинний синтез коду, виконання агентських сесій Agy, локальний супервайзер (:8161).
   - Робочі репозиторії: ~/projects/b-sdd (Core), ~/projects/b-sdd-feedback-loop (Supervisor Daemon).
   - Диспетчер: ./run_b_sdd.sh з автоматичною компіляцією правил (<500 слів) та перевіркою фітнес-шлюзів.
   - Телеметрія: Локальні журнали logs/kindle_delivery.log, logs/supervisor.log.

2. ВУЗОЛ 192.168.3.184 (AST Engine, Headless Kindle Dispatcher & NotebookLM MCP):
   - Роль: Сервер семантичного графу коду GitNexus, локальний headless шлюз компіляції EPUB.
   - Сервіси:
     • NotebookLM MCP Gateway (:8002) - REST/JSON-RPC інтерфейс до Google NotebookLM.
     • GitNexus AST Engine - аналіз радіусу впливу змін (blast radius) та PDG-запити.
     • Резервний контур доставки книг: send_digest.py.

3. ВУЗОЛ 192.168.3.251 (Google Pixel 7 / Alpine Linux у Podroid):
   - Роль: Суб-40мс апаратна System 1 класифікація та нестираємий бітемпоральний леджер.
   - Сервіси:
     • Laya System 1 Decision Engine (:9623): не-авторегресивна нейрокласифікація задач, оцінка ризику порушення ADR (p_violation), рекомендація трійок скілів (Golden Triads).
     • Utopia DB WORM Socket (:9622): незмінний журнал транзакцій, WORM-хеші комітів, бітемпоральний час Tv/Tx.
   - Відмовостійкість: Автоматичний локальний евристичний фолбек у супервайзері у разі недоступності сокетів (degraded_mode=1).

4. EDGE CLOUD ТА ЗОВНІШНІ ШЛЮЗИ:
   - Astryx Cockpit UI: https://b-sdd-ui.pages.dev на Cloudflare Pages з Server-Sent Events (SSE).
   - n8n Automation Engine: https://n8n.exodus.pp.ua/webhook/dispatch-kindle-book для гарантованої доставки на Amazon Send-to-Kindle (tukroschu@kindle.com).
   - Telegram Bot Gateway: інтерактивні сповіщення оператора (chat_id: 6412868393).
""")

    # APPENDIX C: Dual-Gate Pre-Commit Verification Guide
    lines.append("")
    lines.append("=" * 80)
    lines.append("ДОДАТОК C: ІНСТРУКЦІЯ ОПЕРАТОРА З DUAL-GATE PRE-COMMIT КОНТРОЛЮ")
    lines.append("=" * 80)
    lines.append("")
    lines.append("""
1. МАТЕМАТИЧНИЙ ІНВАРІАНТ ДОЗВОЛУ КОМІТУ:
   AllowCommit <=> (P_risk < 0.15) AND (S_intent >= 0.82) AND (MissingAsserts == 0)

2. ВЕКТОР 2 (DIFF RISK GATE):
   - Оцінює обсяг та характер дифу в робочому дереві.
   - Блокує несанкціоноване використання unsanitized shell execution, модифікацію імутабельних скілів без дозволу та прямий запис у захищені конституційні файли.
   - Поріг зупинки: якщо P_risk >= 0.15, коміт блокується вердиктом HALT_FOR_INSPECTION.

3. ВЕКТОР 3 (SPEC INTENT ALIGNMENT GATE):
   - Парсить формальний псевдокод специфікації ALGORITHM та ДРАКОН-схеми (.drakon.json).
   - Зіставляє декларативні вирази ASSERT, EXECUTE та CALL_SKILL з AST-деревом реалізованого Python коду.
   - Обчислює косинусне вирівнювання інтенту S_intent. Якщо S_intent < 0.82 або пропущено хоча б один критичний інваріант — коміт відхиляється.

4. ПРОЦЕДУРА OPERATOR OVERRIDE:
   - Якщо оператор після ручного аналізу ухвалює рішення прийняти зміни примусово, дозволено прапорець bypass.
   - Будь-який такий коміт фіксується у WORM-леджері як виняток з позначкою OPERATOR_OVERRIDE.
""")

    # APPENDIX D: Skills Taxonomy
    lines.append("")
    lines.append("=" * 80)
    lines.append("ДОДАТОК D: КАТАЛОГ 60 СИСТЕМНИХ ТА ПРОЦЕДУРНИХ СКІЛІВ B-SDD")
    lines.append("=" * 80)
    lines.append("")
    skills_cat_path = ROOT / "docs" / "skills_dump" / "ACTIVE_SKILLS_CATALOG.md"
    if skills_cat_path.exists():
        with open(skills_cat_path, "r", encoding="utf-8") as f:
            lines.append(f.read().strip())
        lines.append("")

    # APPENDIX E: Sprint Evolution Ledger
    lines.append("")
    lines.append("=" * 80)
    lines.append("ДОДАТОК E: ХРОНІКА СПРИНТІВ ТА БІТЕМПОРАЛЬНИЙ ЛЕДЖЕР ЗМІН")
    lines.append("=" * 80)
    lines.append("")
    if VOL2_DIR.exists():
        sprint_files = sorted([f for f in os.listdir(VOL2_DIR) if "sprint_" in f and f.endswith(".md")])
        for sf in sprint_files:
            sf_path = VOL2_DIR / sf
            with open(sf_path, "r", encoding="utf-8") as f:
                lines.append(f"\n--- {sf} ---\n")
                lines.append(f.read().strip())
                lines.append("")

    full_text = "\n".join(lines)
    encoded_bytes = full_text.encode("utf-8")

    with open(out_txt, "wb") as f:
        f.write(encoded_bytes)

    with open(out_md, "wb") as f:
        f.write(encoded_bytes)

    size = len(encoded_bytes)
    print(f"✓ Compiled monolithic handbook: {out_txt}")
    print(f"  Size: {size} bytes ({size / 1024:.1f} KB)")
    print(f"  Markdown mirror: {out_md}")

    if size < 150 * 1024:
        print(f"[-] Warning: Output size {size} is less than required 150 KB!", file=sys.stderr)
        sys.exit(1)

    return out_txt


if __name__ == "__main__":
    compile_handbook()
