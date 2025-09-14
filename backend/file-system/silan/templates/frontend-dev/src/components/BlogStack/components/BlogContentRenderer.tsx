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
      {content.map((item) => renderContent(item))}
    </div>
  );
}; 