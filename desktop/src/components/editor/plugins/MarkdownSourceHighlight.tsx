import React from 'react';
import type { MarkdownSourceSegment } from '../model/MarkdownSourceProjection';

export const MarkdownSourceHighlight = React.forwardRef<
  HTMLPreElement,
  { segments: readonly MarkdownSourceSegment[] }
>(function MarkdownSourceHighlight({ segments }, ref) {
  return (
    <pre
      ref={ref}
      className="novel-source-highlight"
      aria-hidden="true"
      data-source-projection="mdast"
    >
      <code>
        {segments.map((segment) => (
          <span
            key={`${segment.start}:${segment.end}`}
            className={segment.styles.map((style) => `novel-source-token--${style}`).join(' ')}
          >
            {segment.text}
          </span>
        ))}
        <span className="novel-source-highlight__sentinel"> </span>
      </code>
    </pre>
  );
});
