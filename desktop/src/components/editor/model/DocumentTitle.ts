import {
  $createHeadingNode,
  $isHeadingNode,
  type HeadingNode,
} from '@lexical/rich-text';
import {
  $getRoot,
  RootNode,
  type LexicalEditor,
  type LexicalNode,
} from 'lexical';

/**
 * The Markdown document title is the first root-level H1. Keeping this rule in
 * the Lexical model makes title identity independent from rendered DOM order.
 */
export function $getDocumentTitleNode(): HeadingNode | null {
  const firstBlock = $getRoot().getFirstChild();
  return $isHeadingNode(firstBlock) && firstBlock.getTag() === 'h1'
    ? firstBlock
    : null;
}

export function $isDocumentTitleNode(node: LexicalNode | null | undefined): boolean {
  const title = $getDocumentTitleNode();
  return Boolean(node && title && node.getKey() === title.getKey());
}

/** Ensure the first root block is the document's dedicated H1 title. */
export function $ensureDocumentTitleNode(): HeadingNode {
  const existing = $getDocumentTitleNode();
  if (existing) return existing;

  const title = $createHeadingNode('h1');
  const root = $getRoot();
  const firstBlock = root.getFirstChild();
  if (firstBlock) firstBlock.insertBefore(title);
  else root.append(title);
  return title;
}

export function $getDocumentTitleText(): string {
  return $getDocumentTitleNode()?.getTextContent().trim() || '';
}

/**
 * Own the title structural invariant inside Lexical's reconciliation cycle.
 * The default title remains presentation-only placeholder text. Deleting or
 * demoting the title therefore creates an empty editable title block instead
 * of injecting persisted metadata into the Markdown body.
 */
export function registerDocumentTitleTransform(
  editor: LexicalEditor,
): () => void {
  return editor.registerNodeTransform(RootNode, () => {
    $ensureDocumentTitleNode();
  });
}
