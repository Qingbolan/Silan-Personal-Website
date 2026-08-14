import React from 'react';
import { useLexicalComposerContext } from '@lexical/react/LexicalComposerContext';
import { DraggableBlockPlugin_EXPERIMENTAL } from '@lexical/react/LexicalDraggableBlockPlugin';
import { registerCodeHighlighting } from '@lexical/code';
import { $getExtensionOutput } from '@lexical/extension';
import { MdastImportExtension } from '@lexical/mdast';
import {
  COMMAND_PRIORITY_HIGH,
  KEY_DOWN_COMMAND,
  PASTE_COMMAND,
} from 'lexical';
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
  const [anchor, setAnchor] = React.useState<HTMLElement | null>(null);

  React.useEffect(() => editor.registerRootListener((root) => {
    setAnchor(root?.parentElement || null);
  }), [editor]);

  if (disabled || !anchor) return null;
  return (
    <DraggableBlockPlugin_EXPERIMENTAL
      anchorElem={anchor}
      menuRef={menuRef}
      targetLineRef={targetLineRef}
      menuComponent={<div ref={menuRef} className="drag-handle" aria-label="Move block" />}
      targetLineComponent={<div ref={targetLineRef} className="lexical-block-drop-line" />}
      isOnMenu={(element) => menuRef.current?.contains(element) === true}
    />
  );
}
