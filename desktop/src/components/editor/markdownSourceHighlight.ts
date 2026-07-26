import type { EditorReviewFinding } from './novelEditorPluginRegistry';

const escapeHtml = (value: string) => value
  .replace(/&/g, '&amp;')
  .replace(/</g, '&lt;')
  .replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;')
  .replace(/'/g, '&#39;');

const inlineTokenPattern = /(`[^`\n]+`)|(!?\[[^\]\n]+\]\([^)]+\))|(\[\[[^\]\n]+\]\])|(^|[\s([{])(#[-\p{L}\p{N}_/]+)|(\*\*[^*\n]+\*\*)|(__[^_\n]+__)|(\*[^*\n]+\*)|(_[^_\n]+_)/gu;

const span = (className: string, value: string) => (
  `<span class="${className}">${escapeHtml(value)}</span>`
);

type SourceReviewRange = {
  from: number;
  to: number;
  className: string;
};

const reviewClassName = (finding: EditorReviewFinding) => (
  `md-src-ai-review-mark md-src-ai-review-mark--${finding.severity}`
);

const findSourceReviewRanges = (markdown: string, findings: EditorReviewFinding[]) => {
  const ranges: SourceReviewRange[] = [];
  findings.forEach((finding) => {
    const quote = finding.quote.trim();
    if (!quote) return;
    let offset = markdown.indexOf(quote);
    while (offset >= 0) {
      ranges.push({
        from: offset,
        to: offset + quote.length,
        className: reviewClassName(finding),
      });
      offset = markdown.indexOf(quote, offset + quote.length);
    }
  });
  return ranges.sort((left, right) => left.from - right.from || right.to - left.to);
};

const splitRangeBoundaries = (from: number, to: number, ranges: SourceReviewRange[]) => {
  const boundaries = new Set([from, to]);
  ranges.forEach((range) => {
    if (range.to <= from || range.from >= to) return;
    boundaries.add(Math.max(from, range.from));
    boundaries.add(Math.min(to, range.to));
  });
  return Array.from(boundaries).sort((left, right) => left - right);
};

const reviewClassForSegment = (from: number, to: number, ranges: SourceReviewRange[]) => (
  ranges.find((range) => range.from <= from && range.to >= to)?.className || ''
);

const highlightPlainText = (
  line: string,
  from: number,
  to: number,
  ranges: SourceReviewRange[],
) => {
  if (from >= to) return '';
  const boundaries = splitRangeBoundaries(from, to, ranges);
  return boundaries.slice(0, -1).map((start, index) => {
    const end = boundaries[index + 1];
    const text = line.slice(start, end);
    const className = reviewClassForSegment(start, end, ranges);
    return className ? span(className, text) : escapeHtml(text);
  }).join('');
};

const highlightToken = (
  className: string,
  line: string,
  from: number,
  to: number,
  ranges: SourceReviewRange[],
) => {
  const boundaries = splitRangeBoundaries(from, to, ranges);
  return boundaries.slice(0, -1).map((start, index) => {
    const end = boundaries[index + 1];
    const tokenClassName = [
      className,
      reviewClassForSegment(start, end, ranges),
    ].filter(Boolean).join(' ');
    return span(tokenClassName, line.slice(start, end));
  }).join('');
};

const shiftRanges = (
  ranges: SourceReviewRange[],
  offset: number,
  length: number,
) => ranges
  .map((range) => ({
    ...range,
    from: range.from - offset,
    to: range.to - offset,
  }))
  .filter((range) => range.to > 0 && range.from < length);

const highlightInlineMarkdown = (line: string, ranges: SourceReviewRange[] = []) => {
  let highlighted = '';
  let lastIndex = 0;

  for (const match of line.matchAll(inlineTokenPattern)) {
    const matchText = match[0];
    const index = match.index ?? 0;
    highlighted += highlightPlainText(line, lastIndex, index, ranges);

    if (match[1]) highlighted += highlightToken('md-src-inline-code', line, index, index + matchText.length, ranges);
    else if (match[2]) {
      highlighted += highlightToken(
        match[2].startsWith('!') ? 'md-src-image' : 'md-src-link',
        line,
        index,
        index + matchText.length,
        ranges,
      );
    } else if (match[3]) highlighted += highlightToken('md-src-wiki-link', line, index, index + matchText.length, ranges);
    else if (match[5]) {
      const prefix = match[4] ?? '';
      highlighted += highlightPlainText(line, index, index + prefix.length, ranges);
      highlighted += highlightToken('md-src-tag', line, index + prefix.length, index + matchText.length, ranges);
    } else if (match[6] || match[7]) highlighted += highlightToken('md-src-strong', line, index, index + matchText.length, ranges);
    else if (match[8] || match[9]) highlighted += highlightToken('md-src-emphasis', line, index, index + matchText.length, ranges);
    else highlighted += highlightPlainText(line, index, index + matchText.length, ranges);

    lastIndex = index + matchText.length;
  }

  highlighted += highlightPlainText(line, lastIndex, line.length, ranges);
  return highlighted || '&nbsp;';
};

export const highlightMarkdownSource = (
  markdown: string,
  reviewFindings: EditorReviewFinding[] = [],
) => {
  const lines = markdown.split('\n');
  const reviewRanges = findSourceReviewRanges(markdown, reviewFindings);
  let lineStart = 0;
  let inCodeFence = false;

  return lines.map((line) => {
    const ranges = reviewRanges
      .filter((range) => range.from < lineStart + line.length && range.to > lineStart)
      .map((range) => ({
        ...range,
        from: Math.max(0, range.from - lineStart),
        to: Math.min(line.length, range.to - lineStart),
      }));
    lineStart += line.length + 1;

    const fence = line.match(/^(\s*)(`{3,}|~{3,})(.*)$/);
    if (fence) {
      inCodeFence = !inCodeFence;
      return `${escapeHtml(fence[1])}${span('md-src-fence', fence[2])}${span('md-src-code-info', fence[3])}`;
    }

    if (inCodeFence) return span('md-src-code-line', line || ' ');

    const heading = line.match(/^(#{1,6})(\s+.*)$/);
    if (heading) {
      const markerEnd = heading[1].length;
      return `${highlightToken('md-src-heading-marker', line, 0, markerEnd, ranges)}${highlightToken('md-src-heading-text', line, markerEnd, line.length, ranges)}`;
    }

    const quote = line.match(/^(\s*>+)(\s?.*)$/);
    if (quote) {
      const markerEnd = quote[1].length;
      return `${highlightToken('md-src-quote-marker', line, 0, markerEnd, ranges)}${highlightToken('md-src-quote-text', line, markerEnd, line.length, ranges)}`;
    }

    const task = line.match(/^(\s*)([-+*])(\s+\[[ xX]\]\s+)(.*)$/);
    if (task) {
      const markerStart = task[1].length;
      const taskStart = markerStart + task[2].length;
      const contentStart = taskStart + task[3].length;
      const content = line.slice(contentStart);
      return [
        highlightPlainText(line, 0, markerStart, ranges),
        highlightToken('md-src-list-marker', line, markerStart, taskStart, ranges),
        highlightToken('md-src-task-marker', line, taskStart, contentStart, ranges),
        highlightInlineMarkdown(content, shiftRanges(ranges, contentStart, content.length)),
      ].join('');
    }

    const unordered = line.match(/^(\s*)([-+*])(\s+)(.*)$/);
    if (unordered) {
      const markerStart = unordered[1].length;
      const spacingStart = markerStart + unordered[2].length;
      const contentStart = spacingStart + unordered[3].length;
      const content = line.slice(contentStart);
      return [
        highlightPlainText(line, 0, markerStart, ranges),
        highlightToken('md-src-list-marker', line, markerStart, spacingStart, ranges),
        highlightPlainText(line, spacingStart, contentStart, ranges),
        highlightInlineMarkdown(content, shiftRanges(ranges, contentStart, content.length)),
      ].join('');
    }

    const ordered = line.match(/^(\s*)(\d+\.)(\s+)(.*)$/);
    if (ordered) {
      const markerStart = ordered[1].length;
      const spacingStart = markerStart + ordered[2].length;
      const contentStart = spacingStart + ordered[3].length;
      const content = line.slice(contentStart);
      return [
        highlightPlainText(line, 0, markerStart, ranges),
        highlightToken('md-src-list-marker', line, markerStart, spacingStart, ranges),
        highlightPlainText(line, spacingStart, contentStart, ranges),
        highlightInlineMarkdown(content, shiftRanges(ranges, contentStart, content.length)),
      ].join('');
    }

    if (/^\s*\|.*\|\s*$/.test(line)) return highlightToken('md-src-table', line, 0, line.length || 1, ranges);
    if (/^\s*(-{3,}|\*{3,}|_{3,})\s*$/.test(line)) return highlightToken('md-src-hr', line, 0, line.length, ranges);

    return highlightInlineMarkdown(line, ranges);
  }).join('\n');
};
