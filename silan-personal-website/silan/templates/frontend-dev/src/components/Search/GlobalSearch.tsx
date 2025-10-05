import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, X, Loader2, FileText, Lightbulb, Briefcase, ArrowRight } from 'lucide-react';
import { useLanguage } from '../LanguageContext';
import { useTheme } from '../ThemeContext';
import { globalSearch, type GlobalSearchResponse } from '../../api/search/searchApi';
import { debounce } from 'lodash';

interface GlobalSearchProps {
  isOpen: boolean;
  onClose: () => void;
  initialQuery?: string;
}

const GlobalSearch: React.FC<GlobalSearchProps> = ({ isOpen, onClose, initialQuery = '' }) => {
  const { language } = useLanguage();
  const { colors } = useTheme();
  const navigate = useNavigate();
  const [query, setQuery] = useState(initialQuery);
  const [results, setResults] = useState<GlobalSearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const modalRef = useRef<HTMLDivElement>(null);

  // Focus input when modal opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  // Close on ESC key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // Close when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (modalRef.current && !modalRef.current.contains(e.target as Node)) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen, onClose]);

  // Debounced search function
  const performSearch = useCallback(
    debounce(async (searchQuery: string) => {
      if (!searchQuery.trim()) {
        setResults(null);
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      try {
        const response = await globalSearch({ query: searchQuery, limit: 5 }, language);
        setResults(response);
      } catch (error) {
        console.error('Search error:', error);
        setResults(null);
      } finally {
        setIsLoading(false);
      }
    }, 300),
    [language]
  );

  // Trigger search when query changes
  useEffect(() => {
    performSearch(query);
  }, [query, performSearch]);

  const handleResultClick = (type: 'blog' | 'project' | 'idea', id: string) => {
    const paths = {
      blog: `/blog/${id}`,
      project: `/projects/${id}`,
      idea: `/ideas/${id}`
    };
    navigate(paths[type]);
    onClose();
  };

  const handleViewAllResults = () => {
    if (query.trim()) {
      navigate(`/search?q=${encodeURIComponent(query)}`);
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4"
        style={{ backgroundColor: 'rgba(0, 0, 0, 0.5)' }}
      >
        <motion.div
          ref={modalRef}
          initial={{ scale: 0.9, y: -20 }}
          animate={{ scale: 1, y: 0 }}
          exit={{ scale: 0.9, y: -20 }}
          className="w-full max-w-2xl rounded-2xl shadow-2xl overflow-hidden"
          style={{ backgroundColor: colors.background }}
        >
          {/* Search Input */}
          <div className="p-4 border-b" style={{ borderColor: colors.cardBorder }}>
            <div className="relative">
              <Search
                size={20}
                className="absolute left-4 top-1/2 transform -translate-y-1/2"
                style={{ color: colors.textTertiary }}
              />
              <input
                ref={inputRef}
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={language === 'en' ? 'Search blogs, projects, ideas...' : '搜索博客、项目、想法...'}
                className="w-full pl-12 pr-12 py-3 rounded-lg text-base focus:outline-none"
                style={{
                  backgroundColor: colors.surface,
                  color: colors.textPrimary,
                  border: `1px solid ${colors.cardBorder}`
                }}
              />
              {isLoading && (
                <Loader2
                  size={20}
                  className="absolute right-4 top-1/2 transform -translate-y-1/2 animate-spin"
                  style={{ color: colors.primary }}
                />
              )}
              {!isLoading && query && (
                <button
                  onClick={() => setQuery('')}
                  className="absolute right-4 top-1/2 transform -translate-y-1/2 p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
                  style={{ color: colors.textTertiary }}
                >
                  <X size={16} />
                </button>
              )}
            </div>
          </div>

          {/* Search Results */}
          <div className="max-h-96 overflow-y-auto p-4">
            {!query && (
              <div className="text-center py-12" style={{ color: colors.textSecondary }}>
                <Search size={48} className="mx-auto mb-4 opacity-30" />
                <p>{language === 'en' ? 'Start typing to search' : '开始输入以搜索'}</p>
              </div>
            )}

            {query && !isLoading && results && results.total === 0 && (
              <div className="text-center py-12" style={{ color: colors.textSecondary }}>
                <Search size={48} className="mx-auto mb-4 opacity-30" />
                <p>{language === 'en' ? 'No results found' : '未找到结果'}</p>
              </div>
            )}

            {results && results.total > 0 && (
              <div className="space-y-6">
                {/* Blog Results */}
                {results.blogs.length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold mb-2 flex items-center" style={{ color: colors.textSecondary }}>
                      <FileText size={16} className="mr-2" />
                      {language === 'en' ? 'Blogs' : '博客'} ({results.blogs.length})
                    </h3>
                    <div className="space-y-2">
                      {results.blogs.map((blog) => (
                        <motion.div
                          key={blog.id}
                          whileHover={{ scale: 1.02 }}
                          onClick={() => handleResultClick('blog', blog.slug || blog.id)}
                          className="p-3 rounded-lg cursor-pointer transition-colors"
                          style={{ backgroundColor: colors.surface }}
                        >
                          <h4 className="font-medium mb-1" style={{ color: colors.textPrimary }}>
                            {language === 'en' ? blog.title : blog.titleZh || blog.title}
                          </h4>
                          <p className="text-sm line-clamp-2" style={{ color: colors.textSecondary }}>
                            {language === 'en' ? (blog.summary || '') : (blog.summaryZh || blog.summary || '')}
                          </p>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Project Results */}
                {results.projects.length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold mb-2 flex items-center" style={{ color: colors.textSecondary }}>
                      <Briefcase size={16} className="mr-2" />
                      {language === 'en' ? 'Projects' : '项目'} ({results.projects.length})
                    </h3>
                    <div className="space-y-2">
                      {results.projects.map((project) => (
                        <motion.div
                          key={project.id}
                          whileHover={{ scale: 1.02 }}
                          onClick={() => handleResultClick('project', project.id)}
                          className="p-3 rounded-lg cursor-pointer transition-colors"
                          style={{ backgroundColor: colors.surface }}
                        >
                          <h4 className="font-medium mb-1" style={{ color: colors.textPrimary }}>
                            {project.title}
                          </h4>
                          <p className="text-sm line-clamp-2" style={{ color: colors.textSecondary }}>
                            {project.description}
                          </p>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Idea Results */}
                {results.ideas.length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold mb-2 flex items-center" style={{ color: colors.textSecondary }}>
                      <Lightbulb size={16} className="mr-2" />
                      {language === 'en' ? 'Ideas' : '想法'} ({results.ideas.length})
                    </h3>
                    <div className="space-y-2">
                      {results.ideas.map((idea) => (
                        <motion.div
                          key={idea.id}
                          whileHover={{ scale: 1.02 }}
                          onClick={() => handleResultClick('idea', idea.id)}
                          className="p-3 rounded-lg cursor-pointer transition-colors"
                          style={{ backgroundColor: colors.surface }}
                        >
                          <h4 className="font-medium mb-1" style={{ color: colors.textPrimary }}>
                            {idea.title}
                          </h4>
                          <p className="text-sm line-clamp-2" style={{ color: colors.textSecondary }}>
                            {idea.description}
                          </p>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                )}

                {/* View All Results Button */}
                <button
                  onClick={handleViewAllResults}
                  className="w-full py-3 rounded-lg font-medium flex items-center justify-center space-x-2 transition-colors"
                  style={{
                    backgroundColor: colors.primary,
                    color: '#ffffff'
                  }}
                >
                  <span>{language === 'en' ? 'View All Results' : '查看所有结果'}</span>
                  <ArrowRight size={16} />
                </button>
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default GlobalSearch;
