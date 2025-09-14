import React, { ReactNode, useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import TopNavigation from './TopNavigation';
import { useTheme } from '../components/ThemeContext';
import SimpleBackground from '../components/NeuralBackground';
interface MainLayoutProps {
  children: ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const { colors } = useTheme();
  const [scrollProgress, setScrollProgress] = useState(0);

  // Track scroll progress
  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
      const progress = scrollHeight > 0 ? (scrollTop / scrollHeight) * 100 : 0;
      setScrollProgress(Math.min(100, Math.max(0, progress)));
    };

    window.addEventListener('scroll', handleScroll);
    handleScroll(); // Initial call

    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Simple Clean Background */}
      <SimpleBackground />
      
      {/* Global Reading Progress Bar */}
      <div className="fixed top-0 left-0 z-50 w-full h-1">
        <div 
          className="h-full transition-all duration-300 ease-out"
          style={{ 
            width: `${scrollProgress}%`,
            backgroundColor: colors.primary
          }}
        />
      </div>
      
      {/* Navigation */}
      <div className="relative z-20">
        <TopNavigation />
      </div>

      {/* Main Content Area */}
      <motion.main
        className="relative z-10 pt-16 xs:pt-18 sm:pt-20" // Add top padding to account for fixed navbar
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ 
          duration: 0.5, 
          ease: [0.25, 0.1, 0.25, 1] // Smooth ease
        }}
      >
        {/* Content wrapper with proper spacing and mobile optimization */}
        <div className="mx-auto px-3 xs:px-4 sm:px-6 lg:px-8">
          <div className="relative pt-4 xs:pt-6 sm:pt-8 md:pt-12 pb-8 xs:pb-12 sm:pb-16 md:pb-24">
            {children}
          </div>
        </div>
      </motion.main>
    </div>
  );
};

export default MainLayout; 