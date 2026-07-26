import React from 'react';
import { invoke, isTauri } from '@tauri-apps/api/core';
import {
  createCoverBrief,
  generateCoverAsset,
  initialCoverGenerationState,
  transitionCoverGeneration,
  type CoverGenerationRequest,
  type CoverTarget,
} from '../lib/coverGeneration';
import { toWebviewMediaUrl } from '../lib/media';
import type { ImportedMediaAsset, OpenAiCredentialStatus } from '../types';

export function AiCoverGenerator({
  target,
  contentKind,
  title,
  description,
  language,
  disabled = false,
  onConfigureOpenAi,
  onUse,
}: {
  target: CoverTarget;
  contentKind: 'blog' | 'series';
  title: string;
  description?: string | null;
  language?: string | null;
  disabled?: boolean;
  onConfigureOpenAi?: () => void;
  onUse: (asset: ImportedMediaAsset) => void;
}) {
  const [brief, setBrief] = React.useState(() => createCoverBrief({
    contentKind,
    title,
    description,
    language,
  }));
  const [size, setSize] = React.useState<CoverGenerationRequest['size']>('1536x1024');
  const [quality, setQuality] = React.useState<CoverGenerationRequest['quality']>('medium');
  const [candidateSize, setCandidateSize] = React.useState<CoverGenerationRequest['size']>('1536x1024');
  const [optionsVisible, setOptionsVisible] = React.useState(false);
  const [generation, dispatch] = React.useReducer(
    transitionCoverGeneration,
    initialCoverGenerationState,
  );
  const [credential, setCredential] = React.useState<OpenAiCredentialStatus['state'] | 'loading' | 'unavailable'>('loading');

  React.useEffect(() => {
    if (!isTauri()) {
      setCredential('unavailable');
      return undefined;
    }
    let active = true;
    void invoke<OpenAiCredentialStatus>('get_openai_credentials')
      .then((status) => {
        if (active) setCredential(status.state);
      })
      .catch(() => {
        if (active) setCredential('unavailable');
      });
    return () => {
      active = false;
    };
  }, []);

  const candidateUrl = generation.asset
    ? toWebviewMediaUrl(generation.asset.local_path || generation.asset.uri)
    : '';
  const headlineLength = Array.from(brief.headline).length;
  const headlineLong = brief.language === 'zh' ? headlineLength > 28 : headlineLength > 70;
  const generating = generation.phase === 'generating';
  const canGenerate = Boolean(
    credential === 'ready'
    && brief.headline.trim()
    && brief.value.trim(),
  );

  const generate = async () => {
    if (!canGenerate || disabled || generating) return;
    dispatch({ type: 'started' });
    try {
      const asset = await generateCoverAsset(target, brief, {
        size,
        quality,
        outputFormat: 'png',
      });
      setCandidateSize(size);
      dispatch({ type: 'succeeded', asset });
    } catch (reason) {
      dispatch({ type: 'failed', error: String(reason) });
    }
  };

  const applyCandidate = () => {
    if (!generation.asset || generation.phase === 'generating') return;
    onUse(generation.asset);
    dispatch({ type: 'applied' });
  };

  return (
    <div className="ai-cover-generator" data-expanded={optionsVisible || undefined}>
      {!optionsVisible ? (
        <div className="ai-cover-launch">
          <span>Generate a new cover from the article title and summary.</span>
          <button
            type="button"
            disabled={disabled}
            aria-expanded="false"
            onClick={() => setOptionsVisible(true)}
          >
            Generate with AI
          </button>
        </div>
      ) : (
        <>
      <header className="ai-cover-generator-header">
        <div>
          <span>AI cover</span>
          <strong>XHS editorial method</strong>
        </div>
        <div className="ai-cover-header-actions">
          {onConfigureOpenAi && (credential === 'missing' || credential === 'invalid') ? (
            <button
              type="button"
              className="ai-cover-credential"
              data-state={credential}
              disabled={disabled}
              onClick={onConfigureOpenAi}
            >
              {credential === 'missing' ? 'Configure OpenAI' : 'Replace OpenAI key'}
            </button>
          ) : (
            <span className="ai-cover-credential" data-state={credential}>
              {credential === 'ready' ? 'OpenAI ready' : credential === 'loading' ? 'Checking OpenAI' : 'Desktop only'}
            </span>
          )}
          <button
            type="button"
            className="ai-cover-collapse"
            disabled={generating}
            title="Hide generation settings"
            aria-label="Hide generation settings"
            aria-expanded="true"
            onClick={() => setOptionsVisible(false)}
          >
            Hide
          </button>
        </div>
      </header>

      <div className="ai-cover-fields">
        <label className="ai-cover-field">
          <span>Cover headline</span>
          <small className="ai-cover-field-help">The one sentence a reader should understand at thumbnail size.</small>
          <input
            type="text"
            value={brief.headline}
            disabled={disabled || generating}
            onChange={(event) => setBrief((current) => ({ ...current, headline: event.target.value }))}
          />
          <small className="ai-cover-field-count" data-warning={headlineLong || undefined}>{headlineLength} characters</small>
        </label>
        <label className="ai-cover-field">
          <span>Reader</span>
          <small className="ai-cover-field-help">Name the person who should immediately recognize this as relevant.</small>
          <input
            type="text"
            value={brief.audience}
            disabled={disabled || generating}
            onChange={(event) => setBrief((current) => ({ ...current, audience: event.target.value }))}
          />
        </label>
        <label className="ai-cover-field ai-cover-field--wide">
          <span>Problem and value</span>
          <small className="ai-cover-field-help">State the practical problem and the result this article or series delivers.</small>
          <textarea
            rows={3}
            value={brief.value}
            disabled={disabled || generating}
            onChange={(event) => setBrief((current) => ({ ...current, value: event.target.value }))}
          />
        </label>
        <label className="ai-cover-field ai-cover-field--wide">
          <span>Concrete visual</span>
          <small className="ai-cover-field-help">Describe a real scene, object, or material that can carry the idea visually.</small>
          <textarea
            rows={2}
            value={brief.visualDirection}
            disabled={disabled || generating}
            placeholder="Optional scene, object, or material to show"
            onChange={(event) => setBrief((current) => ({ ...current, visualDirection: event.target.value }))}
          />
        </label>
      </div>

      <div className="ai-cover-options">
        <div className="ai-cover-option">
          <div className="ai-cover-option-copy">
            <span>Format</span>
            <small>Wide fits website cards; portrait can be reused on social platforms.</small>
          </div>
          <div className="ai-cover-segmented" role="radiogroup" aria-label="Cover format">
            <button
              type="button"
              role="radio"
              aria-checked={size === '1536x1024'}
              className={size === '1536x1024' ? 'active' : ''}
              disabled={disabled || generating}
              onClick={() => setSize('1536x1024')}
            >
              Wide
            </button>
            <button
              type="button"
              role="radio"
              aria-checked={size === '1024x1536'}
              className={size === '1024x1536' ? 'active' : ''}
              disabled={disabled || generating}
              onClick={() => setSize('1024x1536')}
            >
              Portrait
            </button>
          </div>
        </div>
        <div className="ai-cover-option">
          <div className="ai-cover-option-copy">
            <span>Quality</span>
            <small>Medium is the practical default. High takes longer and costs more.</small>
          </div>
          <div className="ai-cover-segmented ai-cover-segmented--quality" role="radiogroup" aria-label="Image quality">
            {(['low', 'medium', 'high'] as const).map((value) => (
              <button
                key={value}
                type="button"
                role="radio"
                aria-checked={quality === value}
                className={quality === value ? 'active' : ''}
                disabled={disabled || generating}
                onClick={() => setQuality(value)}
              >
                {value[0].toUpperCase() + value.slice(1)}
              </button>
            ))}
          </div>
        </div>
        <button
          type="button"
          className="ai-cover-generate"
          disabled={!canGenerate || disabled || generating}
          onClick={() => void generate()}
        >
          {generating ? 'Generating' : generation.asset ? 'Regenerate' : 'Generate cover'}
        </button>
      </div>

      {candidateUrl && (
        <div className="ai-cover-candidate" data-applied={generation.phase === 'applied' || undefined}>
          <div
            className="ai-cover-candidate-preview"
            data-orientation={candidateSize === '1024x1536' ? 'portrait' : 'wide'}
          >
            <img src={candidateUrl} alt="Generated cover candidate" />
          </div>
          <div>
            <span>Generated candidate</span>
            <small>Review the image, then choose it as the current cover.</small>
            <button
              type="button"
              disabled={disabled || generating || generation.phase === 'applied'}
              onClick={applyCandidate}
            >
              {generation.phase === 'applied' ? 'Selected' : 'Use as cover'}
            </button>
          </div>
        </div>
      )}

      {generation.error && (
        <p className="ai-cover-error" role="alert">
          <span>{generation.error}</span>
        </p>
      )}
        </>
      )}
    </div>
  );
}
