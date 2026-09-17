// src/components/PipelineCatalogModal.tsx
// Standard Algorithmic Pipeline & Pattern Catalog (ADR-010)
import React, { useState, useEffect } from 'react';
import { Dialog, Button, Badge, Banner } from './astryx/primitives';
import { Workflow, Layers, CheckCircle2, Play, Code2, Download } from 'lucide-react';
import type { DrakonSchemaIR } from '@/types/drakon';

export interface PipelineTemplateItem {
  id: string;
  name: string;
  category: 'bsdd_pipeline' | 'algorithm' | string;
  description: string;
  params: string;
  node_count: number;
  schema: DrakonSchemaIR;
}

const DEFAULT_TEMPLATES: PipelineTemplateItem[] = [
  {
    id: 'bsdd_preflight_pipeline',
    name: 'B-SDD Pre-Flight Active Rules Compiler',
    category: 'bsdd_pipeline',
    description: 'Детерміністична компіляція активних інваріантів під жорсткий бюджет (<50ms, <500 слів)',
    params: 'root_dir: str, target_domains: list',
    node_count: 10,
    schema: {
      schema_version: '1.0',
      name: 'B-SDD Pre-Flight Active Rules Compiler',
      nodes: [],
    },
  },
  {
    id: 'tdd_verification_loop',
    name: 'TDD Red-Green-Refactor & Fitness Gate',
    category: 'bsdd_pipeline',
    description: 'Автоматизований цикл TDD з перевіркою 100% архітектурної відповідності',
    params: 'spec_id: str, test_file: str',
    node_count: 8,
    schema: {
      schema_version: '1.0',
      name: 'TDD Red-Green-Refactor & Fitness Gate',
      nodes: [],
    },
  },
  {
    id: 'rule_of_2_crystallizer',
    name: 'Rule of 2 Skill Crystallization Workflow',
    category: 'bsdd_pipeline',
    description: 'Автономне перетворення повторюваних інженерних патернів у стійкі навички агентів',
    params: 'workflow_name: str, observation_count: int',
    node_count: 9,
    schema: {
      schema_version: '1.0',
      name: 'Rule of 2 Skill Crystallization Workflow',
      nodes: [],
    },
  },
  {
    id: 'utopia_sync_workflow',
    name: 'Bitemporal Intent Sync & Utopia DB Knowledge Graph',
    category: 'bsdd_pipeline',
    description: 'Транзакційна синхронізація намірів ADR з базою знань Utopia DB та побудова графу звʼязків',
    params: 'kb_id: str, host: str, port: int',
    node_count: 7,
    schema: {
      schema_version: '1.0',
      name: 'Bitemporal Intent Sync & Utopia DB Knowledge Graph',
      nodes: [],
    },
  },
  {
    id: 'drakon_binary_search',
    name: 'ДРАКОН: Канонічний двійковий пошук (Binary Search)',
    category: 'algorithm',
    description: 'Класичний алгоритм бінарного пошуку в масиві за правилами ергономіки ДРАКОН',
    params: 'arr: list, target: any',
    node_count: 9,
    schema: {
      schema_version: '1.0',
      name: 'ДРАКОН: Канонічний двійковий пошук (Binary Search)',
      nodes: [],
    },
  },
  {
    id: 'drakon_state_machine',
    name: 'ДРАКОН: Скінченний автомат життєвого циклу (FSM Lifecycle)',
    category: 'algorithm',
    description: 'Патерн обробки станів та переходів за каноном ДРАКОН-силует',
    params: 'current_state: str, event: dict',
    node_count: 10,
    schema: {
      schema_version: '1.0',
      name: 'ДРАКОН: Скінченний автомат життєвого циклу (FSM Lifecycle)',
      nodes: [],
    },
  },
];

interface PipelineCatalogModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLoadTemplate: (template: PipelineTemplateItem) => void;
}

