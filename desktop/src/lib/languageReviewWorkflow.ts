import React from 'react';
import { invoke } from '@tauri-apps/api/core';
import type {
  DocumentLanguageAudit,
  LanguageAuditFinding,
  LanguageAuditReport,
} from '../types';

export type LanguageReviewTarget =
  | { kind: 'translation'; id: string; label: string }
  | { kind: 'blog'; slug: string; label: string }
  | { kind: 'episode_series'; seriesSlug: string; label: string };

export type LanguageReviewState = {
  phase: 'idle' | 'running' | 'complete' | 'failed';
  visible: boolean;
  target: LanguageReviewTarget | null;
  report: LanguageAuditReport | null;
  error: string | null;
};

export type LanguageReviewEvent =
  | { type: 'started'; target: LanguageReviewTarget }
  | { type: 'completed'; report: LanguageAuditReport }
  | { type: 'failed'; error: string }
  | { type: 'findingResolved'; findingId: string }
  | { type: 'opened' }
  | { type: 'closed' };

const initialState: LanguageReviewState = {
  phase: 'idle',
  visible: false,
  target: null,
  report: null,
  error: null,
};

function stableHash(value: string) {
  let hash = 2166136261;
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return (hash >>> 0).toString(36);
}

export function languageReviewFindingId(
  result: Pick<DocumentLanguageAudit, 'source_path' | 'language'>,
  finding: LanguageAuditFinding,
) {
  return `review-${stableHash([
    result.source_path,
    result.language,
    finding.category,
    finding.source_line || 0,
    finding.quote,
    finding.suggestion,
  ].join('\u001f'))}`;
}

function resolveReportFinding(report: LanguageAuditReport, findingId: string) {
  const results = report.results.map((result) => ({
    ...result,
    findings: result.findings.filter(
      (finding) => languageReviewFindingId(result, finding) !== findingId,
    ),
  }));
  const findings = results.flatMap((result) => result.findings);
  return {
    ...report,
    results,
    findings_total: findings.length,
    major_findings: findings.filter((finding) => finding.severity === 'major').length,
  };
}

export function languageReviewTransition(
  state: LanguageReviewState,
  event: LanguageReviewEvent,
): LanguageReviewState {
  switch (event.type) {
    case 'started':
      return {
        phase: 'running',
        visible: true,
        target: event.target,
        report: null,
        error: null,
      };
    case 'completed':
      return { ...state, phase: 'complete', report: event.report, error: null };
    case 'failed':
      return { ...state, phase: 'failed', report: null, error: event.error };
    case 'findingResolved':
      return state.report
        ? { ...state, report: resolveReportFinding(state.report, event.findingId) }
        : state;
    case 'opened':
      return state.report ? { ...state, visible: true } : state;
    case 'closed':
      return state.phase === 'running' ? state : { ...state, visible: false };
  }
}

async function executeLanguageReview(target: LanguageReviewTarget) {
  switch (target.kind) {
    case 'translation':
      return invoke<LanguageAuditReport>('review_document_language', { id: target.id });
    case 'blog':
      return invoke<LanguageAuditReport>('review_blog_language', { slug: target.slug });
    case 'episode_series':
      return invoke<LanguageAuditReport>('review_episode_series_language', {
        seriesSlug: target.seriesSlug,
      });
  }
}

export function useLanguageReviewWorkflow() {
  const [state, dispatch] = React.useReducer(languageReviewTransition, initialState);

  const run = React.useCallback(async (target: LanguageReviewTarget) => {
    dispatch({ type: 'started', target });
    try {
      const report = await executeLanguageReview(target);
      dispatch({ type: 'completed', report });
    } catch (reason) {
      dispatch({ type: 'failed', error: String(reason) });
    }
  }, []);

  const retry = React.useCallback(() => {
    if (state.target && state.phase !== 'running') void run(state.target);
  }, [run, state.phase, state.target]);

  return {
    state,
    run,
    retry,
    close: () => dispatch({ type: 'closed' }),
    openReport: () => dispatch({ type: 'opened' }),
    resolveFinding: (findingId: string) => dispatch({ type: 'findingResolved', findingId }),
  };
}
