// src/components/DrakonStudio/DrakonIconPalette.tsx
import React from 'react';
import iconAction from '@/assets/drakon/action.png';
import iconQuestion from '@/assets/drakon/question.png';
import iconSelect from '@/assets/drakon/select.png';
import iconCase from '@/assets/drakon/case.png';
import iconBranch from '@/assets/drakon/branch.png';
import iconEnd from '@/assets/drakon/end.png';
import iconShelf from '@/assets/drakon/shelf.png';
import iconInput from '@/assets/drakon/input.png';
import iconOutput from '@/assets/drakon/output.png';
import iconProcess from '@/assets/drakon/process.png';
import iconTimer from '@/assets/drakon/timer.png';
import iconPause from '@/assets/drakon/pause.png';
import iconDuration from '@/assets/drakon/duration.png';
import iconForeach from '@/assets/drakon/foreach.png';
import iconPar from '@/assets/drakon/par.png';
import iconInsertion from '@/assets/drakon/insertion.png';
import iconComment from '@/assets/drakon/comment.png';

export interface DrakonIconDef {
  id: string;
  name: string;
  category: 'core' | 'io' | 'control' | 'meta';
  iconUrl: string;
  tooltip: string;
}

export const DRAKON_ICONS: DrakonIconDef[] = [
  // Core
  { id: 'action', name: 'Дія (Action)', category: 'core', iconUrl: iconAction, tooltip: 'Імперативна дія або присвоєння на осі шампура' },
  { id: 'question', name: 'Умова (Question)', category: 'core', iconUrl: iconQuestion, tooltip: 'Логічне розгалуження (Так - униз, Ні - вправо)' },
  { id: 'select', name: 'Вибір (Select)', category: 'core', iconUrl: iconSelect, tooltip: 'Заголовок множинного вибору (switch)' },
  { id: 'case', name: 'Варіант (Case)', category: 'core', iconUrl: iconCase, tooltip: 'Гілка варіанту для блоку Select' },
  { id: 'branch', name: 'Гілка (Branch)', category: 'core', iconUrl: iconBranch, tooltip: 'Заголовок нової вертикальної гілки алгоритму' },
  { id: 'end', name: 'Кінець (End)', category: 'core', iconUrl: iconEnd, tooltip: 'Точка завершення алгоритму' },

  // I/O & Storage
  { id: 'input', name: 'Ввід (Input)', category: 'io', iconUrl: iconInput, tooltip: 'Прийом вхідних даних або повідомлень' },
  { id: 'output', name: 'Вивід (Output)', category: 'io', iconUrl: iconOutput, tooltip: 'Відправка вихідних даних або подій' },
  { id: 'shelf', name: 'Полиця (Shelf)', category: 'io', iconUrl: iconShelf, tooltip: 'Двокамерний блок для збереження стану та наказів' },

  // Control & Real-time
  { id: 'process', name: 'Процес (Process)', category: 'control', iconUrl: iconProcess, tooltip: 'Асинхронний запуск фонового процесу' },
  { id: 'timer', name: 'Таймер (Timer)', category: 'control', iconUrl: iconTimer, tooltip: 'Ініціалізація або скидання таймера' },
  { id: 'pause', name: 'Пауза (Pause)', category: 'control', iconUrl: iconPause, tooltip: 'Очікування події або таймера' },
  { id: 'duration', name: 'Тривалість (Duration)', category: 'control', iconUrl: iconDuration, tooltip: 'Обмеження або затримка часу виконання' },
  { id: 'foreach', name: 'Цикл (Foreach)', category: 'control', iconUrl: iconForeach, tooltip: 'Ітерація по колекції або масиву' },
  { id: 'par', name: 'Паралелізм (Par)', category: 'control', iconUrl: iconPar, tooltip: 'Паралельне виконання гілок' },

  // Meta & Docs
  { id: 'insertion', name: 'Вставка (Insertion)', category: 'meta', iconUrl: iconInsertion, tooltip: 'Виклик підпрограми або іншої ДРАКОН-схеми' },
  { id: 'comment', name: 'Коментар (Comment)', category: 'meta', iconUrl: iconComment, tooltip: 'Пояснювальний текстовий коментар' },
];

interface DrakonIconPaletteProps {
  onInsertIcon: (type: string) => void;
  activeSocketType?: string | null;
}

export const DrakonIconPalette: React.FC<DrakonIconPaletteProps> = ({
  onInsertIcon,
  activeSocketType,
}) => {
  return (
    <div className="h-10 bg-panel border-b border-border-subtle px-3 flex items-center gap-1 shrink-0 overflow-x-auto select-none">
      <span className="text-[10px] font-mono uppercase text-amber font-bold tracking-wider mr-1.5 shrink-0">
        Ікони:
      </span>

      <div className="flex items-center gap-1 min-w-max">
        {DRAKON_ICONS.map((icon) => {
          const isActive = activeSocketType === icon.id;
          return (
            <button
              key={icon.id}
              onClick={() => onInsertIcon(icon.id)}
              title={`${icon.name}: ${icon.tooltip}`}
              className={`flex items-center gap-1.5 px-2 py-1 rounded text-xs font-mono transition-all border shrink-0 ${
                isActive
                  ? 'bg-amber text-slate-950 border-amber font-bold shadow-md'
                  : 'bg-card hover:bg-slate-800 text-slate-300 border-border-subtle hover:border-slate-600'
              }`}
            >
              <img src={icon.iconUrl} alt={icon.id} className="w-3.5 h-3.5 object-contain" />
              <span className="text-[11px] capitalize">{icon.id}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default DrakonIconPalette;
