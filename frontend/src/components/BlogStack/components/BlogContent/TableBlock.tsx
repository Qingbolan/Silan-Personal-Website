import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import rehypeHighlight from 'rehype-highlight';

export interface TableBlockProps {
  header: React.ReactNode[];
  rows: React.ReactNode[][];
}

const TableBlock: React.FC<TableBlockProps> = ({ header, rows }) => {
  const renderCell = (content: React.ReactNode) => {
    if (typeof content !== 'string') return content;
    return (
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex as any, rehypeHighlight as any]}
        components={{
          a: ({ node, ...props }) => (
            <a {...props} target="_blank" rel="noopener noreferrer" />
          ),
          p: ({ node, ...props }) => <span {...props} className={`inline ${props.className || ''}`.trim()} />,
          strong: ({ node, ...props }) => <strong {...props} />,
          em: ({ node, ...props }) => <em {...props} />,
          del: ({ node, ...props }) => <del {...props} />,
          br: () => <br />,
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
              <pre className="my-2 overflow-x-auto text-left">
                <code className={className} {...props}>{children}</code>
              </pre>
            );
          },
          ul: ({ node, children, ...props }) => <span {...props}>{children}</span>,
          ol: ({ node, children, ...props }) => <span {...props}>{children}</span>,
          li: ({ node, children, ...props }) => <span {...props}>{children}</span>,
          blockquote: ({ node, children, ...props }) => <span {...props}>{children}</span>,
          table: ({ node, children, ...props }) => <span {...props}>{children}</span>,
        }}
      >
        {content}
      </ReactMarkdown>
    );
  };

  return (
    <div className="my-6 overflow-auto not-prose rounded-xl border border-theme-card-border bg-theme-surface-elevated shadow-medium">
      <table className="w-full text-sm">
        {header.length > 0 && (
          <thead className="bg-theme-surface-secondary sticky top-0 z-10">
            <tr className="border-b border-theme-card-border">
              {header.map((h, i) => (
                <th
                  key={`th-${i}`}
                  className="text-left font-semibold px-4 py-2 align-top border border-theme-card-border whitespace-nowrap"
                >
                  <div className="flex items-center gap-2">{renderCell(h)}</div>
                </th>
              ))}
            </tr>
          </thead>
        )}
        <tbody>
          {rows.map((row, r) => (
            <tr key={`tr-${r}`} className={`border-b last:border-0 border-theme-card-border hover:bg-theme-surface-tertiary/40 ${r % 2 === 1 ? 'bg-theme-surface/60' : ''}`}>
              {row.map((cell, c) => (
                <td
                  key={`td-${r}-${c}`}
                  className="px-4 py-2 align-top border border-theme-card-border whitespace-pre-wrap [&_code]:px-1.5 [&_code]:py-0.5 [&_code]:rounded [&_code]:bg-theme-surface-secondary [&_code]:text-theme-primary"
                >
                  {renderCell(cell)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TableBlock;
