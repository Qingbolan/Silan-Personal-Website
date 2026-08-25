// src/components/Resume/RecentSection.tsx
//
// Résumé "recent moments" panel — a year/month grouped activity timeline.
// The homepage and dedicated moments page share the same chronological model.
import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { dsRoot } from '../../components/ds/dsAttr';
import { markdownToPlainExcerpt } from '../../lib/markdown';

export interface RecentItem {
  id: string;
  title: string;
  description: string;
  date: string;
  tags: string[];
  pinned?: boolean;
}

interface RecentSectionProps {
  data: RecentItem[];
  title: string;
  delay?: number;
}

const RecentSection: React.FC<RecentSectionProps> = ({ data, title, delay = 0 }) => {
  const { t, i18n } = useTranslation();
  const locale = i18n.resolvedLanguage?.startsWith('zh') ? 'zh-CN' : 'en';
  const navigate = useNavigate();

  /* --- Relative time label. --------------------------------------------- */
  const getRelativeTime = (dateString: string) => {
    const date = new Date(dateString);
    if (Number.isNaN(date.getTime())) return dateString;
    const diffDays = Math.max(0, Math.floor((Date.now() - date.getTime()) / 86_400_000));
    const formatter = new Intl.RelativeTimeFormat(
      locale,
      { numeric: 'auto' },
    );
    if (diffDays >= 365) return formatter.format(-Math.floor(diffDays / 365), 'year');
    if (diffDays >= 30) return formatter.format(-Math.floor(diffDays / 30), 'month');
    return formatter.format(-diffDays, 'day');
  };

  const sortedData = useMemo(
    () => [...data].sort(
      (a, b) => Number(Boolean(b.pinned)) - Number(Boolean(a.pinned))
        || new Date(b.date).getTime() - new Date(a.date).getTime(),
    ),
    [data],
  );

  const groupedData = useMemo(() => {
    const groups = new Map<string, {
      label: string;
      year: number;
      month: number;
      pinned: boolean;
      items: typeof sortedData;
    }>();
    sortedData.forEach((item) => {
      const date = new Date(item.date);
      const valid = !Number.isNaN(date.getTime());
      const year = valid ? date.getFullYear() : 0;
      const month = valid ? date.getMonth() : 0;
      const key = item.pinned
        ? 'pinned'
        : valid ? `${year}-${String(month + 1).padStart(2, '0')}` : 'unknown';
      const label = item.pinned
        ? locale.startsWith('zh') ? '置顶' : 'Pinned'
        : valid
        ? new Intl.DateTimeFormat(
            locale,
            { year: 'numeric', month: 'long' },
          ).format(date)
        : item.date;
      const group = groups.get(key) ?? {
        label,
        year,
        month,
        pinned: Boolean(item.pinned),
        items: [],
      };
      group.items.push(item);
      groups.set(key, group);
    });
    return [...groups.values()].sort((a, b) =>
      Number(b.pinned) - Number(a.pinned)
      || b.year - a.year
      || b.month - a.month,
    );
  }, [sortedData, locale]);

  return (
    <motion.section
      {...dsRoot}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
    >
      <div>
          <div className="mb-4">
            <h3 className="text-xl font-bold tracking-[-0.015em] text-ds-fg sm:text-2xl">
              {title}
            </h3>
          </div>

          {/* Year/month groups with day-led entries, like a chronological journal. */}
          <div
            className="space-y-5 sm:space-y-6"
            role="list"
            aria-label={t('resume.moments', { defaultValue: 'Recent moments' })}
          >
            {groupedData.map((group) => (
              <section
                key={group.pinned ? 'pinned' : `${group.year}-${group.month}`}
                aria-label={group.label}
              >
                <h4 className="border-b border-ds-border pb-2 font-mono text-ds-xs font-medium uppercase tracking-[0.08em] text-ds-fg-subtle">
                  {group.label}
                </h4>
                <div className="divide-y divide-ds-border">
                  {group.items.map((item, index) => {
                    const date = new Date(item.date);
                    const day = Number.isNaN(date.getTime()) ? '—' : String(date.getDate()).padStart(2, '0');
                    const summary = markdownToPlainExcerpt(item.description, item.title, 280);
                    return (
                      <motion.article
                        key={item.id}
                        role="link"
                        tabIndex={0}
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.25, delay: Math.min(index * 0.04, 0.16) }}
                        onClick={() => navigate(`/moments?id=${encodeURIComponent(item.id)}`)}
                        onKeyDown={(event) => {
                          if (event.key === 'Enter' || event.key === ' ') {
                            event.preventDefault();
                            navigate(`/moments?id=${encodeURIComponent(item.id)}`);
                          }
                        }}
                        aria-label={`${t('resume.view_details', { defaultValue: 'View details' })}: ${item.title}`}
                        className="group grid cursor-pointer grid-cols-[3rem_minmax(0,1fr)] gap-3 py-3.5 outline-none transition-colors hover:bg-ds-surface-2 focus-visible:rounded-ds-sm focus-visible:shadow-ds-focus sm:grid-cols-[4rem_minmax(0,1fr)] sm:gap-4 sm:py-4"
                      >
                        <time
                          dateTime={item.date}
                          className="pt-0.5 font-mono text-2xl font-medium leading-none tabular-nums tracking-[-0.06em] text-ds-fg sm:text-3xl"
                        >
                          {day}
                        </time>
                        <div className="min-w-0">
                          <div className="grid min-w-0 gap-1.5 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-start sm:gap-3">
                            <div className="flex min-w-0 items-start gap-1.5">
                              {item.pinned && (
                                <span className="mt-1 shrink-0 font-mono text-ds-2xs font-semibold uppercase tracking-[0.12em] text-ds-primary">
                                  {locale.startsWith('zh') ? '置顶' : 'PIN'}
                                </span>
                              )}
                              <h5 className="min-w-0 text-pretty text-ds-base font-semibold leading-6 text-ds-fg transition-colors group-hover:text-ds-primary sm:text-ds-lg sm:leading-7">
                                {item.title}
                              </h5>
                            </div>
                            <div className="flex shrink-0 items-center sm:justify-end">
                              <span className="whitespace-nowrap text-ds-xs text-ds-fg-subtle">
                                {getRelativeTime(item.date)}
                              </span>
                            </div>
                          </div>
                          {summary && (
                            <p className="mt-1.5 line-clamp-2 max-w-[88ch] text-pretty text-ds-sm leading-[1.5] text-ds-fg-muted sm:text-ds-base">
                              {summary}
                            </p>
                          )}
                        </div>
                      </motion.article>
                    );
                  })}
                </div>
              </section>
            ))}
          </div>
      </div>
    </motion.section>
  );
};

export default RecentSection;
