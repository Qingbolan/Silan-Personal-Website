import type { Project, AnnualPlan, GraphData, Language, ProjectDetail, ProjectBlogReference } from '../../types/api';
import { get, post, del, formatLanguage } from '../utils';
import { type PaginationRequest, type SearchRequest, type ListResponse } from '../config';

// Backend API request/response types
interface ProjectListRequest extends PaginationRequest {
  type?: string;
  featured?: boolean;
  status?: string;
  search?: string;
  year?: number;
  annual_plan?: string;
  tags?: string;
}

interface ProjectListResponse extends ListResponse<Project> {
  projects: Project[];
  total: number;
  page: number;
  size: number;
  total_pages: number;
}

interface ProjectSearchRequest extends SearchRequest {
  query?: string;
  tags?: string;
  year?: number;
  plan_id?: string;
}


// API Functions

/**
 * Get projects list with pagination and filtering
 */
export const fetchProjects = async (
  params: Partial<ProjectListRequest> = {},
  language: Language = 'en'
): Promise<Project[]> => {
  const response = await get<ProjectListResponse>('/api/v1/projects', {
    ...params,
    lang: formatLanguage(language)
  });
  return response.projects || [];
};

/**
 * Get single project by slug
 */
export const fetchProject = async (
  slug: string, 
  language: Language = 'en'
): Promise<Project | null> => {
  const response = await get<Project>(`/api/v1/projects/${slug}`, {
    lang: formatLanguage(language)
  });
  return response;
};

/**
 * Get single project by ID (numeric)
 */
export const fetchProjectById = async (
  id: number | string, 
  language: Language = 'en'
): Promise<Project | null> => {
  const response = await get<Project>(`/api/v1/projects/id/${id}`, {
    lang: formatLanguage(language)
  });
  return response;
};

/**
 * Get detailed project information
 */
export const fetchProjectDetail = async (
  id: string, 
  language: Language = 'en'
): Promise<ProjectDetail | null> => {
  const response = await get<ProjectDetail>(`/api/v1/projects/${id}/detail`, {
    lang: formatLanguage(language)
  });
  return response;
};

/**
 * Get project categories
 */
export const fetchCategories = async (language: Language = 'en'): Promise<string[]> => {
  const response = await get<string[]>('/api/v1/projects/categories', {
    lang: formatLanguage(language)
  });
  return response;
};

/**
 * Get project technologies/tags
 */
export const getProjectTags = async (language: Language = 'en'): Promise<string[]> => {
  const response = await get<string[]>('/api/v1/projects/tags', {
    lang: formatLanguage(language)
  });
  return response;
};

/**
 * Get project graph data for visualization
 */
export const fetchGraphData = async (
  category: string = 'all', 
  language: Language = 'en'
): Promise<GraphData> => {
  const response = await get<GraphData>('/api/v1/projects/graph', {
    category,
    lang: formatLanguage(language)
  });
  return response;
};

/**
 * Get project related blogs
 */
export const getProjectRelatedBlogs = async (
  projectId: string, 
  language: Language = 'en'
): Promise<ProjectBlogReference[]> => {
  const response = await get<ProjectBlogReference[]>(`/api/v1/projects/${projectId}/blogs`, {
    lang: formatLanguage(language)
  });
  return response;
};

/**
 * Search project details with filters
 */
export const searchProjectDetails = async (
  params: ProjectSearchRequest,
  language: Language = 'en'
): Promise<ProjectDetail[]> => {
  const response = await get<ProjectDetail[]>('/api/v1/projects/search', {
    ...params,
    lang: formatLanguage(language)
  });
  return response;
};

// Extended functions for project details
export const fetchProjectDetailById = async (
  id: string, 
  language: Language = 'en'
): Promise<ProjectDetail | null> => {
  try {
    // Fetch both basic project info and detail info
    const [basicProject, projectDetail] = await Promise.all([
      get<Project>(`/api/v1/projects/id/${id}`, {
        lang: formatLanguage(language)
      }),
      get<any>(`/api/v1/projects/${id}/detail`, {
        lang: formatLanguage(language)
      }).catch(() => null) // Don't fail if detail doesn't exist
    ]);

    if (!basicProject) {
      return null;
    }

    // Merge basic project info with detail info to create a complete ProjectDetail
    const licenseName = projectDetail?.license || 'MIT';
    const licenseText: string | undefined = projectDetail?.license_text;

    const mergedDetail: ProjectDetail = {
      id: basicProject.id,
      title: basicProject.name,
      description: basicProject.description,
      fullDescription: projectDetail?.detailed_description || basicProject.description,
      tags: basicProject.tags || [],
      year: basicProject.year,
      
      // Timeline from detail or defaults
      timeline: projectDetail?.timeline || {
        start: '',
        end: '',
        duration: ''
      },
      
      // Metrics from detail or defaults
      metrics: projectDetail?.metrics || {
        linesOfCode: 0,
        commits: 0,
        stars: 0,
        downloads: 0
      },
      
      // Related blogs
      relatedBlogs: projectDetail?.related_blogs || [],
      
      // Default version info
      versions: {
        latest: projectDetail?.version || '1.0.0',
        releases: []
      },
      
      // Default status info
      status: {
        buildStatus: 'unknown' as const,
        coverage: 0,
        vulnerabilities: 0,
        lastUpdated: projectDetail?.updated_at || new Date().toISOString().split('T')[0],
        license: projectDetail?.license || 'MIT',
        language: 'Multiple',
        size: 'Medium'
      },
      
      // Default quick start info
      quickStart: {
        installation: ['Clone the repository', 'Install dependencies', 'Run the application'],
        basicUsage: 'Follow the README instructions to get started',
        requirements: ['Node.js', 'Git']
      },
      
      // Default community info
      community: {
        contributors: 1,
        forks: 0,
        watchers: 0,
        issues: {
          open: 0,
          closed: 0,
          recent: []
        },
        discussions: []
      },
      
      // Default dependencies
      dependencies: {
        production: [],
        development: []
      },
      
      // Default performance
      performance: {
        benchmarks: [],
        analytics: {
          downloads: [],
          usage: []
        }
      },
      
      // Additional fields
      features: [],
      teamSize: 1,
      myRole: 'Developer',
      planId: basicProject.annualPlan,
      
      // URLs (these might not be in the basic project, so we use defaults)
      github: '', // These would need to be added to the basic project type
      demo: ''    // or fetched from somewhere else
    };

    // Populate licenseInfo if backend returned full license text
    if (licenseText) {
      (mergedDetail as any).licenseInfo = {
        name: licenseName,
        spdxId: licenseName,
        fullText: licenseText,
        url: '',
        permissions: [],
        conditions: [],
        limitations: [],
        description: ''
      };
    }

    return mergedDetail;
  } catch (err) {
    console.error('Error fetching project detail:', err);
    return null;
  }
};

