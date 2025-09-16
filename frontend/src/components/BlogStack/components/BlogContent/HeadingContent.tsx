import React from 'react';
import { Typography } from 'antd';
import { BlogContent } from '../../types/blog';

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
  // Generate anchor-friendly ID for the heading
  const anchorId = item.id;
  
  // Ensure we have a valid level (1-6), default to 2
  const level = Math.max(1, Math.min(6, item.level || 2)) as 1 | 2 | 3 | 4 | 5;

  return (
    <div 
      id={anchorId}
      className={`heading-content ${isWideScreen ? 'wide-screen' : ''}`}
      style={{
        scrollMarginTop: '100px', // Account for fixed header
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
          fontSize: isWideScreen ?
            (level === 1 ? '2rem' : level === 2 ? '1.75rem' : level === 3 ? '1.5rem' : '1.25rem') :
            (level === 1 ? '1.75rem' : level === 2 ? '1.5rem' : level === 3 ? '1.25rem' : '1.125rem')
        }}
        className={`heading-level-${level} ${isWideScreen ? 'wide' : 'normal'}`}
      >
        {item.content}
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