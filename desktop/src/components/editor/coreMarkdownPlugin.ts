import Placeholder from '@tiptap/extension-placeholder';
import Table from '@tiptap/extension-table';
import TableCell from '@tiptap/extension-table-cell';
import TableHeader from '@tiptap/extension-table-header';
import TableRow from '@tiptap/extension-table-row';
import TaskItem from '@tiptap/extension-task-item';
import TaskList from '@tiptap/extension-task-list';
import StarterKit from '@tiptap/starter-kit';
import {
  AIHighlight,
  CustomKeymap,
  GlobalDragHandle,
  HighlightExtension,
  HorizontalRule,
  TiptapLink,
  UpdatedImage,
} from 'novel';
import { Markdown } from 'tiptap-markdown';
import type { MarkdownEditorPlugin } from './novelEditorPluginRegistry';

export const coreMarkdownPlugin: MarkdownEditorPlugin = {
  id: 'core-markdown',
  priority: 1000,
  createExtensions: ({ placeholder, readOnly }) => [
    StarterKit.configure({
      history: readOnly ? false : {},
      horizontalRule: false,
    }),
    TiptapLink.configure({
      openOnClick: readOnly,
      autolink: true,
      defaultProtocol: 'https',
    }),
    UpdatedImage.configure({
      allowBase64: true,
    }),
    HighlightExtension,
    AIHighlight,
    HorizontalRule,
    Table.configure({
      resizable: false,
    }),
    TableRow,
    TableHeader,
    TableCell,
    TaskList,
    TaskItem.configure({
      nested: true,
    }),
    Placeholder.configure({
      placeholder,
    }),
    Markdown.configure({
      html: true,
      tightLists: true,
      bulletListMarker: '-',
      linkify: true,
      breaks: false,
      transformPastedText: true,
      transformCopiedText: true,
    }),
    CustomKeymap,
    ...(!readOnly ? [
      GlobalDragHandle.configure({
        dragHandleWidth: 20,
        scrollTreshold: 80,
        excludedTags: ['hr'],
      }),
    ] : []),
  ],
};
