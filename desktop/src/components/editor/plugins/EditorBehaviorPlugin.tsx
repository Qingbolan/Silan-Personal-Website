import React from 'react';
import { useLexicalComposerContext } from '@lexical/react/LexicalComposerContext';
import { DraggableBlockPlugin_EXPERIMENTAL } from '@lexical/react/LexicalDraggableBlockPlugin';
import { registerCodeHighlighting } from '@lexical/code';
import { $getExtensionOutput } from '@lexical/extension';
import { MdastImportExtension } from '@lexical/mdast';
import {
  $createParagraphNode,
  $getNearestNodeFromDOMNode,
  $getSelection,
  $isRangeSelection,
  COMMAND_PRIORITY_HIGH,
  KEY_DOWN_COMMAND,
  PASTE_COMMAND,
  type EditorState,
} from 'lexical';
import { GripVertical, Plus } from 'lucide-react';
import {
  EditorShortcutController,
  resolveEditorShortcut,
  type EditorShortcutResult,
} from '../interaction/EditorShortcutController';
import { $insertMarkdown } from '../model/MarkdownDocument';
import { MarkdownSourceProjector } from '../model/MarkdownSourceProjection';

export function MarkdownPastePlugin({ disabled }: { disabled: boolean }) {
  const [editor] = useLexicalComposerContext();
  const sourceProjector = React.useMemo(() => editor.read(() => (
    new MarkdownSourceProjector($getExtensionOutput(MdastImportExtension).registry)
  )), [editor]);

  React.useEffect(() => editor.registerCommand(
    PASTE_COMMAND,
    (event) => {
      if (disabled || !('clipboardData' in event) || !event.clipboardData) return false;
      const explicitMarkdown = event.clipboardData.getData('text/markdown');
      const plainText = event.clipboardData.getData('text/plain');
      const html = event.clipboardData.getData('text/html');
      const markdown = explicitMarkdown
        || (!html && sourceProjector.hasSyntax(plainText) ? plainText : '');
      if (!markdown) return false;
      event.preventDefault();
      return $insertMarkdown(markdown);
    },
    COMMAND_PRIORITY_HIGH,
  ), [disabled, editor, sourceProjector]);

  return null;
}

export function CodeHighlightPlugin() {
  const [editor] = useLexicalComposerContext();
  React.useEffect(() => registerCodeHighlighting(editor), [editor]);
  return null;
}

export function ActiveBlockPlugin({ disabled }: { disabled: boolean }) {
  const [editor] = useLexicalComposerContext();

  React.useEffect(() => {
    let activeElement: HTMLElement | null = null;

    const clearActiveElement = () => {
      activeElement?.classList.remove('lexical-active-block');
      activeElement = null;
    };

    if (disabled) {
      clearActiveElement();
      return undefined;
    }

    const markActiveElement = (editorState: EditorState) => {
      const activeKey = editorState.read(() => {
        const selection = $getSelection();
        if (!$isRangeSelection(selection)) return null;
        return selection.anchor.getNode().getTopLevelElement()?.getKey() || null;
      });
      const nextElement = activeKey ? editor.getElementByKey(activeKey) : null;
      if (nextElement === activeElement) return;
      clearActiveElement();
      activeElement = nextElement;
      activeElement?.classList.add('lexical-active-block');
    };

    const unregisterUpdate = editor.registerUpdateListener(({ editorState }) => {
      markActiveElement(editorState);
    });
    const unregisterRoot = editor.registerRootListener(() => {
      markActiveElement(editor.getEditorState());
    });

    return () => {
      unregisterUpdate();
      unregisterRoot();
      clearActiveElement();
    };
  }, [disabled, editor]);

  return null;
}

export function EditorKeymapPlugin({
  onToggleSourceMode,
}: {
  onToggleSourceMode: () => void;
}) {
  const [editor] = useLexicalComposerContext();
  const controller = React.useMemo(() => new EditorShortcutController(editor, {
    toggleSourceMode: onToggleSourceMode,
  }), [editor, onToggleSourceMode]);
  const [notice, setNotice] = React.useState<EditorShortcutResult>(null);

  React.useEffect(() => {
    if (!notice) return undefined;
    const timeout = window.setTimeout(() => setNotice(null), 2400);
    return () => window.clearTimeout(timeout);
  }, [notice]);

  React.useEffect(() => editor.registerCommand(
    KEY_DOWN_COMMAND,
    (event) => {
      const action = resolveEditorShortcut(event);
      if (!action) return false;
      event.preventDefault();
      void controller.run(action).then(setNotice);
      return true;
    },
    COMMAND_PRIORITY_HIGH,
  ), [controller, editor]);

  return notice ? (
    <div
      className="lexical-editor-shortcut-status"
      data-state={notice.phase}
      role={notice.phase === 'error' ? 'alert' : 'status'}
    >
      {notice.message}
    </div>
  ) : null;
}

export function BlockDragPlugin({ disabled }: { disabled: boolean }) {
  const [editor] = useLexicalComposerContext();
  const menuRef = React.useRef<HTMLDivElement | null>(null);
  const targetLineRef = React.useRef<HTMLDivElement | null>(null);
  const activeBlockRef = React.useRef<HTMLElement | null>(null);
  const [anchor, setAnchor] = React.useState<HTMLElement | null>(null);

  React.useEffect(() => editor.registerRootListener((root) => {
    setAnchor(root?.parentElement || null);
  }), [editor]);

  const insertParagraphAfter = React.useCallback(() => {
    const activeBlock = activeBlockRef.current;
    if (!activeBlock) return;
    editor.update(() => {
      const target = $getNearestNodeFromDOMNode(activeBlock)?.getTopLevelElement();
      if (!target) return;
      const paragraph = $createParagraphNode();
      target.insertAfter(paragraph);
      paragraph.selectStart();
    }, { onUpdate: () => editor.focus() });
  }, [editor]);

  if (disabled || !anchor) return null;
  return (
    <DraggableBlockPlugin_EXPERIMENTAL
      anchorElem={anchor}
      menuRef={menuRef}
      targetLineRef={targetLineRef}
      menuComponent={(
        <div ref={menuRef} className="block-controls" role="group" aria-label="Block controls">
          <button
            type="button"
            className="block-controls__add"
            aria-label="Add block below"
            title="Add block below"
            onMouseDown={(event) => {
              event.preventDefault();
              event.stopPropagation();
            }}
            onClick={insertParagraphAfter}
          >
            <Plus size={15} />
          </button>
          <span className="drag-handle" aria-hidden="true" title="Drag to move block">
            <GripVertical size={15} />
          </span>
        </div>
      )}
      targetLineComponent={<div ref={targetLineRef} className="lexical-block-drop-line" />}
      isOnMenu={(element) => menuRef.current?.contains(element) === true}
      onElementChanged={(element) => {
        activeBlockRef.current = element;
      }}
    />
  );
}
