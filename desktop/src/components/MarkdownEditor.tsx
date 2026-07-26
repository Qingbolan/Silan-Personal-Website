import React from 'react';
import type { Editor } from '@tiptap/core';
import {
  EditorBubble,
  EditorBubbleItem,
  EditorContent,
  EditorRoot,
  handleCommandNavigation,
  ImageResizer,
  type JSONContent,
  useEditor as useNovelEditor,
} from 'novel';
import {
  type LucideIcon,
  Bold,
  Bot,
  Braces,
  Code2,
  Copy,
  Heading2,
  Italic,
  Link2,
  List,
  ListOrdered,
  Minus,
  Quote,
  Redo2,
  MessageSquareWarning,
  Sparkles,
  Strikethrough,
  Table2,
  Undo2,
} from 'lucide-react';
import { coreMarkdownPlugin } from './editor/coreMarkdownPlugin';
import { deepSeekReviewPlugin } from './editor/deepSeekReviewPlugin';
import {
  type EditorReviewFinding,
  type MarkdownEditorPlugin,
  type SlashCommandDefinition,
  NovelEditorPluginRegistry,
} from './editor/novelEditorPluginRegistry';
import { highlightMarkdownSource } from './editor/markdownSourceHighlight';
import {
  NovelSlashCommandMenu,
  slashCommandPlugin,
} from './editor/slashCommandPlugin';

export type {
  EditorReviewFinding,
  MarkdownEditorPlugin,
  SlashCommandDefinition,
} from './editor/novelEditorPluginRegistry';

type EditorPhase = 'creating' | 'ready';
type ToolbarCommand =
  | 'heading'
  | 'bold'
  | 'italic'
  | 'strike'
  | 'bullet-list'
  | 'ordered-list'
  | 'quote'
  | 'code-block'
  | 'inline-code'
  | 'divider'
  | 'table'
  | 'undo'
  | 'redo';

export type MarkdownEditorHandle = {
  focus: () => void;
  getMarkdown: () => string;
  insertMarkdown: (markdown: string) => string | null;
  replaceMarkdown: (markdown: string) => string | null;
  focusReviewFinding: (findingId: string) => boolean;
  applyReviewSuggestion: (findingId: string) => string | null;
};

export type MarkdownEditingMode = 'rich' | 'source';
export type MarkdownSelectionAssistAction = 'agent_edit' | 'optimize_expression' | 'comment_issue';
export type MarkdownSelectionAssistRequest = {
  action: MarkdownSelectionAssistAction;
  selectedText: string;
  beforeContext: string;
  afterContext: string;
  instruction?: string;
};
export type MarkdownSelectionAssistResult = {
  replacement?: string;
  comment?: string;
};

export type MarkdownEditorProps = {
  value: string;
  className?: string;
  ariaLabel?: string;
  disabled?: boolean;
  readOnly?: boolean;
  toolbarVisible?: boolean;
  autoFocus?: boolean;
  placeholder?: string;
  editingMode?: MarkdownEditingMode;
  plugins?: MarkdownEditorPlugin[];
  slashCommands?: SlashCommandDefinition[];
  reviewFindings?: EditorReviewFinding[];
  onChange?: (value: string) => void;
  onEditingModeChange?: (mode: MarkdownEditingMode) => void;
  onKeyDown?: (event: React.KeyboardEvent<HTMLDivElement>) => void;
  onSelectionAssist?: (request: MarkdownSelectionAssistRequest) => Promise<MarkdownSelectionAssistResult>;
  onReviewFindingActivate?: (findingId: string) => void;
  onReviewFindingApplied?: (findingId: string) => void;
};

const emptyPlugins: MarkdownEditorPlugin[] = [];
const emptySlashCommands: SlashCommandDefinition[] = [];

const toolbarButtons: Array<{
  command: ToolbarCommand;
  label: string;
  icon: LucideIcon;
  dividerBefore?: boolean;
}> = [
  { command: 'heading', label: 'Heading', icon: Heading2 },
  { command: 'bold', label: 'Bold', icon: Bold },
  { command: 'italic', label: 'Italic', icon: Italic },
  { command: 'strike', label: 'Strikethrough', icon: Strikethrough },
  { command: 'bullet-list', label: 'Bullet list', icon: List, dividerBefore: true },
  { command: 'ordered-list', label: 'Ordered list', icon: ListOrdered },
  { command: 'quote', label: 'Blockquote', icon: Quote },
  { command: 'code-block', label: 'Code block', icon: Braces, dividerBefore: true },
  { command: 'inline-code', label: 'Inline code', icon: Braces },
  { command: 'divider', label: 'Divider', icon: Minus },
  { command: 'table', label: 'Table', icon: Table2 },
  { command: 'undo', label: 'Undo', icon: Undo2, dividerBefore: true },
  { command: 'redo', label: 'Redo', icon: Redo2 },
];

