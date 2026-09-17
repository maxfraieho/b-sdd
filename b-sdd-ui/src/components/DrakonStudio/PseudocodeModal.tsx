// src/components/DrakonStudio/PseudocodeModal.tsx
// Astryx-native Pseudocode & AST Export Dialog (ADR-008, ADR-009)
import React, { useState, useEffect } from 'react';
import { diagramToPseudocode, diagramToTree, pseudocodeToMarkdown } from '@/lib/drakon/pseudocode';
import { Dialog, Button, Badge, Segmented } from '@/components/astryx/primitives';
import {
  FileCode2,
  Copy,
  Check,
  Download,
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
  const [activeTab, setActiveTab] = useState<string>('pseudocode');
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
    <Dialog
      isOpen={isOpen}
      onClose={onClose}
      maxWidth="max-w-4xl"
      title={
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded bg-amber/10 border border-amber/30 text-amber">
            <FileCode2 className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm font-bold text-slate-100 font-mono flex items-center gap-2">
              <span>Експорт псевдокоду та структурних правил</span>
              <Badge tone="amber" outline>
                {diagramName}
              </Badge>
            </div>
            <p className="text-[11px] text-slate-400 font-sans font-normal mt-0.5">
              Автоматична трансляція візуальної ДРАКОН-схеми в алгоритмічний псевдокод та дерево правил
            </p>
          </div>
        </div>
      }
      footer={
        <div className="flex items-center justify-between w-full text-xs">
          <span className="text-slate-400 font-mono text-[11px] flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-amber" />
            <span>Готово до передачі AI-агенту для детермінованої генерації коду</span>
          </span>
          <Button variant="secondary" size="sm" onClick={onClose}>
            Закрити
          </Button>
        </div>
      }
    >
      <div className="-m-4 flex flex-col h-[65vh] overflow-hidden">
        {/* Tab & Action Bar */}
        <div className="px-6 py-2.5 bg-[#090d13] border-b border-[#1e293b] flex items-center justify-between text-xs font-mono shrink-0">
          <Segmented
            value={activeTab}
            onChange={(val) => setActiveTab(val)}
            options={[
              {
                value: 'pseudocode',
                label: (
                  <span className="flex items-center gap-1.5">
                    <Code className="w-3.5 h-3.5" />
                    <span>Псевдокод (DrakonGen)</span>
                  </span>
                ),
              },
              {
                value: 'tree',
                label: (
                  <span className="flex items-center gap-1.5">
                    <TreeDeciduous className="w-3.5 h-3.5" />
                    <span>Структурне дерево (AST JSON)</span>
                  </span>
                ),
              },
            ]}
          />

          <div className="flex items-center gap-2">
            <Button
              variant="secondary"
              size="sm"
              onClick={handleCopy}
              disabled={isLoading || !currentContent}
              icon={copied ? <Check className="w-3.5 h-3.5 text-emerald" /> : <Copy className="w-3.5 h-3.5" />}
            >
              {copied ? 'Скопійовано' : 'Копіювати'}
            </Button>

            <Button
              variant="primary"
              size="sm"
              onClick={handleDownload}
              disabled={isLoading || !currentContent}
              icon={<Download className="w-3.5 h-3.5" />}
            >
              Завантажити
            </Button>
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-hidden relative bg-[#090d13] flex flex-col">
          {isLoading ? (
            <div className="flex-1 flex flex-col items-center justify-center text-slate-400 gap-2">
              <Loader2 className="w-6 h-6 animate-spin text-amber" />
              <span className="text-xs font-mono">Генерація псевдокоду через drakongen.js...</span>
            </div>
          ) : error ? (
            <div className="p-6 text-rose font-mono text-xs">{error}</div>
          ) : (
            <pre className="flex-1 overflow-auto p-6 font-mono text-xs leading-relaxed text-slate-200 selection:bg-amber/30 select-text whitespace-pre">
              {currentContent}
            </pre>
          )}
        </div>
      </div>
    </Dialog>
  );
};

export default PseudocodeModal;
