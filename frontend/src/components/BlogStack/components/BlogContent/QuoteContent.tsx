import React from 'react';
import { BlogContent } from '../../types/blog';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import rehypeHighlight from 'rehype-highlight';

interface QuoteContentProps {
  item: BlogContent;
}

export const QuoteContent: React.FC<QuoteContentProps> = ({ item }) => {

  return (
    <section className="my-16 break-inside-avoid">
      <div className="px-6">
        <div className="relative">
          {/* Decorative Quote Mark */}
          <div 
            className="absolute -top-8 transform -translate-x-1/2 text-8xl leading-none 
                       text-theme-accent/20 pointer-events-none select-none font-serif"
            aria-hidden="true"
          >
            "
          </div>
          
          {/* Quote Content */}
          <blockquote 
            className="relative z-10 text-center py-12 px-8"
          >
            <div className="prose prose-lg max-w-3xl mx-auto selection:bg-theme-accent/20">
              <ReactMarkdown
                remarkPlugins={[remarkGfm, remarkMath]}
                rehypePlugins={[rehypeKatex as any, rehypeHighlight as any]}
                components={{
                  a: ({ node, ...props }) => (
                    <a {...props} target="_blank" rel="noopener noreferrer" />
                  ),
                  p: ({ node, ...props }) => (
                    <p
                      {...props}
                      className={`text-lg sm:text-xl lg:text-2xl leading-relaxed text-theme-text-primary font-normal italic tracking-wide ${props.className || ''}`.trim()}
                      style={{
                        textRendering: 'optimizeLegibility',
                        WebkitFontSmoothing: 'antialiased',
                        MozOsxFontSmoothing: 'grayscale',
                        lineHeight: '1.6'
                      }}
                    />
                  ),
                  em: ({ node, ...props }) => (
                    <em {...props} className={`italic ${props.className || ''}`.trim()} />
                  ),
                  strong: ({ node, ...props }) => (
                    <strong {...props} className={`font-semibold ${props.className || ''}`.trim()} />
                  ),
                  code: ({ className, children, ...props }) => {
                    const isBlock = (className && /language-/.test(className)) || String(children).includes('\n');
                    if (!isBlock) {
                      return (
                        <code
                          {...props}
                          className={`px-1.5 py-0.5 rounded bg-theme-surface-secondary text-theme-primary ${className || ''}`.trim()}
                        >
                          {children}
                        </code>
                      );
                    }
                    return (
                      <pre className="my-4 overflow-x-auto text-left inline-block">
                        <code className={className} {...props}>{children}</code>
                      </pre>
                    );
                  },
                  ul: ({ className, ...props }) => (
                    <ul {...props} className={`my-4 pl-6 list-disc text-left inline-block ${className || ''}`.trim()} />
                  ),
                  ol: ({ className, ...props }) => (
                    <ol {...props} className={`my-4 pl-6 list-decimal text-left inline-block ${className || ''}`.trim()} />
                  ),
                  li: ({ className, children, ...props }) => (
                    <li {...props} className={`leading-7 mb-1 ${className || ''}`.trim()}>{children}</li>
                  ),
                  table: ({ className, ...props }) => (
                    <div className="overflow-x-auto my-4 inline-block text-left">
                      <table {...props} className={`w-full border-collapse text-sm ${className || ''}`.trim()} />
                    </div>
                  ),
                  thead: ({ className, ...props }) => (
                    <thead {...props} className={`bg-gray-50 dark:bg-gray-800 ${className || ''}`.trim()} />
                  ),
                  tr: ({ className, ...props }) => (
                    <tr {...props} className={`border-b last:border-0 border-gray-200 dark:border-gray-700 ${className || ''}`.trim()} />
                  ),
                  th: ({ className, ...props }) => (
                    <th {...props} className={`text-left font-semibold px-3 py-2 align-top border border-gray-200 dark:border-gray-700 ${className || ''}`.trim()} />
                  ),
                  td: ({ className, ...props }) => (
                    <td {...props} className={`px-3 py-2 align-top border border-gray-200 dark:border-gray-700 ${className || ''}`.trim()} />
                  ),
                }}
              >
                {item.content}
              </ReactMarkdown>
            </div>
          </blockquote>
        </div>
      </div>
    </section>
  );
}; 