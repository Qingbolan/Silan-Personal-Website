import React, { useState, useMemo, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Clock, Filter, Eye, Zap, 
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import Markdown from '../ui/Markdown';
import { useTheme } from '../ThemeContext';

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
  const { colors } = useTheme();
  const listRef = useRef<HTMLDivElement | null>(null);
  const [isTruncated, setIsTruncated] = useState(false);
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
      case 'ongoing': return 'text-theme-600 bg-theme-50 border-theme-200';
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

  // Filter and sort data (newest first). Height will be limited by container.
  // Normalize types to a known set
  const normalizeType = (t: string): 'work' | 'education' | 'research' | 'publication' | 'project' | 'other' => {
    const s = (t || '').toLowerCase();
    if (['work', 'job', 'career'].includes(s)) return 'work';
    if (['education', 'school', 'study'].includes(s)) return 'education';
    if (['research', 'r&d', 'rd'].includes(s)) return 'research';
    if (['publication', 'paper', 'pub'].includes(s)) return 'publication';
    if (['project', 'projects', 'proj'].includes(s)) return 'project';
    return 'other';
  };

  const normalized = useMemo(() => data.map(item => ({ ...item, _type: normalizeType(item.type) })), [data]);

  const typeOrder: Array<'work' | 'education' | 'research' | 'publication' | 'project'> = [
    'work', 'education', 'research', 'publication', 'project'
  ];

  const availableTypes = useMemo(() => {
    const counts: Record<string, number> = {};
    normalized.forEach(i => { counts[i._type] = (counts[i._type] || 0) + 1; });
    return ['all', ...typeOrder.filter(t => (counts[t] || 0) > 0)];
  }, [normalized]);

  useEffect(() => {
    if (!availableTypes.includes(filter)) {
      setFilter('all');
    }
  }, [availableTypes, filter]);

  const filteredData = useMemo(() => {
    const source = filter === 'all' ? normalized : normalized.filter(item => item._type === filter);
    return [...source].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
  }, [normalized, filter]);

  // Detect if list is visually truncated by max-height
  useEffect(() => {
    const check = () => {
      const el = listRef.current;
      if (!el) return;
      setIsTruncated(el.scrollHeight > el.clientHeight + 2); // allow small rounding
    };
    check();
    window.addEventListener('resize', check);
    return () => window.removeEventListener('resize', check);
  }, [filteredData]);

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
          {availableTypes.map((type) => {
            const labelMap: Record<string, string> = {
              all: t('resume.all_types', { defaultValue: 'All Types' }),
              work: t('resume.work', { defaultValue: 'Work' }),
              education: t('resume.education', { defaultValue: 'Education' }),
              research: t('resume.research', { defaultValue: 'Research' }),
              publication: t('resume.publication', { defaultValue: 'Publication' }),
              project: t('resume.project', { defaultValue: 'Project' })
            };
            const label = labelMap[type] ?? type;
            return (
            <button
              key={type}
              onClick={() => setFilter(type)}
              className={`px-2 xs:px-3 py-1 xs:py-1.5 text-xs xs:text-sm rounded-full transition-colors duration-200 btn-touch ${
                filter === type
                  ? 'bg-theme-primary text-white'
                  : 'bg-theme-surface-elevated text-theme-secondary hover:bg-theme-surface-tertiary'
              }`}
            >
              {label}
            </button>
            );
          })}
        </div>
      </div>

      {/* Recent Items (show top N, limited height, gradient + CTA) */}
      <div className="relative" role="list" aria-label={t('resume.recent_updates', { defaultValue: 'Recent updates' })}>
        <div ref={listRef} className="space-y-2 xs:space-y-3 max-h-72 sm:max-h-80 lg:max-h-96 overflow-hidden">
          {filteredData.map((item: RecentItem, index: number) => (
          <motion.div
            key={item.id}
            className="p-3 xs:p-4 rounded-lg border border-theme-surface-tertiary bg-theme-surface-elevated hover:bg-theme-card transition-colors duration-200 cursor-pointer"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            role="link"
            tabIndex={0}
            onClick={() => navigate(`/recent-updates?id=${encodeURIComponent(item.id)}`)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                navigate(`/recent-updates?id=${encodeURIComponent(item.id)}`);
              }
            }}
            aria-label={`${t('resume.view_details', { defaultValue: 'View details' })}: ${item.title}`}
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

                {/* Description rendered as Markdown with theme-aware styles */}
                <Markdown className="text-xs xs:text-sm mb-1.5 xs:mb-2">{item.description}</Markdown>

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
        {/* Gradient overlay + CTA */}
        {isTruncated && (
          <>
            <div
              aria-hidden
              className="pointer-events-none absolute inset-x-0 bottom-0 h-16 sm:h-20"
              style={{
                background: `linear-gradient(180deg, rgba(0,0,0,0) 0%, ${colors.surfaceElevated}CC 60%, ${colors.surfaceElevated}FF 100%)`
              }}
            />
            <div className="absolute inset-x-0 bottom-2 flex justify-center">
              <button
                onClick={handleViewMore}
                className="inline-flex items-center gap-1.5 xs:gap-2 px-3 xs:px-4 py-1.5 xs:py-2 text-xs xs:text-sm font-medium text-theme-primary hover:text-white transition-colors rounded-lg btn-touch"
                style={{ backgroundColor: `${colors.primary}1A` }}
              >
                {t('resume.view_all', { defaultValue: 'Show More' })}
              </button>
            </div>
          </>
        )}
      </div>

      {/* View More Button - Always show if there's more than 1 item */}
      {/* Bottom CTA moved into gradient overlay */}
    </motion.section>
  );
};

export default RecentSection; 
