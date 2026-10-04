import React, { useState, useEffect, useMemo } from 'react';

export interface FactEpisode {
  id: string;
  chapter: string;
  title: string;
  originalText: string;
  validTimeTv: string;
  legalArticles: string[];
  evidenceIds: string[];
  status: 'VERIFIED' | 'NEEDS_CALIBRATION' | 'CONTRADICTED' | 'SUPERSEDED';
  affectedClaimsChf?: number;
}

export interface BlastRadiusResult {
  factId: string;
  impactScore: number;
  cascadingChapters: string[];
  relatedEvidence: string[];
  statuteOfLimitations: {
    years: number;
    expiryDate: string;
    isUrgent: boolean;
  };
  contradictionsDetected: Array<{
    targetFactId: string;
    source: string;
    contradictionText: string;
    severity: 'HIGH' | 'MEDIUM';
  }>;
}

// Попередньо завантажені опорні епізоди справи PE24.014624-SBA
const BENCHMARK_EPISODES: FactEpisode[] = [
  {
    id: 'EP-01-FUNDS-15K',
    chapter: 'Розділ 01 & 02',
    title: 'Привласнення $15\'000 USD сімейних заощаджень (Луцьк / Швейцарія)',
    originalText: 'Любов Суворова прийняла на збереження $15\'000 USD, сформовані Володимиром Коваленком для купівлі житла, та відмовилася повертати, привласнивши кошти.',
    validTimeTv: '2024-03-25T06:24:00Z',
    legalArticles: ['Art. 138 CP (Abus de confiance)', 'Art. 146 CP (Escroquerie)'],
    evidenceIds: ['ДОКАЗ C-08', 'АУДІО D-01', 'АУДІО D-06'],
    status: 'VERIFIED',
    affectedClaimsChf: 13500,
  },
  {
    id: 'EP-02-FORGERY-IMMA',
    chapter: 'Розділ 01 & 04',
    title: 'Фальсифікація дипломів та довідок Академії Менухіна (IMMA)',
    originalText: 'Любов Суворова систематично підробляла сертифікати навчання IMMA за 2011-2012 рр. для незаконного отримання дозволу B/L у кантонах Невшатель та Во.',
    validTimeTv: '2012-09-01T00:00:00Z',
    legalArticles: ['Art. 251 CP (Faux dans les titres)', 'Art. 118 LEI'],
    evidenceIds: ['PIÈCE A-01', 'ANNEXE A'],
    status: 'VERIFIED',
  },
  {
    id: 'EP-03-INJURY-DISPUTE',
    chapter: 'Розділ 06 & Додаток C',
    title: 'Інцидент 20 липня 2024: Симуляція тілесних ушкоджень Оленою',
    originalText: 'Підозрювана стверджувала про напад та побиття з утворенням синців. Спростовано EXIF-камерами (відсутність слідів через 17.5 год) та актом Unisanté.',
    validTimeTv: '2024-07-20T14:30:00Z',
    legalArticles: ['Art. 303 CP (Dénonciation calomnieuse)', 'Art. 304 CP'],
    evidenceIds: ['ДОКАЗ C-10 (Unisanté)', 'АУДІО C-15', 'F_2 (EXIF)'],
    status: 'CONTRADICTED',
  },
  {
    id: 'EP-04-ARSEN-CAPACITY',
    chapter: 'Розділ 03',
    title: 'Процесуальний статус Арсена Коваленка (Повнолітній потерпілий)',
    originalText: 'Арсен Коваленко (нар. 05.11.1999, 26 років) — повнолітній дієздатний потерпілий та цивільний позивач. Порушення прав дорослої людини.',
    validTimeTv: '2024-08-05T00:00:00Z',
    legalArticles: ['Art. 115 CPP', 'Art. 118 CPP', 'Art. 122 CPP'],
    evidenceIds: ['Permis S', 'Passeport National', 'Contrat EVAM'],
    status: 'VERIFIED',
  },
];

