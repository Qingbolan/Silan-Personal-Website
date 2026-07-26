import type { AnyExtension, Editor, Range } from '@tiptap/core';
import type { LucideIcon } from 'lucide-react';
import type { LanguageAuditFinding } from '../../types';

export type EditorReviewFinding = LanguageAuditFinding & {
  id: string;
};

export type SlashCommandDefinition = {
  id: string;
  title: string;
  description: string;
  keywords: string[];
  icon: LucideIcon;
  run: (editor: Editor, range: Range) => void;
};

export type MarkdownEditorPluginContext = {
  placeholder: () => string;
  slashCommands: SlashCommandDefinition[];
  resolveSlashCommands: () => SlashCommandDefinition[];
  readOnly: boolean;
  onReviewFindingActivate: (findingId: string) => void;
};

export type MarkdownEditorPlugin = {
  id: string;
  priority?: number;
  slashCommands?: SlashCommandDefinition[];
  createExtensions: (context: MarkdownEditorPluginContext) => AnyExtension[];
};

/**
 * Immutable composition root for editor capabilities.
 *
 * Plugins own their Novel/TipTap extensions and optional slash-command contributions.
 * Duplicate plugin and command identifiers fail immediately so extension
 * ownership remains explicit.
 */
export class NovelEditorPluginRegistry {
  readonly #plugins: MarkdownEditorPlugin[];

  constructor(plugins: MarkdownEditorPlugin[]) {
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

  slashCommands() {
    return this.#plugins.flatMap((plugin) => plugin.slashCommands || []);
  }

  extensions(context: Omit<MarkdownEditorPluginContext, 'slashCommands' | 'resolveSlashCommands'> & {
    resolveSlashCommands?: () => SlashCommandDefinition[];
  }) {
    const fullContext: MarkdownEditorPluginContext = {
      ...context,
      slashCommands: this.slashCommands(),
      resolveSlashCommands: context.resolveSlashCommands || (() => this.slashCommands()),
    };
    return this.#plugins.flatMap((plugin) => plugin.createExtensions(fullContext));
  }
}
