import React, { useMemo } from 'react';
import { BlogContent, UserAnnotation, SelectedText } from '../types/blog';
import {
  TextContent,
  QuoteContent,
  ImageContent,
  VideoContent,
  CodeContent,
  HeadingContent,
} from './BlogContent';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import rehypeHighlight from 'rehype-highlight';

interface BlogContentRendererProps {
  content: BlogContent[];
  isWideScreen: boolean;
  userAnnotations: Record<string, UserAnnotation>;
  annotations: Record<string, boolean>;
  showAnnotationForm: string | null;
  newAnnotationText: string;
  selectedText: SelectedText | null;
  highlightedAnnotation: string | null;
  onTextSelection: () => void;
  onToggleAnnotation: (contentId: string) => void;
  onSetShowAnnotationForm: (contentId: string | null) => void;
  onSetNewAnnotationText: (text: string) => void;
  onAddUserAnnotation: (contentId: string) => void;
  onRemoveUserAnnotation: (annotationId: string) => void;
  onHighlightAnnotation: (annotationId: string) => void;
  onCancelAnnotation: () => void;
}

/** 更可靠地判断“像 Markdown 的文本块”，但避免 fenced code */
const looksLikeLooseMarkdown = (text: string): boolean => {
  if (!text) return false;
  if (/```/.test(text)) return false; // fenced code 优先
  const mdSignals =
    /^(#{1,6})\s/m.test(text) || // 标题
    /^[-*+]\s/m.test(text) || // 无序列表
    /^\d+\.\s/m.test(text) || // 有序列表
    /^>\s/m.test(text) || // 引用
    /\[[^\]]+\]\([^\)]+\)/.test(text) || // 链接
    /^(-{3,}|\*{3,}|_{3,})$/m.test(text); // 分割线
  return mdSignals;
};

type CanonicalType = NonNullable<BlogContent['type']>;

const normalizeType = (t?: string): CanonicalType => {
  const type = (t || 'text').toLowerCase().trim();
  if (['blockquote', 'quote'].includes(type)) return 'quote';
  if (['img', 'image', 'picture', 'gif'].includes(type)) return 'image';
  if (['video', 'youtube', 'vimeo', 'bilibili'].includes(type)) return 'video';
  if (['code', 'codeblock', 'pre'].includes(type)) return 'code';
  if (['heading', 'title', 'h', 'h0', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'].includes(type)) return 'heading';
  if (['md', 'markdown'].includes(type)) return 'markdown';
  if (['text', 'paragraph', 'p'].includes(type)) return 'text';
  return 'text';
};

const coerceHeadingLevel = (rawType: string | undefined, level?: number): number => {
  // 如果传入了 hN 之类的
  if (rawType && /^h[1-6]$/i.test(rawType)) {
    const n = parseInt(rawType.slice(1), 10);
    return Math.min(6, Math.max(1, n));
  }
  // title 默认 H1
  if ((rawType || '').toLowerCase() === 'title' && !level) return 1;
  const n = typeof level === 'number' ? level : 2;
  return Math.min(6, Math.max(1, n));
};

/** 轻量清洗：把“看起来像列表/任务清单”的单行文本转成更正宗的 Markdown */
const normalizeInlineMarkdownHeuristics = (raw: string): string => {
  let s = raw ?? '';
  if (!s) return s;

  // 把行首的可视化圆点“• ”转成 "- "
  if (s.includes('\n') && /(^|\n)\s*•\s+/.test(s)) {
    s = s.replace(/(^|\n)\s*•\s+/g, '$1- ');
  }

  // 单行任务清单：" - [ ] a - [x] b" -> 多行
  if (!s.includes('\n') && /\s-\s(?=\[[ xX]\]\s)/.test(s)) {
    s = s.replace(/\s-\s(?=\[[ xX]\]\s)/g, '\n- ');
    if (!/^\s*[-*+]\s/.test(s)) s = `- ${s}`;
  }

  // 单行无序列表："A - B - C" -> 多行
  if (!s.includes('\n')) {
    const parts = s.split(/\s-\s(?!\[[ xX]\]\s)/);
    if (parts.length >= 3) {
      s = parts.map((p) => `- ${p.trim().replace(/^[•*+\-]\s*/, '')}`).join('\n');
    }
  }

  // 单行有序列表："1. A 2. B" / "1) A 2) B" / "1、A 2、B" -> 多行
  // 修复原实现中的多余括号
  if (
    !s.includes('\n') &&
    /^\s*\d+[\.)、]\s/.test(s) &&
    /\s(?=\d+[\.)、]\s)/.test(s) === false // 如果原串没有清晰分隔，下面再尝试强制换行
  ) {
    s = s.replace(/\s(?=\d+[\.)、]\s)/g, '\n');
  }

  return s;
};

type PreparedItem = BlogContent & {
  id: string;
  type: CanonicalType;
  level?: number;
  kindIndex: number; // 稳定的“同类内索引”，用于 drop cap / 布局
};

export const BlogContentRenderer: React.FC<BlogContentRendererProps> = (props) => {
  const {
    content,
    isWideScreen,
    userAnnotations,
    annotations,
    showAnnotationForm,
    newAnnotationText,
    selectedText,
    highlightedAnnotation,
    onTextSelection,
    onToggleAnnotation,
    onSetShowAnnotationForm,
    onSetNewAnnotationText,
    onAddUserAnnotation,
    onRemoveUserAnnotation,
    onHighlightAnnotation,
    onCancelAnnotation,
  } = props;

  // 预处理：归一化 + 计算稳定 kindIndex
  const prepared = useMemo<PreparedItem[]>(() => {
    const counters: Record<CanonicalType, number> = {
      text: 0,
      quote: 0,
      image: 0,
      video: 0,
      code: 0,
      heading: 0,
      markdown: 0,
    };

    return (content || []).map((item, idx) => {
      const canonType = normalizeType(item.type as unknown as string);
      const id = item.id || `content-${idx}`;
      const base: PreparedItem = {
        ...(item as BlogContent),
        id,
        type: canonType,
        kindIndex: counters[canonType]++,
      };

      if (canonType === 'heading') {
        base.level = coerceHeadingLevel(item.type as string | undefined, item.level);
      }
      return base;
    });
  }, [content]);

  const renderMarkdown = (item: PreparedItem) => {
    // 不要误处理 fenced code
    const shouldTweak = item.content && !/```/.test(item.content);
    const md = shouldTweak ? normalizeInlineMarkdownHeuristics(item.content) : (item.content ?? '');

    return (
      <div key={item.id} className="prose prose-lg max-w-none">
        <ReactMarkdown
          remarkPlugins={[remarkGfm, remarkMath]}
          rehypePlugins={[rehypeKatex as any, rehypeHighlight as any]}
          components={{
            a: ({ node, ...aProps }) => (
              <a {...aProps} target="_blank" rel="noopener noreferrer" />
            ),
            ul: ({ node, ...ulProps }) => {
              const isTask = (ulProps.className || '').includes('contains-task-list');
              const cls = `my-4 ${isTask ? 'pl-2 list-none' : 'pl-6 list-disc'} ${ulProps.className || ''}`.trim();
              return <ul {...ulProps} className={cls} />;
            },
            ol: ({ node, ...olProps }) => {
              const isTask = (olProps.className || '').includes('contains-task-list');
              const cls = `my-4 ${isTask ? 'pl-2 list-none' : 'pl-6 list-decimal'} ${olProps.className || ''}`.trim();
              return <ol {...olProps} className={cls} />;
            },
            li: ({ node, children, ...liProps }) => {
              const isTaskItem = (liProps.className || '').includes('task-list-item');
              const cls = `leading-7 mb-1 ${isTaskItem ? 'list-none ml-0' : ''} ${liProps.className || ''}`.trim();
              return (
                <li {...liProps} className={cls}>
                  {children}
                </li>
              );
            },
            input: ({ node, ...inProps }) => (
              <input
                {...inProps}
                disabled
                readOnly
                className={`mr-2 align-middle ${inProps.className || ''}`.trim()}
                style={{ accentColor: 'var(--color-primary, #0066FF)' }}
              />
            ),
          }}
        >
          {md}
        </ReactMarkdown>
      </div>
    );
  };

  const renderContent = (item: PreparedItem) => {
    switch (item.type) {
      case 'text':
        return (
          <TextContent
            key={item.id}
            item={item}
            index={item.kindIndex}
            userAnnotations={userAnnotations}
            annotations={annotations}
            showAnnotationForm={showAnnotationForm}
            newAnnotationText={newAnnotationText}
            selectedText={selectedText}
            highlightedAnnotation={highlightedAnnotation}
            onTextSelection={onTextSelection}
            onToggleAnnotation={onToggleAnnotation}
            onSetShowAnnotationForm={onSetShowAnnotationForm}
            onSetNewAnnotationText={onSetNewAnnotationText}
            onAddUserAnnotation={onAddUserAnnotation}
            onRemoveUserAnnotation={onRemoveUserAnnotation}
            onHighlightAnnotation={onHighlightAnnotation}
            onCancelAnnotation={onCancelAnnotation}
          />
        );

      case 'quote':
        return <QuoteContent key={item.id} item={item} />;

      case 'image':
        return (
          <ImageContent
            key={item.id}
            item={item}
            index={item.kindIndex}
            isWideScreen={isWideScreen}
          />
        );

      case 'video':
        return (
          <VideoContent
            key={item.id}
            item={item}
            index={item.kindIndex}
            isWideScreen={isWideScreen}
          />
        );

      case 'code': {
        const lang = (item as any).language as string | undefined;
        // 若 language 为空且文本像 Markdown，则把高亮语言强制为 markdown
        const coerceToMd =
          (!lang || /^text$/i.test(lang)) &&
          looksLikeLooseMarkdown(item.content || '');
        const codeItem = coerceToMd ? { ...item, language: 'markdown' as const } : item;

        return (
          <CodeContent
            key={item.id}
            item={codeItem as any}
            index={item.kindIndex}
            isWideScreen={isWideScreen}
          />
        );
      }

      case 'heading':
        return (
          <HeadingContent
            key={item.id}
            item={item}
            index={item.kindIndex}
            isWideScreen={isWideScreen}
          />
        );

      case 'markdown':
        return renderMarkdown(item);

      default:
        return null;
    }
  };

  return <div className="mb-0">{prepared.map(renderContent)}</div>;
};
