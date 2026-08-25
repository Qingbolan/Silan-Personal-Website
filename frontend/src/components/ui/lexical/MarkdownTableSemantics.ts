import { configExtension } from '@lexical/extension';
import {
  MdastImportExtension,
  type MdastExportHandler,
  type MdastImportHandler,
} from '@lexical/mdast';
import {
  $createTableCellNode,
  $createTableNode,
  $createTableRowNode,
  $isTableCellNode,
  $isTableNode,
  $isTableRowNode,
  TableCellHeaderStates,
} from '@lexical/table';
import {
  $createParagraphNode,
  $getState,
  $isElementNode,
  $setState,
  createState,
  defineExtension,
} from 'lexical';
import type { AlignType, Table, TableCell, TableRow } from 'mdast';

const parseAlignment = (value: unknown): AlignType => (
  value === 'left' || value === 'center' || value === 'right' ? value : null
);

const sameAlignments = (left: AlignType[], right: AlignType[]) => (
  left.length === right.length
  && left.every((alignment, index) => alignment === right[index])
);

const markdownTableAlignState = createState('silanMarkdownTableAlign', {
  isEqual: sameAlignments,
  parse: (value): AlignType[] => (
    Array.isArray(value) ? value.map(parseAlignment) : []
  ),
});

const $importTable: MdastImportHandler<Table> = (node, context) => {
  const table = $createTableNode();
  const alignments = node.align?.map(parseAlignment) ?? [];
  $setState(table, markdownTableAlignState, alignments);

  node.children.forEach((row, rowIndex) => {
    const rowNode = $createTableRowNode();
    row.children.forEach((cell, columnIndex) => {
      const cellNode = $createTableCellNode(
        rowIndex === 0
          ? TableCellHeaderStates.ROW
          : TableCellHeaderStates.NO_STATUS,
      );
      const paragraph = $createParagraphNode();
      paragraph.setFormat(alignments[columnIndex] ?? '');
      paragraph.append(...context.importChildren(cell));
      cellNode.append(paragraph);
      rowNode.append(cellNode);
    });
    table.append(rowNode);
  });

  return table;
};

const $exportTable: MdastExportHandler = (node, context) => {
  if (!$isTableNode(node)) return null;
  const rows: TableRow[] = [];

  node.getChildren().forEach((row) => {
    if (!$isTableRowNode(row) || !context.isIncluded(row)) return;
    const cells: TableCell[] = [];
    row.getChildren().forEach((cell) => {
      if (!$isTableCellNode(cell)) return;
      const children: TableCell['children'] = [];
      cell.getChildren().forEach((child) => {
        if (!$isElementNode(child)) return;
        if (children.length > 0) children.push({ type: 'break' });
        children.push(...context.exportInline(child));
      });
      cells.push({ children, type: 'tableCell' });
    });
    rows.push({ children: cells, type: 'tableRow' });
  });

  return {
    align: $getState(node, markdownTableAlignState),
    children: rows,
    type: 'table',
  } as Table;
};

/**
 * Keep the public renderer's GFM table state identical to the desktop editor:
 * mdast owns tokenization while this extension maps alignment to Lexical.
 */
export const MarkdownTableSemanticsExtension = defineExtension({
  dependencies: [
    configExtension(MdastImportExtension, {
      exportRules: [{ $export: $exportTable, type: 'table' }],
      importRules: [{ $import: $importTable, type: 'table' }],
    }),
  ],
  name: 'silan/markdown-table-semantics',
});

