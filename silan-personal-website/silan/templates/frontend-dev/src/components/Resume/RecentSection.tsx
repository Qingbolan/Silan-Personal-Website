import React, { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { 
  Clock, Filter, Eye, ChevronRight, Zap, 
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

export interface RecentItem {
  id: string;
  type: 'work' | 'education' | 'research' | 'publication' | 'project';
  title: string;
  description: string;
  date: string;
  tags: string[];
  status: 'active' | 'ongoing' | 'completed';
  priority: 'high' | 'medium' | 'low';
}

interface RecentSectionProps {
  data: RecentItem[];
  title: string;
  delay?: number;
}

const RecentSection: React.FC<RecentSectionProps> = ({ data, title, delay = 0 }) => {
  const { t } = useTranslation();
  const [filter, setFilter] = useState<string>('all');
  const navigate = useNavigate();

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
      case 'high': return <Zap size={12} className="text-red-500" />;
      case 'medium': return <Clock size={12} className="text-yellow-500" />;
      case 'low': return <Eye size={12} className="text-gray-400" />;
      default: return null;
    }
  };

  // Filter data - always show only the first item
  const filteredData = useMemo(() => {
    const filtered = filter === 'all' ? data : data.filter(item => item.type === filter);
    return filtered.slice(0, 1);
  }, [data, filter]);

  const filterTypes = ['all', 'work', 'education', 'research', 'publication', 'project'];

  const handleViewMore = () => {
    // Navigate to recent updates page using React Router
    navigate('/recent-updates');
  };

  return (
    <motion.section
      className="p-4 xs:p-6 sm:p-8 rounded-xl xs:rounded-2xl border border-theme-border card-mobile"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
    >
      {/* Header with Filter */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4 xs:mb-6 gap-3 xs:gap-4">
        <h3 className="text-lg xs:text-xl sm:text-2xl font-bold text-theme-primary flex items-center gap-2">
          {title}
        </h3>
        
        {/* Filter Controls */}
        <div className="flex items-center gap-1.5 xs:gap-2 flex-wrap">
          <span className="text-xs xs:text-sm text-theme-secondary flex items-center gap-1">
            <Filter size={12} className="w-3 h-3 xs:w-3.5 xs:h-3.5" />
            {t('resume.filter_by_type')}:
          </span>
          {filterTypes.map((type) => (
            <button
              key={type}
              onClick={() => setFilter(type)}
              className={`px-2 xs:px-3 py-1 xs:py-1.5 text-xs xs:text-sm rounded-full transition-colors duration-200 btn-touch ${
                filter === type
                  ? 'bg-theme-primary text-white'
                  : 'bg-theme-surface-elevated text-theme-secondary hover:bg-theme-surface-tertiary'
              }`}
            >
              {type === 'all' ? t('resume.all_types') : t(`resume.${type}`)}
            </button>
          ))}
        </div>
      </div>

      {/* Recent Items */}
      <div className="space-y-2 xs:space-y-3">
        {filteredData.map((item: RecentItem, index: number) => (
          <motion.div
            key={item.id}
            className="p-3 xs:p-4 rounded-lg border border-theme-surface-tertiary bg-theme-surface-elevated hover:bg-theme-card transition-colors duration-200"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
          >
            <div className="flex items-start gap-2 xs:gap-3">
              <div className="flex-1 min-w-0">
                {/* Header */}
                <div className="flex items-start justify-between gap-2 xs:gap-4 mb-1.5 xs:mb-2">
                  <h4 className="font-semibold text-theme-primary text-sm xs:text-base">
                    {item.title}
                  </h4>
                  <div className="flex items-center gap-1 xs:gap-2">
                    <span className="w-3 h-3 xs:w-3.5 xs:h-3.5">{getPriorityIndicator(item.priority)}</span>
                    <span className="text-xs xs:text-sm text-theme-secondary whitespace-nowrap">
                      {getRelativeTime(item.date)}
                    </span>
                  </div>
                </div>

                {/* Description */}
                <p className="text-xs xs:text-sm text-theme-secondary mb-1.5 xs:mb-2 leading-relaxed">
                  {item.description}
                </p>

                {/* Footer */}
                <div className="flex flex-wrap items-center justify-between gap-1.5 xs:gap-2">
                  {/* Tags */}
                  <div className="flex flex-wrap gap-1">
                    {item.tags.slice(0, 2).map((tag: string, tagIndex: number) => (
                      <span
                        key={tagIndex}
                        className="px-1.5 xs:px-2 py-0.5 xs:py-1 text-xs rounded-md bg-theme-surface-tertiary text-theme-tertiary"
                      >
                        {tag}
                      </span>
                    ))}
                    {item.tags.length > 2 && (
                      <span className="text-xs text-theme-secondary">
                        +{item.tags.length - 2}
                      </span>
                    )}
                  </div>

                  {/* Status Badge */}
                  <span className={`px-1.5 xs:px-2 py-0.5 xs:py-1 text-xs rounded-full border ${getStatusColor(item.status)}`}>
                    {t(`resume.status.${item.status}`)}
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* View More Button - Always show if there's more than 1 item */}
      {data.length > 1 && (
        <div className="mt-3 xs:mt-4 text-center">
          <button
            onClick={handleViewMore}
            className="inline-flex items-center gap-1.5 xs:gap-2 px-3 xs:px-4 py-1.5 xs:py-2 text-xs xs:text-sm font-medium text-theme-primary hover:text-theme-accent transition-colors hover:bg-theme-surface-elevated rounded-lg btn-touch"
          >
            {t('resume.view_all')} ({data.length - 1} more)
            <ChevronRight size={14} className="w-3.5 h-3.5 xs:w-4 xs:h-4" />
          </button>
        </div>
      )}
    </motion.section>
  );
};

export default RecentSection; 