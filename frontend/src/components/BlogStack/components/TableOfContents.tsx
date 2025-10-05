import React from 'react';
import { Anchor } from 'antd';
import type { AnchorLinkItemProps } from 'antd/es/anchor/Anchor';
import { Section } from '../types/blog';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import rehypeHighlight from 'rehype-highlight';
interface TableOfContentsProps {
  sections: Section[];
  className?: string;
}

export const TableOfContents: React.FC<TableOfContentsProps> = ({
  sections,
  className = ''
}) => {
  // Convert sections to Ant Design Anchor items format with proper hierarchy
  const anchorItems: AnchorLinkItemProps[] = React.useMemo(() => {
    if (sections.length === 0) return [];
    
    // Use flat structure but with visual hierarchy via CSS
    return sections.map(section => ({
      key: section.id,
      href: `#${section.id}`,
      title: (
        <span 
          className={`simple-toc-item level-${section.level}`}
          title={section.title}
        >
          <ReactMarkdown
            remarkPlugins={[remarkGfm, remarkMath]}
            rehypePlugins={[rehypeKatex as any, rehypeHighlight as any]}
            // Force inline rendering to avoid block elements inside Anchor title
            components={{
              // Prevent nested anchors inside Anchor item title
              a: ({ node, children }) => (
                <span className="underline decoration-dotted underline-offset-2">
                  {children}
                </span>
              ),
              p: ({ node, ...props }) => (
                <span {...props} />
              ),
              strong: ({ node, ...props }) => (
                <strong {...props} />
              ),
              em: ({ node, ...props }) => (
                <em {...props} />
              ),
              del: ({ node, ...props }) => (
                <del {...props} />
              ),
              code: ({ className, children, ...props }) => (
                <code
                  {...props}
                  className={`px-1 py-0.5 rounded bg-theme-surface-secondary text-theme-primary ${className || ''}`.trim()}
                  style={{ fontSize: '0.9em' }}
                >
                  {children}
                </code>
              ),
              // Defensive: collapse possible lists/blocks to inline spans
              ul: ({ node, children, ...props }) => <span {...props}>{children}</span>,
              ol: ({ node, children, ...props }) => <span {...props}>{children}</span>,
              li: ({ node, children, ...props }) => <span {...props}>{children}</span>,
              blockquote: ({ node, children, ...props }) => <span {...props}>{children}</span>,
              table: ({ node, children, ...props }) => <span {...props}>{children}</span>,
              thead: ({ node, children, ...props }) => <span {...props}>{children}</span>,
              tbody: ({ node, children, ...props }) => <span {...props}>{children}</span>,
              tr: ({ node, children, ...props }) => <span {...props}>{children}</span>,
              th: ({ node, children, ...props }) => <span {...props}>{children}</span>,
              td: ({ node, children, ...props }) => <span {...props}>{children}</span>,
              hr: () => null,
              br: () => <span> / </span>,
              h1: ({ node, children, ...props }) => <strong {...props}>{children}</strong>,
              h2: ({ node, children, ...props }) => <strong {...props}>{children}</strong>,
              h3: ({ node, children, ...props }) => <strong {...props}>{children}</strong>,
              h4: ({ node, children, ...props }) => <strong {...props}>{children}</strong>,
              h5: ({ node, children, ...props }) => <strong {...props}>{children}</strong>,
              h6: ({ node, children, ...props }) => <strong {...props}>{children}</strong>,
            }}
          >
            {section.title}
          </ReactMarkdown>
        </span>
      ),
    }));
  }, [sections]);

  if (sections.length === 0) {
    return null;
  }

  return (
    <div
      className={`simple-toc ${className}`}
      style={{
        position: 'relative',
        maxHeight: 'calc(100vh - 120px)', // 增加更多缓冲空间给顶部按钮和间距
        overflow: 'hidden' // 外层隐藏溢出
      }}
    >
      {/* TOC Content */}
      <div style={{
        maxHeight: 'calc(100vh - 160px)', // 与外层一致
        overflow: 'auto', // 内层可滚动
        paddingRight: '4px', // 为滚动条留出更多空间
      }}>
        <Anchor
          items={anchorItems}
          offsetTop={120}
          targetOffset={120}
          showInkInFixed={true}
          affix={false}
          bounds={10}
          className="simple-toc-anchor"
        />
      </div>
    </div>
  );
};