// Backward compatibility exports
export const fetchAnnualPlans = async (language: Language = 'en'): Promise<AnnualPlan[]> => {
  // This function is now handled by plans API
  const { fetchAnnualPlans: fetchPlans } = await import('../plans/planApi');
  return fetchPlans(language);
};

export const fetchAnnualPlanByName = async (
  name: string, 
  language: Language = 'en'
): Promise<AnnualPlan | null> => {
  // This function is now handled by plans API
  const { fetchAnnualPlanByName: fetchPlanByName } = await import('../plans/planApi');
  return fetchPlanByName(name, language);
};

export const fetchProjectsWithPlans = async (language: Language = 'en'): Promise<Project[]> => {
  return fetchProjects({}, language);
};

export const fetchProjectsByPlan = async (
  planName: string,
  language: Language = 'en'
): Promise<Project[]> => {
  const projects = await fetchProjects({}, language);
  return projects.filter(project => project.annualPlan === planName);
};

// ====== Project Comment API Functions ======

export interface ProjectCommentData {
  id: string;
  project_id: string;
  parent_id?: string;
  author_name: string;
  author_avatar_url?: string;
  content: string;
  type: string;
  created_at: string;
  user_identity_id?: string;
  likes_count: number;
  is_liked_by_user: boolean;
  replies: ProjectCommentData[];
}

export interface ProjectCommentListResponse {
  comments: ProjectCommentData[];
  total: number;
}

export interface LikeProjectCommentResponse {
  likes_count: number;
  is_liked_by_user: boolean;
}

/**
 * List project comments by type
 */
export const listProjectComments = async (
  projectId: string,
  type: string = 'general',
  fingerprint?: string,
  userIdentityId?: string,
  language: 'en' | 'zh' = 'en'
): Promise<ProjectCommentData[]> => {
  const url = `/api/v1/projects/${projectId}/comments?type=${type}&lang=${formatLanguage(language)}`;
  const response = await get<ProjectCommentListResponse>(url);
  return response.comments || [];
};

/**
 * Create a new project comment
 */
export const createProjectComment = async (
  projectId: string,
  content: string,
  fingerprint: string,
  options?: {
    type?: string;
    authorName?: string;
    authorEmail?: string;
    userIdentityId?: string;
    parentId?: string;
    language?: 'en' | 'zh';
  }
): Promise<ProjectCommentData> => {
  const body: any = {
    content,
    type: options?.type || 'general',
    fingerprint,
  };
  if (options?.authorName && options.authorName.trim()) body.author_name = options.authorName.trim();
  if (options?.authorEmail && options.authorEmail.trim()) body.author_email = options.authorEmail.trim();
  if (options?.userIdentityId && options.userIdentityId.trim()) body.user_identity_id = options.userIdentityId.trim();
  if (options?.parentId && options.parentId.trim()) body.parent_id = options.parentId.trim();

  // Align with backend model: if no user_identity_id provided, backend requires author_name and author_email
  if (!body.user_identity_id) {
    if (!body.author_name || typeof body.author_name !== 'string' || !body.author_name.trim()) {
      body.author_name = 'Anonymous';
    }
    if (!body.author_email || typeof body.author_email !== 'string' || body.author_email.trim().length < 5 || !body.author_email.includes('@')) {
      body.author_email = 'anonymous@example.com';
    }
  }

  // Add language as query parameter
  const url = `/api/v1/projects/${projectId}/comments?lang=${formatLanguage(options?.language || 'en')}`;
  const res = await post<ProjectCommentData>(url, body);
  return res;
};

/**
 * Like/unlike a project comment
 */
export const likeProjectComment = async (
  commentId: string,
  fingerprint?: string,
  userIdentityId?: string,
  language: 'en' | 'zh' = 'en'
): Promise<LikeProjectCommentResponse> => {
  const data: any = { lang: formatLanguage(language) };
  if (fingerprint) data.fingerprint = fingerprint;
  if (userIdentityId) data.user_identity_id = userIdentityId;
  const res = await post<LikeProjectCommentResponse>(`/api/v1/projects/comments/${commentId}/like`, data);
  return res;
};

/**
 * Delete a project comment
 */
export const deleteProjectComment = async (
  commentId: string,
  payload: { fingerprint: string; userIdentityId?: string; language?: 'en' | 'zh' }
): Promise<void> => {
  await del(`/api/v1/projects/comments/${commentId}`, {
    fingerprint: payload.fingerprint,
    user_identity_id: payload.userIdentityId || '',
  });
};