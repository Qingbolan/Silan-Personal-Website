import type { 
  ResumeData, 
  PersonalInfo, 
  Language, 
  EducationItem,
  ResearchItem,
  ExperienceItem,
  RecentUpdate,
  Publication,
  Award,
} from '../../types/api';
import { get, formatLanguage } from '../utils';

// API Functions

/**
 * Get complete resume data
 */
export const fetchResumeData = async (language: Language = 'en'): Promise<ResumeData> => {
  const apiCall = async () => {
    const response = await get<any>('/api/v1/resume', { lang: formatLanguage(language) });
    
    // Transform backend response to match frontend expected structure
    const transformedData: ResumeData = {
      name: response.personal_info?.full_name || '',
      title: response.personal_info?.title || '',
      current: response.personal_info?.current_status || '',
      contacts: [
        { type: 'email', value: response.personal_info?.email || '' },
        { type: 'phone', value: response.personal_info?.phone || '' },
        { type: 'location', value: response.personal_info?.location || '' }
      ].filter(contact => contact.value),
      socialLinks: response.personal_info?.social_links?.map((link: any) => ({
        type: link.platform,
        url: link.url
      })) || [],
      sections: {
        education: {
          title: 'Education',
          content: response.education?.map((edu: any) => ({
            school: edu.institution,
            degree: edu.degree,
            date: edu.is_current 
              ? `${edu.start_date} - Present`
              : `${edu.start_date} - ${edu.end_date || ''}`,
            details: edu.details || [],
            logo: edu.institution_logo_url,
            website: edu.institution_website,
            location: edu.location
          })) || []
        },
        experience: {
          title: 'Work Experience',
          content: response.experience?.map((exp: any) => ({
            company: exp.company,
            role: exp.position,
            date: exp.is_current 
              ? `${exp.start_date} - Present`
              : `${exp.start_date} - ${exp.end_date || ''}`,
            details: exp.details || [],
            logo: exp.company_logo_url,
            website: exp.company_website,
            location: exp.location
          })) || []
        },
        research: {
          title: 'Research Experience',
          content: response.research?.map((research: any) => ({
            title: research.title,
            location: research.location,
            date: research.is_ongoing 
              ? `${research.start_date} - Present`
              : `${research.start_date} - ${research.end_date || ''}`,
            details: research.details || []
          })) || []
        },
        publications: {
          title: 'Publications',
          content: response.publications?.map((pub: any) => pub.title) || []
        },
        awards: {
          title: 'Awards',
          content: response.awards?.map((award: any) => award.description || award.title) || []
        },
        skills: {
          title: 'Skills',
          content: response.skills || []
        },
        recent: {
          title: 'Recent Updates',
          content: response.recent_updates?.map((update: any) => ({
            id: update.id,
            title: update.title,
            description: update.description,
            date: update.date,
            tags: update.tags || [],
            type: update.type,
            status: update.status,
            priority: update.priority
          })) || []
        }
      }
    };
    
    return transformedData;
  };
  
  return apiCall();
};

/**
 * Get personal information
 */
export const fetchPersonalInfo = async (language: Language = 'en'): Promise<PersonalInfo> => {
  const apiCall = async () => {
    const response = await get<any>('/api/v1/resume/personal', { lang: formatLanguage(language) });
    
    // Return backend response directly since types now match
    return response;
  }; 
  return apiCall();
}

/**
 * Get education list
 */
export const fetchEducation = async (language: Language = 'en'): Promise<EducationItem[]> => {
  const apiCall = async () => {
    const response = await get<any[]>('/api/v1/resume/education', { lang: formatLanguage(language) });
    
    // Return backend response directly since types now match
    return response;
  };  
  return apiCall();
};

/**
 * Get work experience list
 */
export const fetchWorkExperience = async (language: Language = 'en'): Promise<ExperienceItem[]> => {
  const apiCall = async () => {
    const response = await get<any[]>('/api/v1/resume/experience', { lang: formatLanguage(language) });
    
    // Return backend response directly since types now match
    return response;
  };
  
  return apiCall();
};

/**
 * Get research projects list
 */
export const fetchResearchProjects = async (language: Language = 'en'): Promise<ResearchItem[]> => {
  const apiCall = async () => {
    const response = await get<ResearchItem[]>('/api/v1/resume/research', { lang: formatLanguage(language) });
    return response;
  };
  
  return apiCall();
};

/**
 * Get publications list
 */
export const fetchPublications = async (language: Language = 'en'): Promise<Publication[]> => {
  const apiCall = async () => {
    const response = await get<Publication[]>('/api/v1/resume/publications', { lang: formatLanguage(language) });
    return response;
  };
  
  return apiCall();
};

/**
 * Get awards list
 */
export const fetchAwards = async (language: Language = 'en'): Promise<Award[]> => {
  const apiCall = async () => {
    const response = await get<Award[]>('/api/v1/resume/awards', { lang: formatLanguage(language) });
    return response;
  };
  
  return apiCall();
};

/**
 * Get recent updates
 */
export const fetchRecentUpdates = async (language: Language = 'en'): Promise<RecentUpdate[]> => {
  const apiCall = async () => {
    const response = await get<RecentUpdate[]>('/api/v1/resume/recent', { lang: formatLanguage(language) });
    return response;
  };
  
  return apiCall();
};
