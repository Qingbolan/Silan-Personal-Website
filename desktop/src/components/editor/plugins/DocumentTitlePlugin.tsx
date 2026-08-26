import React from 'react';
import { useLexicalComposerContext } from '@lexical/react/LexicalComposerContext';
import type { EditorState, NodeKey } from 'lexical';
import {
  $getDocumentTitleNode,
  registerDocumentTitleTransform,
} from '../model/DocumentTitle';
import { readEditorSnapshot } from '../model/MarkdownDocument';

export type MarkdownDocumentMeta = {
  authorName: string;
  authorAvatarUrl?: string;
  authorAvatarLabel?: string;
  modifiedAt: string;
  modifiedLabel: string;
};

type DocumentTitlePosition = {
  left: number;
  top: number;
  width: number;
};

/**
 * Lexical-native document title behavior. Title identity comes exclusively
 * from EditorState; the DOM element resolved from the node key is used only
 * for positioning presentation-only metadata.
 */
export function DocumentTitlePlugin({
  defaultTitle,
  meta,
}: {
  defaultTitle: string;
  meta?: MarkdownDocumentMeta;
}) {
  const [editor] = useLexicalComposerContext();
  const [position, setPosition] = React.useState<DocumentTitlePosition | null>(null);

  React.useLayoutEffect(
    () => registerDocumentTitleTransform(editor),
    [editor],
  );

  React.useLayoutEffect(() => {
    let root: HTMLElement | null = null;
    let titleKey: NodeKey | null = null;
    let titleElement: HTMLElement | null = null;
    let resizeObserver: ResizeObserver | null = null;
    let animationFrame = 0;

    const stopObservingTitle = () => {
      titleElement?.classList.remove('lexical-document-title');
      titleElement?.classList.remove('lexical-document-title--empty');
      titleElement?.removeAttribute('data-placeholder');
      resizeObserver?.disconnect();
      resizeObserver = null;
      titleElement = null;
    };

    const observeTitle = (nextTitle: HTMLElement | null) => {
      if (nextTitle === titleElement) return;
      stopObservingTitle();
      titleElement = nextTitle;
      if (!root || !titleElement) return;
      titleElement.classList.add('lexical-document-title');
      titleElement.dataset.placeholder = defaultTitle;
      resizeObserver = new ResizeObserver(scheduleMeasure);
      resizeObserver.observe(root);
      resizeObserver.observe(titleElement);
    };

    const measure = () => {
      animationFrame = 0;
      observeTitle(titleKey ? editor.getElementByKey(titleKey) : null);
      if (!root || !titleElement) {
        setPosition(null);
        return;
      }
      const next = {
        left: titleElement.offsetLeft,
        top: titleElement.offsetTop + titleElement.offsetHeight + 10 - root.scrollTop,
        width: titleElement.offsetWidth,
      };
      setPosition((current) => (
        current
        && current.left === next.left
        && current.top === next.top
        && current.width === next.width
          ? current
          : next
      ));
    };

    function scheduleMeasure() {
      if (animationFrame) window.cancelAnimationFrame(animationFrame);
      animationFrame = window.requestAnimationFrame(measure);
    }

    const readTitleKey = (editorState: EditorState) => {
      const titleSnapshot = readEditorSnapshot(
        editor,
        editorState,
        () => {
          const title = $getDocumentTitleNode();
          return {
            key: title?.getKey() || null,
            empty: !title?.getTextContent().trim(),
          };
        },
      );
      titleKey = titleSnapshot.key;
      const nextTitleElement = titleKey ? editor.getElementByKey(titleKey) : null;
      observeTitle(nextTitleElement);
      titleElement?.classList.toggle('lexical-document-title--empty', titleSnapshot.empty);
      if (titleElement) titleElement.dataset.placeholder = defaultTitle;
      scheduleMeasure();
    };

    const observeRoot = (nextRoot: HTMLElement | null) => {
      root?.removeEventListener('scroll', scheduleMeasure);
      stopObservingTitle();
      root = nextRoot;
      root?.addEventListener('scroll', scheduleMeasure, { passive: true });
      readTitleKey(editor.getEditorState());
      scheduleMeasure();
    };

    const unregisterRoot = editor.registerRootListener(observeRoot);
    const unregisterUpdate = editor.registerUpdateListener(({ editorState }) => {
      readTitleKey(editorState);
      scheduleMeasure();
    });

    return () => {
      unregisterRoot();
      unregisterUpdate();
      root?.removeEventListener('scroll', scheduleMeasure);
      stopObservingTitle();
      if (animationFrame) window.cancelAnimationFrame(animationFrame);
    };
  }, [defaultTitle, editor]);

  if (!meta || !position) return null;
  return (
    <div
      className="novel-document-meta"
      style={{ left: position.left, top: position.top, width: position.width }}
      contentEditable={false}
    >
      <span className="novel-document-meta__avatar" aria-hidden="true">
        {meta.authorAvatarUrl ? (
          <img src={meta.authorAvatarUrl} alt="" />
        ) : (
          meta.authorAvatarLabel || meta.authorName.slice(0, 1).toUpperCase()
        )}
      </span>
      <strong>{meta.authorName}</strong>
      <span className="novel-document-meta__divider" aria-hidden="true" />
      <time dateTime={meta.modifiedAt}>{meta.modifiedLabel}</time>
    </div>
  );
}
