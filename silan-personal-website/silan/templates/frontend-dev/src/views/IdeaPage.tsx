import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Lightbulb, Clock, Plus, Search, AlertCircle } from 'lucide-react';
import { useTheme } from '../components/ThemeContext';
import { useLanguage } from '../components/LanguageContext';
import { IdeaData } from '../types';
import { fetchIdeas } from '../api';

interface IdeaCardProps {
  idea: IdeaData;
  index: number;
  onView?: (idea: IdeaData) => void;
}

const IdeaCard: React.FC<IdeaCardProps> = ({ idea, index, onView }) => {
  const { language } = useLanguage();
  
  // Guard against null/undefined idea
  if (!idea) {
    return null;
  }

  const getStatusText = useCallback((status: string) => {
    if (language === 'en') {
      switch (status) {
        case 'published':
          return 'Published';
        case 'validating':
          return 'Validating';
        case 'experimenting':
          return 'Experimenting';
        case 'hypothesis':
          return 'Hypothesis';
        case 'concluded':
          return 'Concluded';
        default:
          return 'Draft';
      }
    } else {
      switch (status) {
        case 'published':
          return '已发表';
        case 'validating':
          return '验证中';
        case 'experimenting':
          return '实验中';
        case 'hypothesis':
          return '假设';
        case 'concluded':
          return '已结论';
        default:
          return '草案';
      }
    }
  }, [language]);

  const getStatusClass = useCallback((status: string) => {
    switch (status) {
      case 'published':
        return 'text-theme-success bg-theme-success-20';
      case 'validating':
        return 'text-blue-600 bg-blue-100';
      case 'experimenting':
        return 'text-purple-600 bg-purple-100';
      case 'hypothesis':
        return 'text-theme-warning bg-theme-warning-20';
      case 'concluded':
        return 'text-gray-600 bg-gray-100';
      default:
        return 'text-theme-accent bg-theme-primary-20';
    }
  }, []);

  const handleClick = useCallback(() => {
    onView?.(idea);
  }, [onView, idea]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  }, [handleClick]);

  return (
    <motion.div
      className="group p-6 rounded-2xl cursor-pointer focus:outline-none focus:ring-2 focus:ring-offset-2 ring-theme-primary card-interactive"
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: index * 0.1 }}
      whileHover={{ y: -5 }}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      tabIndex={0}
      role="button"
      aria-label={`View idea: ${idea.title}`}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-lg ${getStatusClass(idea.status)}`}>
            <Lightbulb size={20} className={
              idea.status === 'published' ? 'text-theme-success' : 
              idea.status === 'validating' ? 'text-blue-600' :
              idea.status === 'experimenting' ? 'text-purple-600' :
              idea.status === 'hypothesis' ? 'text-theme-warning' : 
              idea.status === 'concluded' ? 'text-gray-600' :
              'text-theme-accent'
            } />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-theme-primary">
              {idea.title}
            </h3>
            <p className="text-sm text-theme-tertiary">
              {idea.category}
            </p>
          </div>
        </div>
        
        <motion.div
          className={`px-3 py-1 rounded-full text-xs font-semibold status-badge ${getStatusClass(idea.status)}`}
          whileHover={{ scale: 1.05 }}
        >
          {getStatusText(idea.status)}
        </motion.div>
      </div>

      {/* Description */}
      <p className="text-sm leading-relaxed mb-4 text-theme-secondary">
        {idea.description}
      </p>

      {/* Tags */}
      {idea.tags.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {idea.tags.map((tag, tagIndex) => (
            <motion.span
              key={tagIndex}
              className="px-2 py-1 text-xs rounded-lg font-medium tag-default whitespace-nowrap"
              whileHover={{ scale: 1.05 }}
              transition={{ duration: 0.2 }}
            >
              {tag}
            </motion.span>
          ))}
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center space-x-1 text-theme-tertiary">
          <Clock size={12} />
          <span>{new Date(idea.createdAt).toLocaleDateString()}</span>
        </div>
        <motion.button
          className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 p-1 rounded focus:opacity-100 focus:outline-none focus:ring-1 ring-theme-primary text-theme-accent"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
          onClick={(e) => {
            e.stopPropagation();
            handleClick();
          }}
          aria-label={`View details for ${idea.title}`}
        >
          <Plus size={16} />
        </motion.button>
      </div>
    </motion.div>
  );
};

interface FilterChipProps {
  label: string;
  active: boolean;
  onClick: () => void;
}

const FilterChip: React.FC<FilterChipProps> = ({ label, active, onClick }) => {
  return (
    <motion.button
      onClick={onClick}
      className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 ring-theme-primary ring-offset-theme-background filter-chip ${
        active ? 'active' : ''
      }`}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      aria-pressed={active}
    >
      {label}
    </motion.button>
  );
};

