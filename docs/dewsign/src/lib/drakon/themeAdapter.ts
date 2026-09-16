// src/lib/drakon/themeAdapter.ts
import type { DrakonConfigTheme } from '@/types/drakonwidget';

/**
 * Maps Swiss High-Tech Dark / Light palettes to DrakonWidget canvas theme.
 * Swiss Dark:
 * - Canvas Background: #070B12 (Deep black graphite)
 * - Icons Background: #162035 (Slate card fill)
 * - Icon Border: #24324D (Subtle border)
 * - Text color: #F8FAFC (Slate 50)
 * - Skewer & connectors: #3B82F6 / #10B981
 */
export function getSwissDrakonTheme(isDark = true): DrakonConfigTheme {
  if (isDark) {
    return {
      background: '#070B12',
      iconBack: '#162035',
      iconBorder: '#24324D',
      color: '#F8FAFC',
      lines: '#3B82F6', // Skewer blue
      lineWidth: 2,
      shadowColor: 'rgba(0, 0, 0, 0.6)',
      shadowBlur: 8,
      scrollBar: 'rgba(255, 255, 255, 0.15)',
      scrollBarHover: 'rgba(245, 158, 11, 0.4)', // Amber hover
      backText: '#94A3B8',
      icons: {
        header: {
          iconBack: '#1E293B',
          iconBorder: '#3B82F6',
          color: '#38BDF8',
        },
        action: {
          iconBack: '#162035',
          iconBorder: '#24324D',
          color: '#F8FAFC',
        },
        question: {
          iconBack: '#291805',
          iconBorder: '#F59E0B',
          color: '#FCD34D',
        },
        end: {
          iconBack: '#064E3B',
          iconBorder: '#10B981',
          color: '#6EE7B7',
        },
      },
    };
  }

  // High-contrast clean light fallback
  return {
    background: '#F1F5F9',
    iconBack: '#FFFFFF',
    iconBorder: '#CBD5E1',
    color: '#0F172A',
    lines: '#2563EB',
    lineWidth: 1.5,
    shadowColor: 'rgba(0, 0, 0, 0.1)',
    shadowBlur: 4,
    scrollBar: 'rgba(0, 0, 0, 0.2)',
    scrollBarHover: 'rgba(0, 0, 0, 0.4)',
    backText: '#64748B',
  };
}