function getMarkdown(editor: Editor) {
  return editor.storage.markdown.getMarkdown() as string;
}

function useEditorRevision(editor: Editor | null) {
  const [, rerender] = React.useReducer((current) => current + 1, 0);

  React.useEffect(() => {
    if (!editor) return undefined;
    const update = () => rerender();
    editor.on('transaction', update);
    return () => {
      editor.off('transaction', update);
    };
  }, [editor]);
}

function MarkdownToolbar({
  editor,
  disabled,
  sourceMode,
  onCommand,
  onLink,
  onSourceModeChange,
}: {
  editor: Editor | null;
  disabled: boolean;
  sourceMode: boolean;
  onCommand: (command: ToolbarCommand) => void;
  onLink: (href: string) => void;
  onSourceModeChange: (sourceMode: boolean) => void;
}) {
  const [linkOpen, setLinkOpen] = React.useState(false);
  const [href, setHref] = React.useState('https://');
  useEditorRevision(editor);

  const activeCommands = editor ? {
    heading: editor.isActive('heading', { level: 2 }),
    bold: editor.isActive('bold'),
    italic: editor.isActive('italic'),
    strike: editor.isActive('strike'),
    'bullet-list': editor.isActive('bulletList'),
    'ordered-list': editor.isActive('orderedList'),
    quote: editor.isActive('blockquote'),
    'code-block': editor.isActive('codeBlock'),
    'inline-code': editor.isActive('code'),
    divider: false,
    table: editor.isActive('table'),
    undo: false,
    redo: false,
    link: editor.isActive('link'),
  } satisfies Record<ToolbarCommand, boolean> & { link: boolean } : null;

  const submitLink = (event: React.FormEvent) => {
    event.preventDefault();
    const nextHref = href.trim();
    if (!nextHref) return;
    onLink(nextHref);
    setHref('https://');
    setLinkOpen(false);
  };

  return (
    <div className="novel-toolbar" role="toolbar" aria-label="Markdown formatting">
      {toolbarButtons.map(({ command, label, icon: Icon, dividerBefore }) => (
        <React.Fragment key={command}>
          {dividerBefore && <span className="novel-toolbar-divider" aria-hidden="true" />}
          <button
            type="button"
            disabled={disabled || sourceMode}
            className={activeCommands?.[command] ? 'active' : ''}
            title={label}
            aria-label={label}
            aria-pressed={activeCommands?.[command] || undefined}
            onMouseDown={(event) => event.preventDefault()}
            onClick={() => onCommand(command)}
          >
            <Icon size={15} />
          </button>
        </React.Fragment>
      ))}
      <span className="novel-toolbar-divider" aria-hidden="true" />
      <button
        type="button"
        disabled={disabled || sourceMode}
        className={linkOpen || activeCommands?.link ? 'active' : ''}
        title="Link"
        aria-label="Link"
        aria-expanded={linkOpen}
        onMouseDown={(event) => event.preventDefault()}
        onClick={() => setLinkOpen((current) => !current)}
      >
        <Link2 size={15} />
      </button>
      <span className="novel-toolbar-divider" aria-hidden="true" />
      <button
        type="button"
        disabled={disabled}
        className={sourceMode ? 'active' : ''}
        title={sourceMode ? 'Switch to rich editor' : 'Switch to source mode'}
        aria-label={sourceMode ? 'Switch to rich editor' : 'Switch to source mode'}
        aria-pressed={sourceMode}
        onMouseDown={(event) => event.preventDefault()}
        onClick={() => onSourceModeChange(!sourceMode)}
      >
        <Code2 size={15} />
      </button>
      {linkOpen && (
        <form className="novel-link-popover" onSubmit={submitLink}>
          <label htmlFor="novel-link-href">Link destination</label>
          <div>
            <input
              id="novel-link-href"
              value={href}
              inputMode="url"
              autoComplete="url"
              autoFocus
              onChange={(event) => setHref(event.target.value)}
            />
            <button type="submit" disabled={disabled || !href.trim()}>Apply</button>
          </div>
        </form>
      )}
    </div>
  );
}

