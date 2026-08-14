import { Heart, Link2, Lock, MessageCircle, PencilLine } from 'lucide-react';
import { contentGroupTags, contentGroupUpdatedAt, selectPrimaryDocument, translationPreview } from '../lib/content';
import { contentLifecycleFor } from '../lib/contentLifecycle';
import { toWebviewMediaUrl } from '../lib/media';
import { Badge } from './ds/Badge';
import type { ContentGroup, EditorDocument, MomentsSettings } from '../types';

type MomentFeedProps = {
  groups: ContentGroup[];
  empty: string;
  query: string;
  settings: MomentsSettings | null;
  languageByDocument: Record<string, string>;
  eyebrow: string;
  title: string;
  meta: string[];
  onOpen: (group: ContentGroup) => void;
};

const primaryTranslation = (document?: EditorDocument | null) => (
  document?.translations.find((translation) => translation.language === document.canonical_language)
  || document?.translations[0]
  || null
);

const updateDateParts = (value: string) => {
  const date = value ? new Date(value) : null;
  if (!date || Number.isNaN(date.getTime())) return { day: '', month: '' };
  return {
    day: new Intl.DateTimeFormat('en', { day: 'numeric' }).format(date),
    month: new Intl.DateTimeFormat('en', { month: 'short' }).format(date),
  };
};

const contentGroupDate = (group: ContentGroup) => group.date || contentGroupUpdatedAt(group);

const momentVisibilityIcon = (visibility: string) => {
  if (visibility === 'private') return <Lock size={18} aria-label="Private moment" />;
  if (visibility === 'unlisted') return <Link2 size={18} aria-label="Unlisted moment" />;
  return <PencilLine size={16} aria-label="Public moment" />;
};

export function MomentFeed({
  groups,
  empty,
  query,
  settings,
  languageByDocument,
  eyebrow,
  title,
  meta,
  onOpen,
}: MomentFeedProps) {
  const ordered = [...groups].sort((left, right) =>
    Number(Boolean(right.pinned)) - Number(Boolean(left.pinned))
    || contentGroupDate(right).localeCompare(contentGroupDate(left)),
  );

  if (ordered.length === 0) {
    return (
      <div className="moments-feed-empty">
        {query.trim() ? 'No matching moments.' : empty}
      </div>
    );
  }

  const profile = settings?.profile;
  const displayName = profile?.display_name.trim() || 'Profile';
  const avatarUrl = toWebviewMediaUrl(profile?.avatar_url);
  const avatarLabel = profile?.avatar_label.trim() || displayName.charAt(0) || 'P';

  return (
    <section className="moments-feed moments-moments" aria-label="Moments feed">
      <header className="moments-cover">
        <div className="moments-cover-art" aria-hidden="true" />
        <div className="moments-cover-title">
          <div className="eyebrow">{eyebrow}</div>
          <h1>{title}</h1>
          <div className="meta">
            {meta.map((item) => <span key={item}>{item}</span>)}
          </div>
        </div>
        <div className="moments-profile" data-align={profile?.alignment || 'right'}>
          <strong>{displayName}</strong>
          <div className="moments-avatar" aria-hidden="true">
            {avatarUrl ? <img src={avatarUrl} alt="" loading="lazy" /> : avatarLabel}
          </div>
        </div>
      </header>

      <div className="moments-timeline">
        {ordered.map((group) => {
          const document = selectPrimaryDocument(group);
          const preferredLanguage = document ? languageByDocument[document.id] : '';
          const translation = document?.translations.find((item) => item.language === preferredLanguage)
            || primaryTranslation(document);
          const updateDate = contentGroupDate(group);
          const date = updateDateParts(updateDate);
          const tags = contentGroupTags(group, 3);
          const preview = translation?.content || translationPreview(document) || group.title;
          const lifecycle = contentLifecycleFor('moment', group.status, group.visibility);

          return (
            <article className="moments-timeline-row" key={group.id}>
              <time className="moments-date" dateTime={updateDate}>
                {group.pinned && <em>PIN</em>}
                <strong>{date.day}</strong>
                <span>{date.month}.</span>
              </time>
              <button type="button" className="moments-entry" onClick={() => onOpen(group)}>
                <div>
                  <p>{preview}</p>
                  <div className="moments-tags">
                    <Badge size="sm" tone="neutral">{lifecycle.statusLabel}</Badge>
                    <Badge
                      size="sm"
                      tone={lifecycle.visibility === 'public' ? 'success' : lifecycle.visibility === 'unlisted' ? 'warning' : 'neutral'}
                    >
                      {lifecycle.visibilityLabel}
                    </Badge>
                    {tags.map((tag) => <span key={tag}>#{tag}</span>)}
                  </div>
                  <div
                    className="moments-engagement"
                    aria-label={`${group.engagement.likes} likes and ${group.engagement.comments} comments`}
                  >
                    <span title={`${group.engagement.likes} likes`}>
                      <Heart size={14} />
                      {group.engagement.likes}
                    </span>
                    <span title={`${group.engagement.comments} comments`}>
                      <MessageCircle size={14} />
                      {group.engagement.comments}
                    </span>
                  </div>
                </div>
                {momentVisibilityIcon(lifecycle.visibility)}
              </button>
            </article>
          );
        })}
      </div>
    </section>
  );
}
