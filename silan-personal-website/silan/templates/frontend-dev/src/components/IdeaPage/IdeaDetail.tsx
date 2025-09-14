import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  ArrowLeft,
  Lightbulb,
  Calendar,
  Clock,
  ExternalLink,
  CheckCircle,
  Circle,
  Play,
  BookOpen,
  FileText,
  Share2,
  Heart,
  MessageSquare,
  BarChart3,
  Beaker
} from 'lucide-react';
import { useTheme } from '../ThemeContext';
import { useLanguage } from '../LanguageContext';
import CommunityFeedback from '../CommunityFeedback';
import { IdeaData } from '../../types';
import { fetchIdeaById } from '../../api/ideas/ideaApi';


const IdeaDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { colors, isDarkMode } = useTheme();
  const { language } = useLanguage();

  const [idea, setIdea] = useState<IdeaData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('abstract');
  const [liked, setLiked] = useState(false);

  useEffect(() => {
    const loadIdea = async () => {
      if (!id) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        
        // Fetch idea from API with language support
        const ideaData = await fetchIdeaById(id, language as 'en' | 'zh');
        
        if (ideaData) {
          setIdea(ideaData);
        } else {
          // If no data found, you can optionally fall back to mock data for development
          // or show a not found message
          setIdea(null);
        }
      } catch (err) {
        console.error('Error loading idea:', err);
        setIdea(null);
      } finally {
        setLoading(false);
      }
    };
    
    loadIdea();
  }, [id, language]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published': return { color: '#059669', backgroundColor: '#DCFCE7' };
      case 'validating': return { color: '#0284C7', backgroundColor: '#DBEAFE' };
      case 'experimenting': return { color: '#7C3AED', backgroundColor: '#EDE9FE' };
      case 'hypothesis': return { color: '#D97706', backgroundColor: '#FEF3C7' };
      default: return { color: colors.textSecondary, backgroundColor: colors.surface };
    }
  };

  const getExperimentIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle size={16} style={{ color: '#059669' }} />;
      case 'running': return <Play size={16} style={{ color: '#0284C7' }} />;
      case 'failed': return <Circle size={16} style={{ color: '#DC2626' }} />;
      default: return <Circle size={16} style={{ color: colors.textTertiary }} />;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString(language === 'en' ? 'en-US' : 'zh-CN');
  };

  const tabs = [
    { id: 'abstract', label: language === 'en' ? 'Abstract' : '摘要', icon: <Lightbulb size={18} /> },
    { id: 'progress', label: language === 'en' ? 'Latest Progress' : '最新进展', icon: <Beaker size={18} /> },
    { id: 'results', label: language === 'en' ? 'Results' : '结果', icon: <BarChart3 size={18} /> },
    { id: 'references', label: language === 'en' ? 'References' : '参考文献', icon: <BookOpen size={18} /> },
    { id: 'discussion', label: language === 'en' ? 'Discussion' : '讨论', icon: <MessageSquare size={18} /> }
  ];

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: colors.background }}>
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center">
          <Lightbulb size={48} className="mx-auto mb-4 animate-pulse" style={{ color: colors.accent }} />
          <p style={{ color: colors.textSecondary }}>{language === 'en' ? 'Loading research details...' : '加载研究详情...'}</p>
        </motion.div>
      </div>
    );
  }

  if (!idea) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: colors.background }}>
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center">
          <BookOpen size={48} className="mx-auto mb-4" style={{ color: colors.error }} />
          <h2 className="text-xl font-semibold mb-2" style={{ color: colors.textPrimary }}>
            {language === 'en' ? 'Research Not Found' : '未找到研究'}
          </h2>
          <button
            onClick={() => navigate('/ideas')}
            className="px-4 py-2 rounded-lg hover:opacity-90 transition-opacity"
            style={{ backgroundColor: colors.primary, color: 'white' }}
          >
            {language === 'en' ? 'Back to Ideas' : '返回想法列表'}
          </button>
        </motion.div>
      </div>
    );
  }

  const renderAbstract = () => (
    <div className="space-y-8">
      <div>
        <h3 className="text-xl font-semibold mb-4" style={{ color: colors.textPrimary }}>{language === 'en' ? 'Abstract' : '摘要'}</h3>
        <p className="leading-relaxed text-justify" style={{ color: colors.textSecondary }}>
          {language === 'en' ? idea.abstract : idea.abstractZh || idea.abstract}
        </p>
      </div>

      {idea.hypothesis && (
        <div>
          <h3 className="text-xl font-semibold mb-4" style={{ color: colors.textPrimary }}>{language === 'en' ? 'Research Hypothesis' : '研究假设'}</h3>
          <div className="p-6 rounded-xl border-l-4" style={{ 
            backgroundColor: isDarkMode ? 'rgba(59, 130, 246, 0.1)' : '#EFF6FF', 
            borderColor: '#3B82F6' 
          }}>
            <p className="leading-relaxed italic" style={{ color: colors.textSecondary }}>
              {language === 'en' ? idea.hypothesis : idea.hypothesisZh || idea.hypothesis}
            </p>
          </div>
        </div>
      )}

      {idea.motivation && (
        <div>
          <h3 className="text-xl font-semibold mb-4" style={{ color: colors.textPrimary }}>{language === 'en' ? 'Research Motivation' : '研究动机'}</h3>
          <p className="leading-relaxed" style={{ color: colors.textSecondary }}>
            {language === 'en' ? idea.motivation : idea.motivationZh || idea.motivation}
          </p>
        </div>
      )}

      {idea.keywords && (
        <div>
          <h3 className="text-xl font-semibold mb-4" style={{ color: colors.textPrimary }}>{language === 'en' ? 'Keywords' : '关键词'}</h3>
          <div className="flex flex-wrap gap-2">
            {idea.keywords.map((keyword, index) => (
              <span key={index} className="px-3 py-1 rounded-lg text-sm" style={{ 
                backgroundColor: colors.surface, 
                color: colors.textPrimary 
              }}>
                {keyword}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const renderProgress = () => (
    <div className="space-y-6">
      {idea.methodology ? (
        <div>
          <h3 className="text-xl font-semibold mb-4" style={{ color: colors.textPrimary }}>{language === 'en' ? 'Latest Progress' : '最新进展'}</h3>
          <p className="leading-relaxed" style={{ color: colors.textSecondary }}>
            {language === 'en' ? idea.methodology : idea.methodologyZh || idea.methodology}
          </p>
        </div>
      ) : (
        <div className="text-center py-12" style={{ color: colors.textSecondary }}>
          <Beaker size={48} className="mx-auto mb-4 opacity-50" />
          <p>{language === 'en' ? 'Progress details coming soon...' : '进展详情即将发布...'}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Link to={`/blog/${idea.id}`} className="p-6 rounded-xl hover:shadow-lg transition-shadow" style={{ backgroundColor: colors.cardBackground }}>
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-lg" style={{ backgroundColor: colors.surface }}>
              <FileText size={24} style={{ color: colors.accent }} />
            </div>
            <div>
              <h4 className="font-semibold mb-2" style={{ color: colors.textPrimary }}>{language === 'en' ? 'Related Blog Posts' : '相关博客文章'}</h4>
              <p className="text-sm" style={{ color: colors.textSecondary }}>
                {language === 'en' ? 'Read our latest blog posts about this research' : '阅读我们关于这项研究的最新博客文章'}
              </p>
            </div>
          </div>
        </Link>

        <Link to={`/projects/${idea.id}`} className="p-6 rounded-xl hover:shadow-lg transition-shadow" style={{ backgroundColor: colors.cardBackground }}>
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-lg" style={{ backgroundColor: colors.surface }}>
              <ExternalLink size={24} style={{ color: colors.accent }} />
            </div>
            <div>
              <h4 className="font-semibold mb-2" style={{ color: colors.textPrimary }}>{language === 'en' ? 'Project Details' : '项目详情'}</h4>
              <p className="text-sm" style={{ color: colors.textSecondary }}>
                {language === 'en' ? 'View the complete project implementation' : '查看完整的项目实现'}
              </p>
            </div>
          </div>
        </Link>
      </div>

      {idea.techStack && (
        <div>
          <h3 className="text-xl font-semibold mb-4" style={{ color: colors.textPrimary }}>{language === 'en' ? 'Technical Stack' : '技术栈'}</h3>
          <div className="flex flex-wrap gap-2">
            {idea.techStack.map((tech, index) => (
              <span key={index} className="px-3 py-2 rounded-lg text-sm font-medium border" style={{ 
                backgroundColor: colors.surface, 
                color: colors.textPrimary,
                borderColor: colors.cardBorder
              }}>
                {tech}
              </span>
            ))}
          </div>
        </div>
      )}

      {idea.experiments && (
        <div>
          <h3 className="text-xl font-semibold mb-4" style={{ color: colors.textPrimary }}>{language === 'en' ? 'Recent Experiments' : '最近实验'}</h3>
          <div className="space-y-4">
            {idea.experiments.map((experiment) => (
              <div key={experiment.id} className="p-6 rounded-xl" style={{ 
                backgroundColor: colors.cardBackground, 
                boxShadow: colors.shadowSm 
              }}>
                <div className="flex items-start gap-4">
                  <div className="mt-1">{getExperimentIcon(experiment.status)}</div>
                  <div className="flex-1">
                    <h4 className="font-semibold mb-2" style={{ color: colors.textPrimary }}>
                      {language === 'en' ? experiment.title : experiment.titleZh || experiment.title}
                    </h4>
                    <p className="mb-3" style={{ color: colors.textSecondary }}>
                      {language === 'en' ? experiment.description : experiment.descriptionZh || experiment.description}
                    </p>
                    <div className="flex items-center gap-4 text-sm" style={{ color: colors.textTertiary }}>
                      <span>{language === 'en' ? 'Started: ' : '开始: '}{formatDate(experiment.startDate || '')}</span>
                      {experiment.endDate && <span>{language === 'en' ? 'Ended: ' : '结束: '}{formatDate(experiment.endDate)}</span>}
                    </div>
                    {experiment.results && (
                      <div className="mt-3 p-3 rounded-lg" style={{ backgroundColor: colors.surface }}>
                        <p className="text-sm" style={{ color: colors.textSecondary }}>{experiment.results}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const renderResults = () => (
    <div className="space-y-6">
      {idea.preliminaryResults && (
        <div>
          <h3 className="text-xl font-semibold mb-4" style={{ color: colors.textPrimary }}>{language === 'en' ? 'Preliminary Results' : '初步结果'}</h3>
          <p className="leading-relaxed" style={{ color: colors.textSecondary }}>
            {language === 'en' ? idea.preliminaryResults : idea.preliminaryResultsZh || idea.preliminaryResults}
          </p>
        </div>
      )}

      {idea.keyFindings && (
        <div>
          <h3 className="text-xl font-semibold mb-4" style={{ color: colors.textPrimary }}>{language === 'en' ? 'Key Findings' : '主要发现'}</h3>
          <ul className="space-y-2">
            {(language === 'en' ? idea.keyFindings : idea.keyFindingsZh || idea.keyFindings).map((finding, index) => (
              <li key={index} className="flex items-start gap-3">
                <CheckCircle size={16} style={{ color: '#059669' }} className="mt-1" />
                <span style={{ color: colors.textSecondary }}>{finding}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {idea.limitations && (
        <div>
          <h3 className="text-xl font-semibold mb-4" style={{ color: colors.textPrimary }}>{language === 'en' ? 'Limitations' : '局限性'}</h3>
          <ul className="space-y-2">
            {(language === 'en' ? idea.limitations : idea.limitationsZh || idea.limitations).map((limitation, index) => (
              <li key={index} className="flex items-start gap-3">
                <div className="w-2 h-2 rounded-full mt-2" style={{ backgroundColor: '#F59E0B' }}></div>
                <span style={{ color: colors.textSecondary }}>{limitation}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {idea.futureDirections && (
        <div>
          <h3 className="text-xl font-semibold mb-4" style={{ color: colors.textPrimary }}>{language === 'en' ? 'Future Directions' : '未来方向'}</h3>
          <ul className="space-y-2">
            {(language === 'en' ? idea.futureDirections : idea.futureDirectionsZh || idea.futureDirections).map((direction, index) => (
              <li key={index} className="flex items-start gap-3">
                <div className="w-2 h-2 rounded-full mt-2" style={{ backgroundColor: '#3B82F6' }}></div>
                <span style={{ color: colors.textSecondary }}>{direction}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {!idea.preliminaryResults && !idea.keyFindings && !idea.limitations && !idea.futureDirections && (
        <div className="text-center py-12" style={{ color: colors.textSecondary }}>
          <BarChart3 size={48} className="mx-auto mb-4 opacity-50" />
          <p>{language === 'en' ? 'Research results will be published here as they become available.' : '研究结果将在可用时发布在此处。'}</p>
        </div>
      )}
    </div>
  );

  const renderReferences = () => (
    <div className="space-y-4">
      {idea.relatedWorks && idea.relatedWorks.length > 0 ? (
        idea.relatedWorks.map((ref) => (
          <div key={ref.id} className="p-6 rounded-xl" style={{ backgroundColor: colors.cardBackground, boxShadow: colors.shadowSm }}>
            <div className="flex items-start gap-4">
              <div className="p-2 rounded-lg" style={{ backgroundColor: colors.surface }}>
                <FileText size={16} />
              </div>
              <div className="flex-1">
                <h4 className="font-semibold mb-2" style={{ color: colors.textPrimary }}>{ref.title}</h4>
                <p className="text-sm mb-2" style={{ color: colors.textSecondary }}>
                  {ref.authors.join(', ')} ({ref.year}) - {ref.venue}
                </p>
                {ref.notes && <p className="text-sm mb-3" style={{ color: colors.textTertiary }}>{ref.notes}</p>}
                {ref.url && (
                  <a href={ref.url} target="_blank" rel="noopener noreferrer" 
                     className="inline-flex items-center gap-2 text-sm" style={{ color: colors.accent }}>
                    <ExternalLink size={14} />
                    {language === 'en' ? 'View Paper' : '查看论文'}
                  </a>
                )}
              </div>
            </div>
          </div>
        ))
      ) : (
        <div className="text-center py-12" style={{ color: colors.textSecondary }}>
          <BookOpen size={48} className="mx-auto mb-4 opacity-50" />
          <p>{language === 'en' ? 'References will be added as research progresses.' : '参考文献将随着研究进展而添加。'}</p>
        </div>
      )}
    </div>
  );

  const renderDiscussion = () => <CommunityFeedback projectId={`idea-${idea.id}`} />;

  const renderContent = () => {
    switch (activeTab) {
      case 'abstract': return renderAbstract();
      case 'progress': return renderProgress();
      case 'results': return renderResults();
      case 'references': return renderReferences();
      case 'discussion': return renderDiscussion();
      default: return renderAbstract();
    }
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="py-8">
      <div className="max-w-6xl mx-auto px-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <div className="flex items-center gap-2 mb-6 text-sm text-theme-secondary">
            <button
              onClick={() => navigate('/ideas')}
              className="flex items-center gap-2 hover:text-theme-primary transition-colors"
            >
              <ArrowLeft size={16} />
              {language === 'en' ? 'Back to Ideas' : '返回想法列表'}
            </button>
          </div>

          <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
            <div className="flex-1">
              <div className="flex items-center gap-4 mb-4">
                <div className={`p-3 rounded-xl ${getStatusColor(idea.status)}`}>
                  <Lightbulb size={24} />
                </div>
                <div>
                  <h1 className="text-2xl lg:text-3xl font-bold text-theme-primary mb-2">{idea.title}</h1>
                  <div className="flex flex-wrap items-center gap-4 text-sm text-theme-secondary">
                    <span className="flex items-center gap-1">
                      <Calendar size={14} />
                      {language === 'en' ? 'Created: ' : '创建于: '}{formatDate(idea.createdAt)}
                    </span>
                    {idea.lastUpdated && (
                      <span className="flex items-center gap-1">
                        <Clock size={14} />
                        {language === 'en' ? 'Updated: ' : '更新于: '}{formatDate(idea.lastUpdated)}
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {idea.tags && idea.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-6">
                  {idea.tags.map((tag, index) => (
                    <span key={index} className="px-3 py-1 bg-theme-surface text-theme-primary rounded-lg text-sm font-medium">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>

            <div className="flex flex-col sm:flex-row gap-3">
              <button
                onClick={() => setLiked(!liked)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                  liked ? 'bg-red-100 text-red-600 hover:bg-red-200' : 'bg-theme-surface text-theme-secondary hover:bg-theme-hover'
                }`}
              >
                <Heart size={16} fill={liked ? 'currentColor' : 'none'} />
                {language === 'en' ? 'Like' : '喜欢'}
              </button>
              <button className="flex items-center gap-2 px-4 py-2 bg-theme-surface text-theme-secondary hover:bg-theme-hover rounded-lg transition-colors">
                <Share2 size={16} />
                {language === 'en' ? 'Share' : '分享'}
              </button>
              {idea.demoUrl && (
                <a href={`/projects/${idea.id}/demo`} 
                   className="flex items-center gap-2 px-4 py-2 bg-theme-primary text-white hover:opacity-90 rounded-lg transition-opacity">
                  <ExternalLink size={16} />
                  {language === 'en' ? 'Project Demo' : '项目演示'}
                </a>
              )}
            </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="border-b border-theme-surface mb-8">
          <nav className="flex space-x-8 overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 py-4 px-2 border-b-2 font-medium text-sm whitespace-nowrap transition-colors ${
                  activeTab === tab.id
                    ? 'border-theme-primary text-theme-primary'
                    : 'border-transparent text-theme-secondary hover:text-theme-primary hover:border-theme-secondary'
                }`}
              >
                {tab.icon}
                {tab.label}
              </button>
            ))}
          </nav>
        </motion.div>

        <motion.div key={activeTab} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }} className="mb-8">
          {renderContent()}
        </motion.div>
      </div>
    </motion.div>
  );
};

export default IdeaDetail; 