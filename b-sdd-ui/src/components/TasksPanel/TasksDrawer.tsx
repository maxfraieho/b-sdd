// src/components/TasksPanel/TasksDrawer.tsx
// Astryx-native Specs & Tasks Drawer (ADR-009, ADR-010)
import React, { useState } from 'react';
import type { SpecItem, ProjectInfo } from '@/types/specs';
import { Drawer, Button, Badge, Segmented } from '@/components/astryx/primitives';
import {
  CheckSquare,
  Square,
  ListTodo,
  Layers,
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
  const [activeTab, setActiveTab] = useState<string>('tasks');
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
    <Drawer
      isOpen={isOpen}
      onClose={onClose}
      width="w-full sm:w-[600px] md:w-[680px]"
      title={
        <div className="flex items-center gap-2.5">
          <ListTodo className="w-5 h-5 text-amber shrink-0" />
          <div>
            <div className="text-sm font-bold text-slate-100 font-mono">
              Етапи розробки та Задачі (Specs & Tasks)
            </div>
            {projectInfo && (
              <div className="flex items-center gap-3 text-[11px] text-slate-400 font-mono mt-0.5 font-normal">
                <span className="flex items-center gap-1 text-slate-300">
                  <FolderGit2 className="w-3 h-3 text-cyan" />
                  {projectInfo.name}
                </span>
                <span className="flex items-center gap-1">
                  <GitBranch className="w-3 h-3 text-emerald" />
                  {projectInfo.branch}
                </span>
                <span className="text-slate-500">commit: {projectInfo.commit}</span>
              </div>
            )}
          </div>
        </div>
      }
    >
      <div className="-m-4 flex flex-col h-full font-mono text-xs">
        {/* Global Progress Bar */}
        <div className="px-6 py-3 bg-[#090d13] border-b border-[#1e293b] flex items-center justify-between text-xs">
          <div className="flex items-center gap-2 font-mono">
            <TrendingUp className="w-4 h-4 text-emerald" />
            <span className="text-slate-300 font-semibold">Загальний прогрес специфікацій:</span>
            <span className="text-emerald font-bold">{completedAllTasks} / {totalAllTasks} задач ({overallPercent}%)</span>
          </div>

          <div className="w-36 h-2 bg-[#0d121c] rounded-full overflow-hidden border border-[#1e293b]">
            <div
              className="h-full bg-emerald transition-all duration-300"
              style={{ width: `${overallPercent}%` }}
            />
          </div>
        </div>

        {/* Spec Tabs */}
        <div className="px-6 py-2 bg-[#0d121c] border-b border-[#1e293b] flex items-center gap-1.5 overflow-x-auto text-xs">
          {specs.map((spec) => {
            const isSelected = spec.id === currentSpec?.id;
            return (
              <button
                key={spec.id}
                onClick={() => onSelectSpec(spec.id)}
                className={`px-3 py-1.5 rounded border font-mono text-[11px] shrink-0 flex items-center gap-1.5 transition-all cursor-pointer ${
                  isSelected
                    ? 'bg-[#1a2233] text-amber border-amber/40 shadow-xs'
                    : 'bg-[#141b27] text-slate-400 border-[#1e293b] hover:text-slate-200 hover:border-slate-600'
                }`}
              >
                <span className="font-bold">{spec.id.split('-')[0]}</span>
                <span className="truncate max-w-[120px] font-sans">{spec.title}</span>
                <Badge tone={isSelected ? 'amber' : 'neutral'} className="text-[10px]">
                  {spec.completed_count}/{spec.tasks_count}
                </Badge>
              </button>
            );
          })}
        </div>

        {/* Subtabs for current spec (Tasks / Spec doc / Plan) */}
        {currentSpec && (
          <div className="px-6 py-2 bg-[#141b27] border-b border-[#1e293b] flex items-center justify-between text-xs">
            <Segmented
              value={activeTab}
              onChange={(val) => setActiveTab(val)}
              options={[
                {
                  value: 'tasks',
                  label: (
                    <span className="flex items-center gap-1.5">
                      <CheckSquare className="w-3.5 h-3.5" />
                      <span>Задачі ({currentSpec.tasks.length})</span>
                    </span>
                  ),
                },
                {
                  value: 'spec',
                  label: (
                    <span className="flex items-center gap-1.5">
                      <FileText className="w-3.5 h-3.5" />
                      <span>Опис (spec.md)</span>
                    </span>
                  ),
                },
                {
                  value: 'plan',
                  label: (
                    <span className="flex items-center gap-1.5">
                      <Layers className="w-3.5 h-3.5" />
                      <span>План (plan.md)</span>
                    </span>
                  ),
                },
              ]}
            />

            <div className="text-[11px] font-mono text-slate-400">
              Специфікація: <span className="text-amber font-semibold">{currentSpec.percent}%</span>
            </div>
          </div>
        )}

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-3 bg-[#0d121c]">
          {currentSpec && activeTab === 'tasks' && (
            <div className="space-y-2">
              <div className="text-xs text-slate-400 font-mono flex items-center justify-between pb-1 border-b border-[#1e293b]">
                <span>Перелік задач у <code>{currentSpec.path}/tasks.md</code></span>
                <span>Натисніть на чекбокс для перемикання</span>
              </div>

              {currentSpec.tasks.map((task) => {
                const toggling = isToggling === task.id;
                return (
                  <div
                    key={task.id}
                    onClick={() => handleCheckboxClick(task.id, task.completed)}
                    className={`p-3 rounded border flex items-start gap-3 cursor-pointer select-none transition-all ${
                      task.completed
                        ? 'bg-[#141b27]/60 border-[#1e293b] hover:border-emerald/30 text-slate-300'
                        : 'bg-[#141b27] border-[#1e293b] hover:border-amber/50 text-slate-100 shadow-xs'
                    }`}
                  >
                    <button
                      className="mt-0.5 text-slate-400 hover:text-amber transition-colors shrink-0 cursor-pointer"
                      disabled={toggling}
                    >
                      {task.completed ? (
                        <CheckSquare className="w-4 h-4 text-emerald" />
                      ) : (
                        <Square className="w-4 h-4 text-slate-500 hover:text-amber" />
                      )}
                    </button>

                    <div className="space-y-1 flex-1">
                      <div className="flex items-center gap-2">
                        <Badge tone="amber" outline>
                          {task.id}
                        </Badge>
                        {task.completed && (
                          <Badge tone="emerald" outline>
                            <CheckCircle2 className="w-3 h-3" />
                            виконано
                          </Badge>
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
            <div className="p-4 bg-[#090d13] rounded border border-[#1e293b] text-xs font-mono whitespace-pre-wrap leading-relaxed text-slate-200">
              {currentSpec.spec_markdown || 'Опис специфікації відсутній.'}
            </div>
          )}

          {currentSpec && activeTab === 'plan' && (
            <div className="p-4 bg-[#090d13] rounded border border-[#1e293b] text-xs font-mono whitespace-pre-wrap leading-relaxed text-slate-200">
              {currentSpec.plan_markdown || 'Архітектурний план відсутній.'}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-[#141b27] border-t border-[#1e293b] flex items-center justify-between text-xs shrink-0">
          <span className="text-slate-400 font-mono text-[11px]">
            Зміни зберігаються напряму в <code>specs/**/tasks.md</code>
          </span>
          <Button variant="secondary" size="sm" onClick={onClose}>
            Закрити
          </Button>
        </div>
      </div>
    </Drawer>
  );
};

export default TasksDrawer;
