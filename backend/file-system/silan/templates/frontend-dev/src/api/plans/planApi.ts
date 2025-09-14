import type { AnnualPlan, Project, Language, Plan, ProjectWithPlan } from '../../types/api';
import { get, formatLanguage } from '../utils';


// API Functions

/**
 * Fetch all annual plans
 */
export const fetchAnnualPlans = async (language: Language = 'en'): Promise<AnnualPlan[]> => {
  const response = await get<AnnualPlan[]>('/api/v1/plans/annual', {
    lang: formatLanguage(language)
  });
  return response;
};

/**
 * Get current active annual plan (most recent year)
 */
export const fetchCurrentAnnualPlan = async (language: Language = 'en'): Promise<AnnualPlan | null> => {
  const response = await get<AnnualPlan>('/api/v1/plans/annual/current', {
    lang: formatLanguage(language)
  });
  return response;
};

/**
 * Get annual plan by name
 */
export const fetchAnnualPlanByName = async (planName: string, language: Language = 'en'): Promise<AnnualPlan | null> => {
  const response = await get<AnnualPlan>(`/api/v1/plans/annual/${planName}`, {
    lang: formatLanguage(language)
  });
  return response;
};

/**
 * Fetch all projects with language support
 */
export const fetchProjectsWithAnnualPlans = async (language: Language = 'en'): Promise<Project[]> => {
  // Directly use the projects API instead of a non-existent plans/projects endpoint
  try {
    const { fetchProjects } = await import('../projects/projectApi');
    return await fetchProjects({}, language);
  } catch (error) {
    console.warn('Failed to import projects API:', error);
    return [];
  }
};

/**
 * Get projects by annual plan name
 */
export const fetchProjectsByAnnualPlan = async (planName: string, language: Language = 'en'): Promise<Project[]> => {
  try {
    const response = await get<Project[]>(`/api/v1/plans/${planName}/projects`, {
      lang: formatLanguage(language)
    });
    return response;
  } catch (error) {
    // Fallback: filter projects by plan name
    try {
      const projects = await fetchProjectsWithAnnualPlans(language);
      return projects.filter(project => project.annualPlan === planName);
    } catch (fallbackError) {
      console.warn('Failed to fetch projects by plan:', fallbackError);
      return [];
    }
  }
};

// Conversion functions for backward compatibility
const convertAnnualPlanToPlan = (annualPlan: AnnualPlan): Plan => ({
  id: annualPlan.name,
  name: annualPlan.name,
  nameZh: annualPlan.nameZh, // Use correct Chinese name
  description: annualPlan.description,
  descriptionZh: annualPlan.descriptionZh, // Use correct Chinese description
  slogan: annualPlan.description,
  sloganZh: annualPlan.descriptionZh, // Use Chinese description as slogan
  goals: annualPlan.objectives,
  goalsZh: annualPlan.objectivesZh, // Use correct Chinese objectives
  image: '/logo.svg',
  icon: 'Calendar',
  startYear: annualPlan.year,
  endYear: annualPlan.year,
  status: annualPlan.year === new Date().getFullYear() ? 'active' : 
           annualPlan.year < new Date().getFullYear() ? 'completed' : 'planned'
});

const convertProjectToProjectWithPlan = (project: Project): ProjectWithPlan => ({
  id: project.id.toString(),
  title: project.name,
  description: project.description,
  image: '/api/placeholder/400/250',
  tags: project.tags,
  github: undefined,
  demo: undefined,
  planId: project.annualPlan,
  year: project.year
});

// Backward compatibility wrapper functions
export const fetchPlans = async (language: Language = 'en'): Promise<Plan[]> => {
  const annualPlans = await fetchAnnualPlans(language);
  return annualPlans.map(convertAnnualPlanToPlan);
};

export const fetchCurrentPlan = async (language: Language = 'en'): Promise<Plan | null> => {
  const currentAnnualPlan = await fetchCurrentAnnualPlan(language);
  return currentAnnualPlan ? convertAnnualPlanToPlan(currentAnnualPlan) : null;
};

export const fetchProjectsWithPlans = async (language: Language = 'en'): Promise<ProjectWithPlan[]> => {
  const projects = await fetchProjectsWithAnnualPlans(language);
  return projects.map(convertProjectToProjectWithPlan);
};