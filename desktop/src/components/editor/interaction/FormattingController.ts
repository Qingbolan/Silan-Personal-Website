import { $createCodeNode, $isCodeNode } from '@lexical/code';
import { INSERT_HORIZONTAL_RULE_COMMAND } from '@lexical/extension';
import { $isLinkNode, $toggleLink } from '@lexical/link';
import {
  $isListNode,
  INSERT_CHECK_LIST_COMMAND,
  INSERT_ORDERED_LIST_COMMAND,
  INSERT_UNORDERED_LIST_COMMAND,
  REMOVE_LIST_COMMAND,
} from '@lexical/list';
import {
  $createHeadingNode,
  $createQuoteNode,
  $isHeadingNode,
  $isQuoteNode,
  type HeadingTagType,
} from '@lexical/rich-text';
import { $forEachSelectedTextNode, $setBlocksType } from '@lexical/selection';
import { $isTableNode, INSERT_TABLE_COMMAND } from '@lexical/table';
import { $findMatchingParent } from '@lexical/utils';
import {
  $createParagraphNode,
  $getSelection,
  $isRangeSelection,
  FORMAT_TEXT_COMMAND,
  REDO_COMMAND,
  UNDO_COMMAND,
  type ElementNode,
  type LexicalEditor,
} from 'lexical';
import type { MarkdownSelectionRange } from '../extensionPoints';
import { $tryRestoreSelectionRange } from '../model/SelectionRange';
import { $isDocumentTitleNode } from '../model/DocumentTitle';

export type BlockFormat =
  | 'title'
  | 'paragraph'
  | 'h1'
  | 'h2'
  | 'h3'
  | 'h4'
  | 'h5'
  | 'h6'
  | 'quote'
  | 'code';

export type FormattingCommand =
  | 'bold'
  | 'italic'
  | 'underline'
  | 'strike'
  | 'bullet-list'
  | 'ordered-list'
  | 'check-list'
  | 'inline-code'
  | 'clear-format'
  | 'divider'
  | 'table'
  | 'undo'
  | 'redo';

export type FormattingSnapshot = {
  block: BlockFormat;
  bold: boolean;
  bulletList: boolean;
  checkList: boolean;
  codeLanguage: string;
  inlineCode: boolean;
  italic: boolean;
  link: boolean;
  linkHref: string;
  orderedList: boolean;
  strike: boolean;
  table: boolean;
  underline: boolean;
};

export const EMPTY_FORMATTING_SNAPSHOT: FormattingSnapshot = {
  block: 'paragraph',
  bold: false,
  bulletList: false,
  checkList: false,
  codeLanguage: '',
  inlineCode: false,
  italic: false,
  link: false,
  linkHref: '',
  orderedList: false,
  strike: false,
  table: false,
  underline: false,
};

export function $readFormattingSnapshot(): FormattingSnapshot {
  const selection = $getSelection();
  if (!$isRangeSelection(selection)) return EMPTY_FORMATTING_SNAPSHOT;

  const node = selection.anchor.getNode();
  const list = $findMatchingParent(node, $isListNode);
  const heading = $findMatchingParent(node, $isHeadingNode);
  const link = $findMatchingParent(node, $isLinkNode);
  const code = $findMatchingParent(node, $isCodeNode);
  const block: BlockFormat = heading
    ? $isDocumentTitleNode(heading)
      ? 'title'
      : (heading.getTag() as HeadingTagType)
    : $findMatchingParent(node, $isQuoteNode)
      ? 'quote'
      : code
        ? 'code'
        : 'paragraph';

  return {
    block,
    bold: selection.hasFormat('bold'),
    bulletList: list?.getListType() === 'bullet',
    checkList: list?.getListType() === 'check',
    codeLanguage: code?.getLanguage() || '',
    inlineCode: selection.hasFormat('code'),
    italic: selection.hasFormat('italic'),
    link: Boolean(link),
    linkHref: link?.getURL() || '',
    orderedList: list?.getListType() === 'number',
    strike: selection.hasFormat('strikethrough'),
    table: Boolean($findMatchingParent(node, $isTableNode)),
    underline: selection.hasFormat('underline'),
  };
}

