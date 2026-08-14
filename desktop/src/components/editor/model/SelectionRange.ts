import {
  $createRangeSelection,
  $getNodeByKey,
  $getSelection,
  $isElementNode,
  $isRangeSelection,
  $isTextNode,
  $setSelection,
  type RangeSelection,
  type TextNode,
} from 'lexical';
import type { MarkdownSelectionRange } from '../extensionPoints';

export function $captureSelectionRange(): MarkdownSelectionRange | null {
  const selection = $getSelection();
  if (!$isRangeSelection(selection)) return null;
  return {
    anchorKey: selection.anchor.key,
    anchorOffset: selection.anchor.offset,
    anchorType: selection.anchor.type,
    focusKey: selection.focus.key,
    focusOffset: selection.focus.offset,
    focusType: selection.focus.type,
  };
}

export function $selectionRangeForTextNode(node: TextNode): MarkdownSelectionRange {
  return {
    anchorKey: node.getKey(),
    anchorOffset: 0,
    anchorType: 'text',
    focusKey: node.getKey(),
    focusOffset: node.getTextContentSize(),
    focusType: 'text',
  };
}

export function $restoreSelectionRange(range: MarkdownSelectionRange): RangeSelection {
  const selection = $createRangeSelection();
  selection.anchor.set(range.anchorKey, range.anchorOffset, range.anchorType);
  selection.focus.set(range.focusKey, range.focusOffset, range.focusType);
  $setSelection(selection);
  return selection;
}

function $isPointAttached(
  key: string,
  offset: number,
  type: MarkdownSelectionRange['anchorType'],
) {
  const node = $getNodeByKey(key);
  if (!node?.isAttached() || offset < 0) return false;
  if (type === 'text') return $isTextNode(node) && offset <= node.getTextContentSize();
  return $isElementNode(node) && offset <= node.getChildrenSize();
}

/** Restore only when both captured points still identify the same live tree. */
export function $tryRestoreSelectionRange(
  range: MarkdownSelectionRange,
): RangeSelection | null {
  if (
    !$isPointAttached(range.anchorKey, range.anchorOffset, range.anchorType)
    || !$isPointAttached(range.focusKey, range.focusOffset, range.focusType)
  ) return null;
  return $restoreSelectionRange(range);
}
