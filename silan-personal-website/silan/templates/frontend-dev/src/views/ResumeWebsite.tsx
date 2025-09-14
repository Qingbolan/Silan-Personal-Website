import React, { useState, useEffect, useMemo } from 'react';
import { motion } from 'framer-motion';
import { AlertCircle } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useLanguage } from '../components/LanguageContext';
import { useTheme } from '../components/ThemeContext';
import { LoadingSpinner } from '../components/ui';
import { fetchResumeData } from '../api/home/resumeApi';
import { ProjectSection, SectionCard, Timeline, TableOfContents, RecentSection, type RecentItem } from '../components/Resume';



interface ResumeData {
  name: string;
  title: string;
  current: string;
  contacts: Array<{
    type: string;
    value: string;
  }>;
  socialLinks: Array<{
    type: string;
    url: string;
  }>;
  sections: {
    education: {
      title: string;
      content: Array<{
        school: string;
        degree: string;
        date: string;
        details: string[];
        logo?: string;
        website?: string;
        location?: string;
      }>;
    };
    experience: {
      title: string;
      content: Array<{
        company: string;
        role: string;
        date: string;
        details: string[];
        logo?: string;
        website?: string;
        location?: string;
      }>;
    };
    research: {
      title: string;
      content: Array<{
  title: string;
  location: string;
        date: string;
        details: string[];
      }>;
    };
    publications: {
      title: string;
      content: string[];
    };
    awards: {
      title: string;
      content: string[];
    };
    skills: {
      title: string;
      content: string[];
    };
    recent: {
      title: string;
      content: RecentItem[];
    };
  };
}

// Components moved to separate files

