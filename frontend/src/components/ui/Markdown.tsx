import React from 'react';
import { Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownProps {
  children: string;
  className?: string;
}

const Markdown: React.FC<MarkdownProps> = ({ children, className }) => {
  return (
    <div className={`markdown-body ${className || ''}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ node, ...props }) => (
            <h1 className="text-theme-primary font-bold mt-6 mb-4 text-3xl" {...props} />
          ),
          h2: ({ node, ...props }) => (
            <h2 className="text-theme-primary font-bold mt-5 mb-3 text-2xl" {...props} />
          ),
          h3: ({ node, ...props }) => (
            <h3 className="text-theme-primary font-semibold mt-4 mb-2 text-xl" {...props} />
          ),
          p: ({ node, ...props }) => (
            <p className="text-theme-secondary my-2 leading-relaxed" {...props} />
          ),
          a: ({ node, href, children, ...props }) => {
            if (!href) {
              return <span {...props}>{children}</span>;
            }
            const isExternal = /^https?:\/\//i.test(href);
            const commonClass = 'text-theme-accent underline hover:opacity-80 break-all';
            if (href.startsWith('/')) {
              return (
                <Link to={href} className={commonClass} {...(props as any)}>
                  {children}
                </Link>
              );
            }
            if (isExternal) {
              return (
                <a href={href} target="_blank" rel="noopener noreferrer" className={commonClass} {...props}>
                  {children}
                </a>
              );
            }
            return (
              <a href={href} className={commonClass} {...props}>
                {children}
              </a>
            );
          },
          ul: ({ node, ...props }) => (
            <ul className="list-disc pl-5 my-3 marker:text-theme-secondary" {...props} />
          ),
          ol: ({ node, ...props }) => (
            <ol className="list-decimal pl-5 my-3 marker:text-theme-secondary" {...props} />
          ),
          li: ({ node, ...props }) => (
            <li className="my-1 text-theme-secondary marker:text-theme-secondary" {...props} />
          ),
          blockquote: ({ node, ...props }) => (
            <blockquote className="border-l-4 border-theme-primary pl-3 my-3 text-theme-secondary" {...props} />
          ),
          code: (codeProps) => {
            const { inline, className, children, ...props } = codeProps as any;
            if (inline) {
              return (
                <code
                  className={`inline-code ${className || ''}`}
                  {...props}
                >
                  {children}
                </code>
              );
            }
            return (
              <pre className="code-block">
                <code className={className} {...props}>{children}</code>
              </pre>
            );
          },
          hr: ({ node, ...props }) => <hr className="my-6 border-theme-card" {...props} />,
          table: ({ node, ...props }) => (
            <div className="overflow-x-auto my-4">
              <table className="w-full border-collapse" {...props} />
            </div>
          ),
          th: ({ node, ...props }) => (
            <th className="text-left p-2 border border-theme-card bg-theme-surface text-theme-primary" {...props} />
          ),
          td: ({ node, ...props }) => (
            <td className="p-2 border border-theme-card text-theme-secondary" {...props} />
          ),
          img: ({ node, ...props }) => (
            <img className="rounded-lg my-3" loading="lazy" {...props} />
          ),
        }}
      >
        {children}
      </ReactMarkdown>
    </div>
  );
};

export default Markdown;