const bubbleItems: Array<{
  label: string;
  icon: LucideIcon;
  active: (editor: Editor) => boolean;
  run: (editor: Editor) => void;
}> = [
  {
    label: 'Bold',
    icon: Bold,
    active: (editor) => editor.isActive('bold'),
    run: (editor) => { editor.chain().focus().toggleBold().run(); },
  },
  {
    label: 'Italic',
    icon: Italic,
    active: (editor) => editor.isActive('italic'),
    run: (editor) => { editor.chain().focus().toggleItalic().run(); },
  },
  {
    label: 'Strikethrough',
    icon: Strikethrough,
    active: (editor) => editor.isActive('strike'),
    run: (editor) => { editor.chain().focus().toggleStrike().run(); },
  },
  {
    label: 'Inline code',
    icon: Code2,
    active: (editor) => editor.isActive('code'),
    run: (editor) => { editor.chain().focus().toggleCode().run(); },
  },
];

function selectionText(editor: Editor) {
  const { from, to } = editor.state.selection;
  return editor.state.doc.textBetween(from, to, '\n').trim();
}

function selectionContext(editor: Editor) {
  const { from, to } = editor.state.selection;
  const documentEnd = editor.state.doc.content.size;
  return {
    from,
    to,
    selectedText: editor.state.doc.textBetween(from, to, '\n').trim(),
    beforeContext: editor.state.doc.textBetween(Math.max(0, from - 1600), from, '\n').trim(),
    afterContext: editor.state.doc.textBetween(to, Math.min(documentEnd, to + 1600), '\n').trim(),
  };
}

const quoteComment = (comment: string) => {
  const body = comment
    .trim()
    .split('\n')
    .map((line) => `> ${line.trim()}`)
    .join('\n');
  return `\n\n> [!note] Issue\n${body}\n`;
};

