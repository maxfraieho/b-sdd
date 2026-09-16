// src/lib/sse.ts
//
// Real Server-Sent Events client for POST /api/copilot/proxy.
// Uses fetch + ReadableStreamDefaultReader because the standard EventSource
// only supports GET; our backend expects a JSON body with the prompt and slot.
//
// Wire format (text/event-stream, one event per blank-line-terminated block):
//     data: {"type":"token","delta":"import "}
//
//     data: {"type":"token","delta":"json"}
//
//     data: {"type":"done","total_tokens":42}
//
// On offline / HTTP error the caller receives an { type: 'error' } event and
// can decide whether to fall back to a simulated stream.

import { API_BASE_URL } from './api';
import type { CopilotProxyPayload, CopilotSseEvent } from './backend-types';

export interface SseHandlers {
  readonly onEvent: (event: CopilotSseEvent) => void;
  readonly onOpen?: () => void;
  readonly onClose?: (reason: 'done' | 'error' | 'abort') => void;
}

export interface SseHandle {
  /** Aborts the underlying fetch/reader. Safe to call multiple times. */
  readonly abort: () => void;
  /** Promise that resolves when the stream ends (any reason). */
  readonly done: Promise<'done' | 'error' | 'abort'>;
}

/**
 * Opens a POST-based SSE stream to the workbench server. Returns an SseHandle
 * so the caller can cancel mid-flight (needed for the Kill Stream button).
 */
export function openCopilotStream(
  payload: CopilotProxyPayload,
  handlers: SseHandlers,
): SseHandle {
  const controller = new AbortController();
  let closed = false;
  let closeReason: 'done' | 'error' | 'abort' = 'done';

  const done = (async (): Promise<'done' | 'error' | 'abort'> => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/copilot/proxy`, {
        method: 'POST',
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          Accept: 'text/event-stream',
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok || !res.body) {
        closeReason = 'error';
        handlers.onEvent({
          type: 'error',
          message: `HTTP ${res.status} ${res.statusText}`,
        });
        return closeReason;
      }

      handlers.onOpen?.();

      const reader = res.body.pipeThrough(new TextDecoderStream()).getReader();
      let buffer = '';

      while (!closed) {
        const { value, done: streamDone } = await reader.read();
        if (streamDone) break;

        buffer += value;

        // SSE frames are separated by a blank line. Split on double-newline.
        const parts = buffer.split(/\r?\n\r?\n/);
        buffer = parts.pop() ?? '';

        for (const rawFrame of parts) {
          const frame = rawFrame.trim();
          if (!frame) continue;

          // Each frame is one or more `field: value` lines. We only care about
          // the `data:` field, potentially concatenated across multiple lines.
          const dataLines = frame
            .split(/\r?\n/)
            .filter((line) => line.startsWith('data:'))
            .map((line) => line.slice(5).trimStart());

          if (dataLines.length === 0) continue;
          const payloadStr = dataLines.join('\n');

          if (payloadStr === '[DONE]') {
            handlers.onEvent({ type: 'done' });
            closeReason = 'done';
            closed = true;
            break;
          }

          try {
            const parsed = JSON.parse(payloadStr) as CopilotSseEvent;
            handlers.onEvent(parsed);
            if (parsed.type === 'done') {
              closeReason = 'done';
              closed = true;
              break;
            }
            if (parsed.type === 'error') {
              closeReason = 'error';
              closed = true;
              break;
            }
          } catch {
            // Frame wasn't JSON — treat the raw text as a plain token so the
            // UI keeps streaming instead of dying on a single malformed line.
            handlers.onEvent({ type: 'token', delta: payloadStr });
          }
        }
      }

      try {
        await reader.cancel();
      } catch {
        // ignore
      }
    } catch (err) {
      if (controller.signal.aborted) {
        closeReason = 'abort';
      } else {
        closeReason = 'error';
        handlers.onEvent({
          type: 'error',
          message: err instanceof Error ? err.message : String(err),
        });
      }
    } finally {
      closed = true;
      handlers.onClose?.(closeReason);
    }

    return closeReason;
  })();

  return {
    abort: () => {
      if (!closed) {
        closed = true;
        closeReason = 'abort';
        try {
          controller.abort();
        } catch {
          // ignore
        }
      }
    },
    done,
  };
}
