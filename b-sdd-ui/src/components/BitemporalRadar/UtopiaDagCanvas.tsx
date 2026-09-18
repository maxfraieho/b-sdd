// src/components/BitemporalRadar/UtopiaDagCanvas.tsx
// -----------------------------------------------------------------------------
// ZONE D — Utopia DB Bitemporal DAG Canvas (ADR-013 / INV-012-04)
// Interactive SVG DAG visualization representing intent dependency topology
// and supersession chains. Scrubbing Valid Time (Tv) reactively highlights
// active decisions vs faded/pruned superseded nodes.
// Invariant FE-INV-01: Contained height, zero page scroll.
// -----------------------------------------------------------------------------
import React, { useEffect, useState, useMemo, useRef } from 'react';
import type { BitemporalAdr } from '@/types/adr';
import { Network, Database, Layers, RefreshCw, Share2, GitFork } from 'lucide-react';

interface DagNode {
  id: string;
  title: string;
  valid_from?: number;
  valid_to?: number | null;
  status: string;
  x?: number;
  y?: number;
}

interface DagEdge {
  source: string;
  target: string;
  type: string;
}

interface CrossRepoEdge {
  source_workspace: string;
  source_file: string;
  source_symbol: string;
  target_workspace: string;
  target_file: string;
  target_symbol: string;
  rel_type: string;
  tx_time: number;
  valid_from: number;
}

interface UtopiaDagCanvasProps {
  validTimeDay: number;
  adrs: BitemporalAdr[];
  selectedAdrId?: string;
  onSelectAdr: (adr: BitemporalAdr) => void;
}

