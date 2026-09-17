// src/hooks/usePhaseRealtime.ts
//
// React hook for subscribing to Appwrite BaaS & B-SDD Realtime Phase Events (ADR-011).
// Provides live phase transitions via Server-Sent Events (SSE) with automatic reconnection.
//
import { useState, useEffect, useCallback } from 'react';
import { subscribeRealtimePhases, setSprintPhase } from '@/lib/api';
import type { PhaseTransitionEvent } from '@/lib/backend-types';

interface UsePhaseRealtimeOptions {
  readonly onTransition?: (event: PhaseTransitionEvent) => void;
}

export function usePhaseRealtime(options: UsePhaseRealtimeOptions = {}) {
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [lastEvent, setLastEvent] = useState<PhaseTransitionEvent | null>(null);

  useEffect(() => {
    const unsubscribe = subscribeRealtimePhases(
      (event) => {
        setIsConnected(true);
        setLastEvent(event);
        if (options.onTransition) {
          options.onTransition(event);
        }
      },
      () => {
        setIsConnected(false);
      },
    );

    return () => {
      unsubscribe();
    };
  }, [options.onTransition]);

  const advancePhase = useCallback(async (phaseId: string, signature?: string) => {
    try {
      const res = await setSprintPhase(phaseId, signature);
      return res;
    } catch (err) {
      console.warn('[usePhaseRealtime] Failed to transition phase:', err);
      throw err;
    }
  }, []);

  return {
    isConnected,
    lastEvent,
    advancePhase,
  };
}
