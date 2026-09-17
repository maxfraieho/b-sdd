// src/components/DrakonStudio/PseudocodeModal.tsx
import React, { useState, useEffect } from 'react';
import { diagramToPseudocode, diagramToTree, pseudocodeToMarkdown } from '@/lib/drakon/pseudocode';
import {
  X,
  FileCode2,
  Copy,
  Check,
  Download,
  Terminal,
  Loader2,
  Sparkles,
  TreeDeciduous,
  Code,
} from 'lucide-react';

interface PseudocodeModalProps {
  isOpen: boolean;
  onClose: () => void;
  diagramJson: object | null;
  diagramName: string;
}

export const PseudocodeModal: React.FC<PseudocodeModalProps> = ({
  isOpen,
  onClose,
  diagramJson,
  diagramName,
}) => {
  const [activeTab, setActiveTab] = useState<'pseudocode' | 'tree'>('pseudocode');
  const [pseudocode, setPseudocode] = useState<string>('');
  const [treeJson, setTreeJson] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!isOpen || !diagramJson) return;

    let mounted = true;
    setIsLoading(true);
    setError(null);

    async function generate() {
      try {
        const code = await diagramToPseudocode(diagramJson!, diagramName, 'en');
        const tree = await diagramToTree(diagramJson!, diagramName, 'en');
        if (mounted) {
          setPseudocode(code);
          setTreeJson(tree);
          setIsLoading(false);
        }
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err.message : 'Не вдалося згенерувати псевдокод');
          setIsLoading(false);
        }
      }
    }

    void generate();

    return () => {
      mounted = false;
    };
  }, [isOpen, diagramJson, diagramName]);

  if (!isOpen) return null;

  const currentContent = activeTab === 'pseudocode' ? pseudocode : treeJson;

  const handleCopy = () => {
    void navigator.clipboard.writeText(currentContent).then(() => {
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    });
  };

  const handleDownload = () => {
    const md = pseudocodeToMarkdown(pseudocode, diagramName);
    const blob = new Blob([activeTab === 'pseudocode' ? md : treeJson], {
      type: activeTab === 'pseudocode' ? 'text/markdown' : 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${diagramName}.${activeTab === 'pseudocode' ? 'pseudocode.md' : 'tree.json'}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-150">
      <div className="w-full max-w-4xl max-h-[85vh] bg-panel border border-border-subtle rounded-xl shadow-2xl flex flex-col overflow-hidden text-slate-100">
        {/* Header */}
        <div className="px-6 py-4 bg-card border-b border-border-subtle flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-amber/10 border border-amber/30 text-amber">
              <FileCode2 className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <span>Експорт псевдокоду та структурних правил</span>
                <span className="text-xs font-mono font-normal text-amber bg-amber/10 px-2 py-0.5 rounded border border-amber/20">
                  {diagramName}
                </span>
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Автоматична трансляція візуальної ДРАКОН-схеми в алгоритмічний псевдокод та дерево правил
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab & Action Bar */}
        <div className="px-6 py-2.5 bg-canvas/80 border-b border-border-subtle flex items-center justify-between text-xs font-mono">
          <div className="flex items-center rounded-lg bg-card p-0.5 border border-border-subtle">
            <button
              onClick={() => setActiveTab('pseudocode')}
              className={`flex items-center gap-1.5 px-3 py-1 rounded transition-colors ${
                activeTab === 'pseudocode'
                  ? 'bg-amber text-slate-950 font-bold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Code className="w-3.5 h-3.5" />
              <span>Псевдокод (DrakonGen)</span>
            </button>
            <button
              onClick={() => setActiveTab('tree')}
              className={`flex items-center gap-1.5 px-3 py-1 rounded transition-colors ${
                activeTab === 'tree'
                  ? 'bg-amber text-slate-950 font-bold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <TreeDeciduous className="w-3.5 h-3.5" />
              <span>Структурне дерево (AST JSON)</span>
            </button>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              disabled={isLoading || !currentContent}
              className="px-3 py-1.5 rounded-lg bg-card hover:bg-slate-800 border border-border-subtle text-slate-200 flex items-center gap-1.5 transition-colors disabled:opacity-50"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Скопійовано' : 'Копіювати'}</span>
            </button>

            <button
              onClick={handleDownload}
              disabled={isLoading || !currentContent}
              className="px-3 py-1.5 rounded-lg bg-amber/15 hover:bg-amber/25 border border-amber/30 text-amber font-semibold flex items-center gap-1.5 transition-colors disabled:opacity-50"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Завантажити</span>
            </button>
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-hidden relative bg-canvas flex flex-col">
          {isLoading ? (
            <div className="flex-1 flex flex-col items-center justify-center text-slate-400 gap-2">
              <Loader2 className="w-6 h-6 animate-spin text-amber" />
              <span className="text-xs font-mono">Генерація псевдокоду через drakongen.js...</span>
            </div>
          ) : error ? (
            <div className="p-6 text-rose-400 font-mono text-xs">{error}</div>
          ) : (
            <pre className="flex-1 overflow-auto p-6 font-mono text-xs leading-relaxed text-slate-200 selection:bg-amber/30 select-text whitespace-pre">
              {currentContent}
            </pre>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-card border-t border-border-subtle flex items-center justify-between text-xs">
          <span className="text-slate-400 font-mono text-[11px] flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-amber" />
            <span>Готово до передачі AI-агенту для детермінованої генерації коду</span>
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

export default PseudocodeModal;
