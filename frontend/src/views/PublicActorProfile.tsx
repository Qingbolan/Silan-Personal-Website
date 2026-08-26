import React, { useCallback, useMemo, useState } from 'react';
import { ArrowLeft, ArrowUpRight, Heart, MessageSquareText } from 'lucide-react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { fetchPublicActor, type PublicActorActivity, type PublicActorActivityKind, type PublicActorProfile as PublicActorProfileData } from '../api/people/peopleApi';
import { mediaUrl } from '../api/utils';
import { useLanguage } from '../components/LanguageContext';
import { Seo } from '../components/Seo';
import Avatar from '../components/ds/article-footer/Avatar';
import { BrandLoading, NetworkError } from '../components/ds';
import { useRemoteResource } from '../hooks/useRemoteResource';
import { useSetPageTitle } from '../layout/PageTitleContext';
import { canonicalInternalPath } from '../utils/navigation';

type ActivityFilter = 'all' | PublicActorActivityKind;

const formatActivityTime = (value: string, language: 'en' | 'zh'): string => {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat(language === 'zh' ? 'zh-CN' : 'en-SG', {
    year: date.getFullYear() === new Date().getFullYear() ? undefined : 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
};

const countryName = (code: string | undefined, language: 'en' | 'zh'): string | undefined => {
  if (!code) return undefined;
  try {
    return new Intl.DisplayNames([language === 'zh' ? 'zh-CN' : 'en'], { type: 'region' }).of(code.toUpperCase());
  } catch {
    return code.toUpperCase();
  }
};

const ActivityRow: React.FC<{
  activity: PublicActorActivity;
  profile: PublicActorProfileData;
  language: 'en' | 'zh';
}> = ({ activity, profile, language }) => {
  const isComment = activity.kind === 'comment';
  const entityPath = activity.entity_path
    ? canonicalInternalPath(activity.entity_path)
    : undefined;
  const entityTitle = activity.entity_title || (language === 'zh' ? '公开内容' : 'public post');
  const action = isComment
    ? (language === 'zh' ? '评论了' : 'commented on')
    : (language === 'zh' ? '赞了' : 'liked');

  return (
    <li className="grid grid-cols-[2.5rem_minmax(0,1fr)] gap-3 border-b border-ds-border py-3.5 last:border-b-0">
      <Avatar
        name={profile.display_name}
        src={profile.avatar_url ? mediaUrl(profile.avatar_url) : undefined}
        countryCode={profile.country_code}
        visitorNumber={profile.visitor_number}
        size="md"
        className="size-10 rounded-[8px]"
      />

      <div className="min-w-0">
        <div className="flex min-w-0 items-center justify-between gap-3">
          <span className="truncate text-[0.9375rem] font-semibold leading-5 text-ds-primary">
            {profile.display_name}
          </span>
          <time
            dateTime={activity.created_at}
            className="shrink-0 text-[0.75rem] leading-5 tabular-nums text-ds-fg-subtle"
          >
            {formatActivityTime(activity.created_at, language)}
          </time>
        </div>

        {isComment && activity.content && (
          <p className="mt-0.5 line-clamp-3 whitespace-pre-wrap text-[0.9375rem] font-normal leading-[1.48] tracking-[-0.006em] text-ds-fg">
            {activity.content}
          </p>
        )}

        <div className="mt-1 flex min-w-0 items-center gap-1.5 text-[0.8125rem] leading-5 text-ds-fg-muted">
          {isComment
            ? <MessageSquareText className="size-3.5 shrink-0" aria-hidden />
            : <Heart className="size-3.5 shrink-0" aria-hidden />}
          <span className="shrink-0">{action}</span>
          {entityPath ? (
            <Link
              to={entityPath}
              className="flex min-w-0 items-center gap-0.5 rounded-ds-xs font-medium text-ds-fg transition-colors hover:text-ds-primary hover:underline focus-visible:shadow-ds-focus"
            >
              <span className="truncate">{entityTitle}</span>
              <ArrowUpRight className="size-3 shrink-0" aria-hidden />
            </Link>
          ) : <span className="truncate font-medium text-ds-fg">{entityTitle}</span>}
        </div>
      </div>
    </li>
  );
};

const PublicActorProfile: React.FC = () => {
  const { actorId } = useParams<{ actorId: string }>();
  const navigate = useNavigate();
  const { language } = useLanguage();
  const lang = language as 'en' | 'zh';
  const [filter, setFilter] = useState<ActivityFilter>('all');
  const load = useCallback(
    () => actorId ? fetchPublicActor(actorId, lang) : Promise.resolve(null),
    [actorId, lang],
  );
  const resource = useRemoteResource<PublicActorProfileData>(actorId, load);
  const profile = resource.data;

  useSetPageTitle(profile?.display_name || (resource.status === 'not-found'
    ? (lang === 'zh' ? '用户不存在' : 'Profile not found')
    : null));

  const activities = useMemo(
    () => profile?.activities.filter((activity) => filter === 'all' || activity.kind === filter) ?? [],
    [filter, profile],
  );

  const copy = lang === 'zh'
    ? {
        back: '返回',
        profile: '用户资料',
        region: '地区',
        activity: '互动记录',
        all: '全部',
        comments: '评论',
        likes: '点赞',
        empty: '暂无公开互动记录',
        missing: '这个用户资料不存在或已经不可见。',
        loading: '正在加载用户资料',
      }
    : {
        back: 'Back',
        profile: 'Profile',
        region: 'Region',
        activity: 'Interactions',
        all: 'All',
        comments: 'Comments',
        likes: 'Likes',
        empty: 'No public interactions yet',
        missing: 'This profile does not exist or is no longer public.',
        loading: 'Loading profile',
      };

  const location = profile
    ? [profile.region_name, countryName(profile.country_code, lang)].filter(Boolean).join(' · ')
    : '';

  return (
    <div className="mx-auto min-h-[calc(100dvh-4rem)] w-full max-w-[46rem] px-4 pb-8 pt-3 sm:px-7 sm:pt-6">
      {profile && (
        <Seo
          title={profile.display_name}
          description={lang === 'zh' ? `${profile.display_name} 的公开互动记录` : `${profile.display_name}'s public interactions`}
          path={`/people/${profile.actor_id}`}
          lang={lang}
          noindex
        />
      )}

      <nav className="flex h-10 items-center justify-between" aria-label={copy.profile}>
        <button
          type="button"
          onClick={() => navigate(-1)}
          className="inline-flex min-h-9 items-center gap-1.5 rounded-ds-xs pr-2 text-ds-sm font-medium text-ds-fg transition-colors hover:text-ds-primary focus-visible:shadow-ds-focus"
        >
          <ArrowLeft className="size-[18px]" aria-hidden />
          {copy.back}
        </button>
        <span className="text-ds-sm font-semibold text-ds-fg">{copy.profile}</span>
        <span className="w-14" aria-hidden />
      </nav>

      {resource.status === 'loading' ? (
        <div className="flex min-h-[26rem] items-center justify-center">
          <BrandLoading inline message={copy.loading} />
        </div>
      ) : resource.status === 'error' ? (
        <div className="flex min-h-[26rem] items-center justify-center">
          <NetworkError error={resource.error} onRetry={resource.reload} />
        </div>
      ) : !profile ? (
        <div className="flex min-h-[26rem] items-center justify-center text-center text-ds-sm text-ds-fg-muted">
          {copy.missing}
        </div>
      ) : (
        <>
          <section className="py-8 sm:py-10" aria-labelledby="profile-name">
            <div className="flex items-start gap-4">
              <Avatar
                name={profile.display_name}
                src={profile.avatar_url ? mediaUrl(profile.avatar_url) : undefined}
                countryCode={profile.country_code}
                visitorNumber={profile.visitor_number}
                size="md"
                className="size-[4.75rem] rounded-[12px] text-xl"
              />
              <div className="min-w-0 pt-0.5">
                <h1 id="profile-name" className="text-pretty text-[1.5rem] font-semibold leading-[1.22] tracking-[-0.02em] text-ds-fg">
                  {profile.display_name}
                </h1>
                {location && (
                  <p className="mt-2 text-[0.9375rem] leading-6 text-ds-fg-muted">
                    {copy.region}：{location}
                  </p>
                )}
              </div>
            </div>
          </section>

          <section className="border-t border-ds-border" aria-labelledby="activity-heading">
            <div className="flex items-center justify-between gap-3 py-3">
              <h2 id="activity-heading" className="text-ds-sm font-semibold text-ds-fg">
                {copy.activity}
              </h2>
              <div className="flex items-center gap-1" role="group" aria-label={copy.activity}>
                {([
                  ['all', copy.all],
                  ['comment', copy.comments],
                  ['like', copy.likes],
                ] as const).map(([value, label]) => (
                  <button
                    key={value}
                    type="button"
                    onClick={() => setFilter(value)}
                    aria-pressed={filter === value}
                    className={`min-h-8 rounded-ds-xs px-2.5 text-ds-xs font-medium transition-colors focus-visible:shadow-ds-focus ${
                      filter === value
                        ? 'bg-ds-primary/10 text-ds-primary'
                        : 'text-ds-fg-muted hover:bg-ds-surface-2 hover:text-ds-fg'
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            {activities.length > 0 ? (
              <ul>
                {activities.map((activity) => (
                  <ActivityRow
                    key={`${activity.kind}-${activity.id}`}
                    activity={activity}
                    profile={profile}
                    language={lang}
                  />
                ))}
              </ul>
            ) : (
              <p className="border-t border-ds-border py-10 text-center text-ds-sm text-ds-fg-subtle">
                {copy.empty}
              </p>
            )}
          </section>
        </>
      )}
    </div>
  );
};

export default PublicActorProfile;
