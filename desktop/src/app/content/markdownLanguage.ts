import type { CaptureTarget } from '../../types';

const ENGLISH_MARKDOWN_LANGUAGE = 'en';
const CHINESE_MARKDOWN_LANGUAGE = 'zh';

export const preferredMarkdownLanguages = [
  ENGLISH_MARKDOWN_LANGUAGE,
  CHINESE_MARKDOWN_LANGUAGE,
];

export const counterpartMarkdownLanguage = (language: string) => {
  const normalized = language.trim().toLowerCase();
  if (normalized === ENGLISH_MARKDOWN_LANGUAGE) return CHINESE_MARKDOWN_LANGUAGE;
  if (normalized === CHINESE_MARKDOWN_LANGUAGE || normalized.startsWith('zh')) {
    return ENGLISH_MARKDOWN_LANGUAGE;
  }
  return '';
};

export const inferMarkdownLanguage = (markdown: string, fallback: string) => {
  const cjkCount = (markdown.match(/[\u3400-\u9fff]/g) || []).length;
  const latinWordCount = (markdown.match(/[A-Za-z][A-Za-z'-]*/g) || []).length;
  if (cjkCount >= 6 || cjkCount > latinWordCount * 2) return CHINESE_MARKDOWN_LANGUAGE;
  if (latinWordCount > 0) return ENGLISH_MARKDOWN_LANGUAGE;
  return fallback.trim().toLowerCase().startsWith('zh')
    ? CHINESE_MARKDOWN_LANGUAGE
    : ENGLISH_MARKDOWN_LANGUAGE;
};

export const attachmentOnlyCaptureNote = (
  target: CaptureTarget,
  fallbackLanguage: string,
) => {
  const isZh = fallbackLanguage.trim().toLowerCase().startsWith('zh');
  if (target === 'moment') return isZh ? '图文记录' : 'Media moment';
  return isZh ? '图文草稿' : 'Media draft';
};

export const fileBytes = async (file: File) => (
  Array.from(new Uint8Array(await file.arrayBuffer()))
);