const IdeaPage: React.FC = () => {
  const [ideas, setIdeas] = useState<IdeaData[]>([]);
  const [filteredIdeas, setFilteredIdeas] = useState<IdeaData[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [selectedStatus, setSelectedStatus] = useState<string>('All');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { colors } = useTheme();
  const { language } = useLanguage();
  const navigate = useNavigate();

  // Set CSS variables based on current theme
  useEffect(() => {
    const root = document.documentElement;
    Object.entries(colors).forEach(([key, value]) => {
      root.style.setProperty(`--color-${key}`, value);
    });
  }, [colors]);

  // Scroll to top on component mount
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  // Load ideas
  useEffect(() => {
    let isMounted = true;
    
    const loadIdeas = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Fetch ideas from API with language support
        const fetchedIdeas = await fetchIdeas({}, language as 'en' | 'zh');
        
        if (isMounted) {
          setIdeas(fetchedIdeas);
          setFilteredIdeas(fetchedIdeas);
          setLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          setError(language === 'en' ? 'Failed to load ideas' : '加载想法失败');
          setLoading(false);
        }
      }
    };

    loadIdeas();

    return () => {
      isMounted = false;
    };
  }, [language]);

  // Filter ideas based on category, status, and search term
  const filteredIdeasMemo = useMemo(() => {
    let filtered = ideas;

    if (selectedCategory !== 'All' && selectedCategory !== '全部') {
      filtered = filtered.filter(idea => idea.category === selectedCategory);
    }

    if (selectedStatus !== 'All' && selectedStatus !== '全部') {
      // Map Chinese status labels back to English status values
      let statusToMatch = selectedStatus;
      if (language === 'zh') {
        const statusMap: Record<string, string> = {
          '草案': 'draft',
          '假设': 'hypothesis',
          '实验中': 'experimenting',
          '验证中': 'validating',
          '已发表': 'published',
          '已结论': 'concluded'
        };
        statusToMatch = statusMap[selectedStatus] || selectedStatus;
      }
      filtered = filtered.filter(idea => idea.status === statusToMatch);
    }

    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      filtered = filtered.filter(idea => 
        idea.title.toLowerCase().includes(searchLower) ||
        idea.description.toLowerCase().includes(searchLower) ||
        idea.tags.some(tag => tag.toLowerCase().includes(searchLower))
      );
    }

    return filtered;
  }, [ideas, selectedCategory, selectedStatus, searchTerm, language]);

  useEffect(() => {
    setFilteredIdeas(filteredIdeasMemo);
  }, [filteredIdeasMemo]);

  const categories = useMemo(() => {
    const allCategories = Array.from(new Set(ideas.map(idea => idea.category)));
    return [language === 'en' ? 'All' : '全部', ...allCategories];
  }, [ideas, language]);

  const statuses = useMemo(() => {
    const statusLabels = ['All', 'draft', 'hypothesis', 'experimenting', 'validating', 'published', 'concluded'];
    return statusLabels.map(status => {
      if (status === 'All') {
        return language === 'en' ? 'All' : '全部';
      }
      if (language === 'zh') {
        switch (status) {
          case 'draft': return '草案';
          case 'hypothesis': return '假设';
          case 'experimenting': return '实验中';
          case 'validating': return '验证中';
          case 'published': return '已发表';
          case 'concluded': return '已结论';
          default: return status;
        }
      }
      return status;
    });
  }, [language]);

  const handleIdeaView = useCallback((idea: IdeaData) => {
    // Navigate to idea detail page
    navigate(`/ideas/${idea.id}`);
  }, [navigate]);

  const handleSearchChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center ">
        <motion.div
          className="text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          role="status"
          aria-live="polite"
        >
          <Lightbulb 
            size={48} 
            className="mx-auto mb-4 animate-pulse text-theme-accent"
          />
          <p className="text-theme-secondary">
            {language === 'en' ? 'Loading ideas...' : '加载想法中...'}
          </p>
        </motion.div>
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
            {language === 'en' ? 'Error Loading Ideas' : '加载想法出错'}
          </h2>
          <p className="text-theme-secondary">{error}</p>
        </motion.div>
      </div>
    );
  }

  return (
    <motion.div
      className="min-h-screen py-20 "
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-5xl md:text-6xl font-bold mb-6 text-theme-primary">
            {language === 'en' ? 'Ideas' : '想法'}
          </h1>
          <p className="text-xl max-w-3xl mx-auto text-theme-secondary">
            {language === 'en' 
              ? "A collection of my thoughts, concepts, and potential projects in various stages of development."
              : "我在各个开发阶段的想法、概念和潜在项目的集合。"
            }
          </p>
        </motion.div>

        {/* Search and Filters */}
        <motion.div
          className="mb-12 space-y-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          {/* Search Bar */}
          <div className="relative max-w-md mx-auto">
            <Search 
              size={20} 
              className="absolute left-4 top-1/2 transform -translate-y-1/2 text-theme-tertiary"
            />
            <input
              type="text"
              placeholder={language === 'en' ? 'Search ideas...' : '搜索想法...'}
              value={searchTerm}
              onChange={handleSearchChange}
              className="w-full pl-12 pr-4 py-3 rounded-xl text-base transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 input-theme ring-theme-primary ring-offset-theme-background"
              aria-label={language === 'en' ? 'Search ideas' : '搜索想法'}
            />
          </div>

          {/* Filter Chips */}
          <div className="flex flex-wrap justify-center gap-4">
            {/* Category Filters */}
            <div className="flex flex-wrap gap-2" role="group" aria-label="Category filters">
              <span className="text-sm font-medium px-2 py-1 text-theme-secondary">
                {language === 'en' ? 'Category:' : '分类：'}
              </span>
              {categories.map(category => (
                <FilterChip
                  key={category}
                  label={category}
                  active={selectedCategory === category}
                  onClick={() => setSelectedCategory(category)}
                />
              ))}
            </div>

            {/* Status Filters */}
            <div className="flex flex-wrap gap-2" role="group" aria-label="Status filters">
              <span className="text-sm font-medium px-2 py-1 text-theme-secondary">
                {language === 'en' ? 'Status:' : '状态：'}
              </span>
              {statuses.map(status => (
                <FilterChip
                  key={status}
                  label={status}
                  active={selectedStatus === status}
                  onClick={() => setSelectedStatus(status)}
                />
              ))}
            </div>
          </div>
        </motion.div>

        {/* Ideas Grid */}
        <AnimatePresence mode="wait">
          <motion.div
            key={`${selectedCategory}-${selectedStatus}-${searchTerm}`}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            {filteredIdeas.map((idea, index) => (
              <IdeaCard
                key={idea.id}
                idea={idea}
                index={index}
                onView={handleIdeaView}
              />
            ))}
          </motion.div>
        </AnimatePresence>

        {/* Empty State */}
        {filteredIdeas.length === 0 && !loading && (
          <motion.div
            className="text-center py-20"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            role="status"
          >
            <div className="w-24 h-24 mx-auto mb-6 rounded-full flex items-center justify-center empty-state-bg">
              <Lightbulb size={32} className="text-theme-secondary" />
            </div>
            <h3 className="text-xl font-semibold mb-2 text-theme-primary">
              {language === 'en' ? 'No ideas found' : '未找到想法'}
            </h3>
            <p className="text-theme-secondary">
              {language === 'en' 
                ? 'Try adjusting your filters or search terms.'
                : '尝试调整您的筛选器或搜索词。'
              }
            </p>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
};

export default IdeaPage; 