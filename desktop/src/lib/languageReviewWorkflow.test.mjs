import assert from 'node:assert/strict';
import test from 'node:test';
import {
  languageReviewFindingId,
  languageReviewTransition,
} from './languageReviewWorkflow.ts';

const idle = {
  phase: 'idle',
  visible: false,
  target: null,
  report: null,
  error: null,
};

test('language review workflow has explicit running and terminal states', () => {
  const target = { kind: 'translation', id: 'part:en', label: 'Body · en' };
  const running = languageReviewTransition(idle, { type: 'started', target });
  assert.equal(running.phase, 'running');
  assert.equal(running.visible, true);
  assert.equal(languageReviewTransition(running, { type: 'closed' }), running);

  const failed = languageReviewTransition(running, {
    type: 'failed',
    error: 'provider unavailable',
  });
  assert.equal(failed.phase, 'failed');
  assert.equal(failed.error, 'provider unavailable');
  assert.equal(languageReviewTransition(failed, { type: 'closed' }).visible, false);
});

test('applying a finding resolves it from the active report', () => {
  const finding = {
    category: 'terminology',
    severity: 'major',
    quote: 'old term',
    explanation: 'Use the canonical term.',
    suggestion: 'canonical term',
    confidence: 0.96,
    source_line: 7,
  };
  const result = {
    target_uri: 'blog://demo/body',
    source_path: 'content/demo/en.md',
    language: 'en',
    title: 'Demo',
    provider: 'deepseek',
    model: 'deepseek-chat',
    summary: 'One finding.',
    findings: [finding],
  };
  const report = {
    state: 'complete',
    provider: 'deepseek',
    model: 'deepseek-chat',
    min_confidence: 0.8,
    scope: 'blog',
    documents_total: 1,
    documents_completed: 1,
    documents_failed: 0,
    findings_total: 1,
    major_findings: 1,
    results: [result],
    failures: [],
  };
  const complete = languageReviewTransition(idle, { type: 'completed', report });
  const resolved = languageReviewTransition(complete, {
    type: 'findingResolved',
    findingId: languageReviewFindingId(result, finding),
  });
  assert.equal(resolved.report?.findings_total, 0);
  assert.equal(resolved.report?.major_findings, 0);
  assert.deepEqual(resolved.report?.results[0].findings, []);
});
