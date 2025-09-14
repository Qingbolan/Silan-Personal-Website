import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

// Import all custom hooks
import { useBlogData } from './hooks/useBlogData';
import { useAnnotations } from './hooks/useAnnotations';

// Import all components
import { BlogLoadingState } from './components/BlogLoadingState';
import SeriesDetailLayout from './SeriesDetailLayout';
import ArticleDetailLayout from './ArticleDetailLayout';

const BlogDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  // UI state
  const [annotations, setAnnotations] = useState<Record<string, boolean>>({});

  // Custom hooks
  const { blog, loading, error } = useBlogData(id);
  const {
    userAnnotations,
    showAnnotationForm,
    newAnnotationText,
    selectedText,
    highlightedAnnotation,
    setNewAnnotationText,
    setShowAnnotationForm,
    handleTextSelection,
    addUserAnnotation,
    removeUserAnnotation,
    highlightAnnotation,
    cancelAnnotation
  } = useAnnotations(id);

  // Handle annotation toggle
  const toggleAnnotation = (contentId: string) => {
    setAnnotations(prev => ({
      ...prev,
      [contentId]: !prev[contentId]
    }));
  };

  // Loading and error states
  if (loading || !blog || error) {
    return <BlogLoadingState loading={loading} error={!!error || (!loading && !blog)} />;
  }

  // Handle back navigation
  const handleBack = () => {
    navigate('/blog');
  };

  // Use series layout if blog post belongs to a series
  if (blog.seriesId) {
    return (
      <SeriesDetailLayout 
        post={blog} 
        onBack={handleBack}
        userAnnotations={userAnnotations}
        annotations={annotations}
        showAnnotationForm={showAnnotationForm}
        newAnnotationText={newAnnotationText}
        selectedText={selectedText}
        highlightedAnnotation={highlightedAnnotation}
        onTextSelection={handleTextSelection}
        onToggleAnnotation={toggleAnnotation}
        onSetShowAnnotationForm={setShowAnnotationForm}
        onSetNewAnnotationText={setNewAnnotationText}
        onAddUserAnnotation={(contentId: string) => addUserAnnotation(contentId)}
        onRemoveUserAnnotation={removeUserAnnotation}
        onHighlightAnnotation={highlightAnnotation}
        onCancelAnnotation={cancelAnnotation}
      />
    );
  }

  // Use three-track layout for all other types (article, vlog, etc.)
  return (
    <ArticleDetailLayout
      post={blog}
      onBack={handleBack}
      userAnnotations={userAnnotations}
      annotations={annotations}
      showAnnotationForm={showAnnotationForm}
      newAnnotationText={newAnnotationText}
      selectedText={selectedText}
      highlightedAnnotation={highlightedAnnotation}
      onTextSelection={handleTextSelection}
      onToggleAnnotation={toggleAnnotation}
      onSetShowAnnotationForm={setShowAnnotationForm}
      onSetNewAnnotationText={setNewAnnotationText}
      onAddUserAnnotation={(contentId: string) => addUserAnnotation(contentId)}
      onRemoveUserAnnotation={removeUserAnnotation}
      onHighlightAnnotation={highlightAnnotation}
      onCancelAnnotation={cancelAnnotation}
    />
  );
};

export default BlogDetail; 