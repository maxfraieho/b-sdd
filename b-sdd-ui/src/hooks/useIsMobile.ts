import { useState, useEffect } from 'react';

/**
 * Reactive hook returning true when viewport width is below breakpoint (default: 768px).
 * Handles window resize and SSR safely.
 */
export function useIsMobile(breakpoint = 768): boolean {
  const [isMobile, setIsMobile] = useState<boolean>(() => {
    if (typeof window !== 'undefined') {
      return window.innerWidth < breakpoint;
    }
    return false;
  });

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < breakpoint);
    };
    window.addEventListener('resize', handleResize);
    handleResize();
    return () => window.removeEventListener('resize', handleResize);
  }, [breakpoint]);

  return isMobile;
}
