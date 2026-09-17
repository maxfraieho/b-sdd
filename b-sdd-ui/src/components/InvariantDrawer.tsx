// src/components/InvariantDrawer.tsx
// Astryx-native Utopia Invariant Inspector Drawer (ADR-008, ADR-009)
import React, { useState } from 'react';
import type { BitemporalAdr, AdrInvariant } from '@/types/adr';
import { Drawer, Badge, Dot } from './astryx/primitives';
import {
  Search,
  Shield,
  Database,
  Filter,
  CheckCircle2,
} from 'lucide-react';

interface InvariantDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  adrs: BitemporalAdr[];
  onSelectInvariant?: (invariantId: string) => void;
}

export const InvariantDrawer: React.FC<InvariantDrawerProps> = ({
  isOpen,
  onClose,
  adrs,
  onSelectInvariant,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedComponent, setSelectedComponent] = useState<string>('all');

  if (!isOpen) return null;

  // Flatten all invariants from ADRs
  const allInvariants: Array<AdrInvariant & { adrId: string; adrTitle: string }> = [];
  adrs.forEach((adr) => {
    adr.invariants.forEach((inv) => {
      allInvariants.push({
        ...inv,
        adrId: adr.id,
        adrTitle: adr.title,
      });
    });
  });

  // Filter invariants
  const filtered = allInvariants.filter((inv) => {
    const matchesSearch =
      inv.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      inv.statement.toLowerCase().includes(searchQuery.toLowerCase()) ||
      inv.adrId.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesComponent =
      selectedComponent === 'all' || inv.component === selectedComponent;

    return matchesSearch && matchesComponent;
  });

  const components = ['all', 'core', 'specs', 'skills', 'handoff', 'analysis', 'infra'];

  return (
    <Drawer
      isOpen={isOpen}
      onClose={onClose}
      width="w-[440px]"
      title={
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded bg-amber/15 border border-amber/30 flex items-center justify-center text-amber">
            <Shield className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-bold text-sm text-slate-100 font-mono">
              Utopia Invariant Inspector
            </h3>
            <p className="text-[10px] text-slate-400 font-mono flex items-center gap-1 font-normal">
              <Database className="w-3 h-3 text-emerald" />
              <span>Hybrid Tantivy + pgvector (.251:9922)</span>
            </p>
          </div>
        </div>
      }
    >
      <div className="-m-4 flex flex-col h-full">
        {/* Search & Filter Bar */}
        <div className="p-3 bg-[#0d121c] border-b border-[#1e293b] space-y-2 shrink-0">
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-slate-500" />
            <input
              type="text"
              placeholder="Search invariants by ID, keyword or semantic intent..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-[#090d13] border border-[#1e293b] rounded pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber font-mono"
            />
          </div>

          {/* Component Pills */}
          <div className="flex items-center gap-1 overflow-x-auto py-0.5">
            <Filter className="w-3 h-3 text-slate-500 mr-0.5 shrink-0" />
            {components.map((comp) => (
              <button
                key={comp}
                onClick={() => setSelectedComponent(comp)}
                className={`px-2 py-0.5 rounded text-[10px] font-mono capitalize shrink-0 transition-colors cursor-pointer ${
                  selectedComponent === comp
                    ? 'bg-amber text-slate-950 font-bold'
                    : 'bg-[#141b27] hover:bg-[#1a2233] text-slate-400 border border-[#1e293b]'
                }`}
              >
                {comp}
              </button>
            ))}
          </div>
        </div>

        {/* Results List */}
        <div className="flex-1 p-3 overflow-y-auto space-y-2.5">
          <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono pb-1">
            <span>MATCHED INVARIANTS ({filtered.length})</span>
            <span className="flex items-center gap-1">
              <Dot tone="emerald" pulse />
              <span>BITEMPORAL AUDIT ACTIVE</span>
            </span>
          </div>

          {filtered.map((inv) => {
            const tone: 'rose' | 'amber' | 'cyan' | 'neutral' =
              inv.severity === 'critical'
                ? 'rose'
                : inv.severity === 'mandatory'
                  ? 'amber'
                  : inv.severity === 'recommended'
                    ? 'cyan'
                    : 'neutral';

            return (
              <div
                key={inv.id}
                onClick={() => onSelectInvariant?.(inv.id)}
                className="p-3 bg-[#141b27] hover:bg-[#1a2233] border border-[#1e293b] rounded cursor-pointer transition-all hover:border-amber/50 space-y-1.5 shadow-xs"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono font-bold text-amber text-xs">{inv.id}</span>
                  <Badge tone={tone} outline>
                    {inv.severity || 'mandatory'}
                  </Badge>
                </div>

                <p className="text-slate-200 text-[11px] leading-relaxed font-sans">
                  {inv.statement}
                </p>

                <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono pt-1 border-t border-[#1e293b]">
                  <span className="truncate max-w-[240px]">{inv.adrId}: {inv.adrTitle}</span>
                  <span className="text-emerald flex items-center gap-0.5">
                    <CheckCircle2 className="w-2.5 h-2.5" />
                    Active
                  </span>
                </div>
              </div>
            );
          })}

          {filtered.length === 0 && (
            <div className="text-center py-8 text-slate-500 font-mono text-xs">
              No matching architectural invariants found.
            </div>
          )}
        </div>
      </div>
    </Drawer>
  );
};

export default InvariantDrawer;