function NovelSelectionBubble({
  disabled,
  onSelectionAssist,
}: {
  disabled: boolean;
  onSelectionAssist?: MarkdownEditorProps['onSelectionAssist'];
}) {
  const { editor } = useNovelEditor();
  const [linkOpen, setLinkOpen] = React.useState(false);
  const [href, setHref] = React.useState('');
  const [busyAction, setBusyAction] = React.useState<MarkdownSelectionAssistAction | 'copy' | null>(null);
  const [assistError, setAssistError] = React.useState('');
  useEditorRevision(editor);

  if (!editor || disabled) return null;

  const submitLink = (event: React.FormEvent) => {
    event.preventDefault();
    const nextHref = href.trim();
    if (!nextHref) return;
    editor.chain().focus().extendMarkRange('link').setLink({ href: nextHref }).run();
    setHref('');
    setLinkOpen(false);
  };

  const copySelection = async () => {
    const text = selectionText(editor);
    if (!text) return;
    setAssistError('');
    setBusyAction('copy');
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      setAssistError('Copy failed');
    } finally {
      setBusyAction(null);
    }
  };

  const runAssist = async (action: MarkdownSelectionAssistAction) => {
    const context = selectionContext(editor);
    if (!context.selectedText) return;
    const instruction = action === 'agent_edit'
      ? window.prompt('Local instruction for the selected text', 'Improve this selected passage without changing surrounding text.')?.trim()
      : undefined;
    if (action === 'agent_edit' && !instruction) return;

    setAssistError('');
    setBusyAction(action);
    try {
      const result = onSelectionAssist
        ? await onSelectionAssist({ action, ...context, instruction })
        : { comment: 'Review this selected passage.' };
      if (action === 'comment_issue') {
        const comment = result.comment?.trim() || 'Review this selected passage.';
        editor
          .chain()
          .focus()
          .setTextSelection(context.to)
          .insertContent(quoteComment(comment))
          .run();
        return;
      }
      const replacement = result.replacement?.trim();
      if (!replacement) {
        setAssistError('No local edit returned');
        return;
      }
      editor
        .chain()
        .focus()
        .insertContentAt({ from: context.from, to: context.to }, replacement)
        .run();
    } catch (reason) {
      setAssistError(String(reason));
    } finally {
      setBusyAction(null);
    }
  };

  return (
    <EditorBubble
      className="novel-bubble-menu"
      tippyOptions={{ placement: 'top', duration: [120, 90] }}
    >
      {bubbleItems.map(({ label, icon: Icon, active, run }) => (
        <EditorBubbleItem
          key={label}
          asChild
          onSelect={run}
        >
          <button
            type="button"
            className={active(editor) ? 'active' : ''}
            aria-label={label}
            title={label}
            onMouseDown={(event) => event.preventDefault()}
          >
            <Icon size={14} />
          </button>
        </EditorBubbleItem>
      ))}
      <span className="novel-bubble-divider" aria-hidden="true" />
      <button
        type="button"
        aria-label="Copy"
        title="Copy"
        disabled={Boolean(busyAction)}
        onMouseDown={(event) => event.preventDefault()}
        onClick={() => void copySelection()}
      >
        <Copy size={14} />
      </button>
      {onSelectionAssist && (
        <>
          <button
            type="button"
            aria-label="Optimize expression"
            title="Optimize expression"
            disabled={Boolean(busyAction)}
            onMouseDown={(event) => event.preventDefault()}
            onClick={() => void runAssist('optimize_expression')}
          >
            <Sparkles size={14} />
          </button>
          <button
            type="button"
            aria-label="Agent local edit"
            title="Agent local edit"
            disabled={Boolean(busyAction)}
            onMouseDown={(event) => event.preventDefault()}
            onClick={() => void runAssist('agent_edit')}
          >
            <Bot size={14} />
          </button>
        </>
      )}
      <button
        type="button"
        aria-label="Comment issue"
        title="Comment issue"
        disabled={Boolean(busyAction)}
        onMouseDown={(event) => event.preventDefault()}
        onClick={() => void runAssist('comment_issue')}
      >
        <MessageSquareWarning size={14} />
      </button>
      <span className="novel-bubble-divider" aria-hidden="true" />
      <button
        type="button"
        className={editor.isActive('link') || linkOpen ? 'active' : ''}
        aria-label="Link"
        title="Link"
        onMouseDown={(event) => event.preventDefault()}
        onClick={() => {
          if (editor.isActive('link')) {
            editor.chain().focus().unsetLink().run();
            return;
          }
          setHref('');
          setLinkOpen((current) => !current);
        }}
      >
        <Link2 size={14} />
      </button>
      {linkOpen && (
        <form className="novel-bubble-link" onSubmit={submitLink}>
          <input
            value={href}
            inputMode="url"
            autoComplete="url"
            autoFocus
            aria-label="Link destination"
            placeholder="Paste a URL"
            onChange={(event) => setHref(event.target.value)}
          />
          <button type="submit" disabled={!href.trim()}>Apply</button>
        </form>
      )}
      {assistError && <span className="novel-bubble-error">{assistError}</span>}
    </EditorBubble>
  );
}

