import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Heart } from 'lucide-react';
import type { MomentLiker } from '../../api/moments/momentApi';
import { Modal } from '../ds';
import { dsRoot } from '../ds/dsAttr';
import MomentLikerAvatar, { momentLikerLabel } from './MomentLikerAvatar';
import { canonicalInternalPath } from '../../utils/navigation';

interface MomentLikerStripProps {
  likers: MomentLiker[];
  liked: boolean;
  language: 'en' | 'zh';
}

const MomentLikerStrip: React.FC<MomentLikerStripProps> = ({ likers, liked, language }) => {
  const [open, setOpen] = useState(false);
  const preview = likers.slice(0, 5);
  const title = language === 'zh' ? '点赞者' : 'Liked by';

  if (likers.length === 0) return null;

  return (
    <>
      <div {...dsRoot} className="ds-hairline mt-2 w-full rounded-ds-sm bg-ds-surface-2 px-3 py-2 sm:flex sm:min-h-11 sm:items-center sm:gap-3 sm:py-0">
        <div className="grid grid-cols-[1.25rem_minmax(0,1fr)] items-start gap-2 sm:hidden">
          <Heart
            className={`mt-1.5 size-4 shrink-0 ${liked ? 'text-red-500' : 'text-ds-fg-subtle'}`}
            fill={liked ? 'currentColor' : 'none'}
            aria-hidden
          />
          <ul className="grid min-w-0 grid-cols-[repeat(7,2.25rem)] gap-x-1 gap-y-1.5" aria-label={title}>
            {likers.map((liker, index) => {
              const key = liker.actor_id || `${liker.kind}-${liker.visitor_number || liker.avatar_url || index}`;
              return (
                <li key={key}>
                {liker.actor_id ? (
                  <Link
                    to={canonicalInternalPath(`/people/${encodeURIComponent(liker.actor_id)}`)}
                    aria-label={momentLikerLabel(liker, language)}
                    className="block size-9 rounded-[7px] transition-transform hover:-translate-y-0.5 focus-visible:shadow-ds-focus"
                  >
                    <MomentLikerAvatar liker={liker} language={language} size="lg" />
                  </Link>
                ) : <MomentLikerAvatar liker={liker} language={language} size="lg" />}
                </li>
              );
            })}
          </ul>
        </div>

        <Heart
          className={`hidden size-4 shrink-0 sm:block ${liked ? 'text-red-500' : 'text-ds-fg-subtle'}`}
          fill={liked ? 'currentColor' : 'none'}
          aria-hidden
        />
        <span className="hidden items-center gap-1.5 sm:flex">
          {preview.map((liker, index) => (
            liker.actor_id ? (
              <Link
                key={liker.actor_id}
                to={canonicalInternalPath(`/people/${encodeURIComponent(liker.actor_id)}`)}
                className="relative rounded-[7px] transition-transform hover:-translate-y-0.5 focus-visible:shadow-ds-focus"
              >
                <MomentLikerAvatar liker={liker} language={language} size="sm" />
              </Link>
            ) : (
              <MomentLikerAvatar
                key={`${liker.kind}-${liker.visitor_number || liker.avatar_url || index}`}
                liker={liker}
                language={language}
                size="sm"
              />
            )
          ))}
        </span>
        <button
          type="button"
          onClick={() => setOpen(true)}
          className="moment-liker-label hidden min-h-8 min-w-0 flex-1 rounded-ds-xs text-left text-ds-xs font-medium text-ds-fg-muted transition-colors hover:text-ds-fg focus-visible:shadow-ds-focus sm:block"
          aria-label={language === 'zh' ? '查看点赞者' : 'View people who liked this'}
        >
          {title}
        </button>
      </div>

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title={title}
        closeLabel={language === 'zh' ? '关闭' : 'Close'}
        size="sm"
        placement="mobile-bottom"
        className="max-h-[72dvh] overflow-y-auto p-4 sm:p-6"
      >
        <ul className="divide-y divide-ds-border">
          {likers.map((liker, index) => {
            const label = momentLikerLabel(liker, language);
            const content = (
              <>
                <MomentLikerAvatar liker={liker} language={language} />
                <span className="min-w-0 flex-1 truncate text-ds-sm font-medium text-ds-fg">{label}</span>
              </>
            );
            return (
              <li
                key={`${liker.kind}-${liker.visitor_number || liker.avatar_url || index}`}
              >
                {liker.actor_id ? (
                  <Link
                    to={canonicalInternalPath(`/people/${encodeURIComponent(liker.actor_id)}`)}
                    onClick={() => setOpen(false)}
                    className="flex items-center gap-3 rounded-ds-xs py-2.5 transition-colors hover:text-ds-primary focus-visible:shadow-ds-focus"
                  >
                    {content}
                  </Link>
                ) : <div className="flex items-center gap-3 py-2.5">{content}</div>}
              </li>
            );
          })}
        </ul>
      </Modal>
    </>
  );
};

export default MomentLikerStrip;
