import React from 'react';

export interface TableBlockProps {
  header: string[];
  rows: string[][];
}

const TableBlock: React.FC<TableBlockProps> = ({ header, rows }) => {
  return (
    <div className="overflow-x-auto my-4 not-prose">
      <table className="w-full border-collapse text-sm">
        {header.length > 0 && (
          <thead className="bg-gray-50 dark:bg-gray-800">
            <tr className="border-b border-gray-200 dark:border-gray-700">
              {header.map((h, i) => (
                <th
                  key={`th-${i}`}
                  className="text-left font-semibold px-3 py-2 align-top border border-gray-200 dark:border-gray-700 whitespace-nowrap"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
        )}
        <tbody>
          {rows.map((row, r) => (
            <tr key={`tr-${r}`} className="border-b last:border-0 border-gray-200 dark:border-gray-700">
              {row.map((cell, c) => (
                <td
                  key={`td-${r}-${c}`}
                  className="px-3 py-2 align-top border border-gray-200 dark:border-gray-700 whitespace-pre-wrap"
                >
                  {cell}
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