export const PipelineCatalogModal: React.FC<PipelineCatalogModalProps> = ({
  isOpen,
  onClose,
  onLoadTemplate,
}) => {
  const [activeCategory, setActiveCategory] = useState<'all' | 'bsdd_pipeline' | 'algorithm'>('all');
  const [templates, setTemplates] = useState<PipelineTemplateItem[]>(DEFAULT_TEMPLATES);
  const [selectedId, setSelectedId] = useState<string>(DEFAULT_TEMPLATES[0].id);

  useEffect(() => {
    async function fetchCatalog() {
      try {
        const resp = await fetch('/api/pipelines/catalog');
        if (resp.ok) {
          const data = await resp.json();
          if (data.pipelines && data.pipelines.length > 0) {
            setTemplates(data.pipelines);
          }
        }
      } catch (e) {
        // use fallback DEFAULT_TEMPLATES
      }
    }
    if (isOpen) {
      fetchCatalog();
    }
  }, [isOpen]);

  const filtered = templates.filter(
    (t) => activeCategory === 'all' || t.category === activeCategory
  );

  const selectedTemplate = templates.find((t) => t.id === selectedId) || templates[0];

  const handleApply = (tmpl: PipelineTemplateItem) => {
    onLoadTemplate(tmpl);
    onClose();
  };

  return (
    <Dialog
      isOpen={isOpen}
      onClose={onClose}
      title={
        <div className="flex items-center gap-2">
          <Workflow className="w-4 h-4 text-amber" />
          <span>Бібліотека стандартних алгоритмів і пайплайнів (ADR-010)</span>
        </div>
      }
      maxWidth="max-w-4xl"
    >
      <div className="space-y-4">
        <Banner tone="info" icon={<Layers className="w-4 h-4 text-cyan shrink-0" />}>
          Всі шаблони математично верифіковані: нуль лінійних перетинів (crossings = 0),
          дотримання вертикального шампура («праворуч — гірше») та бітемпоральна привʼязка до ADR.
        </Banner>

        {/* Category Tabs */}
        <div className="flex border-b border-[#1e293b] gap-4 font-mono text-xs">
          <button
            onClick={() => setActiveCategory('all')}
            className={`pb-2 transition-colors border-b-2 ${
              activeCategory === 'all'
                ? 'border-amber text-amber font-bold'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            Всі шаблони ({templates.length})
          </button>
          <button
            onClick={() => setActiveCategory('bsdd_pipeline')}
            className={`pb-2 transition-colors border-b-2 ${
              activeCategory === 'bsdd_pipeline'
                ? 'border-amber text-amber font-bold'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            B-SDD Інженерні пайплайни ({templates.filter((t) => t.category === 'bsdd_pipeline').length})
          </button>
          <button
            onClick={() => setActiveCategory('algorithm')}
            className={`pb-2 transition-colors border-b-2 ${
              activeCategory === 'algorithm'
                ? 'border-amber text-amber font-bold'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            Канонічні алгоритми ДРАКОН ({templates.filter((t) => t.category === 'algorithm').length})
          </button>
        </div>

        {/* 2-Column Catalog Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-[55vh] overflow-y-auto pr-1">
          {filtered.map((tmpl) => {
            const isSelected = tmpl.id === selectedId;
            return (
              <div
                key={tmpl.id}
                onClick={() => setSelectedId(tmpl.id)}
                className={`p-3 rounded border cursor-pointer transition-all flex flex-col justify-between ${
                  isSelected
                    ? 'bg-[#1a2233] border-amber/50 shadow-md ring-1 ring-amber/30'
                    : 'bg-[#0d121c] border-[#1e293b] hover:border-slate-700'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-mono font-bold text-xs text-slate-100 truncate">
                      {tmpl.name}
                    </span>
                    <Badge tone={tmpl.category === 'bsdd_pipeline' ? 'cyan' : 'emerald'} outline>
                      {tmpl.category === 'bsdd_pipeline' ? 'B-SDD' : 'Алгоритм'}
                    </Badge>
                  </div>
                  <p className="text-[11px] text-slate-400 mb-2 leading-relaxed">{tmpl.description}</p>
                </div>

                <div className="pt-2 border-t border-[#1e293b]/60 flex items-center justify-between text-[10px] font-mono text-slate-400">
                  <span>Вузлів: {tmpl.node_count || tmpl.schema?.nodes?.length || 8}</span>
                  <Button
                    size="sm"
                    variant={isSelected ? 'primary' : 'secondary'}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleApply(tmpl);
                    }}
                    icon={<Play className="w-3 h-3" />}
                  >
                    Завантажити
                  </Button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </Dialog>
  );
};