export const UtopiaDagCanvas: React.FC<UtopiaDagCanvasProps> = ({
  validTimeDay,
  adrs,
  selectedAdrId,
  onSelectAdr,
}) => {
  const [dbNodes, setDbNodes] = useState<DagNode[]>([]);
  const [dbEdges, setDbEdges] = useState<DagEdge[]>([]);
  const [loading, setLoading] = useState(false);
  const [liveDbConnected, setLiveDbConnected] = useState(true);
  const [viewMode, setViewMode] = useState<'adrs' | 'federation'>('adrs');
  const [crossEdges, setCrossEdges] = useState<CrossRepoEdge[]>([]);
  const containerRef = useRef<HTMLDivElement | null>(null);

  const fetchFederation = async () => {
    try {
      const resp = await fetch('/api/graph/cross-repo-edges');
      if (resp.ok) {
        const data = await resp.json();
        setCrossEdges(data.cross_repo_edges || []);
      }
    } catch {
      // Ignore
    }
  };

  useEffect(() => {
    fetchFederation();
  }, []);

  // Fetch from Utopia DB DAG endpoint or fallback to props
  useEffect(() => {
    let cancelled = false;
    const fetchGraph = async () => {
      setLoading(true);
      try {
        const resp = await fetch(`/api/utopia/graph?valid_time_day=${validTimeDay}`);
        if (resp.ok) {
          const data = await resp.json();
          if (!cancelled && data.nodes) {
            setDbNodes(data.nodes);
            setDbEdges(data.edges || []);
            setLiveDbConnected(true);
            setLoading(false);
            return;
          }
        }
      } catch {
        // Fallback to local props
      }

      if (!cancelled) {
        setLiveDbConnected(false);
        // Synthesize graph from adrs props with Tv filtering
        const filtered = adrs
          .filter((a) => {
            const num = parseInt(a.id.replace(/\D/g, '') || '1', 10);
            return num <= validTimeDay;
          })
          .map((a) => {
            const isSup = a.status === 'superseded';
            return {
              id: a.id,
              title: a.title,
              status: isSup ? 'superseded' : 'accepted',
            };
          });

        const edges: DagEdge[] = [];
        for (let i = 1; i < filtered.length; i++) {
          edges.push({
            source: filtered[i].id,
            target: filtered[i - 1].id,
            type: filtered[i].status === 'superseded' ? 'supersedes' : 'depends-on',
          });
        }
        setDbNodes(filtered);
        setDbEdges(edges);
        setLoading(false);
      }
    };

    fetchGraph();
    return () => {
      cancelled = true;
    };
  }, [validTimeDay, adrs]);

  // Compute 2D planar positions along the DAG skewer for ADRs
  const layout = useMemo(() => {
    const nodeMap = new Map<string, DagNode>();
    const nodeWidth = 140;
    const nodeHeight = 52;
    const spacingX = 180;
    const rowHeight = 70;

    dbNodes.forEach((n, idx) => {
      const col = idx;
      const row = idx % 2 === 0 ? 0 : 1;
      const x = 30 + col * spacingX;
      const y = 20 + row * rowHeight;
      nodeMap.set(n.id, { ...n, x, y });
    });

    const positionedNodes = Array.from(nodeMap.values());
    const totalWidth = Math.max(800, positionedNodes.length * spacingX + 100);

    return { positionedNodes, nodeMap, totalWidth, nodeWidth, nodeHeight };
  }, [dbNodes]);

  // Compute 2D planar layout for Cross-Repo Federation
  const fedLayout = useMemo(() => {
    const nodeMap = new Map<string, any>();
    const nodeWidth = 160;
    const nodeHeight = 56;
    const spacingX = 220;

    // Collect endpoints
    const nodeSet = new Map<string, { id: string; label: string; ws: string; sub: string }>();
    crossEdges.forEach((e) => {
      const srcId = `${e.source_workspace}:${e.source_file}`;
      if (!nodeSet.has(srcId)) {
        nodeSet.set(srcId, {
          id: srcId,
          label: e.source_symbol !== 'module' ? e.source_symbol : e.source_file.split('/').pop() || e.source_file,
          ws: e.source_workspace,
          sub: e.source_file,
        });
      }
      const tgtId = `${e.target_workspace}:${e.target_file}`;
      if (!nodeSet.has(tgtId)) {
        nodeSet.set(tgtId, {
          id: tgtId,
          label: e.target_symbol || e.target_file.split('/').pop() || e.target_file,
          ws: e.target_workspace,
          sub: e.target_file,
        });
      }
    });

    const nodesList = Array.from(nodeSet.values());
    nodesList.forEach((n, idx) => {
      const col = idx % 4;
      const row = Math.floor(idx / 4);
      const x = 30 + col * spacingX;
      const y = 25 + row * 80;
      nodeMap.set(n.id, { ...n, x, y });
    });

    const totalWidth = Math.max(850, Math.min(nodesList.length, 4) * spacingX + 150);
    return { nodes: Array.from(nodeMap.values()), nodeMap, totalWidth, nodeWidth, nodeHeight };
  }, [crossEdges]);

  return (
    <div
      ref={containerRef}
      className="relative flex-1 h-full overflow-x-auto overflow-y-hidden select-none bg-[#0a0f18]"
      style={{ scrollbarWidth: 'thin' }}
    >
      {/* Topology Status Overlay & View Mode Switcher */}
      <div className="absolute top-2 left-3 z-10 flex items-center gap-2 px-2 py-0.5 rounded bg-[#101725]/90 border border-[#1e293b] backdrop-blur-sm shadow-xs">
        <div className="flex items-center gap-1 bg-[#0c121e] p-0.5 rounded border border-[#1e293b]/70">
          <button
            onClick={() => setViewMode('adrs')}
            className={`px-2 py-0.5 rounded text-[10px] font-mono flex items-center gap-1 transition-colors cursor-pointer ${
              viewMode === 'adrs'
                ? 'bg-amber/20 text-amber font-semibold border border-amber/40'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Database className="w-2.5 h-2.5" />
            ADR DAG
          </button>
          <button
            onClick={() => {
              setViewMode('federation');
              fetchFederation();
            }}
            className={`px-2 py-0.5 rounded text-[10px] font-mono flex items-center gap-1 transition-colors cursor-pointer ${
              viewMode === 'federation'
                ? 'bg-cyan/20 text-cyan font-semibold border border-cyan/40'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Share2 className="w-2.5 h-2.5 text-cyan" />
            Крос-Репо ({crossEdges.length})
          </button>
        </div>

        <span className="text-slate-600">|</span>
        <span className="text-[10px] font-mono text-cyan-400">
          {viewMode === 'adrs'
            ? `Nodes: ${dbNodes.length} · Edges: ${dbEdges.length}`
            : `Cross-Edges: ${crossEdges.length} · Utopia Federated`}
        </span>
        {loading && <RefreshCw className="w-2.5 h-2.5 animate-spin text-amber-400" />}
      </div>

      {/* Interactive SVG DAG Canvas */}
      <svg
        className="w-full h-full min-w-[800px]"
        style={{ width: viewMode === 'adrs' ? layout.totalWidth : fedLayout.totalWidth, height: 168 }}
      >
        <defs>
          <marker
            id="dag-arrow-depends"
            markerWidth="8"
            markerHeight="8"
            refX="7"
            refY="3.5"
            orient="auto"
          >
            <polygon points="0 0, 8 3.5, 0 7" fill="#3b82f6" />
          </marker>
          <marker
            id="dag-arrow-supersedes"
            markerWidth="8"
            markerHeight="8"
            refX="7"
            refY="3.5"
            orient="auto"
          >
            <polygon points="0 0, 8 3.5, 0 7" fill="#f59e0b" />
          </marker>
          <marker
            id="dag-arrow-cross"
            markerWidth="8"
            markerHeight="8"
            refX="7"
            refY="3.5"
            orient="auto"
          >
            <polygon points="0 0, 8 3.5, 0 7" fill="#06b6d4" />
          </marker>
          <linearGradient id="edge-grad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#1e293b" />
            <stop offset="100%" stopColor="#3b82f6" />
          </linearGradient>
        </defs>

        {/* Directed Edges for ADR Mode */}
        {viewMode === 'adrs' &&
          dbEdges.map((edge, i) => {
            const s = layout.nodeMap.get(edge.source);
            const t = layout.nodeMap.get(edge.target);
            if (!s || !t || s.x === undefined || s.y === undefined || t.x === undefined || t.y === undefined) {
              return null;
            }

            const sx = s.x + layout.nodeWidth / 2;
            const sy = s.y + layout.nodeHeight / 2;
            const tx = t.x + layout.nodeWidth / 2;
            const ty = t.y + layout.nodeHeight / 2;

            const isSupersede = edge.type === 'supersedes';
            const strokeColor = isSupersede ? '#f59e0b' : '#3b82f6';
            const markerEnd = isSupersede ? 'url(#dag-arrow-supersedes)' : 'url(#dag-arrow-depends)';

            const dx = tx - sx;
            const pathD = `M ${sx} ${sy} C ${sx + dx * 0.4} ${sy}, ${tx - dx * 0.4} ${ty}, ${tx} ${ty}`;

            return (
              <g key={`edge-${i}`}>
                <path
                  d={pathD}
                  fill="none"
                  stroke={strokeColor}
                  strokeWidth={1.5}
                  strokeDasharray={isSupersede ? '4 3' : 'none'}
                  opacity={0.65}
                  markerEnd={markerEnd}
                />
              </g>
            );
          })}

        {/* Directed Edges for Cross-Repo Federation Mode */}
        {viewMode === 'federation' &&
          crossEdges.map((edge, i) => {
            const srcId = `${edge.source_workspace}:${edge.source_file}`;
            const tgtId = `${edge.target_workspace}:${edge.target_file}`;
            const s = fedLayout.nodeMap.get(srcId);
            const t = fedLayout.nodeMap.get(tgtId);
            if (!s || !t || s.x === undefined || s.y === undefined || t.x === undefined || t.y === undefined) {
              return null;
            }

            const sx = s.x + fedLayout.nodeWidth;
            const sy = s.y + fedLayout.nodeHeight / 2;
            const tx = t.x;
            const ty = t.y + fedLayout.nodeHeight / 2;

            const dx = tx - sx;
            const pathD = `M ${sx} ${sy} C ${sx + dx * 0.5} ${sy}, ${tx - dx * 0.5} ${ty}, ${tx} ${ty}`;

            return (
              <g key={`fed-edge-${i}`}>
                <path
                  d={pathD}
                  fill="none"
                  stroke="#06b6d4"
                  strokeWidth={1.5}
                  opacity={0.8}
                  markerEnd="url(#dag-arrow-cross)"
                />
              </g>
            );
          })}

        {/* ADR Nodes */}
        {viewMode === 'adrs' &&
          layout.positionedNodes.map((node) => {
            const isSelected = node.id === selectedAdrId;
            const isSuperseded = node.status === 'superseded';
            const nx = node.x ?? 0;
            const ny = node.y ?? 0;

            return (
              <g
                key={node.id}
                transform={`translate(${nx}, ${ny})`}
                className="cursor-pointer transition-transform hover:scale-105"
                onClick={() => {
                  const found = adrs.find((a) => a.id === node.id);
                  if (found) onSelectAdr(found);
                }}
              >
                <rect
                  width={layout.nodeWidth}
                  height={layout.nodeHeight}
                  rx={6}
                  fill={isSuperseded ? '#10141f' : '#141c2c'}
                  stroke={
                    isSelected
                      ? '#38bdf8'
                      : isSuperseded
                      ? '#64748b'
                      : '#1e293b'
                  }
                  strokeWidth={isSelected ? 2 : 1}
                  strokeDasharray={isSuperseded ? '3 3' : 'none'}
                  opacity={isSuperseded ? 0.6 : 1}
                />

                <text
                  x={10}
                  y={18}
                  fill={isSuperseded ? '#94a3b8' : '#38bdf8'}
                  fontSize={10}
                  fontFamily="monospace"
                  fontWeight="bold"
                  className={isSuperseded ? 'line-through' : ''}
                >
                  {node.id}
                </text>

                <rect
                  x={layout.nodeWidth - 52}
                  y={8}
                  width={44}
                  height={14}
                  rx={3}
                  fill={isSuperseded ? '#451a03' : '#064e3b'}
                />
                <text
                  x={layout.nodeWidth - 30}
                  y={18}
                  textAnchor="middle"
                  fill={isSuperseded ? '#f59e0b' : '#34d399'}
                  fontSize={8}
                  fontFamily="monospace"
                  fontWeight="600"
                >
                  {isSuperseded ? 'SUP' : 'ACT'}
                </text>

                <text
                  x={10}
                  y={38}
                  fill={isSuperseded ? '#64748b' : '#e2e8f0'}
                  fontSize={10}
                  fontFamily="sans-serif"
                  className={isSuperseded ? 'line-through' : ''}
                >
                  {node.title.length > 18 ? `${node.title.substring(0, 16)}…` : node.title}
                </text>
              </g>
            );
          })}

        {/* Federation Nodes */}
        {viewMode === 'federation' &&
          fedLayout.nodes.map((node) => {
            const nx = node.x ?? 0;
            const ny = node.y ?? 0;
            const isCore = node.ws === 'core';

            return (
              <g
                key={node.id}
                transform={`translate(${nx}, ${ny})`}
                className="cursor-pointer transition-transform hover:scale-105"
              >
                <rect
                  width={fedLayout.nodeWidth}
                  height={fedLayout.nodeHeight}
                  rx={6}
                  fill="#0e1726"
                  stroke={isCore ? '#06b6d4' : '#10b981'}
                  strokeWidth={1}
                />

                <rect
                  x={8}
                  y={8}
                  width={isCore ? 34 : 44}
                  height={14}
                  rx={3}
                  fill={isCore ? '#083344' : '#064e3b'}
                />
                <text
                  x={isCore ? 25 : 30}
                  y={18}
                  textAnchor="middle"
                  fill={isCore ? '#22d3ee' : '#34d399'}
                  fontSize={8}
                  fontFamily="monospace"
                  fontWeight="bold"
                >
                  {node.ws.toUpperCase()}
                </text>

                <text
                  x={isCore ? 48 : 58}
                  y={18}
                  fill="#f8fafc"
                  fontSize={10}
                  fontFamily="monospace"
                  fontWeight="bold"
                >
                  {node.label.length > 12 ? `${node.label.substring(0, 11)}…` : node.label}
                </text>

                <text
                  x={8}
                  y={40}
                  fill="#94a3b8"
                  fontSize={9}
                  fontFamily="sans-serif"
                >
                  {node.sub.length > 22 ? `…${node.sub.slice(-20)}` : node.sub}
                </text>
              </g>
            );
          })}

        {viewMode === 'federation' && fedLayout.nodes.length === 0 && (
          <text
            x="50%"
            y="50%"
            textAnchor="middle"
            fill="#64748b"
            fontSize={12}
            fontFamily="monospace"
          >
            Крос-репозиторні залежності не виявлено або воркспейси очікують індексації.
          </text>
        )}
      </svg>
    </div>
  );
};

export default UtopiaDagCanvas;
