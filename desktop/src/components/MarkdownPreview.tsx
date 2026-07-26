import MarkdownEditor, {
  type EditorReviewFinding,
} from './MarkdownEditor';

/**
 * Read-only Novel surface. Preview and editing share one Markdown schema,
 * so GFM structures cannot drift between the rendered document and editor.
 */
export function MarkdownPreview({
  content,
  className = 'markdown-preview',
  reviewFindings = [],
  onReviewFindingActivate,
}: {
  content: string;
  className?: string;
  reviewFindings?: EditorReviewFinding[];
  onReviewFindingActivate?: (findingId: string) => void;
}) {
  return (
    <MarkdownEditor
      value={content}
      className={className}
      ariaLabel="Rendered Markdown"
      readOnly
      autoFocus={false}
      reviewFindings={reviewFindings}
      onReviewFindingActivate={onReviewFindingActivate}
    />
  );
}
