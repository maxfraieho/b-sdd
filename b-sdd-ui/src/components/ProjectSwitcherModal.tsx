import React, { useState, useEffect } from 'react';
import { Dialog, Button, Badge, Dot, Banner } from './astryx/primitives';
import { FolderGit2, GitBranch, Github, Plus, Check, ExternalLink, RefreshCw, Search, Code2 } from 'lucide-react';
import type { ProjectInfo } from '@/types/specs';
import { searchCrossWorkspaceSymbols } from '@/lib/api';
import type { WorkspaceSymbol } from '@/lib/backend-types';

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
  stars?: number;
  forks?: number;
  open_issues?: number;
  updated_at?: string;
  html_url?: string;
}

interface ProjectSwitcherModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentProject: ProjectInfo | null;
  workspaces?: WorkspaceItem[];
  githubRepos?: GithubRepoItem[];
  onSwitchProject: (projectId: string, name?: string) => Promise<void>;
  onSyncGithub?: () => Promise<void>;
  isSyncingGithub?: boolean;
  githubSyncedAt?: string;
  githubIsLive?: boolean;
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
  onSyncGithub,
  isSyncingGithub = false,
  githubSyncedAt,
  githubIsLive = true,
}) => {
  const [activeTab, setActiveTab] = useState<'local' | 'github' | 'symbols' | 'add'>('github');
  const [customRepoUrl, setCustomRepoUrl] = useState('');
  const [isSwitching, setIsSwitching] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Cross-workspace AST Symbol Search State (INV-014-04)
  const [symbolQuery, setSymbolQuery] = useState('');
  const [symbols, setSymbols] = useState<WorkspaceSymbol[]>([]);
  const [isSearchingSymbols, setIsSearchingSymbols] = useState(false);
  const [selectedWsFilter, setSelectedWsFilter] = useState<string>('all');

  const handleSearchSymbols = async (q: string, ws?: string) => {
    setIsSearchingSymbols(true);
    try {
      const res = await searchCrossWorkspaceSymbols(q, ws && ws !== 'all' ? ws : undefined);
      setSymbols(res.symbols);
    } catch (e) {
      console.error('Failed to search cross-workspace symbols:', e);
    } finally {
      setIsSearchingSymbols(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'symbols' && symbols.length === 0) {
      void handleSearchSymbols(symbolQuery, selectedWsFilter);
    }
  }, [activeTab]);

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
            <span>GitHub ({githubRepos.length})</span>
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
            <span>Воркспейси ({workspaces.length})</span>
          </button>
          <button
            onClick={() => {
              setActiveTab('symbols');
              if (symbols.length === 0) void handleSearchSymbols(symbolQuery, selectedWsFilter);
            }}
            className={`pb-2 flex items-center gap-1.5 transition-colors border-b-2 ${
              activeTab === 'symbols'
                ? 'border-amber text-amber font-bold'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Code2 className="w-3.5 h-3.5" />
            <span>AST Символи</span>
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
            <span>Підключити</span>
          </button>
        </div>

        {/* Tab 1: GitHub Repositories */}
        {activeTab === 'github' && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono">
              <div className="flex items-center gap-1.5">
                <span>Репозиторії GitHub (`maxfraieho`):</span>
                {githubIsLive ? (
                  <Badge tone="emerald" outline>Live API</Badge>
                ) : (
                  <Badge tone="cyan" outline>Offline Cache</Badge>
                )}
                {githubSyncedAt && (
                  <span className="text-[10px] text-slate-500">
                    Оновлено: {githubSyncedAt.slice(11, 19)}
                  </span>
                )}
              </div>
              {onSyncGithub && (
                <button
                  onClick={() => void onSyncGithub()}
                  disabled={isSyncingGithub}
                  className="flex items-center gap-1 text-[11px] text-amber hover:text-amber-light transition-colors px-2 py-0.5 rounded bg-amber/10 hover:bg-amber/20 border border-amber/30 disabled:opacity-50"
                  title="Отримати свіжий список репозиторіїв з GitHub API"
                >
                  <RefreshCw className={`w-3 h-3 ${isSyncingGithub ? 'animate-spin' : ''}`} />
                  <span>{isSyncingGithub ? 'Синхронізація…' : 'Синхронізувати'}</span>
                </button>
              )}
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
                        {repo.stars !== undefined && repo.stars > 0 && (
                          <span className="text-[10px] text-amber flex items-center gap-0.5">
                            ★ {repo.stars}
                          </span>
                        )}
                        {repo.forks !== undefined && repo.forks > 0 && (
                          <span className="text-[10px] text-slate-400">
                            ⑂ {repo.forks}
                          </span>
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

        {/* Tab 3: AST Symbols (Multi-Tenant Tracing) */}
        {activeTab === 'symbols' && (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="relative flex-1">
                <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
                <input
                  type="text"
                  placeholder="Пошук класів, функцій, інтерфейсів..."
                  value={symbolQuery}
                  onChange={(e) => {
                    setSymbolQuery(e.target.value);
                    void handleSearchSymbols(e.target.value, selectedWsFilter);
                  }}
                  className="w-full bg-[#141b27] border border-[#1e293b] rounded pl-8 pr-3 py-1.5 text-xs font-mono text-slate-100 focus:outline-none focus:ring-1 focus:ring-amber"
                />
              </div>
              <select
                value={selectedWsFilter}
                onChange={(e) => {
                  setSelectedWsFilter(e.target.value);
                  void handleSearchSymbols(symbolQuery, e.target.value);
                }}
                className="bg-[#141b27] border border-[#1e293b] rounded px-2 py-1.5 text-xs font-mono text-slate-300 focus:outline-none focus:ring-1 focus:ring-amber"
              >
                <option value="all">Усі воркспейси</option>
                <option value="core">b-sdd (core)</option>
                <option value="ui">b-sdd-ui</option>
              </select>
            </div>

            <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono">
              <span>Знайдено символів: {symbols.length}</span>
              {isSearchingSymbols && <span className="text-amber">Сканування AST...</span>}
            </div>

            <div className="max-h-64 overflow-y-auto space-y-1.5 pr-1">
              {symbols.length === 0 ? (
                <div className="p-4 text-center text-xs text-slate-500 font-mono border border-dashed border-[#1e293b] rounded">
                  {isSearchingSymbols ? 'Індексація символів...' : 'Символів не знайдено за запитом'}
                </div>
              ) : (
                symbols.map((sym, idx) => (
                  <div
                    key={`${sym.workspace}-${sym.file_path}-${sym.name}-${idx}`}
                    className="p-2 bg-[#0d121c] border border-[#1e293b] rounded flex items-center justify-between hover:border-slate-700 transition-colors"
                  >
                    <div className="flex flex-col gap-0.5 overflow-hidden">
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-slate-100 text-xs truncate">
                          {sym.name}
                        </span>
                        <Badge
                          tone={
                            sym.kind === 'class'
                              ? 'amber'
                              : sym.kind === 'interface'
                              ? 'emerald'
                              : 'cyan'
                          }
                          outline
                        >
                          {sym.kind}
                        </Badge>
                        <span className="text-[10px] text-slate-400 px-1 rounded bg-[#1e293b]">
                          {sym.workspace}
                        </span>
                      </div>
                      <span className="text-[10px] text-slate-500 font-mono truncate">
                        {sym.file_path}:{sym.line_number}
                        {sym.docstring ? ` — ${sym.docstring}` : ''}
                      </span>
                    </div>

                    <Button
                      size="sm"
                      variant="secondary"
                      disabled={isSwitching}
                      onClick={() => handleSelect(sym.workspace, `${sym.workspace} (${sym.name})`)}
                    >
                      Перейти
                    </Button>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* Tab 4: Add/Connect Repository */}
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
