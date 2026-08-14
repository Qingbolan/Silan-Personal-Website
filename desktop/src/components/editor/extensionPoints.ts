import type React from 'react';
import type {
  AnyLexicalExtensionArgument,
  Klass,
  LexicalEditor,
  LexicalNode,
  PointType,
} from 'lexical';
import type { LucideIcon } from 'lucide-react';
import type { LanguageAuditFinding } from '../../types';

export type EditorReviewFinding = LanguageAuditFinding & {
  id: string;
};

export type MarkdownSelectionAssistAction =
  | 'agent_edit'
  | 'optimize_expression'
  | 'comment_issue';

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

export type MarkdownImageImport = {
  alt: string;
  src: string;
  title?: string | null;
};

export type MarkdownImageImporter = (
  files: readonly File[],
) => Promise<readonly MarkdownImageImport[]>;

export type MarkdownSelectionRange = {
  anchorKey: string;
  anchorOffset: number;
  anchorType: PointType['type'];
  focusKey: string;
  focusOffset: number;
  focusType: PointType['type'];
};

export type MarkdownCommandContext = {
  editor: LexicalEditor;
  range: MarkdownSelectionRange;
  deleteTrigger: () => void;
  insertMarkdown: (markdown: string) => void;
};

export type SlashCommandDefinition = {
  id: string;
  title: string;
  description: string;
  keywords: string[];
  icon: LucideIcon;
  run: (context: MarkdownCommandContext) => void;
};

export type MarkdownEditorPluginContext = {
  readOnly: boolean;
};

/**
 * Capability contribution for the Lexical composition root.
 *
 * Nodes and extensions are registered before the editor is constructed;
 * React components are mounted inside the same composer. This keeps schema,
 * behavior, and UI ownership together without exposing Lexical internals to
 * the MarkdownEditor component.
 */
export type MarkdownEditorPlugin = {
  id: string;
  priority?: number;
  nodes?: readonly Klass<LexicalNode>[];
  extensions?: readonly AnyLexicalExtensionArgument[];
  slashCommands?: readonly SlashCommandDefinition[];
  Component?: React.ComponentType<MarkdownEditorPluginContext>;
};

export class LexicalEditorPluginRegistry {
  readonly #plugins: MarkdownEditorPlugin[];

  constructor(plugins: readonly MarkdownEditorPlugin[]) {
    const pluginIds = new Set<string>();
    const commandIds = new Set<string>();
    plugins.forEach((plugin) => {
      if (pluginIds.has(plugin.id)) {
        throw new Error(`Duplicate Markdown editor plugin: ${plugin.id}`);
      }
      pluginIds.add(plugin.id);
      plugin.slashCommands?.forEach((command) => {
        if (commandIds.has(command.id)) {
          throw new Error(`Duplicate slash command: ${command.id}`);
        }
        commandIds.add(command.id);
      });
    });
    this.#plugins = [...plugins].sort(
      (left, right) => (right.priority || 0) - (left.priority || 0),
    );
  }

  nodes() {
    return this.#plugins.flatMap((plugin) => plugin.nodes || []);
  }

  extensions() {
    return this.#plugins.flatMap((plugin) => plugin.extensions || []);
  }

  slashCommands() {
    return this.#plugins.flatMap((plugin) => plugin.slashCommands || []);
  }

  components() {
    return this.#plugins.flatMap((plugin) => (
      plugin.Component ? [{ id: plugin.id, Component: plugin.Component }] : []
    ));
  }
}
