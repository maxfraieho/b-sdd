// src/components/DrakonStudio/DrakonIconPalette.tsx
// -----------------------------------------------------------------------------
// ZONE B — Сегментована палітра ДРАКОН (Astryx Toolbox).
// Замість одного довгого горизонтального ряду з ~20 іконок — 4 вкладки:
//   • Потік       (b0/header, action, end, insertion)
//   • Розгалуження (question, select, case)
//   • Цикли       (loop_start, loop_end, for-begin, for-end)
//   • Система     (timer, pause, duration, process, shelf/comment, address)
// Активна вкладка — amber; для системних — cyan-акцент.
// -----------------------------------------------------------------------------
import React from 'react';
import { GitBranch, Repeat, Workflow, Settings2 } from 'lucide-react';
import iconAction from '@/assets/drakon/action.png';
import iconQuestion from '@/assets/drakon/question.png';
import iconSelect from '@/assets/drakon/select.png';
import iconCase from '@/assets/drakon/case.png';
import iconBranch from '@/assets/drakon/branch.png';
import iconEnd from '@/assets/drakon/end.png';
import iconShelf from '@/assets/drakon/shelf.png';
import iconProcess from '@/assets/drakon/process.png';
import iconTimer from '@/assets/drakon/timer.png';
import iconPause from '@/assets/drakon/pause.png';
import iconDuration from '@/assets/drakon/duration.png';
import iconForeach from '@/assets/drakon/foreach.png';
import iconInsertion from '@/assets/drakon/insertion.png';
import iconComment from '@/assets/drakon/comment.png';
import iconGroupDuration from '@/assets/drakon/group-duration.png';
import iconGroupDurationR from '@/assets/drakon/group-duration-r.png';
import iconSilhouette from '@/assets/drakon/silhouette.png';

export type DrakonTabId = 'flow' | 'branch' | 'loop' | 'system';

export interface DrakonIconDef {
  id: string;
  name: string;
  tab: DrakonTabId;
  iconUrl: string;
  tooltip: string;
}

export const DRAKON_ICONS: DrakonIconDef[] = [
  // ── Потік ────────────────────────────────────────────────────────────────
  { id: 'b0',        name: 'Заголовок (b0)',   tab: 'flow',   iconUrl: iconBranch,    tooltip: 'b0 / header — початок гілки шампура' },
  { id: 'action',    name: 'Дія',              tab: 'flow',   iconUrl: iconAction,    tooltip: 'Імперативна дія на осі шампура' },
  { id: 'end',       name: 'Кінець',           tab: 'flow',   iconUrl: iconEnd,       tooltip: 'Точка завершення алгоритму' },
  { id: 'insertion', name: 'Вставка',          tab: 'flow',   iconUrl: iconInsertion, tooltip: 'Виклик підпрограми або іншої ДРАКОН-схеми' },

  // ── Розгалуження ─────────────────────────────────────────────────────────
  { id: 'question',  name: 'Умова',            tab: 'branch', iconUrl: iconQuestion,  tooltip: 'Логічне розгалуження (Так — вниз, Ні — вправо)' },
  { id: 'select',    name: 'Вибір',            tab: 'branch', iconUrl: iconSelect,    tooltip: 'Заголовок множинного вибору (switch)' },
  { id: 'case',      name: 'Варіант',          tab: 'branch', iconUrl: iconCase,      tooltip: 'Гілка варіанту для блоку Select' },

  // ── Цикли ────────────────────────────────────────────────────────────────
  { id: 'loop_start', name: 'Loop Start',      tab: 'loop',   iconUrl: iconGroupDuration,  tooltip: 'Початок циклу (loop_start)' },
  { id: 'loop_end',   name: 'Loop End',        tab: 'loop',   iconUrl: iconGroupDurationR, tooltip: 'Кінець циклу (loop_end)' },
  { id: 'for_begin',  name: 'For Begin',       tab: 'loop',   iconUrl: iconForeach,    tooltip: 'Початок циклу з лічильником (for-begin)' },
  { id: 'for_end',    name: 'For End',         tab: 'loop',   iconUrl: iconForeach,    tooltip: 'Кінець циклу з лічильником (for-end)' },

  // ── Система ──────────────────────────────────────────────────────────────
  { id: 'timer',    name: 'Таймер',            tab: 'system', iconUrl: iconTimer,    tooltip: 'Ініціалізація або скидання таймера' },
  { id: 'pause',    name: 'Пауза',             tab: 'system', iconUrl: iconPause,    tooltip: 'Очікування події або таймера' },
  { id: 'duration', name: 'Тривалість',        tab: 'system', iconUrl: iconDuration, tooltip: 'Обмеження або затримка часу виконання' },
  { id: 'process',  name: 'Процес',            tab: 'system', iconUrl: iconProcess,  tooltip: 'Асинхронний запуск фонового процесу' },
  { id: 'shelf',    name: 'Полиця / Comment',  tab: 'system', iconUrl: iconShelf,    tooltip: 'Двокамерний блок / коментар' },
  { id: 'comment',  name: 'Коментар',          tab: 'system', iconUrl: iconComment,  tooltip: 'Пояснювальний текстовий коментар' },
  { id: 'address',  name: 'Address',           tab: 'system', iconUrl: iconSilhouette, tooltip: 'Маршрут / силует (address)' },
];

