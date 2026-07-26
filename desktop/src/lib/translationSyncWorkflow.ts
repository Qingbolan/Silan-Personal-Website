import React from 'react';
import type { MarkdownBlockChangeSummary } from './markdownBlockDiff';

export type TranslationSyncState = {
  phase: 'idle' | 'saving_source' | 'syncing' | 'complete' | 'failed';
  key: string | null;
  documentId: string | null;
  sourceLanguage: string | null;
  targetLanguage: string | null;
  sourceChanges: MarkdownBlockChangeSummary | null;
  targetChanges: MarkdownBlockChangeSummary | null;
  error: string | null;
};

export type TranslationSyncEvent =
  | {
      type: 'started';
      key: string;
      documentId: string;
      sourceLanguage: string;
      targetLanguage: string;
      sourceChanges: MarkdownBlockChangeSummary;
      saveRequired: boolean;
    }
  | { type: 'sourceSaved' }
  | { type: 'completed'; targetChanges: MarkdownBlockChangeSummary }
  | { type: 'failed'; error: string }
  | { type: 'reset' };

export const initialTranslationSyncState: TranslationSyncState = {
  phase: 'idle',
  key: null,
  documentId: null,
  sourceLanguage: null,
  targetLanguage: null,
  sourceChanges: null,
  targetChanges: null,
  error: null,
};

export function translationSyncTransition(
  state: TranslationSyncState,
  event: TranslationSyncEvent,
): TranslationSyncState {
  switch (event.type) {
    case 'started':
      return {
        phase: event.saveRequired ? 'saving_source' : 'syncing',
        key: event.key,
        documentId: event.documentId,
        sourceLanguage: event.sourceLanguage,
        targetLanguage: event.targetLanguage,
        sourceChanges: event.sourceChanges,
        targetChanges: null,
        error: null,
      };
    case 'sourceSaved':
      return state.phase === 'saving_source'
        ? { ...state, phase: 'syncing' }
        : state;
    case 'completed':
      return { ...state, phase: 'complete', targetChanges: event.targetChanges, error: null };
    case 'failed':
      return { ...state, phase: 'failed', error: event.error };
    case 'reset':
      return initialTranslationSyncState;
  }
}

export function useTranslationSyncWorkflow() {
  const [state, dispatch] = React.useReducer(
    translationSyncTransition,
    initialTranslationSyncState,
  );
  const begin = React.useCallback((
    input: Omit<Extract<TranslationSyncEvent, { type: 'started' }>, 'type'>,
  ) => dispatch({ type: 'started', ...input }), []);
  const sourceSaved = React.useCallback(() => dispatch({ type: 'sourceSaved' }), []);
  const complete = React.useCallback((targetChanges: MarkdownBlockChangeSummary) => {
    dispatch({ type: 'completed', targetChanges });
  }, []);
  const fail = React.useCallback((error: string) => dispatch({ type: 'failed', error }), []);
  const reset = React.useCallback(() => dispatch({ type: 'reset' }), []);
  return {
    state,
    begin,
    sourceSaved,
    complete,
    fail,
    reset,
  };
}
