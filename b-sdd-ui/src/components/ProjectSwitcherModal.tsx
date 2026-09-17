// src/components/ProjectSwitcherModal.tsx
// Universal Project & Repository Switcher (ADR-010)
import React, { useState } from 'react';
import { Dialog, Button, Badge, Dot, Banner } from './astryx/primitives';
import { FolderGit2, GitBranch, Github, Plus, Check, ExternalLink, RefreshCw } from 'lucide-react';
import type { ProjectInfo } from '@/types/specs';

export interface WorkspaceItem {
  id: string;
  name: string;
  path: string;
  active?: boolean;
}

export interface GithubRepoItem {
  name: string;
  full_name: string;
  description: string;
  is_active?: boolean;
  branch: string;
}

interface ProjectSwitcherModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentProject: ProjectInfo | null;
  workspaces?: WorkspaceItem[];
  githubRepos?: GithubRepoItem[];
  onSwitchProject: (projectId: string, name?: string) => Promise<void>;
}

export const ProjectSwitcherModal: React.FC<ProjectSwitcherModalProps> = ({
  isOpen,
  onClose,
  currentProject,
  workspaces = [],
  githubRepos = [
    {
      name: 'b-sdd',
      full_name: 'maxfraieho/b-sdd',
      description: 'Bitemporal Spec-Driven Development Framework with pure stdlib runtime',
      is_active: true,
      branch: 'main',
    },
    {
      name: 'ai-drakon-scaffolder',
      full_name: 'maxfraieho/ai-drakon-scaffolder',
      description: 'DRAKON visual logic editor, AST generator & test scaffolder',
      is_active: false,
      branch: 'main',
    },
    {
      name: 'utopia-vault',
      full_name: 'maxfraieho/utopia-vault',
      description: 'Sovereign bitemporal vector knowledge base and intent memory',
      is_active: false,
      branch: 'main',
    },
  ],
  onSwitchProject,
}) => {
  const [activeTab, setActiveTab] = useState<'local' | 'github' | 'add'>('github');
  const [customRepoUrl, setCustomRepoUrl] = useState('');
  const [isSwitching, setIsSwitching] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleSelect = async (id: string, name?: string) => {
    setIsSwitching(true);
    setSuccessMessage(null);
    try {
      await onSwitchProject(id, name);
      setSuccessMessage(`Успішно переключено на проєкт: ${name || id}`);
      setTimeout(() => {
        setSuccessMessage(null);
        onClose();
      }, 1200);
    } catch (e) {
      console.error('Failed to switch project:', e);
    } finally {
      setIsSwitching(false);
    }
  };

  const handleAddRepo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!customRepoUrl.trim()) return;
    const repoName = customRepoUrl.trim().split('/').pop()?.replace('.git', '') || 'custom-repo';
    await handleSelect(repoName, repoName);
  };

  return (
    <Dialog
      isOpen={isOpen}
      onClose={onClose}
      title={
        <div className="flex items-center gap-2">
          <FolderGit2 className="w-4 h-4 text-cyan" />
          <span>Універсальний перемикач проєктів (B-SDD Context)</span>
        </div>
      }
      maxWidth="max-w-2xl"
    >
      <div className="space-y-4">
        {/* Banner with Active Info */}
        <Banner tone="info" icon={<FolderGit2 className="w-4 h-4 text-cyan shrink-0" />}>
          <div className="flex flex-col gap-1">
            <div className="font-bold flex items-center gap-2 text-slate-100">
              <span>Активний репозиторій: {currentProject?.name || 'B-SDD Core'}</span>
              <Badge tone="emerald" outline>
                {currentProject?.branch || 'main'}
              </Badge>
            </div>
            <span className="text-[11px] text-slate-400 font-mono">
              Шлях: {currentProject?.path || '/home/vokov/projects/b-sdd'}
            </span>
          </div>
        </Banner>

        {successMessage && (
          <div className="p-3 bg-emerald/10 border border-emerald/40 text-emerald text-xs font-mono rounded flex items-center gap-2">
            <Check className="w-4 h-4 text-emerald" />
            <span>{successMessage}</span>
          </div>
        )}

        {/* Tab Switcher */}
        <div className="flex border-b border-[#1e293b] gap-4 font-mono text-xs">
          <button
            onClick={() => setActiveTab('github')}
            className={`pb-2 flex items-center gap-1.5 transition-colors border-b-2 ${
              activeTab === 'github'
                ? 'border-amber text-amber font-bold'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Github className="w-3.5 h-3.5" />
            <span>GitHub репозиторії ({githubRepos.length})</span>
          </button>
          <button
            onClick={() => setActiveTab('local')}
            className={`pb-2 flex items-center gap-1.5 transition-colors border-b-2 ${
              activeTab === 'local'
                ? 'border-amber text-amber font-bold'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <FolderGit2 className="w-3.5 h-3.5" />
            <span>Локальні воркспейси ({workspaces.length})</span>
          </button>
          <button
            onClick={() => setActiveTab('add')}
            className={`pb-2 flex items-center gap-1.5 transition-colors border-b-2 ${
              activeTab === 'add'
                ? 'border-amber text-amber font-bold'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Підключити новий репозиторій</span>
          </button>
        </div>

        {/* Tab 1: GitHub Repositories */}
        {activeTab === 'github' && (
          <div className="space-y-2">
            <div className="text-[11px] text-slate-400 font-mono">
              Репозиторії облікового запису GitHub (`maxfraieho`):
            </div>
            <div className="grid gap-2">
              {githubRepos.map((repo) => {
                const isCurrent =
                  currentProject?.name.toLowerCase().includes(repo.name.toLowerCase()) ||
                  repo.is_active;
                return (
                  <div
                    key={repo.name}
                    className={`p-3 rounded border flex items-center justify-between transition-colors ${
                      isCurrent
                        ? 'bg-[#1a2233] border-amber/40 shadow-sm'
                        : 'bg-[#0d121c] border-[#1e293b] hover:border-slate-700'
                    }`}
                  >
                    <div className="flex flex-col gap-0.5">
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-slate-100 text-xs">
                          {repo.full_name}
                        </span>
                        {isCurrent ? (
                          <Badge tone="amber">Активний</Badge>
                        ) : (
                          <Badge tone="cyan" outline>
                            {repo.branch}
                          </Badge>
                        )}
                      </div>
                      <p className="text-[11px] text-slate-400">{repo.description}</p>
                    </div>

                    <div className="flex items-center gap-2">
                      <Button
                        size="sm"
                        variant={isCurrent ? 'ghost' : 'secondary'}
                        disabled={isCurrent || isSwitching}
                        onClick={() => handleSelect(repo.name, repo.full_name)}
                      >
                        {isCurrent ? 'Поточний' : 'Вибрати'}
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Tab 2: Local Workspaces */}
        {activeTab === 'local' && (
          <div className="space-y-2">
            <div className="text-[11px] text-slate-400 font-mono">
              Локальні зареєстровані воркспейси (b_sdd.config.json):
            </div>
            <div className="grid gap-2">
              {workspaces.map((ws) => (
                <div
                  key={ws.id}
                  className="p-3 bg-[#0d121c] border border-[#1e293b] rounded flex items-center justify-between"
                >
                  <div className="flex flex-col gap-0.5">
                    <span className="font-mono font-bold text-slate-100 text-xs">{ws.name}</span>
                    <span className="text-[10px] text-slate-500 font-mono">{ws.path}</span>
                  </div>
                  <Button
                    size="sm"
                    variant={ws.active ? 'ghost' : 'secondary'}
                    disabled={ws.active || isSwitching}
                    onClick={() => handleSelect(ws.id, ws.name)}
                  >
                    {ws.active ? 'Активний' : 'Перемкнути'}
                  </Button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab 3: Add/Connect Repository */}
        {activeTab === 'add' && (
          <form onSubmit={handleAddRepo} className="space-y-3 p-3 bg-[#0d121c] border border-[#1e293b] rounded">
            <div>
              <label className="block text-xs font-mono text-slate-300 mb-1">
                URL або повна назва репозиторію GitHub:
              </label>
              <input
                type="text"
                placeholder="наприклад: maxfraieho/my-new-service або https://github.com/..."
                value={customRepoUrl}
                onChange={(e) => setCustomRepoUrl(e.target.value)}
                className="w-full bg-[#141b27] border border-[#1e293b] rounded px-3 py-2 text-xs font-mono text-slate-100 focus:outline-none focus:ring-1 focus:ring-amber"
              />
            </div>
            <div className="flex justify-end">
              <Button
                variant="primary"
                size="sm"
                type="submit"
                disabled={!customRepoUrl.trim() || isSwitching}
                icon={<Plus className="w-3 h-3" />}
              >
                Підключити та перемкнутися
              </Button>
            </div>
          </form>
        )}
      </div>
    </Dialog>
  );
};
