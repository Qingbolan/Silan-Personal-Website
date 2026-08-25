import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

// Import all custom hooks
import { useBlogData } from './hooks/useBlogData';
import { useAnnotations } from './hooks/useAnnotations';

// Import all components
import { BlogLoadingState } from './components/BlogLoadingState';
import { AnnotationUI } from './components/AnnotationUI';
import ArticleDetailLayout from './ArticleDetailLayout';
import SeriesDetailLayout from './SeriesDetailLayout';

// Import reading behavior utilities
import { readingTracker } from '../../utils/readingBehavior';
import { useLanguage } from '../LanguageContext';
import { useSetPageTitle } from '../../layout/PageTitleContext';
import { Seo, blogPostingJsonLd } from '../Seo';
import { canonicalInternalPath } from '../../utils/navigation';

const BlogDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { language } = useLanguage();

  // UI state
  const [annotations, setAnnotations] = useState<Record<string, boolean>>({});

  // Custom hooks
  const [retryKey, setRetryKey] = useState(0);
  const { blog, state } = useBlogData(id, retryKey);
  const {
    userAnnotations,
    showAnnotationForm,
    newAnnotationText,
    selectedText,
    highlightedAnnotation,
    selectionMenu,
    formAnchor,
    setNewAnnotationText,
    setShowAnnotationForm,
    handleTextSelection,
    openAnnotationForm,
    addUserAnnotation,
    removeUserAnnotation,
    highlightAnnotation,
    cancelAnnotation
  } = useAnnotations(id);

  // Reflect the post title in the address-bar breadcrumb.
  useSetPageTitle(
    blog
      ? (language === 'zh' && blog.titleZh ? blog.titleZh : blog.title)
      : state === 'not-found'
        ? (language === 'zh' ? '文章不存在' : 'Article not found')
        : state === 'error'
          ? (language === 'zh' ? '文章暂不可用' : 'Article unavailable')
          : null,
  );

  // Start reading tracking when blog is loaded
  useEffect(() => {
    if (blog && blog.id) {
      readingTracker.startSession(blog.id);

      // Cleanup when component unmounts
      return () => {
        readingTracker.endSession();
      };
    }
  }, [blog]);

  // Handle annotation toggle
  const toggleAnnotation = (contentId: string) => {
    setAnnotations(prev => ({
      ...prev,
      [contentId]: !prev[contentId]
    }));
  };

  // Loading and error states
  if (state !== 'ready' || !blog) {
    return (
      <>
        {state === 'not-found' && (
          <Seo
            title={language === 'zh' ? '文章不存在' : 'Article not found'}
            description={language === 'zh' ? '未找到该公开文章。' : 'This public article could not be found.'}
            path={`/blog/${id ?? ''}`}
            noindex
            lang={language as 'en' | 'zh'}
          />
        )}
        <BlogLoadingState state={state} onRetry={() => setRetryKey((key) => key + 1)} />
      </>
    );
  }

  // Handle back navigation
  const handleBack = () => {
    navigate(canonicalInternalPath('/blog'));
  };

  // Per-article SEO — title, excerpt, cover image and BlogPosting JSON-LD.
  const seoTitle = language === 'zh' && blog.titleZh ? blog.titleZh : blog.title;
  const seoDescription =
    (language === 'zh' && blog.summaryZh ? blog.summaryZh : blog.summary) || '';
  const seoImage = blog.coverImage || blog.vlogCover || blog.videoThumbnail;
  const seoImageAlt = [
    blog.projectName || seoTitle,
    blog.publicationVenue,
    blog.author ? `${language === 'zh' ? '作者' : 'Author'}: ${blog.author}` : undefined,
    'silan.tech',
  ].filter(Boolean).join(' · ');
  const seo = (
    <Seo
      title={seoTitle}
      description={seoDescription}
      path={`/blog/${blog.slug || blog.id}/`}
      image={seoImage}
      imageAlt={seoImageAlt}
      type="article"
      lang={language as 'en' | 'zh'}
      author={blog.author}
      jsonLd={blogPostingJsonLd({
        title: seoTitle,
        description: seoDescription,
        path: `/blog/${blog.slug || blog.id}/`,
        image: seoImage,
        imageAlt: seoImageAlt,
        datePublished: blog.publishDate,
        dateModified: blog.updatedAt || blog.publishDate,
        author: blog.author,
        projectName: blog.projectName,
        projectUrl: blog.projectUrl,
        publicationVenue: blog.publicationVenue,
        externalResources: blog.externalResources,
        lang: language as 'en' | 'zh',
        seriesTitle: blog.seriesId
          ? (language === 'zh' && blog.seriesTitleZh ? blog.seriesTitleZh : blog.seriesTitle)
          : undefined,
        seriesPosition: blog.episodeNumber,
      })}
    />
  );

  // The two-step annotation UI (selection toolbar + anchored composer) is
  // rendered once here — it positions itself `fixed` in the viewport, so it
  // works identically over both layouts.
  const annotationUi = (
    <AnnotationUI
      selectionMenu={selectionMenu}
      formAnchor={formAnchor}
      showAnnotationForm={showAnnotationForm}
      selectedText={selectedText}
      newAnnotationText={newAnnotationText}
      onOpenForm={openAnnotationForm}
      onSetNewAnnotationText={setNewAnnotationText}
      onAddUserAnnotation={(contentId: string) => addUserAnnotation(contentId)}
      onCancelAnnotation={cancelAnnotation}
    />
  );

  if (blog.seriesId) {
    return (
      <>
        {seo}
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
        {annotationUi}
      </>
    );
  }

  return (
    <>
      {seo}
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
      {annotationUi}
    </>
  );
};

export default BlogDetail;
