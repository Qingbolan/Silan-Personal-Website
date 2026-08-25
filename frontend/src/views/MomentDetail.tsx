import React, { useCallback } from 'react';
import { Link, useParams } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { fetchMoment } from '../api/moments/momentApi';
import type { Moment } from '../types/api';
import Markdown from '../components/ui/Markdown';
import MomentActions from '../components/Resume/MomentActions';
import MomentRelatedOutputs from '../components/Moments/MomentRelatedOutputs';
import { useLanguage } from '../components/LanguageContext';
import { Seo, creativeWorkJsonLd } from '../components/Seo';
import { Badge, BrandLoading, NetworkError } from '../components/ds';
import { useRemoteResource } from '../hooks/useRemoteResource';
import { useSetPageTitle } from '../layout/PageTitleContext';
import { markdownToPlainExcerpt, withoutRepeatedTitle } from '../lib/markdown';
import { normalizeContentTimestamp } from '../utils/contentTimestamp';
import { canonicalInternalPath } from '../utils/navigation';

const formatMomentDate = (moment: Moment, language: 'en' | 'zh') => {
  const date = new Date(`${moment.date}T00:00:00`);
  if (Number.isNaN(date.getTime())) return moment.date;
  return new Intl.DateTimeFormat(language === 'zh' ? 'zh-CN' : 'en-SG', {
    year: 'numeric',
    month: 'long',
    day: '2-digit',
  }).format(date);
};

const firstValidContentTimestamp = (...values: Array<string | null | undefined>): string | undefined => {
  for (const value of values) {
    const timestamp = normalizeContentTimestamp(value);
    if (timestamp) return timestamp;
  }
  return undefined;
};

// Standalone detail page (Xiaohongshu note-style split: article left, a
// sticky interaction rail right on desktop; single column with the actions
// in flow below lg). `/moments/:slug` is a real page navigation — the
// browser chrome's back button and the in-page back link both return to
// the moments list.
const MomentDetail: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();
  const { language } = useLanguage();
  const lang = language as 'en' | 'zh';

  const loadMoment = useCallback(
    () => slug ? fetchMoment(slug, lang) : Promise.resolve(null),
    [slug, lang],
  );
  const resource = useRemoteResource<Moment>(slug, loadMoment);
  const moment = resource.data;

  useSetPageTitle(
    moment
      ? moment.title
      : resource.status === 'not-found'
        ? (lang === 'zh' ? '动态不存在' : 'Moment not found')
        : resource.status === 'error'
          ? (lang === 'zh' ? '动态暂不可用' : 'Moment unavailable')
          : null,
  );

  const copy = lang === 'zh'
    ? {
        back: '返回动态',
        loading: '正在加载动态',
        notFoundTitle: '动态不存在',
        notFoundBody: '这条动态不存在，或尚未公开。',
        related: '关联内容',
      }
    : {
        back: 'Back to moments',
        loading: 'Loading moment',
        notFoundTitle: 'Moment not found',
        notFoundBody: 'This moment does not exist or is not public.',
        related: 'Related',
      };

  const detailPath = `/moments/${slug ?? ''}`;
  const description = moment ? markdownToPlainExcerpt(moment.description, moment.title, 180) : '';

  const body = resource.status === 'loading' ? (
    <div className="flex min-h-[24rem] items-center justify-center">
      <BrandLoading inline message={copy.loading} />
    </div>
  ) : resource.status === 'error' ? (
    <div className="flex min-h-[24rem] items-center justify-center p-8">
      <NetworkError onRetry={resource.reload} error={resource.error} />
    </div>
  ) : !moment ? (
    <div className="flex min-h-[24rem] flex-col items-center justify-center gap-4 p-8 text-center">
      <h1 className="text-ds-xl font-semibold text-ds-fg">{copy.notFoundTitle}</h1>
      <p className="max-w-sm text-ds-sm text-ds-fg-muted">{copy.notFoundBody}</p>
    </div>
  ) : (
    <MomentDetailBody moment={moment} lang={lang} copy={copy} />
  );

  return (
    <div className="mx-auto w-full max-w-[76rem] px-4 pb-16 pt-6 sm:px-8 sm:pt-8 lg:px-0">
      {moment && (
        <Seo
          title={moment.title}
          description={description}
          path={detailPath}
          type="article"
          lang={lang}
          jsonLd={creativeWorkJsonLd({
            title: moment.title,
            description,
            path: detailPath,
            lang,
            datePublished: firstValidContentTimestamp(moment.date, moment.created_at),
            dateModified: firstValidContentTimestamp(moment.updated_at, moment.created_at, moment.date),
          })}
        />
      )}

      <Link
        to={canonicalInternalPath('/moments')}
        className="inline-flex items-center gap-1.5 text-ds-sm font-medium text-ds-fg-muted transition-colors hover:text-ds-primary"
      >
        <ArrowLeft className="size-4" aria-hidden />
        {copy.back}
      </Link>

      <div className="mt-5 sm:mt-7">{body}</div>
    </div>
  );
};

