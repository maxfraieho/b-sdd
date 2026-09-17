/* =========================================================
   DRAKON SVG mock renderer
   Renders a DrakonWidget-compatible diagram as sharp SVG.
   Adheres to the 4 canonical rules: vertical skewer,
   right-is-worse, zero crossings, silhouette.
   ========================================================= */
window.DrakonMock = (function () {
  // Node styling per type — Astryx semantic colors
  const TYPE_STYLE = {
    branch:   { fill: 'rgba(167,139,250,0.10)', stroke: '#a78bfa', textColor: '#e2e8f0', shape: 'header' },
    action:   { fill: 'rgba(16,185,129,0.06)',  stroke: '#10b981', textColor: '#e2e8f0', shape: 'rect' },
    question: { fill: 'rgba(245,158,11,0.06)',  stroke: '#f59e0b', textColor: '#e2e8f0', shape: 'hex' },
    end:      { fill: 'rgba(244,63,94,0.08)',   stroke: '#f43f5e', textColor: '#e2e8f0', shape: 'rounded' },
    select:   { fill: 'rgba(6,182,212,0.06)',   stroke: '#06b6d4', textColor: '#e2e8f0', shape: 'trapezoid' },
    process:  { fill: 'rgba(148,163,184,0.06)', stroke: '#94a3b8', textColor: '#e2e8f0', shape: 'rect-double' },
    insertion:{ fill: 'rgba(148,163,184,0.04)', stroke: '#64748b', textColor: '#94a3b8', shape: 'rect-dashed' },
    comment:  { fill: 'transparent',            stroke: '#64748b', textColor: '#94a3b8', shape: 'note' },
  };

  const NODE_W = 260;
  const NODE_H = 56;
  const COL_GAP = 140;
  const ROW_GAP = 32;
  const PAD_X = 60;
  const PAD_Y = 40;

  /**
   * Layout the diagram on a virtual grid using x/y column coordinates
   * derived from the items graph. This mimics the vertical skewer
   * with right-is-worse branches.
   */
  function layout(diagram) {
    const items = diagram.items || {};
    const positions = {};
    // Find the entry via branch b0.one
    const entryId = items.b0 ? items.b0.one : Object.keys(items)[0];
    // Traverse main "down" chain
    let mainY = 0;
    const visited = new Set();
    const stack = [{ id: entryId, col: 0 }];
    while (stack.length) {
      const { id, col } = stack.shift();
      if (!id || visited.has(id) || !items[id]) continue;
      visited.add(id);
      positions[id] = { col, row: mainY };
      mainY += 1;
      const it = items[id];
      // main line first
      if (it.one) stack.unshift({ id: it.one, col });
      // right branch (question 'two')
      if (it.two && !positions[it.two]) {
        // place right branch at col+1, same row as source
        // find later — we'll fix after
      }
    }
    // Second pass: assign right-branch positions relative to their parent
    Object.keys(items).forEach((id) => {
      const it = items[id];
      if (it.two && positions[id] && positions[it.two] === undefined) {
        positions[it.two] = { col: positions[id].col + 1, row: positions[id].row };
        // then its children flow downward in that column
        let curId = items[it.two].one;
        let curRow = positions[it.two].row + 1;
        while (curId && !positions[curId] && items[curId]) {
          positions[curId] = { col: positions[it.two].col, row: curRow };
          curId = items[curId].one;
          curRow += 1;
        }
      }
    });
    return { positions, entryId };
  }

  function renderNodeShape(x, y, w, h, style) {
    switch (style.shape) {
      case 'hex': {
        const inset = 14;
        return `<polygon points="${x + inset},${y} ${x + w - inset},${y} ${x + w},${y + h / 2} ${x + w - inset},${y + h} ${x + inset},${y + h} ${x},${y + h / 2}" fill="${style.fill}" stroke="${style.stroke}" stroke-width="1.5"/>`;
      }
      case 'rounded':
        return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="24" fill="${style.fill}" stroke="${style.stroke}" stroke-width="1.5"/>`;
      case 'header':
        return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="4" fill="${style.fill}" stroke="${style.stroke}" stroke-width="1.5"/>`;
      case 'trapezoid': {
        const inset = 16;
        return `<polygon points="${x + inset},${y} ${x + w - inset},${y} ${x + w},${y + h} ${x},${y + h}" fill="${style.fill}" stroke="${style.stroke}" stroke-width="1.5"/>`;
      }
      case 'rect-double':
        return `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${style.fill}" stroke="${style.stroke}" stroke-width="1.5"/>
                <line x1="${x + 6}" y1="${y}" x2="${x + 6}" y2="${y + h}" stroke="${style.stroke}" stroke-width="1"/>
                <line x1="${x + w - 6}" y1="${y}" x2="${x + w - 6}" y2="${y + h}" stroke="${style.stroke}" stroke-width="1"/>`;
      case 'rect-dashed':
        return `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${style.fill}" stroke="${style.stroke}" stroke-width="1.5" stroke-dasharray="4 3"/>`;
      case 'note':
        return `<path d="M ${x} ${y} L ${x + w - 10} ${y} L ${x + w} ${y + 10} L ${x + w} ${y + h} L ${x} ${y + h} Z" fill="${style.fill}" stroke="${style.stroke}" stroke-width="1"/>`;
      default:
        return `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${style.fill}" stroke="${style.stroke}" stroke-width="1.5"/>`;
    }
  }

  /**
   * Render the diagram to an SVG string.
   * @param diagram DrakonWidget-format diagram
   * @param opts { selectedId, activeSocketType }
   */
  function render(diagram, opts = {}) {
    const items = diagram.items || {};
    const { positions, entryId } = layout(diagram);
    if (!Object.keys(positions).length) return '';

    let maxCol = 0, maxRow = 0;
    Object.values(positions).forEach((p) => { maxCol = Math.max(maxCol, p.col); maxRow = Math.max(maxRow, p.row); });
    const width = PAD_X * 2 + (maxCol + 1) * NODE_W + maxCol * COL_GAP;
    const height = PAD_Y * 2 + (maxRow + 1) * (NODE_H + ROW_GAP);

    // Header (silhouette branch cap)
    let out = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" width="${width}" height="${height}" style="display:block;background:#090d13;">
      <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
          <path d="M0,0 L10,5 L0,10 Z" fill="#334155"/>
        </marker>
        <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
          <path d="M 24 0 L 0 0 0 24" fill="none" stroke="#0f172a" stroke-width="0.5"/>
        </pattern>
      </defs>
      <rect width="${width}" height="${height}" fill="url(#grid)"/>`;

    // ---- Silhouette root branch bar (top) ----
    if (items.b0 && positions[entryId]) {
      const e = positions[entryId];
      const barX = PAD_X + e.col * (NODE_W + COL_GAP);
      const barY = PAD_Y - 24;
      out += `<rect x="${barX}" y="${barY}" width="${NODE_W}" height="16" fill="#0d121c" stroke="#a78bfa" stroke-width="1"/>`;
      out += `<text x="${barX + NODE_W / 2}" y="${barY + 11}" font-family="JetBrains Mono, monospace" font-size="9" letter-spacing="1.5" text-anchor="middle" fill="#a78bfa">▼ ${items.b0.content}</text>`;
    }

    // ---- Edges (draw before nodes so nodes overlap) ----
    Object.keys(items).forEach((id) => {
      const it = items[id];
      if (!positions[id]) return;
      const from = positions[id];
      const fx = PAD_X + from.col * (NODE_W + COL_GAP) + NODE_W / 2;
      const fy = PAD_Y + from.row * (NODE_H + ROW_GAP) + NODE_H;
      // down edge
      if (it.one && positions[it.one]) {
        const to = positions[it.one];
        const tx = PAD_X + to.col * (NODE_W + COL_GAP) + NODE_W / 2;
        const ty = PAD_Y + to.row * (NODE_H + ROW_GAP);
        if (from.col === to.col) {
          out += `<line x1="${fx}" y1="${fy}" x2="${tx}" y2="${ty}" stroke="#334155" stroke-width="1.4" marker-end="url(#arrow)"/>`;
        } else {
          // orthogonal L shape
          const midY = fy + 10;
          out += `<polyline points="${fx},${fy} ${fx},${midY} ${tx},${midY} ${tx},${ty}" fill="none" stroke="#334155" stroke-width="1.4" marker-end="url(#arrow)"/>`;
        }
      }
      // right (question 'two') edge — dashed rose
      if (it.two && positions[it.two]) {
        const to = positions[it.two];
        const sx = PAD_X + from.col * (NODE_W + COL_GAP) + NODE_W;
        const sy = PAD_Y + from.row * (NODE_H + ROW_GAP) + NODE_H / 2;
        const tx = PAD_X + to.col * (NODE_W + COL_GAP);
        const ty = PAD_Y + to.row * (NODE_H + ROW_GAP) + NODE_H / 2;
        out += `<line x1="${sx}" y1="${sy}" x2="${tx}" y2="${ty}" stroke="#f43f5e" stroke-width="1.2" stroke-dasharray="4 3" marker-end="url(#arrow)"/>`;
        // "ні" label
        out += `<text x="${(sx + tx) / 2}" y="${sy - 6}" font-family="JetBrains Mono, monospace" font-size="9" fill="#f43f5e" text-anchor="middle">ні · no</text>`;
      }
    });

    // ---- Nodes ----
    Object.keys(items).forEach((id) => {
      const it = items[id];
      if (!positions[id] || id === 'b0') return;
      const p = positions[id];
      const x = PAD_X + p.col * (NODE_W + COL_GAP);
      const y = PAD_Y + p.row * (NODE_H + ROW_GAP);
      const style = TYPE_STYLE[it.type] || TYPE_STYLE.action;
      const isSelected = opts.selectedId === id;

      // socket highlight on all matching type when a palette icon is active
      const socketHighlight = opts.activeSocketType === it.type;

      out += `<g class="drakon-node" data-node-id="${id}" style="cursor:pointer;">`;
      if (isSelected) {
        out += `<rect x="${x - 4}" y="${y - 4}" width="${NODE_W + 8}" height="${NODE_H + 8}" fill="none" stroke="#f59e0b" stroke-width="1.5" stroke-dasharray="3 3"/>`;
      }
      if (socketHighlight) {
        out += `<rect x="${x - 2}" y="${y - 2}" width="${NODE_W + 4}" height="${NODE_H + 4}" fill="rgba(6,182,212,0.12)" stroke="#06b6d4" stroke-width="1" stroke-dasharray="2 2"/>`;
      }
      out += renderNodeShape(x, y, NODE_W, NODE_H, style);

      // Content text (wrapped to 2 lines)
      const content = String(it.content || '');
      const words = content.split(' ');
      let line1 = '', line2 = '';
      for (const w of words) {
        if ((line1 + ' ' + w).length < 34) line1 += (line1 ? ' ' : '') + w;
        else line2 += (line2 ? ' ' : '') + w;
      }
      if (line2.length > 34) line2 = line2.slice(0, 32) + '…';

      out += `<text x="${x + NODE_W / 2}" y="${y + (line2 ? 22 : 30)}" font-family="Inter, system-ui" font-size="12" font-weight="500" fill="${style.textColor}" text-anchor="middle">${escapeXml(line1)}</text>`;
      if (line2) {
        out += `<text x="${x + NODE_W / 2}" y="${y + 38}" font-family="Inter, system-ui" font-size="12" font-weight="500" fill="${style.textColor}" text-anchor="middle">${escapeXml(line2)}</text>`;
      }
      // Secondary tag (invariant binding)
      if (it.secondary) {
        out += `<text x="${x + NODE_W - 8}" y="${y - 6}" font-family="JetBrains Mono, monospace" font-size="9" fill="#f59e0b" text-anchor="end" letter-spacing="0.5">${escapeXml(it.secondary)}</text>`;
      }
      out += `</g>`;
    });

    out += `</svg>`;
    return out;
  }

  function escapeXml(s) {
    return String(s).replace(/[<>&"']/g, (c) => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;', "'": '&apos;' }[c]));
  }

  return { render };
})();
