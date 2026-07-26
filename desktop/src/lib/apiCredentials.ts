import React from 'react';
import { invoke } from '@tauri-apps/api/core';
import type { ApiCredentialStatus } from '../types';

export type ApiCredentialProvider = 'openai' | 'deepseek';
export type ApiCredentialPhase =
  | 'loading'
  | 'ready'
  | 'saving'
  | 'testing'
  | 'removing'
  | 'failed';

export type ApiCredentialViewState = {
  phase: ApiCredentialPhase;
  status: ApiCredentialStatus | null;
  draft: string;
  error: string | null;
};

type ApiCredentialEvent =
  | { type: 'draft_changed'; draft: string }
  | { type: 'operation_started'; phase: 'saving' | 'testing' | 'removing' }
  | { type: 'operation_succeeded'; status: ApiCredentialStatus; clearDraft: boolean }
  | { type: 'operation_failed'; error: string };

type ApiCredentialOperations = {
  status: () => Promise<ApiCredentialStatus>;
  save: (apiKey: string) => Promise<ApiCredentialStatus>;
  test: () => Promise<ApiCredentialStatus>;
  remove: () => Promise<ApiCredentialStatus>;
  emptyKeyMessage: string;
};

const operations: Record<ApiCredentialProvider, ApiCredentialOperations> = {
  openai: {
    status: () => invoke<ApiCredentialStatus>('get_openai_credentials'),
    save: (apiKey) => invoke<ApiCredentialStatus>('save_openai_credentials', { apiKey }),
    test: () => invoke<ApiCredentialStatus>('test_openai_credentials'),
    remove: () => invoke<ApiCredentialStatus>('remove_openai_credentials'),
    emptyKeyMessage: 'Enter an OpenAI Platform API key.',
  },
  deepseek: {
    status: () => invoke<ApiCredentialStatus>('get_deepseek_credentials'),
    save: (apiKey) => invoke<ApiCredentialStatus>('save_deepseek_credentials', { apiKey }),
    test: () => invoke<ApiCredentialStatus>('test_deepseek_credentials'),
    remove: () => invoke<ApiCredentialStatus>('remove_deepseek_credentials'),
    emptyKeyMessage: 'Enter a DeepSeek API key.',
  },
};

const initialState: ApiCredentialViewState = {
  phase: 'loading',
  status: null,
  draft: '',
  error: null,
};

export function apiCredentialTransition(
  state: ApiCredentialViewState,
  event: ApiCredentialEvent,
): ApiCredentialViewState {
  switch (event.type) {
    case 'draft_changed':
      return { ...state, draft: event.draft, error: null };
    case 'operation_started':
      return { ...state, phase: event.phase, error: null };
    case 'operation_succeeded':
      return {
        phase: 'ready',
        status: event.status,
        draft: event.clearDraft ? '' : state.draft,
        error: null,
      };
    case 'operation_failed':
      return { ...state, phase: 'failed', error: event.error };
  }
}

const errorMessage = (reason: unknown) => String(reason);

export function useApiCredentials(provider: ApiCredentialProvider) {
  const providerOperations = operations[provider];
  const [state, dispatch] = React.useReducer(apiCredentialTransition, initialState);

  React.useEffect(() => {
    let active = true;
    void providerOperations.status()
      .then((status) => {
        if (active) {
          dispatch({ type: 'operation_succeeded', status, clearDraft: true });
        }
      })
      .catch((reason) => {
        if (active) dispatch({ type: 'operation_failed', error: errorMessage(reason) });
      });
    return () => {
      active = false;
    };
  }, [providerOperations]);

  const save = React.useCallback(async () => {
    const apiKey = state.draft.trim();
    if (!apiKey) {
      dispatch({ type: 'operation_failed', error: providerOperations.emptyKeyMessage });
      return;
    }
    dispatch({ type: 'operation_started', phase: 'saving' });
    try {
      const status = await providerOperations.save(apiKey);
      dispatch({ type: 'operation_succeeded', status, clearDraft: true });
    } catch (reason) {
      dispatch({ type: 'operation_failed', error: errorMessage(reason) });
    }
  }, [providerOperations, state.draft]);

  const test = React.useCallback(async () => {
    dispatch({ type: 'operation_started', phase: 'testing' });
    try {
      const status = await providerOperations.test();
      dispatch({ type: 'operation_succeeded', status, clearDraft: false });
    } catch (reason) {
      dispatch({ type: 'operation_failed', error: errorMessage(reason) });
    }
  }, [providerOperations]);

  const remove = React.useCallback(async () => {
    dispatch({ type: 'operation_started', phase: 'removing' });
    try {
      const status = await providerOperations.remove();
      dispatch({ type: 'operation_succeeded', status, clearDraft: true });
    } catch (reason) {
      dispatch({ type: 'operation_failed', error: errorMessage(reason) });
    }
  }, [providerOperations]);

  return {
    state,
    setDraft: (draft: string) => dispatch({ type: 'draft_changed', draft }),
    save,
    test,
    remove,
  };
}
