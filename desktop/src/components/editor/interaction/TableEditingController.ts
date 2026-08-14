import {
  $deleteTableColumnAtSelection,
  $deleteTableRowAtSelection,
  $getNodeTriplet,
  $getTableColumnIndexFromTableCellNode,
  $getTableRowIndexFromTableCellNode,
  $insertTableColumnAtSelection,
  $insertTableRowAtSelection,
  $isTableRowNode,
  $isTableSelection,
  type TableNode,
} from '@lexical/table';
import {
  $createParagraphNode,
  $getSelection,
  $isRangeSelection,
  type LexicalEditor,
} from 'lexical';
import {
  $deleteMarkdownTableAlignment,
  $getMarkdownTableAlignments,
  $insertMarkdownTableAlignment,
  $setMarkdownTableColumnAlignment,
  type MarkdownTableAlignment,
} from '../model/MarkdownTable';

export type TableToolbarAction =
  | 'insert-row-above'
  | 'insert-row-below'
  | 'insert-column-before'
  | 'insert-column-after'
  | 'delete-row'
  | 'delete-column'
  | 'delete-table'
  | 'align-left'
  | 'align-center'
  | 'align-right';

export type TableToolbarState = {
  cellKey: string;
  columnCount: number;
  columnAlignment: MarkdownTableAlignment | null;
  columnIndex: number;
  rowCount: number;
  rowIndex: number;
  tableKey: string;
};

export function $readTableToolbarState(): TableToolbarState | null {
  const selection = $getSelection();
  if ($isRangeSelection(selection) && !selection.isCollapsed()) return null;
  if (!$isRangeSelection(selection) && !$isTableSelection(selection)) return null;
  try {
    const [cell, , table] = $getNodeTriplet(selection.anchor);
    const firstRow = table.getFirstChild();
    return {
      cellKey: cell.getKey(),
      columnCount: $isTableRowNode(firstRow) ? firstRow.getChildrenSize() : 0,
      columnAlignment: $getMarkdownTableAlignments(table)[
        $getTableColumnIndexFromTableCellNode(cell)
      ] || null,
      columnIndex: $getTableColumnIndexFromTableCellNode(cell),
      rowCount: table.getChildrenSize(),
      rowIndex: $getTableRowIndexFromTableCellNode(cell),
      tableKey: table.getKey(),
    };
  } catch {
    return null;
  }
}

export function sameTableToolbarState(
  left: TableToolbarState | null,
  right: TableToolbarState | null,
) {
  if (left === right) return true;
  if (!left || !right) return false;
  return left.columnCount === right.columnCount
    && left.cellKey === right.cellKey
    && left.columnAlignment === right.columnAlignment
    && left.columnIndex === right.columnIndex
    && left.rowCount === right.rowCount
    && left.rowIndex === right.rowIndex
    && left.tableKey === right.tableKey;
}

function $withSelectionRecoveryAfterTableMutation(table: TableNode, mutate: () => void) {
  const parent = table.getParentOrThrow();
  const next = table.getNextSibling();
  const previous = table.getPreviousSibling();
  mutate();
  if (table.isAttached()) return;
  if (next?.isAttached()) {
    next.selectStart();
    return;
  }
  if (previous?.isAttached()) {
    previous.selectEnd();
    return;
  }
  const paragraph = $createParagraphNode();
  parent.append(paragraph);
  paragraph.selectStart();
}

export function runTableToolbarAction(editor: LexicalEditor, action: TableToolbarAction) {
  editor.update(() => {
    const selection = $getSelection();
    if (!$isRangeSelection(selection) && !$isTableSelection(selection)) return;
    const [cell, , table] = $getNodeTriplet(selection.anchor);
    const columnIndex = $getTableColumnIndexFromTableCellNode(cell);
    switch (action) {
      case 'insert-row-above':
        $insertTableRowAtSelection(false);
        break;
      case 'insert-row-below':
        $insertTableRowAtSelection(true);
        break;
      case 'insert-column-before':
        $insertTableColumnAtSelection(false);
        $insertMarkdownTableAlignment(table, columnIndex);
        break;
      case 'insert-column-after':
        $insertTableColumnAtSelection(true);
        $insertMarkdownTableAlignment(table, columnIndex + 1);
        break;
      case 'delete-row':
        $withSelectionRecoveryAfterTableMutation(table, $deleteTableRowAtSelection);
        break;
      case 'delete-column':
        $withSelectionRecoveryAfterTableMutation(table, () => {
          $deleteTableColumnAtSelection();
          if (table.isAttached()) $deleteMarkdownTableAlignment(table, columnIndex);
        });
        break;
      case 'delete-table':
        $withSelectionRecoveryAfterTableMutation(table, () => table.remove());
        break;
      case 'align-left':
      case 'align-center':
      case 'align-right':
        $setMarkdownTableColumnAlignment(
          table,
          columnIndex,
          action === 'align-left'
            ? 'left'
            : action === 'align-center'
              ? 'center'
              : 'right',
        );
        break;
    }
  }, { discrete: true });
  if (typeof window !== 'undefined') {
    window.requestAnimationFrame(() => editor.focus());
  }
}

export class TableEditingController {
  readonly #editor: LexicalEditor;

  constructor(editor: LexicalEditor) {
    this.#editor = editor;
  }

  readState() {
    return this.#editor.read(() => $readTableToolbarState());
  }

  run(action: TableToolbarAction) {
    runTableToolbarAction(this.#editor, action);
  }
}
