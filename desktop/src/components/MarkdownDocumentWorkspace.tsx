import React from 'react';
import {
  AlertCircle,
  CheckCircle2,
  FileSearch,
  GripVertical,
  LoaderCircle,
} from 'lucide-react';
import MarkdownEditor, {
  type MarkdownEditorHandle,
  type MarkdownEditorProps,
} from './MarkdownEditor';
import { MarkdownPreview } from './MarkdownPreview';
import type { MarkdownWorkspaceView } from '../lib/markdownWorkspaceView';

export type MarkdownWorkspaceActivity = {
  state: 'working' | 'complete' | 'review' | 'error';
  label: string;
  detail?: string;
};

type MarkdownDocumentWorkspaceProps = MarkdownEditorProps & {
  previewLabel: string;
  view: MarkdownWorkspaceView;
  activity?: MarkdownWorkspaceActivity | null;
};

/**
 * Renders the controlled edit/split/preview state for one Markdown representation.
 * The controlled Markdown value is the persistence boundary: Lexical emits it from
 * the writing pane and the preview consumes the same value on every render.
 * Split binds the left pane to styled Markdown source while keeping the right
 * pane as an independently scrollable rendered document.
 */
export const MarkdownDocumentWorkspace = React.forwardRef<
  MarkdownEditorHandle,
  MarkdownDocumentWorkspaceProps
>(function MarkdownDocumentWorkspace({
  previewLabel,
  view,
  activity,
  value,
  onChange,
  ...editorProps
}, forwardedRef) {
  const [liveValue, setLiveValue] = React.useState(value);
  const [splitPercent, setSplitPercent] = React.useState(() => {
    const stored = Number(window.localStorage.getItem('sv-editor-split-percent'));
    return Number.isFinite(stored) && stored >= 30 && stored <= 70 ? stored : 54;
  });
  const [resizing, setResizing] = React.useState(false);
  const workspaceRef = React.useRef<HTMLDivElement | null>(null);
  const previewPaneRef = React.useRef<HTMLElement | null>(null);
  const previewVisible = view !== 'edit';
  const editorVisible = view !== 'preview';

  React.useEffect(() => {
    setLiveValue(value);
  }, [value]);

  React.useEffect(() => {
    if (view !== 'preview') return undefined;
    const frame = window.requestAnimationFrame(() => {
      previewPaneRef.current?.focus({ preventScroll: true });
    });
    return () => window.cancelAnimationFrame(frame);
  }, [view]);

  const handleEditorChange = React.useCallback((nextValue: string) => {
    setLiveValue(nextValue);
    onChange?.(nextValue);
  }, [onChange]);

  const resizeFromClientX = React.useCallback((clientX: number) => {
    const bounds = workspaceRef.current?.getBoundingClientRect();
    if (!bounds || bounds.width <= 0) return;
    const percent = ((clientX - bounds.left) / bounds.width) * 100;
    setSplitPercent(Math.min(70, Math.max(30, Math.round(percent))));
  }, []);

  const finishResize = React.useCallback((event: React.PointerEvent<HTMLButtonElement>) => {
    if (!resizing) return;
    event.currentTarget.releasePointerCapture(event.pointerId);
    setResizing(false);
    window.localStorage.setItem('sv-editor-split-percent', String(splitPercent));
  }, [resizing, splitPercent]);

  return (
    <div
      ref={workspaceRef}
      className="markdown-document-workspace"
      data-view={view}
      data-resizing={resizing ? 'true' : 'false'}
      style={{ '--editor-pane-width': `${splitPercent}%` } as React.CSSProperties}
    >
      <section
        className="markdown-workspace-pane markdown-workspace-editor"
        aria-label={`${previewLabel} editor`}
        aria-hidden={!editorVisible}
      >
        <MarkdownEditor
          {...editorProps}
          ref={forwardedRef}
          value={liveValue}
          editingMode={view === 'split' ? 'source' : editorProps.editingMode}
          autoFocus={editorProps.autoFocus ?? false}
          onChange={handleEditorChange}
        />
      </section>

      <button
        type="button"
        className="markdown-workspace-resizer"
        role="separator"
        aria-label="Resize editor and preview panes"
        aria-orientation="vertical"
        aria-valuemin={30}
        aria-valuemax={70}
        aria-valuenow={splitPercent}
        onPointerDown={(event) => {
          event.currentTarget.setPointerCapture(event.pointerId);
          setResizing(true);
          resizeFromClientX(event.clientX);
        }}
        onPointerMove={(event) => {
          if (resizing) resizeFromClientX(event.clientX);
        }}
        onPointerUp={finishResize}
        onPointerCancel={finishResize}
        onKeyDown={(event) => {
          if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
          event.preventDefault();
          setSplitPercent((current) => {
            const next = Math.min(70, Math.max(30, current + (event.key === 'ArrowRight' ? 2 : -2)));
            window.localStorage.setItem('sv-editor-split-percent', String(next));
            return next;
          });
        }}
      >
        <GripVertical size={12} />
      </button>

      <section
        ref={previewPaneRef}
        className="markdown-workspace-pane markdown-workspace-preview"
        aria-label={`${previewLabel} live preview`}
        aria-hidden={!previewVisible}
        tabIndex={previewVisible ? 0 : -1}
        onKeyDown={(event) => {
          const pane = previewPaneRef.current;
          if (!pane || event.metaKey || event.ctrlKey || event.altKey) return;
          const page = Math.max(120, pane.clientHeight * 0.82);
          const scrollBy = (top: number) => {
            event.preventDefault();
            pane.scrollBy({ top, behavior: 'auto' });
          };
          if (event.key === 'PageDown' || event.key === ' ') scrollBy(page);
          else if (event.key === 'PageUp') scrollBy(-page);
          else if (event.key === 'ArrowDown') scrollBy(48);
          else if (event.key === 'ArrowUp') scrollBy(-48);
          else if (event.key === 'Home') {
            event.preventDefault();
            pane.scrollTo({ top: 0, behavior: 'auto' });
          } else if (event.key === 'End') {
            event.preventDefault();
            pane.scrollTo({ top: pane.scrollHeight, behavior: 'auto' });
          }
        }}
      >
        <MarkdownPreview
          content={liveValue}
          className="markdown-preview markdown-document-preview"
          reviewFindings={editorProps.reviewFindings}
          onReviewFindingActivate={editorProps.onReviewFindingActivate}
        />
      </section>

      {activity && (
        <div
          className="markdown-workspace-activity"
          data-state={activity.state}
          role="status"
          aria-live="polite"
        >
          {activity.state === 'working' && <LoaderCircle size={13} />}
          {activity.state === 'complete' && <CheckCircle2 size={13} />}
          {activity.state === 'review' && <FileSearch size={13} />}
          {activity.state === 'error' && <AlertCircle size={13} />}
          <span>
            <strong>{activity.label}</strong>
            {activity.detail && <small>{activity.detail}</small>}
          </span>
        </div>
      )}

    </div>
  );
});
