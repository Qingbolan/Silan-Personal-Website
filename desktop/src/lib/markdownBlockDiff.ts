export type MarkdownBlockChangeSummary = {
  before: number;
  after: number;
  changed: number;
  added: number;
  removed: number;
  affected: number;
};

function markdownBlocks(markdown: string) {
  return markdown
    .replace(/\r\n?/g, '\n')
    .split(/\n{2,}/)
    .map((block) => block.trim())
    .filter(Boolean);
}

function longestCommonSubsequence(left: string[], right: string[]) {
  const rows = Array.from(
    { length: left.length + 1 },
    () => new Uint32Array(right.length + 1),
  );
  for (let leftIndex = 1; leftIndex <= left.length; leftIndex += 1) {
    for (let rightIndex = 1; rightIndex <= right.length; rightIndex += 1) {
      rows[leftIndex][rightIndex] = left[leftIndex - 1] === right[rightIndex - 1]
        ? rows[leftIndex - 1][rightIndex - 1] + 1
        : Math.max(
            rows[leftIndex - 1][rightIndex],
            rows[leftIndex][rightIndex - 1],
          );
    }
  }
  return rows[left.length][right.length];
}

/**
 * Compares semantic Markdown blocks instead of characters. A remove/add pair
 * is reported as one changed block; unmatched additions and removals stay
 * explicit for interaction copy.
 */
export function summarizeMarkdownBlockChanges(
  beforeMarkdown: string,
  afterMarkdown: string,
): MarkdownBlockChangeSummary {
  const beforeBlocks = markdownBlocks(beforeMarkdown);
  const afterBlocks = markdownBlocks(afterMarkdown);
  const unchanged = longestCommonSubsequence(beforeBlocks, afterBlocks);
  const unmatchedBefore = beforeBlocks.length - unchanged;
  const unmatchedAfter = afterBlocks.length - unchanged;
  const changed = Math.min(unmatchedBefore, unmatchedAfter);
  const removed = unmatchedBefore - changed;
  const added = unmatchedAfter - changed;
  return {
    before: beforeBlocks.length,
    after: afterBlocks.length,
    changed,
    added,
    removed,
    affected: changed + added + removed,
  };
}
