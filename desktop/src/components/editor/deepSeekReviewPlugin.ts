import { Extension } from '@tiptap/core';
import type { Node as ProseMirrorNode } from '@tiptap/pm/model';
import { Plugin, PluginKey, TextSelection } from '@tiptap/pm/state';
import { Decoration, DecorationSet } from '@tiptap/pm/view';
import type {
  EditorReviewFinding,
  MarkdownEditorPlugin,
} from './novelEditorPluginRegistry';

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    deepSeekReview: {
      setDeepSeekReviewFindings: (findings: EditorReviewFinding[]) => ReturnType;
      focusDeepSeekReviewFinding: (findingId: string) => ReturnType;
      applyDeepSeekReviewSuggestion: (findingId: string) => ReturnType;
    };
  }
}

type ReviewPluginState = {
  findings: EditorReviewFinding[];
  decorations: DecorationSet;
};

type TextIndex = {
  text: string;
  positions: number[];
};

const deepSeekReviewKey = new PluginKey<ReviewPluginState>('deepSeekReview');

function indexDocumentText(document: ProseMirrorNode): TextIndex {
  let text = '';
  const positions: number[] = [];
  let previousParent: ProseMirrorNode | null = null;

  document.descendants((node, position, parent) => {
    if (!node.isText || !node.text) return;
    if (text && previousParent && parent !== previousParent) {
      text += '\n';
      positions.push(position);
    }
    for (let index = 0; index < node.text.length; index += 1) {
      text += node.text[index];
      positions.push(position + index);
    }
    previousParent = parent;
  });

  return { text, positions };
}

function findFindingRange(document: ProseMirrorNode, finding: EditorReviewFinding) {
  const quote = finding.quote.trim();
  if (!quote) return null;
  const index = indexDocumentText(document);
  const offset = index.text.indexOf(quote);
  if (offset < 0) return null;
  const from = index.positions[offset];
  const last = index.positions[offset + quote.length - 1];
  if (from == null || last == null) return null;
  return { from, to: last + 1 };
}

function createDecorations(
  document: ProseMirrorNode,
  findings: EditorReviewFinding[],
) {
  return DecorationSet.create(
    document,
    findings.flatMap((finding) => {
      const range = findFindingRange(document, finding);
      if (!range) return [];
      return [
        Decoration.inline(range.from, range.to, {
          class: `deepseek-review-mark deepseek-review-mark--${finding.severity}`,
          'data-review-finding': finding.id,
          title: finding.explanation,
        }),
      ];
    }),
  );
}

const createDeepSeekReviewExtension = (
  onReviewFindingActivate: (findingId: string) => void,
) => Extension.create({
  name: 'deepSeekReview',
  priority: 150,

  addStorage() {
    return {
      findings: [] as EditorReviewFinding[],
    };
  },

  addCommands() {
    return {
      setDeepSeekReviewFindings: (findings) => ({ tr, dispatch }) => {
        this.storage.findings = findings;
        dispatch?.(tr.setMeta(deepSeekReviewKey, { findings }));
        return true;
      },
      focusDeepSeekReviewFinding: (findingId) => ({ state, tr, dispatch }) => {
        const finding = (this.storage.findings as EditorReviewFinding[])
          .find((candidate) => candidate.id === findingId);
        const range = finding ? findFindingRange(state.doc, finding) : null;
        if (!range) return false;
        dispatch?.(
          tr
            .setSelection(TextSelection.create(state.doc, range.from, range.to))
            .scrollIntoView(),
        );
        return true;
      },
      applyDeepSeekReviewSuggestion: (findingId) => ({ state, tr, dispatch }) => {
        const findings = this.storage.findings as EditorReviewFinding[];
        const finding = findings.find((candidate) => candidate.id === findingId);
        const range = finding ? findFindingRange(state.doc, finding) : null;
        if (!finding || !range) return false;
        const remaining = findings.filter((candidate) => candidate.id !== findingId);
        this.storage.findings = remaining;
        dispatch?.(
          tr
            .insertText(finding.suggestion, range.from, range.to)
            .setMeta(deepSeekReviewKey, { findings: remaining })
            .scrollIntoView(),
        );
        return true;
      },
    };
  },

  addProseMirrorPlugins() {
    return [
      new Plugin<ReviewPluginState>({
        key: deepSeekReviewKey,
        state: {
          init: (_, state) => ({
            findings: [],
            decorations: DecorationSet.create(state.doc, []),
          }),
          apply: (transaction, previous, _, nextState) => {
            const metadata = transaction.getMeta(deepSeekReviewKey) as
              | { findings?: EditorReviewFinding[] }
              | undefined;
            const findings = metadata?.findings || previous.findings;
            if (!transaction.docChanged && !metadata) return previous;
            return {
              findings,
              decorations: createDecorations(nextState.doc, findings),
            };
          },
        },
        props: {
          decorations: (state) => deepSeekReviewKey.getState(state)?.decorations,
          handleClick: (_, __, event) => {
            const element = event.target instanceof Element
              ? event.target.closest<HTMLElement>('[data-review-finding]')
              : null;
            const findingId = element?.dataset.reviewFinding;
            if (!findingId) return false;
            onReviewFindingActivate(findingId);
            return true;
          },
        },
      }),
    ];
  },
});

export const deepSeekReviewPlugin: MarkdownEditorPlugin = {
  id: 'deepseek-review',
  priority: 400,
  createExtensions: ({ onReviewFindingActivate }) => [
    createDeepSeekReviewExtension(onReviewFindingActivate),
  ],
};
