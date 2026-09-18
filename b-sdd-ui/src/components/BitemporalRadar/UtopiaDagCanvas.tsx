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
import { Network, Database, Layers, RefreshCw } from 'lucide-react';

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
  const containerRef = useRef<HTMLDivElement | null>(null);

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

  // Compute 2D planar positions along the DAG skewer
  const layout = useMemo(() => {
    const nodeMap = new Map<string, DagNode>();
    const nodeWidth = 140;
    const nodeHeight = 52;
    const spacingX = 180;
    const rowHeight = 70;

    dbNodes.forEach((n, idx) => {
      // Deterministic layout: alternate slight row offsets to maintain clean planarity
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

  return (
    <div
      ref={containerRef}
      className="relative flex-1 h-full overflow-x-auto overflow-y-hidden select-none bg-[#0a0f18]"
      style={{ scrollbarWidth: 'thin' }}
    >
      {/* Topology Status Overlay */}
      <div className="absolute top-2 left-3 z-10 flex items-center gap-2 px-2 py-0.5 rounded bg-[#101725]/80 border border-[#1e293b] backdrop-blur-sm">
        <Database className={`w-3 h-3 ${liveDbConnected ? 'text-emerald-400' : 'text-amber-400'}`} />
        <span className="text-[10px] font-mono text-slate-300">
          Utopia DB DAG {liveDbConnected ? '(:9922 Live)' : '(Local Cache)'}
        </span>
        <span className="text-slate-600">|</span>
        <span className="text-[10px] font-mono text-cyan-400">
          Nodes: {dbNodes.length} · Edges: {dbEdges.length}
        </span>
        {loading && <RefreshCw className="w-2.5 h-2.5 animate-spin text-amber-400" />}
      </div>

      {/* Interactive SVG DAG Canvas */}
      <svg
        className="w-full h-full min-w-[800px]"
        style={{ width: layout.totalWidth, height: 168 }}
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
          <linearGradient id="edge-grad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#1e293b" />
            <stop offset="100%" stopColor="#3b82f6" />
          </linearGradient>
        </defs>

        {/* Directed Edges */}
        {dbEdges.map((edge, i) => {
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

          // Smooth curved bezier spline between DAG nodes
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

        {/* DAG Nodes */}
        {layout.positionedNodes.map((node) => {
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
              {/* Node Card Rectangle */}
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

              {/* Node Header (ID + Status) */}
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

              {/* Status Badge */}
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

              {/* Node Title (truncated) */}
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
      </svg>
    </div>
  );
};

export default UtopiaDagCanvas;
