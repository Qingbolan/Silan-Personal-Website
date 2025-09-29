import React, { useState, useEffect } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  ChevronUp,
  List,
  BookOpen,
  Clock,
  User,
  Calendar,
  ChevronRight,
  ChevronLeft,
  Eye,
  Heart,
  Share2,
  Play,
  CheckCircle,
  Circle,
  X,
} from 'lucide-react';
import { useLanguage } from '../LanguageContext';
import { useTheme } from '../ThemeContext';
import { BlogData, UserAnnotation, SelectedText } from './types/blog';
import { fetchSeriesData, updateSeriesProgress, SeriesData } from '../../api';
import { BlogContentRenderer } from './components/BlogContentRenderer';
import { BlogBreadcrumb } from './components/Breadcrumb';
import { useTOC } from './hooks/useTOC';
import { TableOfContents } from './components/TableOfContents';
import BlogComments from './components/BlogComments';

interface SeriesDetailLayoutProps {
  post: BlogData;
  onBack: () => void;
  userAnnotations: Record<string, UserAnnotation>;
  annotations: Record<string, boolean>;
  showAnnotationForm: string | null;
  newAnnotationText: string;
  selectedText: SelectedText | null;
  highlightedAnnotation: string | null;
  onTextSelection: () => void;
  onToggleAnnotation: (contentId: string) => void;
  onSetShowAnnotationForm: (show: string | null) => void;
  onSetNewAnnotationText: (text: string) => void;
  onAddUserAnnotation: (contentId: string) => void;
  onRemoveUserAnnotation: (id: string) => void;
  onHighlightAnnotation: (id: string) => void;
  onCancelAnnotation: () => void;
}

