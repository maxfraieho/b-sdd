// src/components/CopilotPanel/ContextBadges.tsx
// Astryx-native Context Badges (ADR-009)
import React from 'react';
import { Plus, FileText, Network, CheckSquare, GitPullRequest } from 'lucide-react';
import { Badge } from '@/components/astryx/primitives';

interface ContextBadgesProps {
  onAttach: (contextType: string) => void;
  attachedContexts: string[];
}

export const ContextBadges: React.FC<ContextBadgesProps> = ({
  onAttach,
  attachedContexts,
}) => {
  const badges = [
    { id: 'adr', label: 'Active ADR (ADR-008)', icon: <FileText className="w-3 h-3" /> },
    { id: 'drakon', label: 'DRAKON-IR Schema', icon: <Network className="w-3 h-3" /> },
    { id: 'pytest', label: 'Pytest 25/25 Report', icon: <CheckSquare className="w-3 h-3" /> },
    { id: 'gitnexus', label: 'GitNexus AST Graph', icon: <GitPullRequest className="w-3 h-3" /> },
  ];

  return (
    <div className="flex flex-wrap items-center gap-1.5 py-1">
      <span className="text-[10px] font-mono text-slate-500 uppercase mr-1">Inject:</span>
      {badges.map((badge) => {
        const isAttached = attachedContexts.includes(badge.id);

        return (
          <button
            key={badge.id}
            onClick={() => onAttach(badge.id)}
            className="cursor-pointer"
          >
            <Badge
              tone={isAttached ? 'amber' : 'neutral'}
              outline={!isAttached}
              className="gap-1.5 px-2 py-1 text-[11px] transition-colors hover:border-amber/50"
            >
              <Plus className={`w-2.5 h-2.5 ${isAttached ? 'rotate-45 text-amber' : 'text-slate-400'}`} />
              {badge.icon}
              <span>{badge.label}</span>
            </Badge>
          </button>
        );
      })}
    </div>
  );
};
