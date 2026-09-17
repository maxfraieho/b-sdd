/* =========================================================
   B-SDD Workbench · API layer
   Mirrors src/lib/api.ts fetchWithFallback contract.
   Attempts live http://localhost:8765 endpoints; falls back
   to in-memory mocks so the prototype works offline.
   ========================================================= */
window.BSDDApi = (function () {
  const BASE = 'http://localhost:8765';
  const TIMEOUT_MS = 800;

  async function fetchWithFallback(path, opts = {}, fallback) {
    if (window.__BSDD_FORCE_OFFLINE__) return fallback;
    try {
      const ctrl = new AbortController();
      const timer = setTimeout(() => ctrl.abort(), TIMEOUT_MS);
      const res = await fetch(BASE + path, {
        ...opts,
        signal: ctrl.signal,
        headers: { 'Content-Type': 'application/json', ...(opts.headers || {}) },
      });
      clearTimeout(timer);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (e) {
      // Silent fallback — prototype must stay usable
      return fallback;
    }
  }

  const B = window.BSDD;

  return {
    fetchWithFallback,
    getHealth:       ()          => fetchWithFallback('/api/health', {}, B.HEALTH),
    getActiveRules:  ()          => fetchWithFallback('/api/rules/active', {}, B.ACTIVE_RULES),
    getAdrs:         (tv, tt)    => fetchWithFallback(`/api/adrs?valid_time=${tv}&transaction_time=${tt}`, {}, { adrs: B.ADRS, total: B.ADRS.length }),
    getProjects:     ()          => fetchWithFallback('/api/projects', {}, { current_project: B.PROJECT, workspaces: [{ ...B.PROJECT, active: true }] }),
    getSpecs:        ()          => fetchWithFallback('/api/specs', {}, { total: B.SPECS.length, specs: B.SPECS }),
    getDrakonSchema: (specId)    => fetchWithFallback(`/api/drakon/schema?spec=${encodeURIComponent(specId)}`, {}, { diagram: B.DRAKON_DIAGRAM, validation: { is_valid: true, errors: [] } }),
    getSprintState:  ()          => fetchWithFallback('/api/sprint/state', {}, B.SPRINT_STATE),

    saveAdr: (filePath, content) =>
      fetchWithFallback('/api/adrs/save', { method: 'POST', body: JSON.stringify({ file_path: filePath, content }) }, { ok: true, path: filePath, bytes: content.length, recompiled: true }),

    saveDrakonSchema: (payload) =>
      fetchWithFallback('/api/drakon/schema', { method: 'POST', body: JSON.stringify(payload) }, { ok: true, validated: true, crossings: 0 }),

    submitReview: (payload) =>
      fetchWithFallback('/api/sprint/review', { method: 'POST', body: JSON.stringify(payload) }, { ok: true, decision: payload.decision }),

    toggleTask: (specId, taskId, completed) =>
      fetchWithFallback('/api/tasks/toggle', { method: 'POST', body: JSON.stringify({ spec_id: specId, task_id: taskId, completed }) }, { ok: true }),

    syncUtopia: () =>
      fetchWithFallback('/api/sync/utopia', { method: 'POST', body: '{}' }, { ok: true, synced: 8, latency_ms: 1247 }),

    copilotProxy: (message, slotId) =>
      fetchWithFallback('/api/copilot/proxy', { method: 'POST', body: JSON.stringify({ message, slot_id: slotId }) }, { ok: true, response: 'Fallback: mock LLM response' }),
  };
})();
