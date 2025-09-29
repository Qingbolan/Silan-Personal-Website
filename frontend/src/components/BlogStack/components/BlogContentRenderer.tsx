import React from 'react';
import { BlogContent, UserAnnotation, SelectedText } from '../types/blog';
import { TextContent, QuoteContent, ImageContent, VideoContent, CodeContent, HeadingContent } from './BlogContent';

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

export const BlogContentRenderer: React.FC<BlogContentRendererProps> = ({
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
  onCancelAnnotation
}) => {
  // Normalize incoming content items to a stable shape to avoid brittle rendering
  const normalizeType = (t?: string): BlogContent['type'] => {
    const type = (t || 'text').toLowerCase().trim();
    if (['blockquote', 'quote'].includes(type)) return 'quote';
    if (['img', 'image', 'picture', 'gif'].includes(type)) return 'image';
    if (['video', 'youtube', 'vimeo', 'bilibili'].includes(type)) return 'video';
    if (['code', 'codeblock', 'pre'].includes(type)) return 'code';
    if (['heading', 'title', 'h', 'h0', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'].includes(type)) return 'heading';
    if (['text', 'paragraph', 'p'].includes(type)) return 'text';
    return 'text';
  };

  const normalizeItem = (item: BlogContent, index: number): BlogContent => {
    const normType = normalizeType(item.type as unknown as string);
    // Shallow clone with normalized type
    const normalized: BlogContent = {
      ...item,
      type: normType,
      id: item.id || `content-${index}`,
    };

    // Normalize heading level if this is a heading-like type coming as hN
    if (item.type && /^h[1-6]$/.test(item.type.toLowerCase())) {
      normalized.type = 'heading';
      const levelNum = parseInt(item.type.substr(1), 10);
      normalized.level = Math.min(6, Math.max(1, levelNum));
    }

    // If a generic "title" or "headingX" arrives, coerce level sensibly
    if (['title'].includes((item.type || '').toLowerCase()) && !item.level) {
      normalized.level = 1;
    }

    // Clamp heading level into 1..6
    if (normalized.type === 'heading') {
      const level = typeof normalized.level === 'number' ? normalized.level : 2;
      normalized.level = Math.min(6, Math.max(1, level));
    }

    return normalized;
  };

  // Track text content index separately for drop cap functionality
  let textContentIndex = 0;
  let imageContentIndex = 0;
  let videoContentIndex = 0;
  let codeContentIndex = 0;

  const renderContent = (item: BlogContent) => {
    switch (item.type) {
      case 'text':
        const currentTextIndex = textContentIndex++;
        return (
          <TextContent
            key={item.id}
            item={item}
            index={currentTextIndex} // Pass text-specific index for drop cap
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
        return (
          <QuoteContent 
            key={item.id} 
            item={item}
          />
        );

      case 'image':
        const currentImageIndex = imageContentIndex++;
        return (
          <ImageContent 
            key={item.id} 
            item={item}
            index={currentImageIndex}
            isWideScreen={isWideScreen}
          />
        );

      case 'video':
        const currentVideoIndex = videoContentIndex++;
        return (
          <VideoContent 
            key={item.id} 
            item={item}
            index={currentVideoIndex}
            isWideScreen={isWideScreen}
          />
        );

      case 'code':
        const currentCodeIndex = codeContentIndex++;
        return (
          <CodeContent 
            key={item.id} 
            item={item}
            index={currentCodeIndex}
            isWideScreen={isWideScreen}
          />
        );

      case 'heading':
        return (
          <HeadingContent 
            key={item.id} 
            item={item}
            index={0} // Headings don't need specific indexing
            isWideScreen={isWideScreen}
          />
        );

      default:
        return null;
    }
  };

  return (
    <div className="mb-0">
      {content.map((item, idx) => renderContent(normalizeItem(item, idx)))}
    </div>
  );
};
