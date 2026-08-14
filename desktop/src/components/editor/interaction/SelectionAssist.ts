import {
  $getRoot,
  $isElementNode,
  $isTextNode,
  type PointType,
  type RangeSelection,
  type TextNode,
} from 'lexical';
import type { MarkdownSelectionAssistRequest } from '../extensionPoints';

type IndexedTextNode = {
  end: number;
  node: TextNode;
  start: number;
};

function $indexDocumentText() {
  const entries: IndexedTextNode[] = [];
  const byKey = new Map<string, IndexedTextNode>();
  let documentText = '';
  let topLevelKey = '';

  $getRoot().getAllTextNodes().forEach((node) => {
    const nextTopLevelKey = node.getTopLevelElementOrThrow().getKey();
    if (documentText && topLevelKey && nextTopLevelKey !== topLevelKey) documentText += '\n';
    const entry = {
      end: documentText.length + node.getTextContentSize(),
      node,
      start: documentText.length,
    };
    entries.push(entry);
    byKey.set(node.getKey(), entry);
    documentText += node.getTextContent();
    topLevelKey = nextTopLevelKey;
  });

  return { byKey, documentText, entries };
}

function $pointOffset(
  point: PointType,
  index: ReturnType<typeof $indexDocumentText>,
) {
  const direct = index.byKey.get(point.key);
  if (point.type === 'text' && direct) {
    return direct.start + Math.min(point.offset, direct.node.getTextContentSize());
  }

  const node = point.getNode();
  if (!$isElementNode(node)) return direct?.start ?? 0;
  const children = node.getChildren();
  if (point.offset >= children.length) {
    const finalText = node.getAllTextNodes().at(-1);
    return finalText ? index.byKey.get(finalText.getKey())?.end ?? index.documentText.length : 0;
  }
  const child = children[point.offset];
  const firstText = $isTextNode(child)
    ? child
    : $isElementNode(child)
      ? child.getAllTextNodes()[0]
      : null;
  return firstText ? index.byKey.get(firstText.getKey())?.start ?? 0 : 0;
}

/** Reads selection context from exact Lexical point keys, not a text search. */
export function $readSelectionAssistContext(
  selection: RangeSelection,
  contextLength = 1600,
): Omit<MarkdownSelectionAssistRequest, 'action' | 'instruction'> | null {
  const selectedText = selection.getTextContent().trim();
  if (!selectedText) return null;
  const index = $indexDocumentText();
  const [startPoint, endPoint] = selection.getStartEndPoints();
  const start = $pointOffset(startPoint, index);
  const end = $pointOffset(endPoint, index);
  return {
    afterContext: index.documentText.slice(end, end + contextLength).trim(),
    beforeContext: index.documentText.slice(Math.max(0, start - contextLength), start).trim(),
    selectedText,
  };
}

export function quoteIssueComment(comment: string) {
  const body = comment.trim().split('\n').map((line) => `> ${line.trim()}`).join('\n');
  return `\n\n> [!note] Issue\n${body}\n`;
}