export function setBlockFormat(editor: LexicalEditor, block: BlockFormat) {
  if (block === 'title') return;
  editor.update(() => {
    const selection = $getSelection();
    if (!$isRangeSelection(selection)) return;
    $setBlocksType<ElementNode>(selection, () => {
      if (block === 'quote') return $createQuoteNode();
      if (block === 'code') return $createCodeNode();
      if (block !== 'paragraph') return $createHeadingNode(block);
      return $createParagraphNode();
    });
  }, { discrete: true });
}

export function runFormattingCommand(editor: LexicalEditor, command: FormattingCommand) {
  switch (command) {
    case 'bold':
      editor.dispatchCommand(FORMAT_TEXT_COMMAND, 'bold');
      return;
    case 'italic':
      editor.dispatchCommand(FORMAT_TEXT_COMMAND, 'italic');
      return;
    case 'underline':
      editor.dispatchCommand(FORMAT_TEXT_COMMAND, 'underline');
      return;
    case 'strike':
      editor.dispatchCommand(FORMAT_TEXT_COMMAND, 'strikethrough');
      return;
    case 'inline-code':
      editor.dispatchCommand(FORMAT_TEXT_COMMAND, 'code');
      return;
    case 'clear-format':
      editor.dispatchCommand(REMOVE_LIST_COMMAND, undefined);
      editor.update(() => {
        const selection = $getSelection();
        if (!$isRangeSelection(selection)) return;
        $forEachSelectedTextNode((node) => node.setFormat(0).setStyle(''));
        $toggleLink(null);
        if (!$findMatchingParent(selection.anchor.getNode(), $isTableNode)) {
          $setBlocksType(selection, () => $createParagraphNode());
        }
      }, { discrete: true });
      return;
    case 'undo':
      editor.dispatchCommand(UNDO_COMMAND, undefined);
      return;
    case 'redo':
      editor.dispatchCommand(REDO_COMMAND, undefined);
      return;
    case 'divider':
      editor.dispatchCommand(INSERT_HORIZONTAL_RULE_COMMAND, undefined);
      return;
    case 'table':
      editor.dispatchCommand(INSERT_TABLE_COMMAND, {
        columns: '3',
        includeHeaders: { columns: false, rows: true },
        rows: '3',
      });
      return;
    case 'bullet-list':
    case 'ordered-list':
    case 'check-list': {
      const active = editor.read(() => {
        const snapshot = $readFormattingSnapshot();
        return command === 'bullet-list'
          ? snapshot.bulletList
          : command === 'ordered-list'
            ? snapshot.orderedList
            : snapshot.checkList;
      });
      editor.dispatchCommand(
        active
          ? REMOVE_LIST_COMMAND
          : command === 'bullet-list'
            ? INSERT_UNORDERED_LIST_COMMAND
            : command === 'ordered-list'
              ? INSERT_ORDERED_LIST_COMMAND
              : INSERT_CHECK_LIST_COMMAND,
        undefined,
      );
    }
  }
}

export function adjustHeadingLevel(editor: LexicalEditor, delta: -1 | 1) {
  const current = editor.read(() => $readFormattingSnapshot().block);
  if (current === 'title' || current === 'quote' || current === 'code') return;
  if (current === 'paragraph') {
    if (delta < 0) setBlockFormat(editor, 'h6');
    return;
  }
  const level = Number(current.slice(1));
  const next = level + delta;
  setBlockFormat(
    editor,
    next > 6 ? 'paragraph' : `h${Math.max(1, next)}` as BlockFormat,
  );
}

export class FormattingController {
  readonly #editor: LexicalEditor;

  constructor(editor: LexicalEditor) {
    this.#editor = editor;
  }

  readSnapshot() {
    return this.#editor.read(() => $readFormattingSnapshot());
  }

  run(command: FormattingCommand) {
    runFormattingCommand(this.#editor, command);
  }

  setBlock(block: BlockFormat) {
    setBlockFormat(this.#editor, block);
  }

  adjustHeading(delta: -1 | 1) {
    adjustHeadingLevel(this.#editor, delta);
  }

  setCodeLanguage(language: string) {
    this.#editor.update(() => {
      const selection = $getSelection();
      if (!$isRangeSelection(selection)) return;
      $findMatchingParent(selection.anchor.getNode(), $isCodeNode)?.setLanguage(language || undefined);
    }, { discrete: true });
  }

  setLink(href: string | null, range?: MarkdownSelectionRange | null) {
    this.#editor.update(() => {
      if (range && !$tryRestoreSelectionRange(range)) return;
      $toggleLink(href);
    }, { discrete: true });
  }
}
