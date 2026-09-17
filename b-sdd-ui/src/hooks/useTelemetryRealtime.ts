// src/hooks/useTelemetryRealtime.ts
// Realtime hook for streaming B-SDD telemetry and compiler SLA vitals (ADR-012)
import { useState, useEffect, useCallback, useRef } from 'react';
import type { TelemetrySummaryResponse } from '@/lib/backend-types';
import { getTelemetry, subscribeRealtimeTelemetry } from '@/lib/api';

export function useTelemetryRealtime() {
  const [telemetry, setTelemetry] = useState<TelemetrySummaryResponse | null>(null);
  const [isLive, setIsLive] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const isMountedRef = useRef(true);

  const refresh = useCallback(async () => {
    try {
      const data = await getTelemetry();
      if (isMountedRef.current) {
        setTelemetry(data);
        setError(null);
      }
    } catch (e: any) {
      if (isMountedRef.current) {
        setError(e?.message || 'Failed to fetch telemetry');
      }
    }
  }, []);

  useEffect(() => {
    isMountedRef.current = true;
    refresh();

    const unsubscribe = subscribeRealtimeTelemetry(
      (data) => {
        if (isMountedRef.current) {
          setTelemetry(data);
          setIsLive(true);
          setError(null);
        }
      },
      () => {
        if (isMountedRef.current) {
          setIsLive(false);
        }
      },
    );

    return () => {
      isMountedRef.current = false;
      unsubscribe();
    };
  }, [refresh]);

  return { telemetry, isLive, error, refresh };
}
