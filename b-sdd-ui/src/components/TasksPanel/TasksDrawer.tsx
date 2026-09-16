// src/components/TasksPanel/TasksDrawer.tsx
import React, { useState } from 'react';
import type { SpecItem, ProjectInfo } from '@/types/specs';
import {
  X,
  CheckSquare,
  Square,
  ListTodo,
  Layers,
  FileCode,
  GitBranch,
  CheckCircle2,
  FolderGit2,
  TrendingUp,
  FileText,
} from 'lucide-react';

interface TasksDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  specs: SpecItem[];
  projectInfo: ProjectInfo | null;
  onToggleTask: (specId: string, taskId: string, completed: boolean) => Promise<void>;
  selectedSpecId: string;
  onSelectSpec: (specId: string) => void;
}

export const TasksDrawer: React.FC<TasksDrawerProps> = ({
  isOpen,
  onClose,
  specs,
  projectInfo,
  onToggleTask,
  selectedSpecId,
  onSelectSpec,
}) => {
  const [activeTab, setActiveTab] = useState<'tasks' | 'spec' | 'plan'>('tasks');
  const [isToggling, setIsToggling] = useState<string | null>(null);

  if (!isOpen) return null;

  const currentSpec = specs.find((s) => s.id === selectedSpecId) || specs[0] || null;

  const handleCheckboxClick = async (taskId: string, currentStatus: boolean) => {
    if (!currentSpec) return;
    setIsToggling(taskId);
    try {
      await onToggleTask(currentSpec.id, taskId, !currentStatus);
    } finally {
      setIsToggling(null);
    }
  };

  const totalAllTasks = specs.reduce((sum, s) => sum + s.tasks_count, 0);
  const completedAllTasks = specs.reduce((sum, s) => sum + s.completed_count, 0);
  const overallPercent = totalAllTasks > 0 ? Math.round((completedAllTasks / totalAllTasks) * 100) : 0;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/70 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="w-full max-w-2xl bg-panel border-l border-border-subtle h-full flex flex-col text-slate-100 shadow-2xl">
        {/* Header */}
        <div className="px-6 py-4 bg-card border-b border-border-subtle flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2.5">
            <ListTodo className="w-5 h-5 text-amber" />
            <div>
              <h2 className="text-sm font-bold text-slate-100 font-mono">
                Етапи розробки та Задачі (Specs & Tasks)
              </h2>
              {projectInfo && (
                <div className="flex items-center gap-3 text-[11px] text-slate-400 font-mono mt-0.5">
                  <span className="flex items-center gap-1 text-slate-300">
                    <FolderGit2 className="w-3 h-3 text-cyan-400" />
                    {projectInfo.name}
                  </span>
                  <span className="flex items-center gap-1">
                    <GitBranch className="w-3 h-3 text-emerald-400" />
                    {projectInfo.branch}
                  </span>
                  <span className="text-slate-500">commit: {projectInfo.commit}</span>
                </div>
              )}
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1 rounded text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Global Progress Bar */}
        <div className="px-6 py-3 bg-canvas/60 border-b border-border-subtle flex items-center justify-between text-xs">
          <div className="flex items-center gap-2 font-mono">
            <TrendingUp className="w-4 h-4 text-emerald-400" />
            <span className="text-slate-300 font-semibold">Загальний прогрес специфікацій:</span>
            <span className="text-emerald-400 font-bold">{completedAllTasks} / {totalAllTasks} задач ({overallPercent}%)</span>
          </div>

          <div className="w-36 h-2 bg-slate-800 rounded-full overflow-hidden border border-border-subtle">
            <div
              className="h-full bg-emerald-500 transition-all duration-300"
              style={{ width: `${overallPercent}%` }}
            />
          </div>
        </div>

        {/* Spec Tabs */}
        <div className="px-6 py-2 bg-card/70 border-b border-border-subtle flex items-center gap-1.5 overflow-x-auto text-xs">
          {specs.map((spec) => {
            const isSelected = spec.id === currentSpec?.id;
            return (
              <button
                key={spec.id}
                onClick={() => onSelectSpec(spec.id)}
                className={`px-3 py-1.5 rounded-lg border font-mono text-[11px] shrink-0 flex items-center gap-1.5 transition-all ${
                  isSelected
                    ? 'bg-amber/15 text-amber border-amber/40 shadow-sm'
                    : 'bg-panel text-slate-400 border-border-subtle hover:text-slate-200'
                }`}
              >
                <span>{spec.id.split('-')[0]}</span>
                <span className="truncate max-w-[120px] font-sans">{spec.title}</span>
                <span className="px-1 py-0.2 rounded bg-black/40 text-[10px] text-slate-400">
                  {spec.completed_count}/{spec.tasks_count}
                </span>
              </button>
            );
          })}
        </div>

        {/* Subtabs for current spec (Tasks / Spec doc / Plan) */}
        {currentSpec && (
          <div className="px-6 py-2 bg-panel border-b border-border-subtle flex items-center justify-between text-xs">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setActiveTab('tasks')}
                className={`px-3 py-1 rounded text-xs font-mono transition-colors flex items-center gap-1.5 ${
                  activeTab === 'tasks'
                    ? 'bg-card text-amber border border-border-subtle'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <CheckSquare className="w-3.5 h-3.5" />
                <span>Задачі ({currentSpec.tasks.length})</span>
              </button>

              <button
                onClick={() => setActiveTab('spec')}
                className={`px-3 py-1 rounded text-xs font-mono transition-colors flex items-center gap-1.5 ${
                  activeTab === 'spec'
                    ? 'bg-card text-amber border border-border-subtle'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <FileText className="w-3.5 h-3.5" />
                <span>Опис (spec.md)</span>
              </button>

              <button
                onClick={() => setActiveTab('plan')}
                className={`px-3 py-1 rounded text-xs font-mono transition-colors flex items-center gap-1.5 ${
                  activeTab === 'plan'
                    ? 'bg-card text-amber border border-border-subtle'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Layers className="w-3.5 h-3.5" />
                <span>План (plan.md)</span>
              </button>
            </div>

            <div className="text-[11px] font-mono text-slate-400">
              Специфікація: <span className="text-slate-200 font-semibold">{currentSpec.percent}%</span>
            </div>
          </div>
        )}

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-3">
          {currentSpec && activeTab === 'tasks' && (
            <div className="space-y-2">
              <div className="text-xs text-slate-400 font-mono flex items-center justify-between pb-1 border-b border-border-subtle">
                <span>Перелік задач у <code>{currentSpec.path}/tasks.md</code></span>
                <span>Натисніть на чекбокс для перемикання</span>
              </div>

              {currentSpec.tasks.map((task) => {
                const toggling = isToggling === task.id;
                return (
                  <div
                    key={task.id}
                    onClick={() => handleCheckboxClick(task.id, task.completed)}
                    className={`p-3 rounded-lg border flex items-start gap-3 cursor-pointer select-none transition-all ${
                      task.completed
                        ? 'bg-card/40 border-border-subtle hover:border-emerald-500/30 text-slate-300'
                        : 'bg-card border-border-subtle hover:border-amber/50 text-slate-100 shadow-sm'
                    }`}
                  >
                    <button
                      className="mt-0.5 text-slate-400 hover:text-amber transition-colors shrink-0"
                      disabled={toggling}
                    >
                      {task.completed ? (
                        <CheckSquare className="w-4 h-4 text-emerald-400" />
                      ) : (
                        <Square className="w-4 h-4 text-slate-500 hover:text-amber" />
                      )}
                    </button>

                    <div className="space-y-1 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-amber px-1.5 py-0.2 rounded bg-amber/10 border border-amber/30">
                          {task.id}
                        </span>
                        {task.completed && (
                          <span className="text-[10px] font-mono text-emerald-400 flex items-center gap-1">
                            <CheckCircle2 className="w-3 h-3" />
                            виконано
                          </span>
                        )}
                      </div>
                      <p
                        className={`text-xs leading-relaxed font-sans ${
                          task.completed ? 'line-through text-slate-500' : 'text-slate-200 font-medium'
                        }`}
                      >
                        {task.title}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {currentSpec && activeTab === 'spec' && (
            <div className="p-4 bg-canvas rounded-lg border border-border-subtle text-xs font-mono whitespace-pre-wrap leading-relaxed text-slate-200">
              {currentSpec.spec_markdown || 'Опис специфікації відсутній.'}
            </div>
          )}

          {currentSpec && activeTab === 'plan' && (
            <div className="p-4 bg-canvas rounded-lg border border-border-subtle text-xs font-mono whitespace-pre-wrap leading-relaxed text-slate-200">
              {currentSpec.plan_markdown || 'Архітектурний план відсутній.'}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-card border-t border-border-subtle flex items-center justify-between text-xs">
          <span className="text-slate-400 font-mono text-[11px]">
            Зміни зберігаються напряму в <code>specs/**/tasks.md</code>
          </span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium transition-colors"
          >
            Закрити
          </button>
        </div>
      </div>
    </div>
  );
};
