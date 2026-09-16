// src/hooks/useLiveData.ts
//
// Reusable React 19 hook that polls a fetchWithFallback-based endpoint on a
// configurable cadence and exposes {data, isLive, error, refresh}. All
// callers get automatic offline degradation to the fallback snapshot.

import { useCallback, useEffect, useRef, useState } from 'react';

export interface UseLiveDataOptions<T> {
  readonly fetcher: () => Promise<{ data: T; live: boolean }>;
  readonly fallback: T;
  /** Poll interval in ms. 0 = fetch once, never refresh. */
  readonly pollMs?: number;
  /** Deps that should cancel and re-fetch (e.g. slider position). */
  readonly deps?: readonly unknown[];
}

export interface LiveData<T> {
  readonly data: T;
  readonly isLive: boolean;
  readonly error: Error | null;
  readonly lastFetchedAt: number | null;
  readonly refresh: () => void;
}

export function useLiveData<T>({
  fetcher,
  fallback,
  pollMs = 0,
  deps = [],
}: UseLiveDataOptions<T>): LiveData<T> {
  const [data, setData] = useState<T>(fallback);
  const [isLive, setIsLive] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [lastFetchedAt, setLastFetchedAt] = useState<number | null>(null);
  const [tick, setTick] = useState(0);

  const fetcherRef = useRef(fetcher);
  fetcherRef.current = fetcher;

  const run = useCallback(async () => {
    try {
      const result = await fetcherRef.current();
      setData(result.data);
      setIsLive(result.live);
      setError(null);
      setLastFetchedAt(Date.now());
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)));
      setIsLive(false);
    }
  }, []);

  // Initial fetch + reactive to deps.
  useEffect(() => {
    void run();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [run, tick, ...deps]);

  // Polling loop.
  useEffect(() => {
    if (!pollMs || pollMs <= 0) return;
    const id = window.setInterval(() => void run(), pollMs);
    return () => window.clearInterval(id);
  }, [pollMs, run]);

  const refresh = useCallback(() => setTick((n) => n + 1), []);

  return { data, isLive, error, lastFetchedAt, refresh };
}
