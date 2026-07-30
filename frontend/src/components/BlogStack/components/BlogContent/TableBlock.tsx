import React from 'react';
import Markdown from '../../../ui/Markdown';

export interface TableBlockProps {
  header: React.ReactNode[];
  rows: React.ReactNode[][];
}

const TableBlock: React.FC<TableBlockProps> = ({ header, rows }) => {
  const renderCell = (content: React.ReactNode) => {
    if (typeof content !== 'string') return content;
    return <Markdown inline>{content}</Markdown>;
  };

  return (
    <div data-ds className="not-prose my-8 overflow-auto rounded-ds-lg border border-ds-border bg-ds-surface-1 shadow-ds-1">
      <table className="w-full min-w-[42rem] border-separate border-spacing-0 text-left text-ds-sm leading-6">
        {header.length > 0 && (
          <thead className="sticky top-0 z-10 bg-ds-surface-2">
            <tr>
              {header.map((h, i) => (
                <th
                  key={`th-${i}`}
                  className="min-w-36 border-b border-r border-ds-border px-4 py-3 align-top font-semibold text-ds-fg last:border-r-0"
                >
                  <div className="flex items-center gap-2">{renderCell(h)}</div>
                </th>
              ))}
            </tr>
          </thead>
        )}
        <tbody>
          {rows.map((row, r) => (
            <tr
              key={`tr-${r}`}
              className="transition-colors duration-ds-fast hover:bg-ds-primary-soft"
            >
              {row.map((cell, c) => (
                <td
                  key={`td-${r}-${c}`}
                  className={`min-w-36 whitespace-pre-wrap border-b border-r border-ds-border px-4 py-3 align-top text-ds-fg-muted last:border-r-0 ${r === rows.length - 1 ? 'border-b-0' : ''} ${r % 2 === 1 ? 'bg-ds-surface-2' : ''}`}
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
