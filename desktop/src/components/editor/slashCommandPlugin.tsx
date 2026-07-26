import React from 'react';
import type { Editor, Range } from '@tiptap/core';
import {
  Command,
  EditorCommand,
  EditorCommandEmpty,
  EditorCommandItem,
  EditorCommandList,
  createSuggestionItems,
  renderItems,
} from 'novel';
import {
  CalendarDays,
  CheckSquare,
  FileText,
  Hash,
  Heading2,
  Image,
  Link2,
  Minus,
  Quote,
  Table2,
} from 'lucide-react';
import type {
  MarkdownEditorPlugin,
  SlashCommandDefinition,
} from './novelEditorPluginRegistry';

const deleteTrigger = (editor: Editor, range: Range) => (
  editor.chain().focus().deleteRange(range)
);

const insertMarkdown = (markdown: string) => (editor: Editor, range: Range) => {
  deleteTrigger(editor, range).insertContent(markdown).run();
};

export const defaultSlashCommands: SlashCommandDefinition[] = [
  {
    id: 'heading',
    title: 'Heading',
    description: 'Start a section title.',
    keywords: ['h2', 'heading', 'title', 'section'],
    icon: Heading2,
    run: (editor, range) => deleteTrigger(editor, range).toggleHeading({ level: 2 }).run(),
  },
  {
    id: 'todo',
    title: 'Task',
    description: 'Add a checkbox action item.',
    keywords: ['todo', 'task', 'checkbox', 'action'],
    icon: CheckSquare,
    run: (editor, range) => deleteTrigger(editor, range).toggleTaskList().run(),
  },
  {
    id: 'quote',
    title: 'Quote',
    description: 'Capture a quote or important sentence.',
    keywords: ['quote', 'blockquote', 'citation'],
    icon: Quote,
    run: (editor, range) => deleteTrigger(editor, range).toggleBlockquote().run(),
  },
  {
    id: 'event',
    title: 'Event record',
    description: 'Structured moment: what changed, evidence, next action.',
    keywords: ['event', 'moment', 'status', '记录', '事件'],
    icon: CalendarDays,
    run: insertMarkdown('## Event\n\n- Time: \n- What changed: \n- Evidence: \n- Next action: \n'),
  },
  {
    id: 'decision',
    title: 'Decision',
    description: 'Record the choice, reason, and follow-up.',
    keywords: ['decision', 'decide', 'choice', '决定'],
    icon: FileText,
    run: insertMarkdown('## Decision\n\n- Decision: \n- Reason: \n- Tradeoff: \n- Follow-up: \n'),
  },
  {
    id: 'internal-link',
    title: 'Internal link',
    description: 'Obsidian-style placeholder for linking knowledge.',
    keywords: ['link', 'wiki', 'obsidian', 'backlink', '双链'],
    icon: Link2,
    run: (editor, range) => deleteTrigger(editor, range).insertContent('[[Untitled]]').run(),
  },
  {
    id: 'tag',
    title: 'Tag',
    description: 'Add a lightweight knowledge tag.',
    keywords: ['tag', 'hash', 'label'],
    icon: Hash,
    run: (editor, range) => deleteTrigger(editor, range).insertContent('#topic ').run(),
  },
  {
    id: 'table',
    title: 'Table',
    description: 'Insert a three-column table.',
    keywords: ['table', 'grid'],
    icon: Table2,
    run: (editor, range) => (
      deleteTrigger(editor, range).insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()
    ),
  },
  {
    id: 'divider',
    title: 'Divider',
    description: 'Separate two blocks.',
    keywords: ['hr', 'divider', 'line'],
    icon: Minus,
    run: (editor, range) => deleteTrigger(editor, range).setHorizontalRule().run(),
  },
  {
    id: 'image-prompt',
    title: 'Image prompt',
    description: 'Inline image-generation request block.',
    keywords: ['image', 'media', 'ai', 'generate'],
    icon: Image,
    run: insertMarkdown('```silan-ai-image\nprompt: \nstyle: editorial documentary\nratio: 1:1\n```\n'),
  },
];

const toNovelSuggestions = (commands: SlashCommandDefinition[]) => (
  createSuggestionItems(commands.map((command) => ({
    title: command.title,
    description: command.description,
    searchTerms: [command.id, ...command.keywords],
    icon: React.createElement(command.icon, { size: 16 }),
    command: ({ editor, range }: { editor: Editor; range: Range }) => {
      command.run(editor, range);
    },
  })))
);

export function NovelSlashCommandMenu({
  commands,
}: {
  commands: SlashCommandDefinition[];
}) {
  return (
    <EditorCommand className="novel-slash-menu" aria-label="Slash commands">
      <div className="novel-slash-query">
        <span>/</span>
        <strong>Commands</strong>
        <small>↑↓ navigate · Enter insert · Esc close</small>
      </div>
      <EditorCommandEmpty className="novel-slash-empty">
        No matching command.
      </EditorCommandEmpty>
      <EditorCommandList>
        {commands.map((command) => {
          const Icon = command.icon;
          return (
            <EditorCommandItem
              key={command.id}
              value={command.title}
              keywords={[command.id, ...command.keywords]}
              onCommand={({ editor, range }) => command.run(editor, range)}
            >
              <Icon size={16} />
              <span>
                <strong>{command.title}</strong>
                <small>{command.description}</small>
              </span>
            </EditorCommandItem>
          );
        })}
      </EditorCommandList>
    </EditorCommand>
  );
}

export const slashCommandPlugin: MarkdownEditorPlugin = {
  id: 'slash-command',
  priority: 500,
  slashCommands: defaultSlashCommands,
  createExtensions: ({ resolveSlashCommands, readOnly }) => {
    if (readOnly) return [];
    return [
      Command.configure({
        suggestion: {
          char: '/',
          startOfLine: true,
          items: () => toNovelSuggestions(resolveSlashCommands()),
          render: renderItems,
        },
      }),
    ];
  },
};
