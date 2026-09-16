// src/hooks/useCopilotStream.ts
//
// Wraps openCopilotStream() in React state: exposes {streamingText, isStreaming,
// error, start, abort}. On backend error, we surface an Error object and let
// the caller decide whether to fall back to a simulated stream (offline mode).

import { useCallback, useEffect, useRef, useState } from 'react';
import { openCopilotStream } from '@/lib/sse';
import type { SseHandle } from '@/lib/sse';
import type { CopilotProxyPayload } from '@/lib/backend-types';

export interface CopilotStreamState {
  readonly streamingText: string;
  readonly isStreaming: boolean;
  readonly error: Error | null;
  readonly totalTokens: number;
  readonly start: (payload: CopilotProxyPayload) => void;
  readonly abort: () => void;
}

export function useCopilotStream(): CopilotStreamState {
  const [streamingText, setStreamingText] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [totalTokens, setTotalTokens] = useState(0);
  const handleRef = useRef<SseHandle | null>(null);

  const abort = useCallback(() => {
    handleRef.current?.abort();
    handleRef.current = null;
  }, []);

  const start = useCallback((payload: CopilotProxyPayload) => {
    handleRef.current?.abort();
    setStreamingText('');
    setError(null);
    setTotalTokens(0);
    setIsStreaming(true);

    handleRef.current = openCopilotStream(payload, {
      onEvent: (evt) => {
        switch (evt.type) {
          case 'token':
            setStreamingText((prev) => prev + evt.delta);
            break;
          case 'done':
            setIsStreaming(false);
            if (typeof evt.total_tokens === 'number') setTotalTokens(evt.total_tokens);
            break;
          case 'error':
            setError(new Error(evt.message));
            setIsStreaming(false);
            break;
          case 'meta':
            // meta events currently informational only.
            break;
        }
      },
      onClose: (reason) => {
        setIsStreaming(false);
        if (reason === 'abort') {
          setError(new Error('Stream aborted by operator'));
        }
      },
    });
  }, []);

  // Cleanup on unmount.
  useEffect(() => () => handleRef.current?.abort(), []);

  return { streamingText, isStreaming, error, totalTokens, start, abort };
}
