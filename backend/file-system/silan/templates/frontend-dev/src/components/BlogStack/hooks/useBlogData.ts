import { useState, useEffect } from 'react';
import { BlogData } from '../types/blog';
import { fetchBlogById, updateBlogViews } from '../../../api';
import { useLanguage } from '../../LanguageContext';

export const useBlogData = (id: string | undefined) => {
  const [blog, setBlog] = useState<BlogData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { language } = useLanguage();

  useEffect(() => {
    const loadBlog = async () => {
      if (!id) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        
        // Fetch blog data with language support
        const blogData = await fetchBlogById(id, language as 'en' | 'zh');
        
        console.log('🔍 useBlogData - Raw blog data received:', blogData);
        console.log('🔍 useBlogData - Blog seriesId:', blogData?.seriesId);
        console.log('🔍 useBlogData - Blog type:', blogData?.type);
        
        if (blogData) {
          setBlog(blogData);
          // Try to update view count, but don't fail if it doesn't work
          try {
            await updateBlogViews(id, language as 'en' | 'zh');
          } catch (viewError) {
            console.log('View count update failed (this is non-critical):', viewError);
          }
        } else {
          setError(language === 'en' ? 'Blog post not found' : '博客文章未找到');
        }
      } catch (err) {
        console.error('Error loading blog:', err);
        setError(language === 'en' ? 'Failed to load blog post' : '加载博客文章失败');
      } finally {
        setLoading(false);
      }
    };

    loadBlog();
  }, [id, language]);

  return { blog, loading, error };
}; 