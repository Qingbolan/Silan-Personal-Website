import type { IdeaData } from '../../types';
import { get, formatLanguage } from '../utils';
import { type PaginationRequest, type SearchRequest, type ListResponse } from '../config';

// Backend API request/response types
interface IdeaListRequest extends PaginationRequest {
  status?: string;
  category?: string;
  difficulty?: string;
  collaboration?: boolean;
  funding?: string;
  search?: string;
  tags?: string;
}

interface IdeaListResponse extends ListResponse<IdeaData> {
  ideas: IdeaData[];
  total: number;
  page: number;
  size: number;
  total_pages: number;
}


interface IdeaSearchRequest extends SearchRequest {
  query?: string;
  category?: string;
  status?: string;
  tags?: string;
}


// API Functions

/**
 * Get ideas list with pagination and filtering
 */
export const fetchIdeas = async (
  params: Partial<IdeaListRequest> = {},
  language: 'en' | 'zh' = 'en'
): Promise<IdeaData[]> => {
  const response = await get<IdeaListResponse>('/api/v1/ideas', {
    ...params,
    lang: formatLanguage(language)
  });
  
  // Ensure consistent data structure
  const ideas = (response.ideas || []).map(idea => ({
    ...idea,
    tags: idea.tags || []
  }));
  
  return ideas;
};

/**
 * Get single idea by ID
 */
export const fetchIdeaById = async (id: string, language: 'en' | 'zh' = 'en'): Promise<IdeaData | null> => {
  const response = await get<IdeaData>(`/api/v1/ideas/${id}`, {
    lang: formatLanguage(language)
  });
  
  if (!response) return null;
  
  // Ensure consistent data structure
  return {
    ...response,
    tags: response.tags || []
  };
};


/**
 * Search ideas with filters
 */
export const searchIdeas = async (
  params: IdeaSearchRequest,
  language: 'en' | 'zh' = 'en'
): Promise<IdeaData[]> => {
  const response = await get<IdeaListResponse>('/api/v1/ideas/search', {
    ...params,
    lang: formatLanguage(language)
  });
  
  // Ensure consistent data structure
  const ideas = (response.ideas || []).map(idea => ({
    ...idea,
    tags: idea.tags || []
  }));
  
  return ideas;
};

/**
 * Get idea categories
 */
export const getIdeaCategories = async (language: 'en' | 'zh' = 'en'): Promise<string[]> => {
  const apiCall = async () => {
    const response = await get<string[]>('/api/v1/ideas/categories', {
      lang: formatLanguage(language)
    });
    return response;
  };
  return apiCall();
};

/**
 * Get idea tags
 */
export const getIdeaTags = async (language: 'en' | 'zh' = 'en'): Promise<string[]> => {
  const response = await get<string[]>('/api/v1/ideas/tags', {
    lang: formatLanguage(language)
  });
  return response;
};