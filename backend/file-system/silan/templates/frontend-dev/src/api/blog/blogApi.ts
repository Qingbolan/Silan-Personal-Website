import type { BlogData } from '../../components/BlogStack/types/blog';
import { get, post, formatLanguage } from '../utils';
import { type PaginationRequest, type SearchRequest } from '../config';
import { processRawContent, parseAcademicMarkdown } from '../../utils/markdownParser';

// Backend API request/response types
interface BlogListRequest extends PaginationRequest {
  status?: string;
  content_type?: string;
  featured?: boolean;
  tag?: string;
  category?: string;
  author?: string;
  search?: string;
}

interface BlogSearchRequest extends SearchRequest {
  query?: string;
  category?: string;
  tags?: string;
  author?: string;
}

interface UpdateBlogLikesResponse {
  likes: number;
}

// Series-specific API functions
export interface SeriesEpisode {
  id: string;
  title: string;
  titleZh?: string;
  duration?: string;
  completed?: boolean;
  current?: boolean;
  order: number;
}

export interface SeriesData {
  id: string;
  title: string;
  titleZh?: string;
  description: string;
  descriptionZh?: string;
  episodes: SeriesEpisode[];
  totalDuration: string;
  completedCount: number;
}

// API functions

/**
 * Get blog posts list with pagination and filtering
 */
export const fetchBlogPosts = async (
  params: Partial<BlogListRequest> = {},
  language: 'en' | 'zh' = 'en'
): Promise<BlogData[]> => {
  const response = await get<any>('/api/v1/blog/posts', {
    ...params,
    lang: formatLanguage(language)
  });
  
  // Ensure consistent data structure and map fields
  const posts = (response.posts || []).map((post: any) => ({
    ...post,
    tags: post.tags || [],
    // Map series fields from snake_case to camelCase
    seriesId: post.series_id,
    seriesTitle: post.series_title,
    seriesTitleZh: post.series_title_zh,
    seriesDescription: post.series_description,
    seriesDescriptionZh: post.series_description_zh,
    episodeNumber: post.episode_number,
    totalEpisodes: post.total_episodes,
    seriesImage: post.series_image,
    // Map other fields
    publishDate: post.publish_date,
    readTime: post.read_time
  })) as BlogData[];
  
  return posts;
};

/**
 * Get single blog post by slug or ID
 */
export const fetchBlogById = async (slugOrId: string, language: 'en' | 'zh' = 'en'): Promise<BlogData | null> => {
  // Check if input looks like a UUID (ID) or a slug
  const isUUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(slugOrId);
  
  // Try the appropriate endpoint based on the input format
  try {
    const endpoint = isUUID 
      ? `/api/v1/blog/posts/id/${slugOrId}`  // Use ID endpoint for UUIDs
      : `/api/v1/blog/posts/${slugOrId}`;    // Use slug endpoint for slugs
      
    const response = await get<any>(endpoint, {
      lang: formatLanguage(language)
    });
    
    if (response) {
      console.log('🔍 Raw API response:', response);
      console.log('🔍 Raw content:', response.content);
      console.log('🔍 Raw content length:', response.content?.length);
      console.log('🔍 First content item:', response.content?.[0]);
      
      // Process the content with markdown parser
      const processedContent = response.content ? processRawContent(response.content) : [];
      console.log('✅ Processed content:', processedContent);
      console.log('✅ Processed content length:', processedContent.length);
      console.log('✅ Content types breakdown:', processedContent.reduce((acc, item) => {
        acc[item.type] = (acc[item.type] || 0) + 1;
        return acc;
      }, {} as Record<string, number>));
      
      // Map backend response to frontend structure
      return {
        ...response,
        tags: response.tags || [],
        content: processedContent, // Use processed content instead of raw
        // Map series fields from snake_case to camelCase
        seriesId: response.series_id,
        seriesTitle: response.series_title,
        seriesTitleZh: response.series_title_zh,
        seriesDescription: response.series_description,
        seriesDescriptionZh: response.series_description_zh,
        episodeNumber: response.episode_number,
        totalEpisodes: response.total_episodes,
        seriesImage: response.series_image,
        // Map other fields
        publishDate: response.publish_date,
        readTime: response.read_time
      } as BlogData;
    }
  } catch (error) {
    console.log(`Failed to fetch by ${isUUID ? 'ID' : 'slug'}, will try getting all posts to find the correct slug`);
  }

  // If that fails, fetch all posts to find the correct slug
  try {
    const allPosts = await fetchBlogPosts({}, language);
    const post = allPosts.find(p => p.id === slugOrId);
    
    if (post && post.slug) {
      console.log(`Found post with slug: ${post.slug}`);
      
      // Fetch the full post content using the correct slug
      const response = await get<any>(`/api/v1/blog/posts/${post.slug}`, {
        lang: formatLanguage(language)
      });
      
      if (response) {
        console.log('🔍 Raw API response (fallback):', response);
        console.log('🔍 Raw content (fallback):', response.content);
        
        // Process the content with markdown parser
        const processedContent = response.content ? processRawContent(response.content) : [];
        console.log('✅ Processed content (fallback):', processedContent);
        
        // Map backend response to frontend structure
        return {
          ...response,
          tags: response.tags || [],
          content: processedContent, // Use processed content instead of raw
          // Map series fields from snake_case to camelCase
          seriesId: response.series_id,
          seriesTitle: response.series_title,
          seriesTitleZh: response.series_title_zh,
          seriesDescription: response.series_description,
          seriesDescriptionZh: response.series_description_zh,
          episodeNumber: response.episode_number,
          totalEpisodes: response.total_episodes,
          seriesImage: response.series_image,
          // Map other fields
          publishDate: response.publish_date,
          readTime: response.read_time
        } as BlogData;
      }
    }
  } catch (error) {
    console.error('Failed to fetch blog post by ID/slug:', error);
  }
  
  return null;
};

