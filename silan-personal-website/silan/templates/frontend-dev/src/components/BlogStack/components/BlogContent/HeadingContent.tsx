import React from 'react';
import { Typography } from 'antd';
import { BlogContent } from '../../types/blog';
import { renderInlineMarkdown } from '../../../../utils/fullMarkdownRenderer';

const { Title } = Typography;

interface HeadingContentProps {
  item: BlogContent;
  index: number;
  isWideScreen: boolean;
}

export const HeadingContent: React.FC<HeadingContentProps> = ({
  item,
  isWideScreen
}) => {
  // Generate stable, anchor-friendly ID
  const slugify = (s: string) =>
    (s || '')
      .toString()
      .toLowerCase()
      .trim()
      .replace(/#[^\s]*/g, '')
      .replace(/[?]/g, '')
      .replace(/[^a-z0-9\s\-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-');

  const anchorId = item.id || slugify(item.content);
  
  // Ensure we have a valid level (1-6), default to 2
  const level = Math.max(1, Math.min(6, item.level || 2)) as 1 | 2 | 3 | 4 | 5;

  return (
    <div
      id={anchorId}
      className={`heading-content group ${isWideScreen ? 'wide-screen' : ''}`}
      style={{
        scrollMarginTop: '100px',
        marginTop: level === 1 ? '2.5rem' : '2rem',
        marginBottom: level === 1 ? '1.5rem' : '1rem'
      }}
    >
      <Title
        level={level}
        style={{
          color: 'var(--color-text-primary, #1f2937)',
          fontFamily: 'var(--font-display, Inter)',
          fontWeight: level === 1 ? 700 : level === 2 ? 600 : 500,
          lineHeight: level === 1 ? 1.2 : 1.3,
          marginBottom: 0,
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          fontSize: isWideScreen ?
            (level === 1 ? '2rem' : level === 2 ? '1.75rem' : level === 3 ? '1.5rem' : '1.25rem') :
            (level === 1 ? '1.75rem' : level === 2 ? '1.5rem' : level === 3 ? '1.25rem' : '1.125rem')
        }}
        className={`heading-level-${level} ${isWideScreen ? 'wide' : 'normal'}`}
      >
        <span>{renderInlineMarkdown(item.content)}</span>
        <a
          href={`#${anchorId}`}
          onClick={(e) => {
            e.preventDefault();
            try {
              const url = new URL(window.location.href);
              url.hash = anchorId;
              window.history.replaceState(null, '', `#${anchorId}`);
              void navigator.clipboard?.writeText(url.toString());
            } catch {}
          }}
          aria-label="Copy link to this heading"
          className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 text-[var(--color-secondary,#64748b)] hover:text-[var(--color-primary,#0066FF)]"
          style={{ textDecoration: 'none' }}
        >
          #
        </a>
      </Title>
      
      {/* Add a subtle divider for h1 and h2 */}
      {(level === 1 || level === 2) && (
        <div 
          className="heading-divider"
          style={{
            width: level === 1 ? '100%' : '60%',
            height: '2px',
            background: level === 1 ? 
              'linear-gradient(90deg, var(--color-primary, #0066FF), transparent)' :
              'linear-gradient(90deg, var(--color-secondary, #6366f1), transparent)',
            marginTop: '0.5rem',
            borderRadius: '1px'
          }}
        />
      )}
    </div>
  );
};