// src/components/ds/MobileTabBar.tsx
//
// Mobile-only bottom tab bar — an app-style navigation rail.
// Desktop keeps the browser-chrome nav capsules in TopNavigation; on
// narrow viewports those hide (see MainLayout) and this bar is the only
// primary navigation. It participates in MainLayout's flex flow so page
// content ends above it instead of scrolling beneath an overlay.
//
// Shows the four primary content destinations in a stable order, with a
// compact "More" tab for utilities that should not compete with page hops.
import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence, useReducedMotion } from 'framer-motion';
import {
  Home,
  Briefcase,
  Aperture,
  BookOpen,
  MoreHorizontal,
  X,
  Globe,
  Moon,
  Sun,
} from 'lucide-react';
import { useLanguage } from '../LanguageContext';
import { useTheme } from '../ThemeContext';
import { cn } from '../../lib/utils';
import { dsRoot } from './dsAttr';
import { canonicalInternalPath, isNavigationPathActive } from '../../utils/navigation';

interface TabRoute {
  path: string;
  label: string;
  icon: React.ReactNode;
}

// The content destinations that stay pinned in the dock.
const PRIMARY_ROUTES = (zh: boolean): TabRoute[] => [
  { path: '/', label: zh ? '主页' : 'Home', icon: <Home size={20} strokeWidth={2} /> },
  { path: '/moments', label: zh ? '瞬间' : 'Moments', icon: <Aperture size={20} strokeWidth={2} /> },
  { path: '/blog', label: zh ? '博客' : 'Blog', icon: <BookOpen size={20} strokeWidth={2} /> },
  { path: '/projects', label: zh ? '项目' : 'Projects', icon: <Briefcase size={20} strokeWidth={2} /> },
];

// Everything else, revealed through the "More" sheet. Currently empty
// (contact page disabled 2026-08) — the sheet still carries the language
// and theme switches, so the More button stays.
const MORE_ROUTES = (): TabRoute[] => [
  // { path: '/contact', label: zh ? '联系' : 'Contact', icon: <Mail size={18} strokeWidth={2} /> },
];

/** One stable tab slot shared by destinations and the More utility. */
const TabSlot: React.FC<{
  route: TabRoute;
  active: boolean;
  current?: boolean;
  onClick: () => void;
  reduceMotion: boolean | null;
  expanded?: boolean;
  hasPopup?: boolean;
}> = ({ route, active, current = active, onClick, reduceMotion, expanded, hasPopup = false }) => (
  <button
    type="button"
    aria-label={route.label}
    aria-current={current ? 'page' : undefined}
    aria-expanded={hasPopup ? expanded : undefined}
    aria-haspopup={hasPopup ? 'menu' : undefined}
    onClick={onClick}
    className="relative flex min-h-[3.5rem] min-w-0 flex-1 flex-col items-center justify-center gap-0.5 rounded-ds-lg px-1 py-1 transition-transform duration-ds-fast active:scale-[0.96]"
  >
    <span
      className={cn(
        'relative flex h-7 w-11 items-center justify-center rounded-full transition-colors duration-ds-fast',
        active ? 'text-ds-primary' : 'text-ds-fg-subtle',
      )}
    >
      {active && (
        <motion.span
          layoutId={reduceMotion ? undefined : 'mobile-tab-active-pill'}
          className="absolute inset-0 rounded-full bg-ds-primary-soft"
          transition={{ type: 'spring', stiffness: 420, damping: 34 }}
        />
      )}
      <span className="relative z-10">{route.icon}</span>
    </span>
    <span
      className={cn(
        'max-w-full truncate text-[11px] font-medium leading-none tracking-[-0.01em] transition-colors duration-ds-fast',
        active ? 'text-ds-primary' : 'text-ds-fg-muted',
      )}
    >
      {route.label}
    </span>
  </button>
);

