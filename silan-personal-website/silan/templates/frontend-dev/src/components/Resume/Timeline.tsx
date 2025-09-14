import React from 'react';
import { motion } from 'framer-motion';

interface TimelineItem {
  title: string;
  subtitle: string;
  date: string;
  details: string[];
  logo?: string;
  website?: string;
  location?: string;
}

interface TimelineProps {
  items: TimelineItem[];
  variant?: 'primary' | 'secondary' | 'accent';
}

const Timeline: React.FC<TimelineProps> = ({ items }) => {

  return (
    <div className="space-y-6">
      {items.map((item, index) => (
        <motion.div
          key={index}
          className="relative pl-2"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: index * 0.1 }}
        >
          {/* Content */}
          <div className="space-y-3">
            <div className="flex items-start space-x-3">
              {/* Company/School Logo */}
              {item.logo && (
                <div className="flex-shrink-0 w-12 h-12 rounded-lg overflow-hidden shadow-sm border border-gray-200">
                  <img 
                    src={item.logo} 
                    alt={`${item.subtitle} logo`}
                    className="w-full h-full object-contain p-1"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none';
                    }}
                  />
                </div>
              )}
              
              <div className="flex-1 min-w-0">
                <h4 className="text-lg font-semibold text-theme-primary mb-1">
                  {item.title}
                </h4>
                <div className="flex flex-wrap items-center gap-2 text-sm">
                  {item.website ? (
                    <a 
                      href={item.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-medium text-theme-accent hover:text-theme-primary transition-colors hover:underline"
                    >
                      {item.subtitle}
                    </a>
                  ) : (
                    <span className="font-medium text-theme-accent">{item.subtitle}</span>
                  )}
                  
                  <span className="w-1 h-1 rounded-full bg-theme-secondary" />
                  <span className="text-theme-secondary">{item.date}</span>
                  
                  {item.location && (
                    <>
                      <span className="w-1 h-1 rounded-full bg-theme-secondary" />
                      <span className="text-theme-secondary text-xs">{item.location}</span>
                    </>
                  )}
                </div>
              </div>
            </div>
            
            {item.details && Array.isArray(item.details) && item.details.length > 0 && (
              <div className="bg-theme-surface-elevated rounded-lg p-4 border border-theme-card/50">
                <ul className="space-y-2">
                  {item.details.map((detail, i) => (
                    <li key={i} className="flex items-start space-x-3">
                      <div className="w-1.5 h-1.5 rounded-full bg-theme-accent mt-2 flex-shrink-0" />
                      <span className="text-theme-secondary text-sm leading-relaxed">
                        {detail}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </motion.div>
      ))}
    </div>
  );
};

export default Timeline; 