/**
 * Search blog posts with filters
 */
export const searchBlogPosts = async (
  params: BlogSearchRequest,
  language: 'en' | 'zh' = 'en'
): Promise<BlogData[]> => {
  const response = await get<any>('/api/v1/blog/search', {
    ...params,
    lang: formatLanguage(language)
  });
  
  // Ensure consistent data structure and map fields
  const posts = (response.posts || []).map((post: any) => ({
    ...post,
    tags: post.tags || [],
    // Map series fields from snake_case to camelCase
    seriesId: post.series_id,
    seriesTitle: post.series_title,
    seriesTitleZh: post.series_title_zh,
    seriesDescription: post.series_description,
    seriesDescriptionZh: post.series_description_zh,
    episodeNumber: post.episode_number,
    totalEpisodes: post.total_episodes,
    seriesImage: post.series_image,
    // Map other fields
    publishDate: post.publish_date,
    readTime: post.read_time
  })) as BlogData[];
  
  return posts;
};

/**
 * Get blog categories
 */
export const getBlogCategories = async (language: 'en' | 'zh' = 'en'): Promise<string[]> => {
  const response = await get<string[]>('/api/v1/blog/categories', {
    lang: formatLanguage(language)
  });
  return response;
};

/**
 * Get blog tags
 */
export const getBlogTags = async (language: 'en' | 'zh' = 'en'): Promise<string[]> => {
  const response = await get<string[]>('/api/v1/blog/tags', {
    lang: formatLanguage(language)
  });
  return response;
};

/**
 * Update blog views
 */
export const updateBlogViews = async (id: string, language: 'en' | 'zh' = 'en'): Promise<void> => {
  // Use form data to avoid CORS preflight request
  const formData = new URLSearchParams();
  formData.append('lang', formatLanguage(language));
  
  try {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8888'}/api/v1/blog/posts/${id}/views`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString(),
    });
    
    if (!response.ok) {
      console.warn(`Failed to update blog views: ${response.status} ${response.statusText}`);
    }
  } catch (error) {
    console.warn('Failed to update blog views (non-critical):', error);
  }
};

/**
 * Update blog likes
 */
export const updateBlogLikes = async (id: string, increment: boolean = true, language: 'en' | 'zh' = 'en'): Promise<number> => {
  const response = await post<UpdateBlogLikesResponse>(`/api/v1/blog/posts/${id}/likes`, {
    increment,
    lang: formatLanguage(language)
  });
  return response.likes;
};

/**
 * Get blog series data
 */
export const fetchSeriesData = async (seriesId: string, language: 'en' | 'zh' = 'en'): Promise<SeriesData | null> => {
  const response = await get<any>(`/api/v1/blog/series/${seriesId}`, {
    lang: formatLanguage(language)
  });
  
  if (!response) return null;
  
  // Map backend response to frontend structure
  return {
    id: response.id,
    title: response.title,
    titleZh: response.title_zh,
    description: response.description,
    descriptionZh: response.description_zh,
    episodes: (response.episodes || []).map((episode: any) => ({
      id: episode.id,
      title: episode.title,
      titleZh: episode.title_zh,
      duration: episode.duration,
      completed: episode.completed || false,
      current: episode.current || false,
      order: episode.order
    })),
    totalDuration: response.total_duration || '',
    completedCount: response.completed_count || 0
  } as SeriesData;
};

/**
 * Update series progress
 */
export const updateSeriesProgress = async (
  seriesId: string, 
  episodeId: string, 
  completed: boolean, 
  language: 'en' | 'zh' = 'en'
): Promise<SeriesData> => {
  const response = await post<SeriesData>(`/api/v1/blog/series/${seriesId}/episodes/${episodeId}/progress`, {
    completed,
    lang: formatLanguage(language)
  });
  return response;
};

/**
 * Set current episode
 */
export const setCurrentEpisode = async (
  seriesId: string, 
  episodeId: string, 
  language: 'en' | 'zh' = 'en'
): Promise<SeriesData> => {
  const response = await post<SeriesData>(`/api/v1/blog/series/${seriesId}/episodes/${episodeId}/current`, {
    lang: formatLanguage(language)
  });
  return response;
};