const SeriesDetailLayout: React.FC<SeriesDetailLayoutProps> = ({
  post,
  onBack,
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
  const { language } = useLanguage();
  const navigate = useNavigate();
  const { isDarkMode } = useTheme();
  const reduceMotion = useReducedMotion();
  const [showBackToTop, setShowBackToTop] = useState(false);
  const [metaSidebarCollapsed, setMetaSidebarCollapsed] = useState(false); // Default open on desktop
  const [tocCollapsed, setTocCollapsed] = useState(false); // Default open on desktop
  const [liked, setLiked] = useState(false);
  const [bookmarked, setBookmarked] = useState(false);

  // API state
  const [seriesData, setSeriesData] = useState<SeriesData | null>(null);
  const [loading, setLoading] = useState(true);

  // Scroll to top on component mount
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  // Handle responsive sidebar states
  useEffect(() => {
    const handleResize = () => {
      const isDesktop = window.innerWidth >= 1024; // lg breakpoint
      if (!isDesktop) {
        // Collapse both sidebars on mobile/tablet
        setMetaSidebarCollapsed(true);
        setTocCollapsed(true);
      } else {
        // On desktop, use default open states if not manually changed
        // Only auto-open if the user hasn't explicitly closed them
        const hasUserInteracted = sessionStorage.getItem('sidebar-user-interaction');
        if (!hasUserInteracted) {
          setMetaSidebarCollapsed(false);
          setTocCollapsed(false);
        }
      }
    };

    // Initial check
    handleResize();

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Use the standard TOC hook instead of manual generation
  const { sections: tableOfContents } = useTOC(post);

  // Load series data
  useEffect(() => {
    const loadSeriesData = async () => {
      console.log('🔍 SeriesDetailLayout - post object:', post);
      console.log('🔍 SeriesDetailLayout - post.seriesId:', post.seriesId);
      
      if (!post.seriesId) {
        console.log('❌ No seriesId found, skipping series data load');
        return;
      }

      try {
        console.log('🚀 Loading series data for seriesId:', post.seriesId);
        setLoading(true);
        const data = await fetchSeriesData(post.seriesId, language as 'en' | 'zh');
        console.log('✅ Series data loaded:', data);
        setSeriesData(data);
      } catch (error) {
        console.error('❌ Failed to load series data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadSeriesData();
  }, [post.seriesId, language]);

  // Handle scroll for back to top button
  useEffect(() => {
    const handleScroll = () => {
      setShowBackToTop(window.scrollY > 300);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Handle episode navigation
  const handleEpisodeClick = async (episodeId: string) => {
    if (!post.seriesId) return;

    try {
      // Navigate to the episode page
      navigate(`/blog/${episodeId}`);
      
      // Optionally update series data to reflect the new current episode
      // This is primarily for UI feedback, the actual navigation will load the new page
      if (seriesData) {
        const updatedEpisodes = seriesData.episodes.map(ep => ({
          ...ep,
          current: ep.id === episodeId
        }));
        setSeriesData({
          ...seriesData,
          episodes: updatedEpisodes
        });
      }
    } catch (error) {
      console.error('Failed to navigate to episode:', error);
    }
  };

  // Handle episode completion toggle
  const handleToggleCompletion = async (episodeId: string, completed: boolean) => {
    if (!post.seriesId) return;

    try {
      const updatedSeries = await updateSeriesProgress(post.seriesId, episodeId, completed, language as 'en' | 'zh');
      setSeriesData(updatedSeries);
    } catch (error) {
      console.error('Failed to update progress:', error);
    }
  };

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: post.title,
        text: post.summary,
        url: window.location.href
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
    }
  };

  const handleLike = () => {
    setLiked(!liked);
    // In real app, this would call an API
  };

  const handleBookmark = () => {
    setBookmarked(!bookmarked);
    // In real app, this would call an API
  };


  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-theme-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-theme-secondary">{language === 'en' ? 'Loading series...' : '加载系列中...'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">

      {/* Fixed Header - Y轴 0，考虑顶部导航栏 */}
      <motion.div
        role="region"
        aria-label={language === 'en' ? 'Series header' : '系列页头'}
        className={`fixed top-16 xs:top-18 sm:top-20 left-0 right-0 z-40 border-b border-theme-border ${metaSidebarCollapsed ? 'lg:ml-12' : 'lg:ml-80'} ${tocCollapsed ? 'lg:mr-12' : 'lg:mr-60'}`}
        initial={reduceMotion ? false : { opacity: 0, y: -12 }}
        animate={reduceMotion ? undefined : { opacity: 1, y: 0 }}
        style={{
          backgroundColor: isDarkMode ? 'rgba(26,26,26,0.50)' : 'rgba(255,255,255,0.70)',
          backdropFilter: 'blur(10px)',
          WebkitBackdropFilter: 'blur(10px)'
        }}
      >
        <div className="max-w-7xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <BlogBreadcrumb
              post={post}
              onBack={onBack}
              onFilterByCategory={(category) => {
                // Navigate back to blog with category filter
                navigate(`/blog?type=${category}`);
              }}
            />

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-4 text-sm text-theme-secondary">
                <div className="flex items-center gap-1">
                  <Eye size={14} />
                  <span>{post.views}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Heart size={14} className={liked ? 'text-red-500 fill-current' : ''} />
                  <span>{post.likes + (liked ? 1 : 0)}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Meta Sidebar - Y轴轨道 1 - Hidden on mobile */}
      <motion.div
        className={`fixed left-0 top-16 xs:top-18 sm:top-20 bottom-0 z-40 transition-all duration-300 hidden lg:block ${metaSidebarCollapsed ? 'w-12' : 'w-80'
          }`}
        initial={reduceMotion ? false : { opacity: 0, x: -20 }}
        animate={reduceMotion ? undefined : { opacity: 1, x: 0 }}
      >
        <div className="h-full overflow-y-auto pt-3 pl-5">
          {/* Sidebar Toggle */}
          <button
            onClick={() => {
              setMetaSidebarCollapsed(!metaSidebarCollapsed);
              sessionStorage.setItem('sidebar-user-interaction', 'true');
            }}
            className="flex items-start gap-2 text-theme-secondary hover:text-theme-primary transition-colors w-full"
          >
            {metaSidebarCollapsed ? <ChevronRight size={16} /> : <List size={14} className="p-0.5 pt-0 text-purple-500 h-6 w-6" />}
            {!metaSidebarCollapsed &&
              <h3 className="font-semibold text-theme-primary text-sm text-left">
                {language === 'zh' && post.titleZh ? post.titleZh : post.title}
              </h3>
            }
          </button>

          {!metaSidebarCollapsed && (
            <>
              {/* Article Meta Info */}
              <div className="rounded-lg border p-2 border-theme-border">

                <div className="space-y-3 text-xs">
                  <div className="flex items-center gap-2 text-theme-secondary">
                    <User size={12} />
                    <span>{post.author}</span>
                  </div>
                  <div className="flex items-center gap-2 text-theme-secondary">
                    <Calendar size={12} />
                    <span>{new Date(post.publishDate).toLocaleDateString()}</span>
                  </div>
                  <div className="flex items-center gap-2 text-theme-secondary">
                    <Clock size={12} />
                    <span>{post.readTime}</span>
                  </div>
                  {post.episodeNumber && (
                    <div className="flex items-center gap-2 text-theme-secondary">
                      <Play size={12} />
                      <span>{language === 'en' ? `Episode ${post.episodeNumber}` : `第${post.episodeNumber}集`}</span>
                    </div>
                  )}
                </div>
              </div>
              {/* Series Navigation */}
              {seriesData && (
                <div className="rounded-lg border border-theme-border">
                  <div className="space-y-1 overflow-y-auto">
                    {seriesData.episodes.map((episode) => (
                      <motion.div
                        key={episode.id}
                        className={`p-2 rounded-lg border cursor-pointer transition-all duration-200 text-sm ${episode.current
                          ? 'bg-theme-primary/10 border-theme-primary text-theme-primary'
                          : 'border-theme-border hover:border-theme-primary/50'
                          }`}
                        whileHover={{ x: 2 }}
                        onClick={() => handleEpisodeClick(episode.id)}
                      >
                        <div className="flex items-center gap-2">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleToggleCompletion(episode.id, !episode.completed);
                            }}
                            className="flex-shrink-0"
                          >
                            {episode.completed ? (
                              <CheckCircle size={16} className="text-green-500" />
                            ) : (
                              <Circle size={16} className="text-theme-tertiary" />
                            )}
                          </button>
                          <span className="text-xs font-medium w-6 text-center">
                            {episode.order}
                          </span>
                          <div className="flex-1 min-w-0">
                            <p className="font-medium truncate text-xs">
                              {language === 'zh' && episode.titleZh ? episode.titleZh : episode.title}
                            </p>
                            <p className="text-xs text-theme-secondary">{episode.duration}</p>
                          </div>
                          {episode.current && <Play size={12} />}
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </motion.div>

      {/* Main Content - Y轴轨道 2 - Responsive layout */}
      <div className={`transition-all duration-300 ${metaSidebarCollapsed ? 'lg:ml-12' : 'lg:ml-80'} ${tocCollapsed ? 'lg:mr-0' : 'lg:mr-60'}`}>
        <div className="pt-24 sm:pt-28 lg:pt-32 pb-20 px-4 sm:px-6 lg:px-8">
          <motion.div
            className="mx-auto w-full max-w-[75ch]"
            initial={reduceMotion ? false : { opacity: 0, y: 20 }}
            animate={reduceMotion ? undefined : { opacity: 1, y: 0 }}
          >

            {/* Article Content */}
            <div className="prose-content space-y-6">
              <BlogContentRenderer
                content={post.content}
                isWideScreen={true}
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
            </div>

            {/* Series Navigation */}
            {seriesData && seriesData.episodes.length > 1 && (
              <div className="mt-12 pt-8 border-t border-theme-border">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    {(() => {
                      const currentIndex = seriesData.episodes.findIndex(ep => ep.id === post.id);
                      const previousEpisode = currentIndex > 0 ? seriesData.episodes[currentIndex - 1] : null;
                      
                      return previousEpisode ? (
                        <motion.button
                          onClick={() => handleEpisodeClick(previousEpisode.id)}
                          className="flex items-center gap-3 p-4 bg-theme-surface rounded-lg border border-theme-border hover:border-theme-primary transition-colors text-left group"
                          whileHover={{ x: -2 }}
                        >
                          <ChevronLeft size={20} className="text-theme-secondary group-hover:text-theme-primary flex-shrink-0" />
                          <div className="min-w-0">
                            <p className="text-sm text-theme-secondary mb-1">
                              {language === 'en' ? 'Previous Episode' : '上一集'}
                            </p>
                            <p className="font-medium text-theme-primary truncate">
                              {previousEpisode.title}
                            </p>
                            <p className="text-xs text-theme-secondary mt-1">
                              {language === 'en' ? `Episode ${previousEpisode.order}` : `第${previousEpisode.order}集`}
                              {previousEpisode.duration && ` • ${previousEpisode.duration}`}
                            </p>
                          </div>
                        </motion.button>
                      ) : null;
                    })()}
                  </div>

                  <div className="flex-1 flex justify-end">
                    {(() => {
                      const currentIndex = seriesData.episodes.findIndex(ep => ep.id === post.id);
                      const nextEpisode = currentIndex < seriesData.episodes.length - 1 ? seriesData.episodes[currentIndex + 1] : null;
                      
                      return nextEpisode ? (
                        <motion.button
                          onClick={() => handleEpisodeClick(nextEpisode.id)}
                          className="flex items-center gap-3 p-4 bg-theme-surface rounded-lg border border-theme-border hover:border-theme-primary transition-colors text-right group"
                          whileHover={{ x: 2 }}
                        >
                          <div className="min-w-0">
                            <p className="text-sm text-theme-secondary mb-1">
                              {language === 'en' ? 'Next Episode' : '下一集'}
                            </p>
                            <p className="font-medium text-theme-primary truncate">
                              {nextEpisode.title}
                            </p>
                            <p className="text-xs text-theme-secondary mt-1">
                              {language === 'en' ? `Episode ${nextEpisode.order}` : `第${nextEpisode.order}集`}
                              {nextEpisode.duration && ` • ${nextEpisode.duration}`}
                            </p>
                          </div>
                          <ChevronRight size={20} className="text-theme-secondary group-hover:text-theme-primary flex-shrink-0" />
                        </motion.button>
                      ) : null;
                    })()}
                  </div>
                </div>
              </div>
            )}
          </motion.div>
        </div>
      </div>

      {/* TOC Sidebar - Y轴轨道 3 - Hidden on mobile */}
      <motion.div
        className={`fixed right-0 top-16 bottom-0 z-40 transition-all duration-300 hidden lg:block ${tocCollapsed ? 'w-12' : 'w-60'
          }`}
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
      >
        <div className="h-full overflow-y-auto pt-3.5 pl-5">
          {/* TOC Toggle */}
          <button
            onClick={() => {
              setTocCollapsed(!tocCollapsed);
              sessionStorage.setItem('sidebar-user-interaction', 'true');
            }}
            className="flex items-center gap-2 text-theme-secondary hover:text-theme-primary transition-colors mb-4 w-full"
          >
            {tocCollapsed ? <ChevronRight size={16} /> : <></>}
            {!tocCollapsed && <span className="font-semibold text-theme-primary text-sm ml-2 text-left">{language === 'en' ? 'Outline' : '大纲'}</span>}
          </button>


          {!tocCollapsed && (
            <>
              {/* Table of Contents using standard component */}
              <div className="rounded-lg border border-theme-border">
                <TableOfContents
                  sections={tableOfContents}
                  className="p-3"
                />
              </div>
            </>
          )}
        </div>
      </motion.div>

      {/* Comments */}
      <div className={`transition-all duration-300 ${metaSidebarCollapsed ? 'ml-12' : 'ml-80'} ${tocCollapsed ? 'mr-0' : 'mr-60'}`}>
          <BlogComments postId={post.id} postSlug={post.slug} />
      </div>

      {/* Mobile Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 z-40 bg-theme-surface/95 backdrop-blur-sm border-t border-theme-border lg:hidden">
        <div className="flex items-center justify-around py-2 px-4">
          <button
            onClick={() => {
              setMetaSidebarCollapsed(!metaSidebarCollapsed);
              sessionStorage.setItem('sidebar-user-interaction', 'true');
            }}
            className="flex flex-col items-center gap-1 text-xs text-theme-secondary hover:text-theme-primary transition-colors p-2"
          >
            <User size={18} />
            <span>{language === 'en' ? 'Info' : '信息'}</span>
          </button>

          <button
            onClick={() => {
              setTocCollapsed(!tocCollapsed);
              sessionStorage.setItem('sidebar-user-interaction', 'true');
            }}
            className="flex flex-col items-center gap-1 text-xs text-theme-secondary hover:text-theme-primary transition-colors p-2"
          >
            <List size={18} />
            <span>{language === 'en' ? 'TOC' : '目录'}</span>
          </button>

          <button
            onClick={scrollToTop}
            className="flex flex-col items-center gap-1 text-xs text-theme-secondary hover:text-theme-primary transition-colors p-2"
          >
            <ChevronUp size={18} />
            <span>{language === 'en' ? 'Top' : '顶部'}</span>
          </button>

          <button
            onClick={handleShare}
            className="flex flex-col items-center gap-1 text-xs text-theme-secondary hover:text-theme-primary transition-colors p-2"
          >
            <Share2 size={18} />
            <span>{language === 'en' ? 'Share' : '分享'}</span>
          </button>
        </div>
      </div>

      {/* Mobile Overlay Sidebars */}
      {/* Meta Sidebar Overlay - Mobile */}
      <motion.div
        className={`fixed inset-0 z-40 lg:hidden ${metaSidebarCollapsed ? 'pointer-events-none' : ''}`}
        initial={{ opacity: 1 }}
        animate={{ opacity: metaSidebarCollapsed ? 0 : 1 }}
      >
        <div
          className="absolute inset-0 bg-black/20 backdrop-blur-sm"
          onClick={() => {
            setMetaSidebarCollapsed(true);
            sessionStorage.setItem('sidebar-user-interaction', 'true');
          }}
        />
        <motion.div
          className="absolute left-0 top-16 bottom-0 w-80 max-w-[85vw] bg-theme-surface border-r border-theme-border"
          initial={{ x: -320 }}
          animate={{ x: metaSidebarCollapsed ? -320 : 0 }}
          transition={{ type: 'tween', duration: 0.3 }}
        >
          <div className="h-full overflow-y-auto p-4">
            <button
              onClick={() => {
                setMetaSidebarCollapsed(true);
                sessionStorage.setItem('sidebar-user-interaction', 'true');
              }}
              className="flex items-center gap-2 text-theme-secondary hover:text-theme-primary transition-colors mb-4 w-full"
            >
              <X size={16} />
              <span>{language === 'en' ? 'Close' : '关闭'}</span>
            </button>

            {/* Same content as desktop meta sidebar - simplified */}
              <div className="rounded-lg p-4 border border-theme-border mb-4">
              <div className="flex items-center gap-2 mb-3">
                <List size={14} className="text-purple-500" />
                <h3 className="font-semibold text-theme-primary text-sm">
                  {language === 'zh' && post.titleZh ? post.titleZh : post.title}
                </h3>
              </div>

              <div className="space-y-2 text-xs">
                <div className="flex items-center gap-2 text-theme-secondary">
                  <User size={12} />
                  <span>{post.author}</span>
                </div>
                <div className="flex items-center gap-2 text-theme-secondary">
                  <Calendar size={12} />
                  <span>{new Date(post.publishDate).toLocaleDateString()}</span>
                </div>
                {post.episodeNumber && (
                  <div className="flex items-center gap-2 text-theme-secondary">
                    <Play size={12} />
                    <span>{language === 'en' ? `Episode ${post.episodeNumber}` : `第${post.episodeNumber}集`}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Tags */}
            {post.tags && post.tags.length > 0 && (
              <div className="rounded-lg p-4 border border-theme-border mb-4">
                <h4 className="font-medium text-theme-primary text-sm mb-2">
                  {language === 'en' ? 'Tags' : '标签'}
                </h4>
                <div className="flex flex-wrap gap-1">
                  {post.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 bg-theme-tertiary text-theme-secondary rounded text-xs"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Quick Actions */}
            <div className="rounded-lg p-4 border border-theme-border">
              <h4 className="font-medium text-theme-primary text-sm mb-3">
                {language === 'en' ? 'Actions' : '操作'}
              </h4>
              <div className="space-y-1">
                <button
                  onClick={handleLike}
                  className={`flex items-center gap-2 w-full text-left text-xs transition-colors p-2 rounded hover:bg-theme-tertiary ${liked ? 'text-red-500' : 'text-theme-secondary hover:text-theme-primary'
                    }`}
                >
                  <Heart size={12} className={liked ? 'fill-current' : ''} />
                  <span>{liked ? (language === 'en' ? 'Liked' : '已点赞') : (language === 'en' ? 'Like' : '点赞')}</span>
                </button>
                <button
                  onClick={handleBookmark}
                  className={`flex items-center gap-2 w-full text-left text-xs transition-colors p-2 rounded hover:bg-theme-tertiary ${bookmarked ? 'text-yellow-500' : 'text-theme-secondary hover:text-theme-primary'
                    }`}
                >
                  <BookOpen size={12} />
                  <span>{bookmarked ? (language === 'en' ? 'Bookmarked' : '已收藏') : (language === 'en' ? 'Bookmark' : '收藏')}</span>
                </button>
                <button
                  onClick={handleShare}
                  className="flex items-center gap-2 w-full text-left text-xs text-theme-secondary hover:text-theme-primary transition-colors p-2 rounded hover:bg-theme-tertiary"
                >
                  <Share2 size={12} />
                  <span>{language === 'en' ? 'Share' : '分享'}</span>
                </button>
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>

      {/* TOC Sidebar Overlay - Mobile */}
      <motion.div
        className={`fixed inset-0 z-40 lg:hidden ${tocCollapsed ? 'pointer-events-none' : ''}`}
        initial={reduceMotion ? false : { opacity: 0 }}
        animate={reduceMotion ? undefined : { opacity: tocCollapsed ? 0 : 1 }}
      >
        <div
          className="absolute inset-0 bg-black/20 backdrop-blur-sm"
          onClick={() => {
            setTocCollapsed(true);
            sessionStorage.setItem('sidebar-user-interaction', 'true');
          }}
        />
        <motion.div
          className="absolute right-0 top-16 xs:top-18 sm:top-20 bottom-0 w-60 max-w-[85vw] bg-theme-surface border-l border-theme-border"
          initial={reduceMotion ? false : { x: 320 }}
          animate={reduceMotion ? undefined : { x: tocCollapsed ? 320 : 0 }}
          transition={reduceMotion ? undefined : { type: 'tween', duration: 0.3 }}
        >
          <div className="h-full overflow-y-auto p-4">
            <button
              onClick={() => {
                setTocCollapsed(true);
                sessionStorage.setItem('sidebar-user-interaction', 'true');
              }}
              className="flex items-center gap-2 text-theme-secondary hover:text-theme-primary transition-colors mb-4 w-full"
            >
              <X size={16} />
              <span>{language === 'en' ? 'Close' : '关闭'}</span>
            </button>

            {/* Table of Contents using standard component */}
            <div className="rounded-lg border border-theme-border">
              <div className="p-3 border-b border-theme-border">
                <h4 className="font-medium text-theme-primary text-sm m-0">
                  {language === 'en' ? 'Table of Contents' : '目录'}
                </h4>
              </div>
              <TableOfContents
                sections={tableOfContents}
                className="p-3"
              />
            </div>
          </div>
        </motion.div>
      </motion.div>

      {/* Back to Top Button - Desktop only */}
      {showBackToTop && (
        <motion.button
          className="fixed bottom-8 right-8 w-12 h-12 bg-theme-primary text-white rounded-full shadow-lg items-center justify-center hover:bg-theme-primary/90 transition-colors z-50 hidden lg:flex"
          onClick={scrollToTop}
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
        >
          <ChevronUp size={20} />
        </motion.button>
      )}
    </div>
  );
};

export default SeriesDetailLayout; 