export const MobileTabBar: React.FC = () => {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const { language, languageHref, selectLanguage } = useLanguage();
  const { isDarkMode, toggleTheme } = useTheme();
  const reduceMotion = useReducedMotion();
  const zh = language === 'zh';
  const targetLanguage = zh ? 'en' : 'zh';
  const [moreOpen, setMoreOpen] = useState(false);

  const primaryRoutes = PRIMARY_ROUTES(zh);
  const moreRoutes = MORE_ROUTES();
  const moreActive = moreRoutes.some((r) => isNavigationPathActive(pathname, r.path));
  const moreRoute: TabRoute = {
    path: '#more',
    label: zh ? '更多' : 'More',
    icon: moreOpen
      ? <X size={20} strokeWidth={2} />
      : <MoreHorizontal size={20} strokeWidth={2} />,
  };

  // Close the sheet on navigation (own route change, not just More items).
  useEffect(() => setMoreOpen(false), [pathname]);

  return (
    <>
      <AnimatePresence>
        {moreOpen && (
          <>
            <motion.button
              type="button"
              aria-label={zh ? '关闭更多菜单' : 'Close more menu'}
              className="fixed inset-0 z-40 bg-black/20 sm:hidden"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.16 }}
              onClick={() => setMoreOpen(false)}
            />
            <motion.div
              {...dsRoot}
              role="menu"
              aria-label={zh ? '更多页面' : 'More pages'}
              // The utility sheet grows from the More slot instead of the
              // screen centre, preserving the spatial relationship between
              // trigger and result.
              className="fixed bottom-[calc(4.75rem+env(safe-area-inset-bottom))] right-3 z-50 w-56 origin-bottom-right rounded-ds-xl border border-ds-border bg-ds-surface-1 p-1.5 shadow-ds-3 sm:hidden"
              initial={reduceMotion ? { opacity: 0 } : { opacity: 0, y: 6, scale: 0.95 }}
              animate={reduceMotion ? { opacity: 1 } : { opacity: 1, y: 0, scale: 1 }}
              exit={reduceMotion ? { opacity: 0 } : { opacity: 0, y: 6, scale: 0.95 }}
              transition={{ type: 'spring', stiffness: 420, damping: 36 }}
            >
              {moreRoutes.map((route) => {
                const active = isNavigationPathActive(pathname, route.path);
                return (
                  <button
                    key={route.path}
                    type="button"
                    role="menuitem"
                    onClick={() => navigate(canonicalInternalPath(route.path))}
                    className={cn(
                      'flex w-full items-center gap-2.5 rounded-ds-lg px-3 py-2 text-left transition-colors duration-ds-fast',
                      active ? 'text-ds-primary' : 'text-ds-fg',
                      'active:bg-ds-surface-2',
                    )}
                  >
                    <span className={active ? 'text-ds-primary' : 'text-ds-fg-subtle'}>
                      {route.icon}
                    </span>
                    <span className="text-sm font-medium">{route.label}</span>
                  </button>
                );
              })}

              {moreRoutes.length > 0 && (
                <div className="my-1 border-t border-ds-border" role="separator" />
              )}
              <a
                href={languageHref(targetLanguage)}
                onClick={() => selectLanguage(targetLanguage)}
                role="menuitem"
                className="flex w-full items-center gap-2.5 rounded-ds-lg px-3 py-2 text-left text-ds-fg transition-colors duration-ds-fast active:bg-ds-surface-2"
              >
                <Globe size={18} className="text-ds-fg-subtle" />
                <span className="text-sm font-medium">{zh ? 'English' : '中文'}</span>
              </a>
              <button
                type="button"
                role="menuitem"
                onClick={toggleTheme}
                className="flex w-full items-center gap-2.5 rounded-ds-lg px-3 py-2 text-left text-ds-fg transition-colors duration-ds-fast active:bg-ds-surface-2"
              >
                {isDarkMode ? (
                  <Sun size={18} className="text-ds-fg-subtle" />
                ) : (
                  <Moon size={18} className="text-ds-fg-subtle" />
                )}
                <span className="text-sm font-medium">
                  {zh ? (isDarkMode ? '浅色模式' : '深色模式') : isDarkMode ? 'Light mode' : 'Dark mode'}
                </span>
              </button>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      <nav
        {...dsRoot}
        aria-label={zh ? '主导航' : 'Primary navigation'}
        className="relative z-50 mx-1.5 mb-1.5 grid flex-shrink-0 grid-cols-5 rounded-ds-xl border border-ds-border bg-ds-surface-1 px-1 pt-1 shadow-ds-2 sm:hidden"
        style={{ paddingBottom: 'max(0.5rem, env(safe-area-inset-bottom))' }}
      >
        {primaryRoutes.map((route) => {
          const current = isNavigationPathActive(pathname, route.path);
          return (
            <TabSlot
              key={route.path}
              route={route}
              active={current && !moreOpen}
              current={current}
              onClick={() => navigate(canonicalInternalPath(route.path))}
              reduceMotion={reduceMotion}
            />
          );
        })}

        <TabSlot
          route={moreRoute}
          active={moreActive || moreOpen}
          current={moreActive}
          onClick={() => setMoreOpen((value) => !value)}
          reduceMotion={reduceMotion}
          expanded={moreOpen}
          hasPopup
        />
      </nav>
    </>
  );
};
