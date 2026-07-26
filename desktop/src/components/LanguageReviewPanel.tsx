import {
  AlertCircle,
  CheckCircle2,
  FileSearch,
  LoaderCircle,
  LocateFixed,
  RotateCcw,
  ShieldCheck,
  WandSparkles,
  X,
} from 'lucide-react';
import type { LanguageReviewState } from '../lib/languageReviewWorkflow';
import type {
  DocumentLanguageAudit,
  LanguageAuditCategory,
  LanguageAuditFinding,
} from '../types';

type LanguageReviewPanelProps = {
  state: LanguageReviewState;
  onClose: () => void;
  onRetry: () => void;
  onFindingOpen: (
    result: DocumentLanguageAudit,
    finding: LanguageAuditFinding,
  ) => void;
  onFindingApply: (
    result: DocumentLanguageAudit,
    finding: LanguageAuditFinding,
  ) => void;
};

const categoryLabels: Record<LanguageAuditCategory, string> = {
  unnatural_expression: 'Unnatural expression',
  logical_gap: 'Logical gap',
  concept_misuse: 'Concept misuse',
  terminology: 'Terminology',
};

export function LanguageReviewPanel({
  state,
  onClose,
  onRetry,
  onFindingOpen,
  onFindingApply,
}: LanguageReviewPanelProps) {
  if (!state.visible) return null;
  const report = state.report;

  return (
    <div
      className="dialog-overlay language-review-overlay"
      role="presentation"
      onClick={() => {
        if (state.phase !== 'running') onClose();
      }}
    >
      <section
        className="dialog-card language-review-card"
        role="dialog"
        aria-modal="true"
        aria-labelledby="language-review-title"
        onClick={(event) => event.stopPropagation()}
      >
        <header className="language-review-head">
          <div className="new-project-badge"><FileSearch size={17} /></div>
          <div>
            <span>DEEPSEEK LANGUAGE REVIEW</span>
            <h3 id="language-review-title">{state.target?.label || 'Language review'}</h3>
          </div>
          <button
            type="button"
            className="language-close-button language-review-close"
            disabled={state.phase === 'running'}
            aria-label="Close language review"
            onClick={onClose}
          >
            <X size={15} />
          </button>
        </header>

        {state.phase === 'running' && (
          <div className="language-review-running" role="status">
            <LoaderCircle size={22} />
            <strong>Reviewing saved source…</strong>
            <p>
              The fixed workflow is discovering the target, checking each document,
              validating structured findings, and building one report.
            </p>
          </div>
        )}

        {state.phase === 'failed' && (
          <div className="language-review-failure" role="alert">
            <AlertCircle size={18} />
            <div>
              <strong>Review could not complete</strong>
              <p>{state.error}</p>
            </div>
          </div>
        )}

        {state.phase === 'complete' && report && (
          <>
            <div className="language-review-summary">
              <div>
                {report.documents_failed === 0
                  ? <CheckCircle2 size={18} />
                  : <AlertCircle size={18} />}
                <span>{report.documents_completed}/{report.documents_total} documents</span>
              </div>
              <div>
                <strong>{report.findings_total}</strong>
                <span>findings</span>
              </div>
              <div>
                <strong>{report.major_findings}</strong>
                <span>major</span>
              </div>
              <div className="language-review-model">
                <ShieldCheck size={15} />
                <span>{report.model} · confidence ≥ {report.min_confidence.toFixed(2)}</span>
              </div>
            </div>

            <div className="language-review-results">
              {report.results.map((result) => (
                <section className="language-review-document" key={`${result.source_path}:${result.language}`}>
                  <header>
                    <div>
                      <strong>{result.title}</strong>
                      <span>{result.language} · {result.source_path}</span>
                    </div>
                    <em data-state={result.findings.length === 0 ? 'pass' : 'review'}>
                      {result.findings.length === 0 ? 'Pass' : `${result.findings.length} to review`}
                    </em>
                  </header>

                  {result.findings.length === 0 ? (
                    <p className="language-review-document-summary">{result.summary}</p>
                  ) : (
                    <div className="language-review-findings">
                      {result.findings.map((finding, index) => (
                        <article
                          className="language-review-finding"
                          data-severity={finding.severity}
                          key={`${finding.category}:${finding.source_line || 0}:${index}`}
                        >
                          <div className="language-review-finding-meta">
                            <span>{finding.severity}</span>
                            <strong>{categoryLabels[finding.category]}</strong>
                            <small>
                              {finding.source_line ? `line ${finding.source_line} · ` : ''}
                              {Math.round(finding.confidence * 100)}%
                            </small>
                          </div>
                          <blockquote>{finding.quote}</blockquote>
                          <p>{finding.explanation}</p>
                          <div className="language-review-suggestion">
                            <span>Suggested repair</span>
                            <p>{finding.suggestion}</p>
                          </div>
                          <div className="language-review-finding-actions">
                            <button
                              type="button"
                              onClick={() => onFindingOpen(result, finding)}
                            >
                              <LocateFixed size={13} />
                              Open in editor
                            </button>
                            <button
                              type="button"
                              className="primary"
                              disabled={!finding.suggestion.trim()}
                              onClick={() => onFindingApply(result, finding)}
                            >
                              <WandSparkles size={13} />
                              Apply suggestion
                            </button>
                          </div>
                        </article>
                      ))}
                    </div>
                  )}
                </section>
              ))}

              {report.failures.map((failure) => (
                <section className="language-review-document failed" key={failure.source_path}>
                  <header>
                    <div>
                      <strong>{failure.source_path}</strong>
                      <span>{failure.language}</span>
                    </div>
                    <em data-state="failed">Failed</em>
                  </header>
                  <p className="language-review-document-summary">{failure.error}</p>
                </section>
              ))}
            </div>
          </>
        )}

        {state.phase !== 'running' && (
          <footer className="language-review-actions">
            <button type="button" className="cancel" onClick={onClose}>Close</button>
            <button type="button" className="primary" onClick={onRetry}>
              <RotateCcw size={14} />
              Review again
            </button>
          </footer>
        )}
      </section>
    </div>
  );
}