// The two-pane body — article on the left, the interaction rail on the
// right pinned sticky beside it (the comment list scrolls inside the
// rail). Below lg it is a single column: content first, actions/comments
// in flow after the article.
const MomentDetailBody: React.FC<{
  moment: Moment;
  lang: 'en' | 'zh';
  copy: {
    related: string;
  };
}> = ({ moment, lang, copy }) => {
  const bodyText = withoutRepeatedTitle(moment.description, moment.title);
  const timestamp =
    moment.created_at && !moment.created_at.startsWith('0001-')
      ? moment.created_at
      : `${moment.date}T00:00:00`;
  const formattedDate = formatMomentDate(moment, lang);

  return (
    <div className="lg:grid lg:grid-cols-[minmax(0,1fr)_24rem] lg:gap-10 xl:grid-cols-[minmax(0,1fr)_26rem]">
      <article className="min-w-0 pb-12">
        <div className="mx-auto max-w-[44rem]">
          <header className="border-b border-ds-border pb-0">
            <h1 className="text-balance text-ds-2xl font-semibold leading-[1.12] tracking-[-0.03em] text-ds-fg sm:text-ds-4xl">
              {moment.title}
            </h1>

            <div className="mt-4 flex flex-wrap items-center gap-x-3 gap-y-2">
              <time dateTime={moment.date} className="font-mono text-ds-xs tabular-nums text-ds-fg-subtle">
                {formattedDate}
              </time>
              {moment.tags?.map((tag) => (
                <Badge key={tag} tone="neutral" appearance="soft">
                  #{tag}
                </Badge>
              ))}
            </div>
          </header>

          <Markdown
            documentTitle={moment.title}
            className="mt-5 text-ds-base leading-8 text-ds-fg-muted sm:text-ds-lg [&_.markdown-body]:!pl-0"
          >
            {bodyText}
          </Markdown>

          <MomentRelatedOutputs
            outputs={moment.related_outputs ?? []}
            labels={{
              title: copy.related,
            }}
            className="mt-8"
          />

          {/* Below lg, the interaction rail collapses back into the
              article flow — the sidebar variant only makes sense with
              room beside the text. */}
          <div className="mt-8 lg:hidden">
            <MomentActions momentKey={moment.slug || moment.id} timestamp={timestamp} />
          </div>
        </div>
      </article>

      <aside className="hidden lg:block">
        {/* Sticky rail: the sidebar variant needs a bounded height so its
            comment list scrolls internally while the article keeps using
            the page scroll. */}
        <div className="sticky top-6 h-[calc(100dvh-10rem)] min-h-[24rem] overflow-hidden rounded-ds-lg border border-ds-border bg-ds-surface-2">
          <MomentActions momentKey={moment.slug || moment.id} timestamp={timestamp} variant="sidebar" />
        </div>
      </aside>
    </div>
  );
};

export default MomentDetail;
