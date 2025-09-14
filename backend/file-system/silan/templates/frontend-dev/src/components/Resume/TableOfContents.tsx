import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface TOCItem {
  id: string;
  title: string;
  level: number;
}

interface TableOfContentsProps {
  sections: TOCItem[];
}

const TableOfContents: React.FC<TableOfContentsProps> = ({ sections }) => {
  const [activeSection, setActiveSection] = useState<string>('');
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveSection(entry.target.id);
          }
        });
      },
      {
        rootMargin: '-20% 0% -70% 0%',
        threshold: 0.1,
      }
    );

    // Observe all section elements
    sections.forEach((section) => {
      const element = document.getElementById(section.id);
      if (element) {
        observer.observe(element);
      }
    });

    // Show TOC after initial load
    const timer = setTimeout(() => setIsVisible(true), 1000);

    return () => {
      observer.disconnect();
      clearTimeout(timer);
    };
  }, [sections]);

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId);
    if (element) {
      const offsetTop = element.offsetTop - 100; // Account for header
      window.scrollTo({
        top: offsetTop,
        behavior: 'smooth',
      });
    }
  };

  if (!isVisible || sections.length === 0) return null;

  return (
    <motion.div
      className="fixed right-4 top-24 z-40 hidden lg:block"
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="bg-theme-surface/90 backdrop-blur-sm border border-theme-card/50 rounded-lg p-1.5 shadow-md w-32">
        {/* TOC Items */}
        <nav className="space-y-0.5">
          {sections.map((section) => {
            const isActive = activeSection === section.id;
            
            return (
              <button
                key={section.id}
                onClick={() => scrollToSection(section.id)}
                className={`group w-full text-left px-1.5 py-1 rounded transition-all duration-200 ${
                  isActive
                    ? 'bg-theme-primary/10 text-theme-primary'
                    : 'text-theme-secondary hover:text-theme-primary hover:bg-theme-hover'
                }`}
                title={section.title}
              >
                <div className="flex items-center space-x-1.5">
                  <div className={`w-0.5 h-2 rounded-full transition-colors duration-200 ${
                    isActive ? 'bg-theme-primary' : 'bg-theme-card/50'
                  }`} />
                  
                  <span className="text-xs truncate">
                    {section.title}
                  </span>
                </div>
              </button>
            );
          })}
        </nav>

        {/* Mini progress bar */}
        <div className="mt-1.5 pt-1.5 border-t border-theme-card/30">
          <div className="h-0.5 bg-theme-card/50 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-theme-primary rounded-full"
              initial={{ width: 0 }}
              animate={{ 
                width: `${((sections.findIndex(s => s.id === activeSection) + 1) / sections.length) * 100}%` 
              }}
              transition={{ duration: 0.3 }}
            />
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default TableOfContents; 