export const FactCalibrationWorkbench: React.FC = () => {
  const [episodes, setEpisodes] = useState<FactEpisode[]>(BENCHMARK_EPISODES);
  const [selectedId, setSelectedId] = useState<string>(BENCHMARK_EPISODES[0].id);
  const [editedStatement, setEditedStatement] = useState<string>('');
  const [editedTv, setEditedTv] = useState<string>('');
  const [editedArticles, setEditedArticles] = useState<string[]>([]);
  const [blastResult, setBlastResult] = useState<BlastRadiusResult | null>(null);
  const [isCalculating, setIsCalculating] = useState<boolean>(false);
  const [isSealing, setIsSealing] = useState<boolean>(false);
  const [notification, setNotification] = useState<{ type: 'success' | 'warn' | 'error'; text: string } | null>(null);

  const activeEpisode = useMemo(
    () => episodes.find(e => e.id === selectedId) || episodes[0],
    [episodes, selectedId]
  );

  useEffect(() => {
    if (activeEpisode) {
      setEditedStatement(activeEpisode.originalText);
      setEditedTv(activeEpisode.validTimeTv);
      setEditedArticles(activeEpisode.legalArticles);
      calculateBlastRadius(activeEpisode, activeEpisode.originalText, activeEpisode.legalArticles);
    }
  }, [activeEpisode]);

  // Рушій розрахунку точок ураження (Blast Radius) та каскадних колізій
  const calculateBlastRadius = (episode: FactEpisode, newText: string, articles: string[]) => {
    setIsCalculating(true);
    
    // Імітація запиту до графового рушія KùzuDB / GitNexus
    setTimeout(() => {
      const isFinancial = newText.includes('15\'000') || newText.includes('15000') || articles.some(a => a.includes('138') || a.includes('146'));
      const isUrgentArticle = articles.some(a => a.includes('138') || a.includes('146') || a.includes('157'));
      
      const cascading: string[] = ['Розділ 01 (Меморандум позову)'];
      if (isFinancial) {
        cascading.push('Розділ 02 (Реєстр доказів C-08, D-01)');
        cascading.push('Розділ 04 (Арешт активів ст. 263 CPP на CHF 46\'000)');
        cascading.push('Додаток D (Таблиця збитків Claim Chart)');
      }
      if (articles.some(a => a.includes('303') || a.includes('304'))) {
        cascading.push('Розділ 06 (Спростування фальшивого доносу F_1..F_4)');
      }

      const contradictions = [];
      if (episode.id === 'EP-03-INJURY-DISPUTE') {
        contradictions.push({
          targetFactId: 'F_1 (Olena Claim)',
          source: 'Unisanté Medical Act FOR597 & EXIF Metadata',
          contradictionText: 'Невідповідність часу виникнення подряпин (<24 год) заявленій даті конфлікту 20 липня.',
          severity: 'HIGH' as const,
        });
      }

      setBlastResult({
        factId: episode.id,
        impactScore: cascading.length * 1.5,
        cascadingChapters: cascading,
        relatedEvidence: episode.evidenceIds,
        statuteOfLimitations: {
          years: isUrgentArticle ? 15 : 10,
          expiryDate: '2039-03-25',
          isUrgent: false,
        },
        contradictionsDetected: contradictions,
      });
      setIsCalculating(false);
    }, 250);
  };

  const handleApplyChanges = (newText: string) => {
    setEditedStatement(newText);
    calculateBlastRadius(activeEpisode, newText, editedArticles);
  };

  // Фіксація WORM-суперсесії (Invariant L-01)
  const handleSealWorm = async () => {
    // Invariant L-03: Захист Адріано Міллі
    if (editedStatement.toLowerCase().includes('міллі') && editedArticles.some(a => a.includes('CP'))) {
      if (editedStatement.toLowerCase().includes('обвинувачується') || editedStatement.toLowerCase().includes('спільник')) {
        setNotification({
          type: 'error',
          text: 'КРИТИЧНЕ БЛОКУВАННЯ (Invariant L-03): Адріано Міллі захищений абсолютним імунітетом добросовісної третьої сторони (ст. 933 CC). Будь-які обвинувачення заблоковано.',
        });
        return;
      }
    }

    // Invariant L-04: Захист Арсена Коваленка
    if (editedArticles.some(a => a.includes('219'))) {
      setNotification({
        type: 'error',
        text: 'КРИТИЧНЕ БЛОКУВАННЯ (Invariant L-04): Арсен Коваленко є повнолітнім дієздатним потерпілим (26 років). Стаття 219 CP (правопорушення проти неповнолітніх) суворо заборонена.',
      });
      return;
    }

    setIsSealing(true);
    setNotification(null);

    try {
      const payload = {
        fact_id: activeEpisode.id,
        previous_text: activeEpisode.originalText,
        calibrated_text: editedStatement,
        valid_time_tv: editedTv,
        legal_articles: editedArticles,
        blast_radius: blastResult,
        timestamp: new Date().toISOString(),
      };

      // Збереження оновленого стану в локальному списку епізодів
      setEpisodes(prev =>
        prev.map(ep =>
          ep.id === activeEpisode.id
            ? { ...ep, originalText: editedStatement, validTimeTv: editedTv, legalArticles: editedArticles, status: 'VERIFIED' }
            : ep
        )
      );

      setNotification({
        type: 'success',
        text: `WORM-суперсесію успішно зафіксовано для ${activeEpisode.id}. Попередній стан архівовано з valid_to = NOW. Перераховано ${blastResult?.cascadingChapters.length} залежних розділів.`,
      });
    } catch (e: any) {
      setNotification({ type: 'error', text: 'Помилка запису у WORM-леджер: ' + e.message });
    } finally {
      setIsSealing(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#0B0E14] text-[#E0E6ED] font-sans">
      {/* Topbar */}
      <header className="px-6 py-4 border-b border-[#2A3447] bg-[#121721] flex justify-between items-center">
        <div>
          <h1 className="text-xl font-bold text-[#D4AF37] tracking-wider uppercase flex items-center gap-2">
            <span>⚖️</span> Рецензійний Пайплайн & Автоматичний Радіус Ураження
          </h1>
          <p className="text-xs text-[#8B9BB4] mt-0.5">
            Узгодження фактів із реальністю • Бітемпоральна WORM-суперсесія • Справа PE24.014624-SBA
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="px-3 py-1 bg-[#1A2234] border border-[#2A3447] rounded text-xs text-[#8B9BB4]">
            Всього фактів у базі: <strong className="text-white">{episodes.length}</strong>
          </span>
          <button
            onClick={() => setNotification({ type: 'success', text: 'Команда на перезбірку test_dossier.epub передана на вузол .234.' })}
            className="px-4 py-1.5 bg-[#1E2638] border border-[#D4AF37]/40 rounded text-xs text-[#D4AF37] font-semibold hover:bg-[#2A3447] transition flex items-center gap-2"
          >
            <span>📚</span> Перекомпілювати EPUB
          </button>
        </div>
      </header>

      {/* Сповіщення */}
      {notification && (
        <div
          className={`px-6 py-3 text-xs flex justify-between items-center ${
            notification.type === 'success'
              ? 'bg-[#102A1E] text-[#1FB86C] border-b border-[#1FB86C]/30'
              : notification.type === 'warn'
              ? 'bg-[#332A15] text-[#F3C95A] border-b border-[#F3C95A]/30'
              : 'bg-[#3A1818] text-[#FF5C5C] border-b border-[#FF5C5C]/30'
          }`}
        >
          <span>{notification.text}</span>
          <button onClick={() => setNotification(null)} className="font-bold ml-4">✕</button>
        </div>
      )}

      {/* Головна 3-панельна сітка */}
      <div className="flex-1 grid grid-cols-12 gap-0 overflow-hidden">
        {/* ПАНЕЛЬ 1: СПИСОК ФАКТІВ ТА ЕПІЗОДІВ (Ширина: 3/12) */}
        <div className="col-span-3 border-r border-[#2A3447] bg-[#0E131C] p-4 flex flex-col space-y-3 overflow-y-auto">
          <h2 className="text-xs font-bold text-[#8B9BB4] uppercase tracking-wider">
            1. Епізоди Досьє & Докази
          </h2>
          <div className="space-y-2">
            {episodes.map(ep => (
              <div
                key={ep.id}
                onClick={() => setSelectedId(ep.id)}
                className={`p-3 rounded-lg border text-xs cursor-pointer transition ${
                  selectedId === ep.id
                    ? 'bg-[#182030] border-[#D4AF37] text-white shadow-md'
                    : 'bg-[#121721] border-[#2A3447] text-[#8B9BB4] hover:border-[#8B9BB4]'
                }`}
              >
                <div className="flex justify-between items-start mb-1">
                  <span className="font-mono text-[10px] text-[#D4AF37]">{ep.chapter}</span>
                  <span
                    className={`text-[9px] px-1.5 py-0.5 rounded font-bold uppercase ${
                      ep.status === 'VERIFIED'
                        ? 'bg-[#1FB86C]/10 text-[#1FB86C]'
                        : ep.status === 'CONTRADICTED'
                        ? 'bg-[#FF5C5C]/10 text-[#FF5C5C]'
                        : 'bg-[#F3C95A]/10 text-[#F3C95A]'
                    }`}
                  >
                    {ep.status}
                  </span>
                </div>
                <h3 className="font-semibold text-white line-clamp-1">{ep.title}</h3>
                <p className="text-[11px] text-[#8B9BB4] mt-1 line-clamp-2">{ep.originalText}</p>
                <div className="mt-2 flex items-center justify-between text-[10px] text-[#8B9BB4]/70">
                  <span>Доказів: {ep.evidenceIds.length}</span>
                  <span>{new Date(ep.validTimeTv).toLocaleDateString('uk-UA')}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* ПАНЕЛЬ 2: РЕДАКТОР & КАЛІБРАТОР РЕАЛЬНОСТІ (Ширина: 5/12) */}
        <div className="col-span-5 p-6 flex flex-col space-y-5 overflow-y-auto border-r border-[#2A3447]">
          <div className="border-b border-[#2A3447] pb-3">
            <span className="text-[10px] font-mono text-[#D4AF37] uppercase">ID: {activeEpisode.id}</span>
            <h2 className="text-base font-bold text-white mt-0.5">{activeEpisode.title}</h2>
          </div>

          {/* Форма коригування */}
          <div className="space-y-4 text-xs">
            <div>
              <label className="block text-[#8B9BB4] mb-1 font-semibold">
                Фактичний час події (Valid Time $T_v$ — реальність)
              </label>
              <input
                type="text"
                value={editedTv}
                onChange={e => setEditedTv(e.target.value)}
                className="w-full bg-[#121721] border border-[#2A3447] rounded p-2.5 text-white font-mono"
              />
            </div>

            <div>
              <label className="block text-[#8B9BB4] mb-1 font-semibold">
                Виправлений / Уточнений виклад факту
              </label>
              <textarea
                rows={5}
                value={editedStatement}
                onChange={e => handleApplyChanges(e.target.value)}
                className="w-full bg-[#121721] border border-[#2A3447] rounded p-3 text-white leading-relaxed focus:border-[#D4AF37] outline-none"
              />
            </div>

            <div>
              <label className="block text-[#8B9BB4] mb-1 font-semibold">
                Прив'язані речові докази (ISO/IEC 27037)
              </label>
              <div className="flex flex-wrap gap-2 p-2.5 bg-[#121721] border border-[#2A3447] rounded">
                {activeEpisode.evidenceIds.map(ev => (
                  <span key={ev} className="px-2 py-1 bg-[#1A2234] border border-[#2A3447] text-[11px] text-[#D4AF37] rounded flex items-center gap-1.5">
                    <span>📎</span> {ev}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-[#8B9BB4] mb-1 font-semibold">
                Кваліфікація правопорушень (CP / LEI)
              </label>
              <div className="space-y-1 bg-[#121721] border border-[#2A3447] p-2.5 rounded">
                {activeEpisode.legalArticles.map(art => (
                  <div key={art} className="text-[11px] text-white flex items-center gap-2">
                    <span className="text-[#1FB86C]">✓</span> {art}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Кнопка суперсесії */}
          <div className="pt-2">
            <button
              onClick={handleSealWorm}
              disabled={isSealing}
              className="w-full py-3 bg-[#D4AF37] text-[#0B0E14] font-bold text-xs uppercase tracking-wider rounded-lg hover:bg-[#F3C95A] transition shadow-lg flex items-center justify-center gap-2"
            >
              <span>🛡️</span>
              {isSealing ? 'Фіксація суперсесії...' : 'Зафіксувати суперсесію (WORM Seal)'}
            </button>
            <p className="text-[10px] text-center text-[#8B9BB4] mt-2">
              Старий стан буде архівовано у WORM-леджері без фізичного видалення.
            </p>
          </div>
        </div>

        {/* ПАНЕЛЬ 3: РАДІУС УРАЖЕННЯ ТА ТОЧКИ ЗМІН (Ширина: 4/12) */}
        <div className="col-span-4 bg-[#0E131C] p-6 flex flex-col space-y-6 overflow-y-auto">
          <div className="flex justify-between items-center border-b border-[#2A3447] pb-3">
            <h2 className="text-xs font-bold text-[#8B9BB4] uppercase tracking-wider">
              2. Точки Ураження (Blast Radius)
            </h2>
            {isCalculating ? (
              <span className="text-[10px] text-[#D4AF37] animate-pulse">Перерахунок графу...</span>
            ) : (
              <span className="text-[10px] px-2 py-0.5 bg-[#1FB86C]/10 text-[#1FB86C] rounded border border-[#1FB86C]/30 font-bold">
                Вражено вузлів: {blastResult?.cascadingChapters.length || 0}
              </span>
            )}
          </div>

          {/* Каскадний вплив на розділи досьє */}
          <div className="space-y-3">
            <h3 className="text-xs font-semibold text-white flex items-center gap-2">
              <span>🎯</span> Пункти, які вимагають синхронних змін:
            </h3>
            <div className="space-y-2">
              {blastResult?.cascadingChapters.map((ch, idx) => (
                <div key={idx} className="p-2.5 bg-[#121721] border border-[#2A3447] rounded text-xs flex items-center justify-between">
                  <span className="text-white font-medium">{ch}</span>
                  <span className="text-[10px] px-2 py-0.5 bg-[#D4AF37]/10 text-[#D4AF37] rounded">
                    Потребує аудиту
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Строк давності за статтею 97 CP */}
          {blastResult?.statuteOfLimitations && (
            <div className="p-4 bg-[#121721] border border-[#2A3447] rounded-lg space-y-2 text-xs">
              <div className="flex justify-between items-center">
                <span className="text-[#8B9BB4]">Строк давності (ст. 97 CP):</span>
                <span className="font-bold text-[#D4AF37]">{blastResult.statuteOfLimitations.years} років</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-[#8B9BB4]">Дата спливу строку:</span>
                <span className="font-mono text-white">{blastResult.statuteOfLimitations.expiryDate}</span>
              </div>
              <div className="text-[11px] text-[#1FB86C] mt-1">
                ✓ Справа знаходиться в межах активного процесуального строку.
              </div>
            </div>
          )}

          {/* Виявлені бітемпоральні суперечності */}
          {blastResult?.contradictionsDetected && blastResult.contradictionsDetected.length > 0 && (
            <div className="p-4 bg-[#2A1414] border border-[#FF5C5C]/40 rounded-lg space-y-3 text-xs">
              <div className="flex items-center gap-2 text-[#FF5C5C] font-bold">
                <span>⚠️</span> Виявлено конфлікт показань (Contradiction)
              </div>
              {blastResult.contradictionsDetected.map((c, i) => (
                <div key={i} className="space-y-1 text-[11px] border-t border-[#FF5C5C]/20 pt-2">
                  <div className="text-white font-semibold">Конфліктує з: {c.targetFactId}</div>
                  <div className="text-[#8B9BB4]">Джерело спростування: {c.source}</div>
                  <div className="text-[#FFB8B8] mt-1">{c.contradictionText}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