const TABS: { id: DrakonTabId; label: string; Icon: React.ComponentType<{ className?: string }> }[] = [
  { id: 'flow',   label: 'Потік',        Icon: Workflow },
  { id: 'branch', label: 'Розгалуження', Icon: GitBranch },
  { id: 'loop',   label: 'Цикли',        Icon: Repeat },
  { id: 'system', label: 'Система',      Icon: Settings2 },
];

interface DrakonIconPaletteProps {
  onInsertIcon: (type: string) => void;
  activeSocketType?: string | null;
}

export const DrakonIconPalette: React.FC<DrakonIconPaletteProps> = ({
  onInsertIcon,
  activeSocketType,
}) => {
  const [activeTab, setActiveTab] = React.useState<DrakonTabId>('flow');
  const shownIcons = DRAKON_ICONS.filter((i) => i.tab === activeTab);

  return (
    <div className="bg-[#0d121c] border-b border-[#1e293b] shrink-0 select-none">
      {/* Tab row */}
      <div className="h-8 px-2 flex items-center gap-1 border-b border-[#1e293b]">
        <span className="text-[10px] font-mono uppercase tracking-widest text-[#f59e0b]/80 font-bold mr-2">
          DRAKON Toolbox
        </span>
        <div className="inline-flex bg-[#090d13] border border-[#1e293b] rounded p-0.5">
          {TABS.map(({ id, label, Icon }) => {
            const isActive = activeTab === id;
            const accent = id === 'system' ? '#06b6d4' : '#f59e0b';
            return (
              <button
                key={id}
                onClick={() => setActiveTab(id)}
                className={`inline-flex items-center gap-1.5 px-2.5 h-6 rounded text-[11px] font-mono transition-all ${
                  isActive
                    ? 'bg-[#141b27] text-slate-100 font-bold shadow-inner'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
                style={
                  isActive
                    ? { boxShadow: `inset 0 -2px 0 ${accent}`, color: accent }
                    : undefined
                }
                aria-selected={isActive}
                role="tab"
              >
                <Icon className="w-3 h-3" />
                {label}
              </button>
            );
          })}
        </div>

        <span className="ml-auto text-[10px] font-mono text-slate-500">
          {shownIcons.length} фігур · [{activeTab}]
        </span>
      </div>

      {/* Icon rail */}
      <div className="h-10 px-2 flex items-center gap-1 overflow-x-auto">
        {shownIcons.map((icon) => {
          const isActive = activeSocketType === icon.id;
          return (
            <button
              key={icon.id}
              onClick={() => onInsertIcon(icon.id)}
              title={`${icon.name}: ${icon.tooltip}`}
              className={`shrink-0 inline-flex items-center gap-1.5 px-2 h-7 rounded border text-[11px] font-mono transition-all ${
                isActive
                  ? 'bg-[#f59e0b] text-slate-950 border-[#f59e0b] font-bold shadow-sm'
                  : 'bg-[#141b27] hover:bg-[#1a2233] text-slate-200 border-[#1e293b] hover:border-slate-600'
              }`}
            >
              <img src={icon.iconUrl} alt={icon.id} className="w-4 h-4 object-contain" />
              <span>{icon.name}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default DrakonIconPalette;
