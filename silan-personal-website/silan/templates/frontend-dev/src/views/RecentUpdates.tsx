import React, { useState, useEffect, useMemo } from 'react';
import { motion } from 'framer-motion';
import { 
  Calendar, Clock, Filter, Eye, Star, Zap, BookOpen, 
  Briefcase, GraduationCap, FileText, Target, ArrowLeft
} from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useLanguage } from '../components/LanguageContext';
import { useTheme } from '../components/ThemeContext';
import { LoadingSpinner } from '../components/ui';
import { fetchResumeData } from '../api/home/resumeApi';

interface RecentItem {
  id: string;
  type: 'work' | 'education' | 'research' | 'publication' | 'project';
  title: string;
  description: string;
  date: string;
  tags: string[];
  status: 'active' | 'ongoing' | 'completed';
  priority: 'high' | 'medium' | 'low';
}

interface TimelineEntry {
  year: number;
  month: number;
  count: number;
  items: RecentItem[];
}

// Timeline Component
interface TimelineProps {
  data: RecentItem[];
  onTimeClick: (year: number, month?: number) => void;
  selectedTime: { year: number; month?: number } | null;
}

const Timeline: React.FC<TimelineProps> = ({ data, onTimeClick, selectedTime }) => {
  const { language } = useLanguage();

  // Group data by year and month
  const timelineData = useMemo(() => {
    const grouped: { [key: string]: TimelineEntry } = {};
    
    data.forEach(item => {
      const date = new Date(item.date);
      const year = date.getFullYear();
      const month = date.getMonth();
      const key = `${year}-${month}`;
      
      if (!grouped[key]) {
        grouped[key] = {
          year,
          month,
          count: 0,
          items: []
        };
      }
      
      grouped[key].count++;
      grouped[key].items.push(item);
    });

    return Object.values(grouped).sort((a, b) => {
      if (a.year !== b.year) return b.year - a.year; // Newest first
      return b.month - a.month;
    });
  }, [data]);

  const monthNames = language === 'en' 
    ? ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    : ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'];

  // Group by year for display
  const yearGroups = useMemo(() => {
    const groups: { [year: number]: TimelineEntry[] } = {};
    timelineData.forEach(entry => {
      if (!groups[entry.year]) {
        groups[entry.year] = [];
      }
      groups[entry.year].push(entry);
    });
    return groups;
  }, [timelineData]);

  return (
    <div className="sticky top-8">
      <div className="p-3 xs:p-4 rounded-lg xs:rounded-xl bg-theme-surface-elevated border border-theme-border">
        <h3 className="font-semibold text-theme-primary mb-3 xs:mb-4 flex items-center gap-2 text-sm xs:text-base">
          <Clock size={16} className="xs:w-4 xs:h-4 sm:w-5 sm:h-5" />
          {language === 'en' ? 'Timeline' : '时间线'}
        </h3>
        
        <div className="space-y-2 xs:space-y-3 max-h-96 overflow-y-auto">
          {Object.entries(yearGroups)
            .sort(([a], [b]) => parseInt(b) - parseInt(a))
            .map(([year, entries]) => (
            <div key={year} className="space-y-1 xs:space-y-2">
              {/* Year Header */}
              <button
                onClick={() => onTimeClick(parseInt(year))}
                className={`w-full text-left px-2 xs:px-3 py-1.5 xs:py-2 rounded-lg transition-colors min-h-[44px] text-sm xs:text-base ${
                  selectedTime?.year === parseInt(year) && !selectedTime.month
                    ? 'bg-theme-primary text-white'
                    : 'hover:bg-theme-surface-tertiary text-theme-primary'
                }`}
              >
                <div className="flex justify-between items-center">
                  <span className="font-medium">{year}</span>
                  <span className="text-xs text-theme-secondary">
                    {entries.reduce((sum, entry) => sum + entry.count, 0)} updates
                  </span>
                </div>
              </button>
              
              {/* Months */}
              <div className="ml-2 xs:ml-4 space-y-1">
                {entries.map(entry => (
                  <button
                    key={`${entry.year}-${entry.month}`}
                    onClick={() => onTimeClick(entry.year, entry.month)}
                    className={`w-full text-left px-2 xs:px-3 py-1 rounded text-xs xs:text-sm transition-colors min-h-[40px] ${
                      selectedTime?.year === entry.year && selectedTime.month === entry.month
                        ? 'bg-theme-accent text-white'
                        : 'hover:bg-theme-surface text-theme-secondary'
                    }`}
                  >
                    <div className="flex justify-between items-center">
                      <span>{monthNames[entry.month]}</span>
                      <span className="text-xs">
                        {entry.count}
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
        
        {/* Reset Button */}
        {selectedTime && (
          <button
            onClick={() => onTimeClick(-1)} // Special value to reset
            className="w-full mt-2 xs:mt-3 px-2 xs:px-3 py-1.5 xs:py-2 text-xs xs:text-sm text-theme-secondary hover:text-theme-primary hover:bg-theme-surface-tertiary rounded-lg transition-colors min-h-[44px]"
          >
            {language === 'en' ? 'Show All' : '显示全部'}
          </button>
        )}
      </div>
    </div>
  );
};

const RecentUpdates: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [recentData, setRecentData] = useState<RecentItem[]>([]);
  const [filter, setFilter] = useState<string>('all');
  const [selectedTime, setSelectedTime] = useState<{ year: number; month?: number } | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const { colors } = useTheme();
  const { language } = useLanguage();
  const { t } = useTranslation();

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

  // Load recent data
  useEffect(() => {
    let isMounted = true;
    
    const loadRecentData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const data = await fetchResumeData(language);
        
        if (isMounted && data.sections.recent) {
          setRecentData(data.sections.recent.content);
          setLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          setError(t('resume.failed_to_load'));
          setLoading(false);
        }
      }
    };

    loadRecentData();

    return () => {
      isMounted = false;
    };
  }, [language, t]);

  // Helper function to get relative time
  const getRelativeTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    const diffMonths = Math.floor(diffDays / 30);
    const diffYears = Math.floor(diffDays / 365);

    if (diffYears > 0) {
      return t('resume.years_ago', { years: diffYears });
    } else if (diffMonths > 0) {
      return t('resume.months_ago', { months: diffMonths });
    } else {
      return t('resume.days_ago', { days: diffDays });
    }
  };

  // Type icon mapping
  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'work': return <Briefcase size={16} className="xs:w-4 xs:h-4 sm:w-5 sm:h-5" />;
      case 'education': return <GraduationCap size={16} className="xs:w-4 xs:h-4 sm:w-5 sm:h-5" />;
      case 'research': return <BookOpen size={16} className="xs:w-4 xs:h-4 sm:w-5 sm:h-5" />;
      case 'publication': return <FileText size={16} className="xs:w-4 xs:h-4 sm:w-5 sm:h-5" />;
      case 'project': return <Target size={16} className="xs:w-4 xs:h-4 sm:w-5 sm:h-5" />;
      default: return <Star size={16} className="xs:w-4 xs:h-4 sm:w-5 sm:h-5" />;
    }
  };

  // Status color mapping
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-600 bg-green-50 border-green-200';
      case 'ongoing': return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'completed': return 'text-gray-600 bg-gray-50 border-gray-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  // Priority indicator
  const getPriorityIndicator = (priority: string) => {
    switch (priority) {
      case 'high': return <Zap size={12} className="xs:w-3 xs:h-3 sm:w-4 sm:h-4 text-red-500" />;
      case 'medium': return <Clock size={12} className="xs:w-3 xs:h-3 sm:w-4 sm:h-4 text-yellow-500" />;
      case 'low': return <Eye size={12} className="xs:w-3 xs:h-3 sm:w-4 sm:h-4 text-gray-400" />;
      default: return null;
    }
  };

  // Filter data by type and time
  const filteredData = useMemo(() => {
    let filtered = filter === 'all' ? recentData : recentData.filter(item => item.type === filter);
    
    // Apply time filter
    if (selectedTime) {
      filtered = filtered.filter(item => {
        const date = new Date(item.date);
        const year = date.getFullYear();
        const month = date.getMonth();
        
        if (selectedTime.month !== undefined) {
          return year === selectedTime.year && month === selectedTime.month;
        } else {
          return year === selectedTime.year;
        }
      });
    }
    
    return filtered;
  }, [recentData, filter, selectedTime]);

  const filterTypes = ['all', 'work', 'education', 'research', 'publication', 'project'];

  const handleBack = () => {
    window.history.back();
  };

  const handleTimeClick = (year: number, month?: number) => {
    if (year === -1) {
      setSelectedTime(null); // Reset
    } else {
      setSelectedTime({ year, month });
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
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
      <div className="min-h-screen flex items-center justify-center">
        <motion.div
          className="text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          role="alert"
        >
          <h2 className="text-lg xs:text-xl font-semibold mb-2 text-theme-primary">
            {t('resume.error_loading')}
          </h2>
          <p className="text-theme-secondary text-sm xs:text-base">{error}</p>
        </motion.div>
      </div>
    );
  }

  return (
    <motion.div
      className="min-h-screen py-4 xs:py-6 sm:py-8"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="max-w-7xl mx-auto px-3 xs:px-4 sm:px-6">
        {/* Header */}
        <motion.div
          className="mb-6 xs:mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <button
            onClick={handleBack}
            className="inline-flex items-center gap-1.5 xs:gap-2 mb-3 xs:mb-4 text-theme-secondary hover:text-theme-primary transition-colors min-h-[44px] px-2 py-2 rounded-lg text-sm xs:text-base"
          >
            <ArrowLeft size={16} className="xs:w-4 xs:h-4 sm:w-5 sm:h-5" />
            {language === 'en' ? 'Back to Resume' : '返回简历'}
          </button>
          
          <h1 className="text-2xl xs:text-3xl sm:text-4xl font-bold text-theme-primary flex items-center gap-2 xs:gap-3 mb-2">
            <Calendar size={24} className="xs:w-6 xs:h-6 sm:w-8 sm:h-8" />
            {t('resume.recent_updates')}
          </h1>
          <p className="text-theme-secondary text-sm xs:text-base">
            {language === 'en' 
              ? 'A complete timeline of my latest activities and achievements'
              : '我最新活动和成就的完整时间线'
            }
          </p>
        </motion.div>

        {/* Main Content - Responsive Layout */}
        <div className="grid grid-cols-1 xl:grid-cols-4 gap-4 xs:gap-6 sm:gap-8">
          {/* Left Column - Main Content */}
          <div className="xl:col-span-3 space-y-4 xs:space-y-6">
            {/* Filter Controls */}
            <motion.div
              className="p-3 xs:p-4 sm:p-6 rounded-lg xs:rounded-xl bg-theme-surface-elevated border border-theme-border"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <div className="flex items-center gap-2 xs:gap-3 flex-wrap mb-3 xs:mb-4">
                <span className="text-xs xs:text-sm text-theme-secondary flex items-center gap-1 xs:gap-2">
                  <Filter size={12} className="xs:w-3 xs:h-3 sm:w-4 sm:h-4" />
                  {t('resume.filter_by_type')}:
                </span>
              </div>
              
              {/* Filter Buttons - Responsive Grid */}
              <div className="grid grid-cols-2 xs:grid-cols-3 sm:flex sm:flex-wrap gap-2 xs:gap-3">
                {filterTypes.map((type) => (
                  <button
                    key={type}
                    onClick={() => setFilter(type)}
                    className={`px-3 xs:px-4 py-2 xs:py-2.5 text-xs xs:text-sm rounded-lg transition-colors duration-200 min-h-[44px] font-medium ${
                      filter === type
                        ? 'bg-theme-primary text-white'
                        : 'bg-theme-surface text-theme-secondary hover:bg-theme-surface-tertiary'
                    }`}
                  >
                    {type === 'all' ? t('resume.all_types') : t(`resume.${type}`)}
                  </button>
                ))}
              </div>
              
              <div className="mt-3 xs:mt-4 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2">
                <div className="text-xs xs:text-sm text-theme-tertiary">
                  {language === 'en' 
                    ? `Showing ${filteredData.length} of ${recentData.length} updates`
                    : `显示 ${filteredData.length} / ${recentData.length} 条更新`
                  }
                  {selectedTime && (
                    <span className="ml-2 px-2 py-0.5 xs:py-1 bg-theme-accent/20 text-theme-accent rounded text-xs">
                      {selectedTime.month !== undefined 
                        ? `${selectedTime.year}/${selectedTime.month + 1}`
                        : selectedTime.year
                      }
                    </span>
                  )}
                </div>
                
                {/* Mobile Timeline Toggle - Show only on small screens */}
                <div className="xl:hidden">
                  {selectedTime && (
                    <button
                      onClick={() => setSelectedTime(null)}
                      className="text-xs xs:text-sm px-3 py-1.5 xs:py-2 bg-theme-surface-tertiary text-theme-secondary hover:text-theme-primary rounded-lg transition-colors min-h-[40px]"
                    >
                      {language === 'en' ? 'Clear Time Filter' : '清除时间筛选'}
                    </button>
                  )}
                </div>
              </div>
            </motion.div>

            {/* Recent Items */}
            <motion.div
              className="space-y-4 xs:space-y-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              {filteredData.map((item, index) => (
                <motion.div
                  key={item.id}
                  className="p-4 xs:p-5 sm:p-6 rounded-lg xs:rounded-xl border border-theme-surface-tertiary bg-theme-surface-elevated hover:bg-theme-card transition-colors duration-200"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                >
                  <div className="flex items-start gap-3 xs:gap-4">
                    {/* Type Icon */}
                    <div className="flex-shrink-0 p-2 xs:p-2.5 sm:p-3 rounded-lg xs:rounded-xl bg-theme-primary/10 text-theme-primary">
                      {getTypeIcon(item.type)}
                    </div>

                    <div className="flex-1 min-w-0">
                      {/* Header */}
                      <div className="flex items-start justify-between gap-3 xs:gap-4 mb-2 xs:mb-3">
                        <div className="min-w-0 flex-1">
                          <h3 className="text-base xs:text-lg sm:text-xl font-semibold text-theme-primary mb-1 leading-tight">
                            {item.title}
                          </h3>
                          <div className="flex items-center gap-2 xs:gap-3 text-xs xs:text-sm">
                            <span className="text-theme-secondary">
                              {getRelativeTime(item.date)}
                            </span>
                            <span className="text-theme-tertiary">•</span>
                            <span className="text-theme-accent">
                              {t(`resume.${item.type}`)}
                            </span>
                          </div>
                        </div>
                        
                        <div className="flex flex-col xs:flex-row items-end xs:items-center gap-1 xs:gap-2 flex-shrink-0">
                          {getPriorityIndicator(item.priority)}
                          <span className={`px-2 xs:px-3 py-0.5 xs:py-1 text-xs rounded-full border ${getStatusColor(item.status)}`}>
                            {t(`resume.status.${item.status}`)}
                          </span>
                        </div>
                      </div>

                      {/* Description */}
                      <p className="text-theme-secondary mb-3 xs:mb-4 leading-relaxed text-sm xs:text-base">
                        {item.description}
                      </p>

                      {/* Tags */}
                      <div className="flex flex-wrap gap-1.5 xs:gap-2">
                        {item.tags.map((tag, tagIndex) => (
                          <span
                            key={tagIndex}
                            className="px-2 xs:px-3 py-1 text-xs xs:text-sm rounded-md xs:rounded-lg bg-theme-surface-tertiary text-theme-tertiary border border-theme-border"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </motion.div>

            {/* Empty State */}
            {filteredData.length === 0 && (
              <motion.div
                className="text-center py-8 xs:py-12"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.5 }}
              >
                <Calendar size={40} className="xs:w-10 xs:h-10 sm:w-12 sm:h-12 mx-auto mb-3 xs:mb-4 text-theme-tertiary" />
                <h3 className="text-base xs:text-lg font-semibold text-theme-primary mb-2">
                  {language === 'en' ? 'No updates found' : '没有找到更新'}
                </h3>
                <p className="text-theme-secondary text-sm xs:text-base">
                  {language === 'en' 
                    ? 'Try adjusting your filter to see more updates'
                    : '尝试调整筛选条件以查看更多更新'
                  }
                </p>
              </motion.div>
            )}
          </div>

          {/* Right Column - Timeline (Hidden on narrow screens) */}
          <div className="hidden xl:block xl:col-span-1">
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.6 }}
            >
              <Timeline 
                data={recentData} 
                onTimeClick={handleTimeClick}
                selectedTime={selectedTime}
              />
            </motion.div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default RecentUpdates; 