const MarkdownEditor = React.forwardRef<MarkdownEditorHandle, MarkdownEditorProps>(
  function MarkdownEditor({
    value,
    className = '',
    ariaLabel = 'Markdown editor',
    disabled = false,
    readOnly = false,
    toolbarVisible = false,
    autoFocus = true,
    placeholder = '',
    editingMode,
    plugins = emptyPlugins,
    slashCommands = emptySlashCommands,
    reviewFindings = [],
    onChange,
    onEditingModeChange,
    onKeyDown,
    onSelectionAssist,
    onReviewFindingActivate,
    onReviewFindingApplied,
  }, forwardedRef) {
    const sourceRef = React.useRef<HTMLTextAreaElement | null>(null);
    const sourceHighlightRef = React.useRef<HTMLPreElement | null>(null);
    const valueRef = React.useRef(value);
    const onChangeRef = React.useRef(onChange);
    const reviewFindingsRef = React.useRef(reviewFindings);
    const onReviewFindingActivateRef = React.useRef(onReviewFindingActivate);
    const onReviewFindingAppliedRef = React.useRef(onReviewFindingApplied);
    const disabledRef = React.useRef(disabled || readOnly);
    const placeholderRef = React.useRef(placeholder);
    const slashCommandProviderRef = React.useRef<SlashCommandDefinition[]>([]);
    const [phase, setPhase] = React.useState<EditorPhase>('creating');
    const [uncontrolledMode, setUncontrolledMode] = React.useState<MarkdownEditingMode>('rich');
    const [editor, setEditor] = React.useState<Editor | null>(null);
    const [sourceSelection, setSourceSelection] = React.useState<{
      start: number;
      end: number;
      text: string;
    } | null>(null);
    const [sourceAssistBusy, setSourceAssistBusy] = React.useState<MarkdownSelectionAssistAction | 'copy' | null>(null);
    const [sourceAssistError, setSourceAssistError] = React.useState('');
    const contextualSlashCommandPlugin = React.useMemo<MarkdownEditorPlugin | null>(() => {
      if (slashCommands.length === 0) return null;
      return {
        id: 'contextual-slash-commands',
        priority: 450,
        slashCommands,
        createExtensions: () => [],
      };
    }, [slashCommands]);
    const composition = React.useMemo(() => (
      new NovelEditorPluginRegistry([
        coreMarkdownPlugin,
        slashCommandPlugin,
        deepSeekReviewPlugin,
        ...plugins,
        ...(contextualSlashCommandPlugin ? [contextualSlashCommandPlugin] : []),
      ])
    ), [contextualSlashCommandPlugin, plugins]);
    const extensions = React.useMemo(() => composition.extensions({
      placeholder: () => placeholderRef.current,
      readOnly,
      resolveSlashCommands: () => slashCommandProviderRef.current,
      onReviewFindingActivate: (findingId) => {
        onReviewFindingActivateRef.current?.(findingId);
      },
    }), [composition, readOnly]);
    const availableSlashCommands = React.useMemo(() => composition.slashCommands(), [composition]);
    const activeEditingMode = editingMode ?? uncontrolledMode;
    const sourceMode = activeEditingMode === 'source';

    placeholderRef.current = placeholder;
    reviewFindingsRef.current = reviewFindings;
    onReviewFindingActivateRef.current = onReviewFindingActivate;
    onReviewFindingAppliedRef.current = onReviewFindingApplied;
    slashCommandProviderRef.current = availableSlashCommands;

    const highlightedSource = React.useMemo(
      () => highlightMarkdownSource(value, reviewFindings),
      [reviewFindings, value],
    );

    React.useEffect(() => {
      onChangeRef.current = onChange;
    }, [onChange]);

    React.useEffect(() => {
      disabledRef.current = disabled || readOnly;
      editor?.setEditable(!disabledRef.current);
    }, [disabled, editor, readOnly]);

    React.useEffect(() => {
      if (!editor || phase !== 'ready') return;
      editor.commands.setDeepSeekReviewFindings(reviewFindings);
    }, [editor, phase, reviewFindings]);

    React.useEffect(() => {
      if (!editor || phase !== 'ready') return;
      const current = getMarkdown(editor);
      if (current === value) {
        valueRef.current = value;
        return;
      }
      valueRef.current = value;
      editor.commands.setContent(value, false);
    }, [editor, phase, value]);

    const focus = React.useCallback(() => {
      if (sourceMode) {
        sourceRef.current?.focus();
        return;
      }
      editor?.commands.focus();
    }, [editor, sourceMode]);

    const currentMarkdown = React.useCallback(
      () => (sourceMode ? valueRef.current : editor ? getMarkdown(editor) : valueRef.current),
      [editor, sourceMode],
    );

    const applySourceValue = React.useCallback((nextValue: string) => {
      valueRef.current = nextValue;
      onChangeRef.current?.(nextValue);
      return nextValue;
    }, []);

    const insertMarkdown = React.useCallback((markdown: string) => {
      if (sourceMode) {
        if (disabledRef.current) return null;
        const textarea = sourceRef.current;
        const current = valueRef.current;
        const start = textarea?.selectionStart ?? current.length;
        const end = textarea?.selectionEnd ?? start;
        const nextValue = `${current.slice(0, start)}${markdown}${current.slice(end)}`;
        applySourceValue(nextValue);
        window.requestAnimationFrame(() => {
          const nextCaret = start + markdown.length;
          sourceRef.current?.focus();
          sourceRef.current?.setSelectionRange(nextCaret, nextCaret);
        });
        return nextValue;
      }

      if (!editor || phase !== 'ready' || disabledRef.current) return null;
      editor.chain().focus().insertContent(markdown).run();
      return getMarkdown(editor);
    }, [applySourceValue, editor, phase, sourceMode]);

    const replaceMarkdown = React.useCallback((markdown: string) => {
      if (sourceMode) {
        if (disabledRef.current) return null;
        applySourceValue(markdown);
        window.requestAnimationFrame(() => {
          sourceRef.current?.focus();
          sourceRef.current?.setSelectionRange(markdown.length, markdown.length);
        });
        return markdown;
      }

      if (!editor || phase !== 'ready' || disabledRef.current) return null;
      editor.commands.setContent(markdown, true);
      return getMarkdown(editor);
    }, [applySourceValue, editor, phase, sourceMode]);

    const focusReviewFinding = React.useCallback((findingId: string) => {
      const finding = reviewFindingsRef.current.find((candidate) => candidate.id === findingId);
      if (!finding) return false;
      if (sourceMode) {
        const offset = valueRef.current.indexOf(finding.quote);
        if (offset < 0) return false;
        sourceRef.current?.focus();
        sourceRef.current?.setSelectionRange(offset, offset + finding.quote.length);
        return true;
      }
      if (!editor || phase !== 'ready') return false;
      editor.commands.focus();
      return editor.commands.focusDeepSeekReviewFinding(findingId);
    }, [editor, phase, sourceMode]);

    const applyReviewSuggestion = React.useCallback((findingId: string) => {
      if (disabledRef.current) return null;
      const finding = reviewFindingsRef.current.find((candidate) => candidate.id === findingId);
      if (!finding) return null;
      if (sourceMode) {
        const current = valueRef.current;
        const offset = current.indexOf(finding.quote);
        if (offset < 0) return null;
        const next = `${current.slice(0, offset)}${finding.suggestion}${current.slice(offset + finding.quote.length)}`;
        applySourceValue(next);
        onReviewFindingAppliedRef.current?.(findingId);
        window.requestAnimationFrame(() => {
          const caret = offset + finding.suggestion.length;
          sourceRef.current?.focus();
          sourceRef.current?.setSelectionRange(caret, caret);
        });
        return next;
      }
      if (!editor || phase !== 'ready') return null;
      if (!editor.commands.applyDeepSeekReviewSuggestion(findingId)) return null;
      const next = getMarkdown(editor);
      onReviewFindingAppliedRef.current?.(findingId);
      return next;
    }, [applySourceValue, editor, phase, sourceMode]);

    React.useImperativeHandle(forwardedRef, () => ({
      focus,
      getMarkdown: currentMarkdown,
      insertMarkdown,
      replaceMarkdown,
      focusReviewFinding,
      applyReviewSuggestion,
    }), [
      applyReviewSuggestion,
      currentMarkdown,
      focus,
      focusReviewFinding,
      insertMarkdown,
      replaceMarkdown,
    ]);

    const runCommand = React.useCallback((command: ToolbarCommand) => {
      if (!editor || phase !== 'ready' || disabledRef.current) return;
      switch (command) {
        case 'heading':
          editor.chain().focus().toggleHeading({ level: 2 }).run();
          break;
        case 'bold':
          editor.chain().focus().toggleBold().run();
          break;
        case 'italic':
          editor.chain().focus().toggleItalic().run();
          break;
        case 'strike':
          editor.chain().focus().toggleStrike().run();
          break;
        case 'bullet-list':
          editor.chain().focus().toggleBulletList().run();
          break;
        case 'ordered-list':
          editor.chain().focus().toggleOrderedList().run();
          break;
        case 'quote':
          editor.chain().focus().toggleBlockquote().run();
          break;
        case 'code-block':
          editor.chain().focus().toggleCodeBlock().run();
          break;
        case 'inline-code':
          editor.chain().focus().toggleCode().run();
          break;
        case 'divider':
          editor.chain().focus().setHorizontalRule().run();
          break;
        case 'table':
          editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run();
          break;
        case 'undo':
          editor.chain().focus().undo().run();
          break;
        case 'redo':
          editor.chain().focus().redo().run();
          break;
      }
    }, [editor, phase]);

    const applyLink = React.useCallback((href: string) => {
      if (!editor || phase !== 'ready' || disabledRef.current) return;
      editor.chain().focus().extendMarkRange('link').setLink({ href }).run();
    }, [editor, phase]);

    const updateSourceMode = React.useCallback((nextSourceMode: boolean) => {
      if (!nextSourceMode && editor && getMarkdown(editor) !== valueRef.current) {
        editor.commands.setContent(valueRef.current, false);
      }
      const nextMode = nextSourceMode ? 'source' : 'rich';
      if (editingMode === undefined) {
        setUncontrolledMode(nextMode);
      }
      onEditingModeChange?.(nextMode);
      window.requestAnimationFrame(() => {
        if (nextSourceMode) sourceRef.current?.focus();
        else editor?.commands.focus();
      });
    }, [editingMode, editor, onEditingModeChange]);

    const focusDocumentEnd = React.useCallback((event: React.MouseEvent<HTMLDivElement>) => {
      if (sourceMode || readOnly || disabledRef.current || phase !== 'ready') return;
      const target = event.target as HTMLElement;
      if (
        target !== event.currentTarget
        && !target.classList.contains('novel-editor-root')
        && !target.classList.contains('tiptap')
      ) {
        return;
      }
      event.preventDefault();
      editor?.commands.focus('end');
    }, [editor, phase, readOnly, sourceMode]);

    const handleKeyDown = React.useCallback((event: React.KeyboardEvent<HTMLDivElement>) => {
      onKeyDown?.(event);
    }, [onKeyDown]);

    const handleSourceKeyDown = React.useCallback((event: React.KeyboardEvent<HTMLTextAreaElement>) => {
      onKeyDown?.(event as unknown as React.KeyboardEvent<HTMLDivElement>);
    }, [onKeyDown]);

    const syncSourceHighlightScroll = React.useCallback((event: React.UIEvent<HTMLTextAreaElement>) => {
      const highlight = sourceHighlightRef.current;
      if (!highlight) return;
      highlight.scrollTop = event.currentTarget.scrollTop;
      highlight.scrollLeft = event.currentTarget.scrollLeft;
    }, []);

    const updateSourceSelection = React.useCallback(() => {
      const textarea = sourceRef.current;
      if (!textarea) {
        setSourceSelection(null);
        return;
      }
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const text = valueRef.current.slice(start, end);
      setSourceSelection(text.trim() ? { start, end, text } : null);
    }, []);

    const copySourceSelection = React.useCallback(async () => {
      if (!sourceSelection) return;
      setSourceAssistError('');
      setSourceAssistBusy('copy');
      try {
        await navigator.clipboard.writeText(sourceSelection.text);
      } catch {
        setSourceAssistError('Copy failed');
      } finally {
        setSourceAssistBusy(null);
      }
    }, [sourceSelection]);

    const runSourceSelectionAssist = React.useCallback(async (action: MarkdownSelectionAssistAction) => {
      if (!sourceSelection) return;
      const instruction = action === 'agent_edit'
        ? window.prompt('Local instruction for the selected text', 'Improve this selected passage without changing surrounding text.')?.trim()
        : undefined;
      if (action === 'agent_edit' && !instruction) return;

      setSourceAssistError('');
      setSourceAssistBusy(action);
      try {
        const result = onSelectionAssist
          ? await onSelectionAssist({
            action,
            selectedText: sourceSelection.text,
            beforeContext: valueRef.current.slice(Math.max(0, sourceSelection.start - 1600), sourceSelection.start),
            afterContext: valueRef.current.slice(sourceSelection.end, sourceSelection.end + 1600),
            instruction,
          })
          : { comment: 'Review this selected passage.' };
        const insertion = action === 'comment_issue'
          ? quoteComment(result.comment?.trim() || 'Review this selected passage.')
          : result.replacement?.trim();
        if (!insertion) {
          setSourceAssistError('No local edit returned');
          return;
        }
        const insertAt = action === 'comment_issue' ? sourceSelection.end : sourceSelection.start;
        const replaceEnd = action === 'comment_issue' ? sourceSelection.end : sourceSelection.end;
        const nextValue = `${valueRef.current.slice(0, insertAt)}${insertion}${valueRef.current.slice(replaceEnd)}`;
        applySourceValue(nextValue);
        window.requestAnimationFrame(() => {
          const caret = insertAt + insertion.length;
          sourceRef.current?.focus();
          sourceRef.current?.setSelectionRange(caret, caret);
          setSourceSelection(null);
        });
      } catch (reason) {
        setSourceAssistError(String(reason));
      } finally {
        setSourceAssistBusy(null);
      }
    }, [applySourceValue, onSelectionAssist, sourceSelection]);

    return (
      <div
        className={[
          'editor-host',
          'novel-editor',
          readOnly ? 'novel-editor--preview' : '',
          className,
        ].filter(Boolean).join(' ')}
        data-state={phase}
        data-mode={activeEditingMode}
        data-disabled={disabled || readOnly ? 'true' : 'false'}
        data-empty={value.trim() ? 'false' : 'true'}
        onMouseDown={focusDocumentEnd}
        onKeyDown={handleKeyDown}
      >
        {!readOnly && toolbarVisible && (
          <MarkdownToolbar
            editor={editor}
            disabled={disabled || phase !== 'ready'}
            sourceMode={sourceMode}
            onCommand={runCommand}
            onLink={applyLink}
            onSourceModeChange={updateSourceMode}
          />
        )}
        <EditorRoot>
          <EditorContent
            className="novel-editor-root"
            initialContent={value as unknown as JSONContent}
            extensions={extensions}
            editable={!(disabled || readOnly)}
            editorProps={{
              attributes: {
                'aria-label': ariaLabel,
                ...(readOnly ? {} : { 'aria-multiline': 'true' }),
                role: readOnly ? 'document' : 'textbox',
                'data-novel-surface': readOnly ? 'preview' : 'editor',
              },
              handleDOMEvents: {
                keydown: (_, event) => handleCommandNavigation(event) || false,
              },
            }}
            onBeforeCreate={() => {
              setPhase('creating');
            }}
            onCreate={({ editor: createdEditor }) => {
              setEditor(createdEditor);
              setPhase('ready');
              if (autoFocus && !readOnly) {
                window.requestAnimationFrame(() => {
                  if (sourceMode) sourceRef.current?.focus();
                  else createdEditor.commands.focus('end');
                });
              }
            }}
            onDestroy={() => {
              setEditor(null);
            }}
            onUpdate={({ editor: updatedEditor }) => {
              const markdown = getMarkdown(updatedEditor);
              if (markdown === valueRef.current) return;
              valueRef.current = markdown;
              onChangeRef.current?.(markdown);
            }}
          >
            {!readOnly && !sourceMode && (
              <>
                <NovelSlashCommandMenu commands={availableSlashCommands} />
                <NovelSelectionBubble disabled={disabled} onSelectionAssist={onSelectionAssist} />
                <ImageResizer />
              </>
            )}
          </EditorContent>
        </EditorRoot>
        {!readOnly && sourceMode && (
          <div className="novel-source-surface">
            <pre
              ref={sourceHighlightRef}
              className="novel-source-highlight"
              aria-hidden="true"
              dangerouslySetInnerHTML={{ __html: highlightedSource }}
            />
            <textarea
              ref={sourceRef}
              className="novel-source-editor"
              value={value}
              disabled={disabled}
              spellCheck={false}
              aria-label={`${ariaLabel} source`}
              placeholder={placeholder}
              onChange={(event) => applySourceValue(event.target.value)}
              onKeyDown={handleSourceKeyDown}
              onKeyUp={updateSourceSelection}
              onMouseUp={updateSourceSelection}
              onSelect={updateSourceSelection}
              onScroll={syncSourceHighlightScroll}
            />
            {sourceSelection && (
              <div className="novel-source-selection-menu" role="toolbar" aria-label="Selected text actions">
                <button
                  type="button"
                  aria-label="Copy"
                  title="Copy"
                  disabled={Boolean(sourceAssistBusy)}
                  onMouseDown={(event) => event.preventDefault()}
                  onClick={() => void copySourceSelection()}
                >
                  <Copy size={14} />
                </button>
                {onSelectionAssist && (
                  <>
                    <button
                      type="button"
                      aria-label="Optimize expression"
                      title="Optimize expression"
                      disabled={Boolean(sourceAssistBusy)}
                      onMouseDown={(event) => event.preventDefault()}
                      onClick={() => void runSourceSelectionAssist('optimize_expression')}
                    >
                      <Sparkles size={14} />
                    </button>
                    <button
                      type="button"
                      aria-label="Agent local edit"
                      title="Agent local edit"
                      disabled={Boolean(sourceAssistBusy)}
                      onMouseDown={(event) => event.preventDefault()}
                      onClick={() => void runSourceSelectionAssist('agent_edit')}
                    >
                      <Bot size={14} />
                    </button>
                  </>
                )}
                <button
                  type="button"
                  aria-label="Comment issue"
                  title="Comment issue"
                  disabled={Boolean(sourceAssistBusy)}
                  onMouseDown={(event) => event.preventDefault()}
                  onClick={() => void runSourceSelectionAssist('comment_issue')}
                >
                  <MessageSquareWarning size={14} />
                </button>
                {sourceAssistError && <span>{sourceAssistError}</span>}
              </div>
            )}
          </div>
        )}
        {phase === 'creating' && <div className="novel-editor-state">Preparing editor…</div>}
      </div>
    );
  },
);

export default MarkdownEditor;
