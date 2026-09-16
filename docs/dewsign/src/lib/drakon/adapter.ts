// src/lib/drakon/adapter.ts
import type { DrakonWidget } from '@/types/drakonwidget';

let loadPromise: Promise<void> | null = null;

/**
 * Dynamically loads /libs/drakonwidget.js script.
 * Resolves when window.createDrakonWidget is available.
 */
export function loadDrakonWidget(): Promise<void> {
  if (typeof window !== 'undefined' && window.createDrakonWidget) {
    return Promise.resolve();
  }
  if (loadPromise) return loadPromise;

  loadPromise = new Promise<void>((resolve, reject) => {
    const script = document.createElement('script');
    script.src = '/libs/drakonwidget.js';
    script.async = true;
    script.onload = () => {
      if (window.createDrakonWidget) {
        resolve();
      } else {
        reject(new Error('createDrakonWidget not found on window'));
      }
    };
    script.onerror = () => {
      loadPromise = null;
      reject(new Error('Failed to load /libs/drakonwidget.js'));
    };
    document.head.appendChild(script);
  });
  return loadPromise;
}

/**
 * Creates a new DrakonWidget instance.
 * loadDrakonWidget() must be called and awaited first.
 */
export function createWidget(): DrakonWidget {
  if (!window.createDrakonWidget) {
    throw new Error('DrakonWidget not loaded. Call loadDrakonWidget() first.');
  }
  return window.createDrakonWidget();
}
