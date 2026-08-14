import React from 'react';
import { useLexicalComposerContext } from '@lexical/react/LexicalComposerContext';
import {
  AlignCenter,
  AlignLeft,
  AlignRight,
  ArrowDownToLine,
  ArrowLeftToLine,
  ArrowRightToLine,
  ArrowUpToLine,
  Columns3,
  Rows3,
  TableCellsMerge,
  Trash2,
  type LucideIcon,
} from 'lucide-react';
import {
  $readTableToolbarState,
  sameTableToolbarState,
  TableEditingController,
  type TableToolbarAction,
  type TableToolbarState,
} from '../interaction/TableEditingController';
import {
  OverlayPositionController,
  readEditorToolbarInset,
  type OverlayPosition,
} from '../interaction/OverlayPositionController';
import { readEditorSnapshot } from '../model/MarkdownDocument';

type TableToolbarButton = {
  action: TableToolbarAction;
  alignment?: 'left' | 'center' | 'right';
  dividerBefore?: boolean;
  icon: LucideIcon;
  label: string;
  danger?: boolean;
};

const buttons: TableToolbarButton[] = [
  { action: 'align-left', alignment: 'left', icon: AlignLeft, label: 'Align column left' },
  { action: 'align-center', alignment: 'center', icon: AlignCenter, label: 'Align column center' },
  { action: 'align-right', alignment: 'right', icon: AlignRight, label: 'Align column right' },
  { action: 'insert-row-above', dividerBefore: true, icon: ArrowUpToLine, label: 'Insert row above' },
  { action: 'insert-row-below', icon: ArrowDownToLine, label: 'Insert row below' },
  { action: 'insert-column-before', icon: ArrowLeftToLine, label: 'Insert column before' },
  { action: 'insert-column-after', icon: ArrowRightToLine, label: 'Insert column after' },
  { action: 'delete-row', dividerBefore: true, icon: Rows3, label: 'Delete selected row', danger: true },
  { action: 'delete-column', icon: Columns3, label: 'Delete selected column', danger: true },
  { action: 'delete-table', icon: Trash2, label: 'Delete table', danger: true },
];

const hiddenPosition: OverlayPosition = {
  left: 0,
  placement: 'above',
  top: 0,
  visible: false,
};

export function TableToolbarPlugin({
  disabled,
  offsetForMainToolbar,
}: {
  disabled: boolean;
  offsetForMainToolbar: boolean;
}) {
  const [editor] = useLexicalComposerContext();
  const controller = React.useMemo(() => new TableEditingController(editor), [editor]);
  const [state, setState] = React.useState<TableToolbarState | null>(null);
  const toolbarRef = React.useRef<HTMLDivElement | null>(null);
  const [position, setPosition] = React.useState(hiddenPosition);

  React.useEffect(() => {
    const update = (next: TableToolbarState | null) => {
      setState((current) => (sameTableToolbarState(current, next) ? current : next));
    };
    update(controller.readState());
    return editor.registerUpdateListener(({ editorState }) => {
      update(readEditorSnapshot(editor, editorState, $readTableToolbarState));
    });
  }, [controller, editor]);

  React.useLayoutEffect(() => {
    const toolbar = toolbarRef.current;
    const root = editor.getRootElement()?.parentElement;
    const cell = state ? editor.getElementByKey(state.cellKey) : null;
    if (!state || !toolbar || !root || !cell) return undefined;
    const mainToolbar = offsetForMainToolbar
      ? root.parentElement?.querySelector<HTMLElement>('.novel-toolbar') || null
      : null;
    setPosition(hiddenPosition);
    const positioning = new OverlayPositionController({
      container: root,
      observedElements: [cell, ...(mainToolbar ? [mainToolbar] : [])],
      onPosition: setPosition,
      options: { minTop: () => readEditorToolbarInset(root, offsetForMainToolbar) },
      overlay: toolbar,
      readAnchor: () => cell.getBoundingClientRect(),
    });
    positioning.connect();
    return () => positioning.dispose();
  }, [editor, offsetForMainToolbar, state]);

  if (!state || disabled) return null;

  return (
    <div
      ref={toolbarRef}
      className="lexical-table-toolbar"
      data-placement={position.placement}
      data-positioned={position.visible ? 'true' : 'false'}
      role="toolbar"
      aria-label="Table actions"
      style={{
        left: position.left,
        top: position.top,
        visibility: position.visible ? 'visible' : 'hidden',
      }}
    >
      <span className="lexical-table-toolbar__context">
        <TableCellsMerge size={14} />
        <span>
          Row {state.rowIndex + 1}/{state.rowCount}
          <i aria-hidden="true">·</i>
          Column {state.columnIndex + 1}/{state.columnCount}
        </span>
      </span>
      <span className="lexical-table-toolbar__divider" aria-hidden="true" />
      <div className="lexical-table-toolbar__actions">
        {buttons.map(({ action, alignment, danger, dividerBefore, icon: Icon, label }) => {
          const active = alignment === 'left'
            ? state.columnAlignment === null || state.columnAlignment === 'left'
            : alignment === state.columnAlignment;
          return (
          <React.Fragment key={action}>
            {dividerBefore && (
              <span className="lexical-table-toolbar__divider" aria-hidden="true" />
            )}
            <button
              type="button"
              className={active ? 'active' : ''}
              data-danger={danger ? 'true' : 'false'}
              aria-label={label}
              aria-pressed={alignment ? active : undefined}
              title={label}
              onMouseDown={(event) => event.preventDefault()}
              onClick={() => controller.run(action)}
            >
              <Icon size={14} />
            </button>
          </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
