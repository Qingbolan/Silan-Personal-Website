import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ArrowLeft, 
  ExternalLink, 
  Github, 
  Star, 
  GitFork, 
  Download,
  Shield,
  Calendar,
} from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useLanguage } from '../LanguageContext';
import { getPlanDisplay } from '../../utils/iconMap';
import { fetchAnnualPlanByName } from '../../api/plans/planApi';
import { fetchProjectDetailById } from '../../api';
import ProjectTabs from '../ProjectTabs';
import type { ProjectDetail as ProjectDetailType } from '../../types/api';

const ProjectDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { language } = useLanguage();
  const { t } = useTranslation();
  const [plan, setPlan] = useState<any>(null);
  const [project, setProject] = useState<ProjectDetailType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Fetch project data
  useEffect(() => {
    const loadProject = async () => {
      if (!id) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        
        // Fetch project details with language support
        const projectData = await fetchProjectDetailById(id, language as 'en' | 'zh');
        
        if (projectData) {
          setProject(projectData);
        } else {
          setError(t('projects.projectNotFound'));
        }
      } catch (err) {
        console.error('Error loading project:', err);
        setError(t('projects.failedToLoadProject'));
      } finally {
        setLoading(false);
      }
    };

    loadProject();
  }, [id, language]);
  
  // Fetch plan data
  useEffect(() => {
    const loadPlan = async () => {
      if (project?.planId) {
        try {
          const planData = await fetchAnnualPlanByName(project.planId, language);
          setPlan(planData);
        } catch (error) {
          console.error('Failed to load plan:', error);
        }
      }
    };
    
    loadPlan();
  }, [project?.planId, language]);
  
  if (loading) {
    return (
      <div className="container mx-auto px-6 py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-theme-primary mx-auto mb-4"></div>
          <p className="text-theme-secondary">
            {t('projects.loadingProject')}
          </p>
        </div>
      </div>
    );
  }
  
  if (error || !project) {
    return (
      <div className="container mx-auto px-6 py-12">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-theme-primary mb-4">
            {error || t('projects.projectNotFound')}
          </h1>
          <Link 
            to="/projects"
            className="text-blue-600 hover:underline"
          >
            {t('projects.backToProjects')}
          </Link>
        </div>
      </div>
    );
  }

  const planDisplay = plan ? getPlanDisplay(plan) : null;

  return (
    <div className="min-h-screen">
      <div className="container mx-auto px-6 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-8"
        >
          {/* Breadcrumb */}
          <div className="flex items-center gap-2 mb-6 text-sm text-theme-secondary">
            <Link 
              to="/projects" 
              className="flex items-center gap-1 hover:text-theme-primary transition-colors"
            >
              <ArrowLeft size={16} />
              {t('projects.title')}
            </Link>
            <span>/</span>
            <span className="text-theme-primary">{project.title}</span>
          </div>

          {/* Project Header */}
          <div className="bg-theme-surface rounded-xl p-6 shadow-sm border border-theme-border">
            <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
              <div className="flex-1">
                {/* Plan Badge */}
                {plan && planDisplay && (
                  <div className="flex items-center gap-2 mb-3">
                    {planDisplay}
                    <span className="text-sm font-medium text-theme-secondary">
                      {language === 'en' ? plan.name : plan.nameZh}
                    </span>
                  </div>
                )}

                {/* Title and Description */}
                <h1 className="text-3xl font-bold text-theme-primary mb-3">
                  {language === 'zh' && project.titleZh ? project.titleZh : project.title}
                </h1>
                <p className="text-lg text-theme-secondary mb-4">
                  {project.description}
                </p>

                {/* Tags */}
                <div className="flex flex-wrap gap-2 mb-4">
                  {project.tags?.map((tag: string, index: number) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
                    >
                      {tag}
                    </span>
                  ))}
                </div>

                {/* Quick Stats */}
                <div className="flex flex-wrap items-center gap-6 text-sm text-theme-secondary">
                  <div className="flex items-center gap-1">
                    <Star size={16} />
                    <span>{project.metrics?.stars || 0} {t('projects.stars')}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <GitFork size={16} />
                    <span>{project.community?.forks || 0} {t('projects.forks')}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Download size={16} />
                    <span>{project.metrics?.downloads || 0} {t('projects.downloads')}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Shield size={16} />
                    <span>{project.status?.license || 'MIT'}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Calendar size={16} />
                    <span>{t('projects.updated')} {project.status?.lastUpdated}</span>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col gap-3 lg:min-w-[200px]">
                {project.demo && (
                  <a
                    href={project.demo}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center justify-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <ExternalLink size={16} />
                    {t('projects.liveDemo')}
                  </a>
                )}
                {project.github && (
                  <a
                    href={project.github}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center justify-center gap-2 border border-theme-border text-theme-primary px-4 py-2 rounded-lg hover:bg-theme-surface transition-colors"
                  >
                    <Github size={16} />
                    {t('projects.sourceCode')}
                  </a>
                )}
                <button className="flex items-center justify-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors">
                  <Download size={16} />
                  {t('projects.download')} v{project.versions?.latest || '1.0.0'}
                </button>
              </div>
            </div>

            {/* Project Image */}
            {project.image && (
              <div className="mt-6">
                <img
                  src={project.image}
                  alt={project.title}
                  className="w-full h-64  project-image-placeholder rounded-lg"
                />
              </div>
            )}
          </div>
        </motion.div>

        {/* Tabs Content */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <ProjectTabs projectData={project} />
        </motion.div>
      </div>
    </div>
  );
};

export default ProjectDetail; 