const ResumeWebsite: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [resumeData, setResumeData] = useState<ResumeData | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const { colors } = useTheme();
  const { language } = useLanguage();
  const { t } = useTranslation();

  // Generate table of contents from resume data
  const tocSections = useMemo(() => {
    if (!resumeData || !resumeData.sections) return [];
    
    const sections = [
      { id: 'hero-section', title: resumeData.name, level: 1 },
    ];
    
    if (resumeData.sections?.recent) {
      sections.push({ id: 'recent-section', title: resumeData.sections.recent.title, level: 2 });
    }
    
    if (resumeData.sections?.experience) {
      sections.push({ id: 'experience-section', title: resumeData.sections.experience.title, level: 2 });
    }
    
    if (resumeData.sections?.education) {
      sections.push({ id: 'education-section', title: resumeData.sections.education.title, level: 2 });
    }
    
    if (resumeData.sections?.research) {
      sections.push({ id: 'research-section', title: resumeData.sections.research.title, level: 2 });
    }
    
    if (resumeData.sections?.publications) {
      sections.push({ id: 'publications-section', title: resumeData.sections.publications.title, level: 2 });
    }
    
    if (resumeData.sections?.awards) {
      sections.push({ id: 'awards-section', title: resumeData.sections.awards.title, level: 2 });
    }
    
    if (resumeData.sections?.skills) {
      sections.push({ id: 'skills-section', title: resumeData.sections.skills.title, level: 2 });
    }
    
    return sections;
  }, [resumeData]);

  // Set CSS variables based on current theme
  useEffect(() => {
    const root = document.documentElement;
    Object.entries(colors).forEach(([key, value]) => {
      root.style.setProperty(`--color-${key}`, value);
    });
  }, [colors]);

  // Load resume data
  useEffect(() => {
    let isMounted = true;
    
    const loadResumeData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        const data = await fetchResumeData(language);
        
        console.log('✅ Resume data loaded successfully');
        
        if (isMounted) {
          setResumeData(data);
          setLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          console.error('❌ Failed to load resume data:', err);
          setError(t('resume.failed_to_load'));
          setLoading(false);
        }
      }
    };

    loadResumeData();

    return () => {
      isMounted = false;
    };
  }, [language, t]);

  // Removed unused handleDownloadResume function

  if (loading || !resumeData) {
    return (
      <div className="min-h-screen flex items-center justify-center ">
        <LoadingSpinner 
          size="xl" 
          text={t('resume.loading_profile')} 
          variant="ring"
          color="primary"
        />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center ">
        <motion.div
          className="text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          role="alert"
        >
          <AlertCircle size={48} className="mx-auto mb-4 text-theme-error" />
          <h2 className="text-xl font-semibold mb-2 text-theme-primary">
            {t('resume.error_loading')}
          </h2>
          <p className="text-theme-secondary">{error}</p>
        </motion.div>
      </div>
    );
  }

  return (
    <motion.div
      className="min-h-screen relative"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      {/* Table of Contents */}
      <TableOfContents sections={tocSections} />
      
      {/* Project Section */}
      <div id="hero-section">
        <ProjectSection 
          name={resumeData.name || ''}
          title={resumeData.title || ''}
          current={resumeData.current || ''}
          contacts={resumeData.contacts || []}
          socialLinks={resumeData.socialLinks || []}
        />
      </div>

      {/* Content Sections */}
      <div className="max-w-6xl mx-auto px-3 xs:px-4 pb-12 xs:pb-16 sm:pb-20 space-y-6 xs:space-y-8 sm:space-y-12">
        {/* Recent Section - At the top for prominence */}
        {resumeData.sections?.recent && resumeData.sections.recent.content && (
          <div id="recent-section">
            <RecentSection 
              data={resumeData.sections.recent.content} 
              title={resumeData.sections.recent.title} 
              delay={0.1} 
            />
          </div>
        )}

        {/* Experience Section */}
        {resumeData.sections?.experience && resumeData.sections.experience.content && (
          <div id="experience-section">
            <SectionCard 
              title={resumeData.sections.experience.title} 
              delay={0.2}
            >
              <Timeline 
                items={resumeData.sections.experience.content.map(exp => ({
                  title: exp.role,
                  subtitle: exp.company,
                  date: exp.date,
                  details: exp.details,
                  logo: exp.logo,
                  website: exp.website,
                  location: exp.location
                }))}
                variant="primary"
              />
            </SectionCard>
          </div>
        )}

        {/* Education Section */}
        {resumeData.sections?.education && resumeData.sections.education.content && (
          <div id="education-section">
            <SectionCard 
              title={resumeData.sections.education.title} 
              delay={0.3}
            >
              <Timeline 
                items={resumeData.sections.education.content.map(edu => ({
                  title: edu.degree,
                  subtitle: edu.school,
                  date: edu.date,
                  details: edu.details,
                  logo: edu.logo,
                  website: edu.website,
                  location: edu.location
                }))}
                variant="secondary"
              />
            </SectionCard>
          </div>
        )}

        {/* Research Section */}
        {resumeData.sections?.research && resumeData.sections.research.content && (
          <div id="research-section">
            <SectionCard 
              title={resumeData.sections.research.title} 
              delay={0.4}
            >
              <Timeline 
                items={resumeData.sections.research.content.map(research => ({
                  title: research.title,
                  subtitle: research.location,
                  date: research.date,
                  details: research.details
                }))}
                variant="accent"
              />
            </SectionCard>
          </div>
        )}

        {/* Publications Section */}
        {resumeData.sections?.publications && resumeData.sections.publications.content && (
          <div id="publications-section">
            <SectionCard 
              title={resumeData.sections.publications.title} 
              delay={0.5}
            >
              <div className="space-y-4">
                {resumeData.sections.publications.content.map((publication, index) => (
                  <motion.div
                    key={index}
                    className="p-4 rounded-xl bg-theme-surface-elevated border border-theme-card"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                  >
                    <p className="text-theme-secondary text-sm leading-relaxed">
                      {publication}
                    </p>
                  </motion.div>
                ))}
              </div>
            </SectionCard>
          </div>
        )}

        {/* Awards Section */}
        {resumeData.sections?.awards && resumeData.sections.awards.content && (
          <div id="awards-section">
            <SectionCard 
              title={resumeData.sections.awards.title} 
              delay={0.6}
            >
              <div className="space-y-3">
                {resumeData.sections.awards.content.map((award, index) => (
                  <motion.div
                    key={index}
                    className="flex items-start space-x-3 p-3 rounded-lg bg-theme-surface-elevated"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                  >
                    <div className="w-2 h-2 rounded-full bg-theme-accent mt-2 flex-shrink-0" />
                    <p className="text-theme-secondary text-sm leading-relaxed">{award}</p>
                  </motion.div>
                ))}
              </div>
            </SectionCard>
          </div>
        )}

        {/* Skills Section */}
        {resumeData.sections?.skills && resumeData.sections.skills.content && (
          <div id="skills-section">
            <SectionCard 
              title={resumeData.sections.skills.title} 
              delay={0.7}
            >
              <div className="flex flex-wrap gap-3">
                {resumeData.sections.skills.content.map((skill, index) => (
                  <motion.span
                    key={index}
                    className="px-4 py-2 rounded-lg bg-theme-surface-elevated text-theme-secondary border border-theme-card hover:bg-theme-primary hover:text-white transition-all duration-300 text-sm font-medium cursor-default"
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.3, delay: index * 0.05 }}
                    whileHover={{ scale: 1.05 }}
                  >
                    {skill}
                  </motion.span>
                ))}
              </div>
            </SectionCard>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default ResumeWebsite; 