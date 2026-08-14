import { $convertSelectionToMarkdownString } from '@lexical/mdast';
import {
  $getSelection,
  $isRangeSelection,
  createCommand,
  type LexicalEditor,
} from 'lexical';
import {
  FormattingController,
  type BlockFormat,
  type FormattingCommand,
} from './FormattingController';
import { OPEN_IMAGE_PICKER_COMMAND } from './ImageEditingController';
import { $captureSelectionRange, $tryRestoreSelectionRange } from '../model/SelectionRange';

export const OPEN_LINK_EDITOR_COMMAND = createCommand<void>('OPEN_LINK_EDITOR_COMMAND');

export type EditorShortcutAction =
  | { kind: 'adjust-heading'; delta: -1 | 1 }
  | { kind: 'block'; block: BlockFormat }
  | { kind: 'copy-markdown' }
  | { kind: 'format'; command: FormattingCommand }
  | { kind: 'open-image' }
  | { kind: 'open-link' }
  | { kind: 'paste-plain' }
  | { kind: 'toggle-source' };

export type ShortcutGesture = Pick<
  KeyboardEvent,
  'altKey' | 'ctrlKey' | 'key' | 'metaKey' | 'shiftKey'
>;

export type EditorShortcutResult = {
  phase: 'complete' | 'error';
  message: string;
} | null;

type ClipboardPort = Pick<Clipboard, 'readText' | 'writeText'>;

export function resolveEditorShortcut(
  event: ShortcutGesture,
  mode: 'rich' | 'source' = 'rich',
): EditorShortcutAction | null {
  const primary = event.metaKey || event.ctrlKey;
  if (!primary) return null;
  const key = event.key.toLocaleLowerCase();

  if (key === '/' && !event.altKey && !event.shiftKey) return { kind: 'toggle-source' };
  if (mode === 'source') return null;

  if (event.shiftKey && !event.altKey && key === 'c') return { kind: 'copy-markdown' };
  if (event.shiftKey && !event.altKey && key === 'v') return { kind: 'paste-plain' };
  if (!event.altKey && !event.shiftKey && key === 'k') return { kind: 'open-link' };
  if (!event.altKey && !event.shiftKey && key === '\\') {
    return { kind: 'format', command: 'clear-format' };
  }
  if (!event.altKey && !event.shiftKey && key === '=') {
    return { kind: 'adjust-heading', delta: -1 };
  }
  if (!event.altKey && !event.shiftKey && key === '-') {
    return { kind: 'adjust-heading', delta: 1 };
  }
  if (!event.altKey && !event.shiftKey && /^[0-6]$/.test(key)) {
    return { kind: 'block', block: key === '0' ? 'paragraph' : `h${key}` as BlockFormat };
  }

  const macImage = event.metaKey && event.ctrlKey && !event.shiftKey && key === 'i';
  const otherImage = !event.metaKey && event.ctrlKey && event.shiftKey && key === 'i';
  if (macImage || otherImage) return { kind: 'open-image' };

  const macParagraphCommand = event.metaKey && event.altKey;
  if (macParagraphCommand && key === 't') return { kind: 'format', command: 'table' };
  if (macParagraphCommand && key === 'q') return { kind: 'block', block: 'quote' };
  if (macParagraphCommand && key === 'c') return { kind: 'block', block: 'code' };
  if (macParagraphCommand && key === 'o') return { kind: 'format', command: 'ordered-list' };
  if (macParagraphCommand && key === 'u') return { kind: 'format', command: 'bullet-list' };

  if (!event.metaKey && event.ctrlKey && !event.altKey && !event.shiftKey && key === 't') {
    return { kind: 'format', command: 'table' };
  }
  if (!event.metaKey && event.ctrlKey && event.shiftKey && key === 'q') {
    return { kind: 'block', block: 'quote' };
  }
  if (!event.metaKey && event.ctrlKey && event.shiftKey && key === 'k') {
    return { kind: 'block', block: 'code' };
  }
  if (!event.metaKey && event.ctrlKey && event.shiftKey && key === '[') {
    return { kind: 'format', command: 'ordered-list' };
  }
  if (!event.metaKey && event.ctrlKey && event.shiftKey && key === ']') {
    return { kind: 'format', command: 'bullet-list' };
  }

  if (event.shiftKey && key === 's') return { kind: 'format', command: 'strike' };
  if (event.shiftKey && key === '8') return { kind: 'format', command: 'bullet-list' };
  if (event.shiftKey && key === '7') return { kind: 'format', command: 'ordered-list' };
  if (event.shiftKey && (key === '`' || key === '~')) {
    return { kind: 'format', command: 'inline-code' };
  }
  if (!event.altKey && !event.shiftKey && key === 'e') {
    return { kind: 'format', command: 'inline-code' };
  }
  return null;
}

export class EditorShortcutController {
  readonly #editor: LexicalEditor;
  readonly #formatting: FormattingController;
  readonly #clipboard: ClipboardPort | null;
  readonly #toggleSourceMode: () => void;

  constructor(
    editor: LexicalEditor,
    {
      clipboard = typeof navigator === 'undefined' ? null : navigator.clipboard,
      toggleSourceMode,
    }: {
      clipboard?: ClipboardPort | null;
      toggleSourceMode: () => void;
    },
  ) {
    this.#editor = editor;
    this.#formatting = new FormattingController(editor);
    this.#clipboard = clipboard;
    this.#toggleSourceMode = toggleSourceMode;
  }

  async run(action: EditorShortcutAction): Promise<EditorShortcutResult> {
    switch (action.kind) {
      case 'block':
        this.#formatting.setBlock(action.block);
        return null;
      case 'format':
        this.#formatting.run(action.command);
        return null;
      case 'adjust-heading':
        this.#formatting.adjustHeading(action.delta);
        return null;
      case 'open-image':
        this.#editor.dispatchCommand(OPEN_IMAGE_PICKER_COMMAND, undefined);
        return null;
      case 'open-link':
        this.#editor.dispatchCommand(OPEN_LINK_EDITOR_COMMAND, undefined);
        return null;
      case 'toggle-source':
        this.#toggleSourceMode();
        return null;
      case 'copy-markdown':
        return this.#copyMarkdown();
      case 'paste-plain':
        return this.#pastePlainText();
    }
  }

  async #copyMarkdown(): Promise<EditorShortcutResult> {
    if (!this.#clipboard) return { phase: 'error', message: 'Clipboard is unavailable' };
    const markdown = this.#editor.read(() => $convertSelectionToMarkdownString());
    if (!markdown) return { phase: 'error', message: 'Select content to copy as Markdown' };
    try {
      await this.#clipboard.writeText(markdown);
      return { phase: 'complete', message: 'Markdown copied' };
    } catch (reason) {
      return { phase: 'error', message: `Copy failed: ${String(reason)}` };
    }
  }

  async #pastePlainText(): Promise<EditorShortcutResult> {
    if (!this.#clipboard) return { phase: 'error', message: 'Clipboard is unavailable' };
    const range = this.#editor.read(() => $captureSelectionRange());
    if (!range) return { phase: 'error', message: 'Place the caret before pasting' };
    try {
      const text = await this.#clipboard.readText();
      let inserted = false;
      this.#editor.update(() => {
        const selection = $tryRestoreSelectionRange(range);
        if (!selection) return;
        selection.insertRawText(text);
        inserted = true;
      }, { discrete: true });
      return inserted
        ? { phase: 'complete', message: 'Plain text pasted' }
        : { phase: 'error', message: 'Selection changed before paste completed' };
    } catch (reason) {
      return { phase: 'error', message: `Paste failed: ${String(reason)}` };
    }
  }
}
