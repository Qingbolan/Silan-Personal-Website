import React, { useState, useEffect, useMemo, ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Home,
  Briefcase,
  Lightbulb,
  BookOpen,
  Mail,
  Menu,
  X,
  Globe,
  Sun,
  Moon,
  Search,
} from 'lucide-react';
import { useLanguage } from '../components/LanguageContext';
import { useTheme } from '../components/ThemeContext';

interface NavItemData {
  key: string;
  icon: ReactNode;
  label: string;
}

interface NavItemProps {
  to: string;
  icon: ReactNode;
  label: string;
  active: boolean;
  onClick?: () => void;
  isMobile?: boolean;
}

const NAV_ITEMS = (language: string): NavItemData[] => [
  { key: '/', icon: <Home size={16} className="xs:w-4 xs:h-4 sm:w-5 sm:h-5" />, label: language === 'en' ? 'Home' : '主页' },
  { key: '/projects', icon: <Briefcase size={16} className="xs:w-4 xs:h-4 sm:w-5 sm:h-5" />, label: language === 'en' ? 'Projects' : '项目' },
  { key: '/ideas', icon: <Lightbulb size={16} className="xs:w-4 xs:h-4 sm:w-5 sm:h-5" />, label: language === 'en' ? 'Ideas' : '想法' },
  { key: '/blog', icon: <BookOpen size={16} className="xs:w-4 xs:h-4 sm:w-5 sm:h-5" />, label: language === 'en' ? 'Blog' : '博客' },
  { key: '/contact', icon: <Mail size={16} className="xs:w-4 xs:h-4 sm:w-5 sm:h-5" />, label: language === 'en' ? 'Contact' : '联系' },
];

const NavItem: React.FC<NavItemProps> = ({ to, icon, label, active, onClick, isMobile = false }) => {
  const { colors } = useTheme();
  
  return (
    <Link
      to={to}
      onClick={onClick}
      className="relative group"
    >
      <motion.div
        className={`flex items-center justify-center xs:justify-start space-x-0 xs:space-x-2 sm:space-x-3 px-2 xs:px-3 sm:px-4 py-2 xs:py-2.5 sm:py-3 rounded-lg xs:rounded-xl font-medium transition-all duration-300 btn-touch ${
          isMobile 
            ? 'text-base xs:text-sm sm:text-base w-full min-h-[48px]' 
            : 'text-xs xs:text-sm min-h-[40px] xs:min-h-[44px]'
        }`}
        whileHover={{ scale: 1.02, y: -1 }}
        whileTap={{ scale: 0.98 }}
        style={{
          color: active ? colors.primary : colors.textSecondary,
          backgroundColor: 'transparent',
        }}
      >
        <motion.span 
          className="flex items-center justify-center"
          animate={{ 
            color: active ? colors.primary : colors.textSecondary,
            scale: active ? 1.1 : 1 
          }}
          transition={{ duration: 0.2 }}
        >
          {icon}
        </motion.span>
        <span className={isMobile ? 'block ml-2' : 'hidden xs:hidden sm:block'}>{label}</span>
      </motion.div>
      
      {active && (
        <motion.div
          className="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-1 h-1 rounded-full"
          style={{ backgroundColor: colors.primary }}
          layoutId="activeIndicator"
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ type: "spring", stiffness: 300, damping: 20 }}
        />
      )}
    </Link>
  );
};

const ThemeToggle: React.FC = () => {
  const { isDarkMode, toggleTheme, colors } = useTheme();
  
  return (
    <motion.button
      onClick={toggleTheme}
      className="p-2 xs:p-2.5 sm:p-3 rounded-lg xs:rounded-xl transition-all duration-300 relative overflow-hidden btn-touch flex items-center justify-center"
      style={{ 
        color: colors.textSecondary,
        backgroundColor: 'transparent'
      }}
      whileHover={{ 
        scale: 1.05,
        backgroundColor: `${colors.textSecondary}10`,
        boxShadow: `0 4px 15px ${colors.textSecondary}15`
      }}
      whileTap={{ scale: 0.95 }}
    >
      <AnimatePresence mode="wait">
        <motion.div
          key={isDarkMode ? 'sun' : 'moon'}
          initial={{ rotate: -180, opacity: 0 }}
          animate={{ rotate: 0, opacity: 1 }}
          exit={{ rotate: 180, opacity: 0 }}
          transition={{ duration: 0.3, ease: "easeInOut" }}
        >
          {isDarkMode ? <Sun size={16} className="xs:w-4 xs:h-4 sm:w-5 sm:h-5" /> : <Moon size={16} className="xs:w-4 xs:h-4 sm:w-5 sm:h-5" />}
        </motion.div>
      </AnimatePresence>
    </motion.button>
  );
};

const SearchBox: React.FC = () => {
  const { colors } = useTheme();
  const { language } = useLanguage();
  const [searchValue, setSearchValue] = useState('');
  const [isSearchFocused, setIsSearchFocused] = useState(false);
  const inputRef = React.useRef<HTMLInputElement>(null);

  // Keyboard shortcut for search
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);
  
  return (
    <motion.div
      className="relative hidden md:block"
      whileHover={{ scale: 1.01 }}
      transition={{ duration: 0.2 }}
    >
      <div className="relative">
        <Search 
          size={16} 
          className="absolute left-3 top-1/2 transform -translate-y-1/2 transition-colors duration-200" 
          style={{ 
            color: isSearchFocused ? colors.primary : colors.textTertiary 
          }}
        />
        <input
          ref={inputRef}
          type="text"
          value={searchValue}
          onChange={(e) => setSearchValue(e.target.value)}
          onFocus={() => setIsSearchFocused(true)}
          onBlur={() => setIsSearchFocused(false)}
          placeholder={language === 'en' ? 'Search...' : '搜索...'}
          className="w-48 lg:w-56 pl-10 pr-10 py-1.5 rounded-xl text-sm transition-all duration-300 focus:outline-none border"
          style={{
            backgroundColor: colors.surface,
            color: colors.textPrimary,
            borderColor: isSearchFocused ? colors.primary : colors.cardBorder,
            boxShadow: isSearchFocused 
              ? `0 0 0 3px ${colors.primary}15, 0 4px 12px ${colors.primary}10` 
              : `0 2px 4px ${colors.shadowSm}`
          }}
        />
        {searchValue && (
          <motion.button
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            onClick={() => setSearchValue('')}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200"
            style={{ color: colors.textTertiary }}
          >
            <X size={14} />
          </motion.button>
        )}
        
        {/* Search shortcut hint */}
        {!isSearchFocused && !searchValue && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center gap-1">
            <kbd 
              className="px-2 py-1 text-xs rounded border"
              style={{ 
                backgroundColor: colors.background,
                color: colors.textTertiary,
                borderColor: colors.cardBorder
              }}
            >
              {navigator.platform.includes('Mac') ? '⌘K' : 'Ctrl+K'}
            </kbd>
          </div>
        )}
      </div>
    </motion.div>
  );
};

const LanguageToggle: React.FC = () => {
  const { language, setLanguage } = useLanguage();
  const { colors } = useTheme();
  
  return (
    <motion.button
      onClick={() => setLanguage(language === 'en' ? 'zh' : 'en')}
      className="flex items-center justify-center xs:justify-start space-x-0 xs:space-x-1 sm:space-x-2 px-2 xs:px-3 py-2 xs:py-2.5 sm:py-3 font-medium rounded-lg xs:rounded-xl transition-all duration-300 text-xs xs:text-sm btn-touch"
      style={{ 
        color: colors.textSecondary,
        backgroundColor: 'transparent'
      }}
      whileHover={{ 
        scale: 1.05,
        backgroundColor: `${colors.textSecondary}10`,
        boxShadow: `0 4px 15px ${colors.textSecondary}15`
      }}
      whileTap={{ scale: 0.95 }}
    >
      <Globe size={14} className="xs:w-3.5 xs:h-3.5 sm:w-4 sm:h-4" />
      <span className="hidden xs:block font-semibold">
        {language === 'en' ? 'EN' : '中'}
      </span>
    </motion.button>
  );
};

const Logo: React.FC = () => {
  const { colors } = useTheme();
  
  return (
    <Link to="/" className="flex items-center space-x-2 xs:space-x-3 group">
      <motion.div
        className="relative flex items-center justify-center w-6 h-6 xs:w-9 xs:h-9 sm:w-10 sm:h-10 rounded-lg xs:rounded-xl overflow-hidden"
        style={{
          boxShadow: `0 4px 20px ${colors.primary}25`,
        }}
        whileHover={{ 
          scale: 1.05,
          boxShadow: `0 6px 25px ${colors.primary}35`,
        }}
        whileTap={{ scale: 0.95 }}
        transition={{ duration: 0.2 }}
      >
        <img src="/image.png" alt="Silan Hu" className="w-full h-full object-contain" />
        <motion.div
          className="absolute inset-0 bg-white opacity-0"
          whileHover={{ opacity: 0.1 }}
          transition={{ duration: 0.2 }}
        />
      </motion.div>
      <div className="hidden xs:block">
        <motion.div 
          className="text-lg text-nowrap font-bold tracking-tight leading-tight"
          style={{ color: colors.textPrimary }}
          whileHover={{ scale: 1.02 }}
          transition={{ duration: 0.2 }}
        >
          Silan Hu
        </motion.div>
        <div 
          className="text-[10px] text-nowrap tracking-wider uppercase opacity-60 leading-tight -mt-0.5" 
        >
          ZIYUN·2025
        </div>
      </div>
    </Link>
  );
};

const TopNavigation: React.FC = () => {
  const [open, setOpen] = useState<boolean>(false);
  // const [scrolled, setScrolled] = useState<boolean>(false);
  const { pathname } = useLocation();
  const { language } = useLanguage();
  const { colors } = useTheme();

  // Close mobile menu on route change
  useEffect(() => setOpen(false), [pathname]);

  const items = useMemo(() => NAV_ITEMS(language), [language]);
  
  const isItemActive = (currentPath: string, itemPath: string): boolean => {
    if (itemPath === '/') return currentPath === '/';
    return currentPath === itemPath || currentPath.startsWith(itemPath + '/');
  };

  return (
    <motion.nav
      className="fixed top-0 left-0 right-0 z-50 transition-all duration-300"
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
    >
      {/* Subtle gradient line at bottom */}
      <div 
        className="absolute bottom-0 left-0 right-0 h-px opacity-20"
      />
      
      <div className="mx-auto px-3 xs:px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 xs:h-18 sm:h-20">
          {/* Logo */}
          <Logo />
    
          {/* Right side - All controls and navigation */}
          <div className="flex items-center space-x-1 lg:space-x-2">
            {/* Search Box */}
            <SearchBox />

            {/* Desktop Navigation - Hide on mobile/tablet, show on desktop */}
            <div className="hidden lg:flex items-center space-x-1 xl:space-x-1">
              {items.map(item => (
                <NavItem
                  key={item.key}
                  to={item.key}
                  icon={item.icon}
                  label={item.label}
                  active={isItemActive(pathname, item.key)}
                />
              ))}
            </div>

            {/* Controls */}
            <div className="flex items-center space-x-1">
              <LanguageToggle />
              <ThemeToggle />
              
              {/* Mobile Menu Button - Show on tablet and smaller */}
              <motion.button
                className="lg:hidden p-2 xs:p-2.5 sm:p-3 rounded-lg xs:rounded-xl ml-1 xs:ml-2 relative overflow-hidden btn-touch flex items-center justify-center"
                onClick={() => setOpen(prev => !prev)}
                style={{ 
                  color: colors.textSecondary,
                  backgroundColor: 'transparent'
                }}
                whileHover={{ 
                  backgroundColor: `${colors.textSecondary}10`,
                  boxShadow: `0 4px 15px ${colors.textSecondary}15`
                }}
                whileTap={{ scale: 0.95 }}
              >
                <AnimatePresence mode="wait">
                  <motion.div
                    key={open ? 'close' : 'menu'}
                    initial={{ rotate: -90, opacity: 0 }}
                    animate={{ rotate: 0, opacity: 1 }}
                    exit={{ rotate: 90, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    {open ? <X size={20} className="xs:w-5 xs:h-5 sm:w-6 sm:h-6" /> : <Menu size={20} className="xs:w-5 xs:h-5 sm:w-6 sm:h-6" />}
                  </motion.div>
                </AnimatePresence>
              </motion.button>
            </div>
          </div>
        </div>

        {/* Mobile Menu */}
        <AnimatePresence>
          {open && (
            <motion.div
              className="lg:hidden overflow-hidden"
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3, ease: "easeInOut" }}
            >
              <div className="py-4 xs:py-6 space-y-1 xs:space-y-2">
                {/* Mobile Search */}
                <motion.div
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0, duration: 0.3 }}
                  className="md:hidden mb-4"
                >
                  <div className="relative">
                    <Search 
                      size={16} 
                      className="absolute left-3 top-1/2 transform -translate-y-1/2 transition-colors duration-200" 
                      style={{ color: colors.textTertiary }}
                    />
                    <input
                      type="text"
                      placeholder={language === 'en' ? 'Search...' : '搜索...'}
                      className="w-full pl-10 pr-4 py-3 rounded-xl text-sm transition-all duration-300 focus:outline-none border"
                      style={{
                        backgroundColor: colors.surface,
                        color: colors.textPrimary,
                        borderColor: colors.cardBorder
                      }}
                      onFocus={(e) => {
                        e.target.style.borderColor = colors.primary;
                        e.target.style.boxShadow = `0 0 0 3px ${colors.primary}15, 0 4px 12px ${colors.primary}10`;
                      }}
                      onBlur={(e) => {
                        e.target.style.borderColor = colors.cardBorder;
                        e.target.style.boxShadow = `0 2px 4px ${colors.shadowSm}`;
                      }}
                    />
                  </div>
                </motion.div>

                {items.map((item, index) => (
                  <motion.div
                    key={item.key}
                    initial={{ x: -20, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    transition={{ delay: (index + 1) * 0.1, duration: 0.3 }}
                  >
                    <NavItem
                      to={item.key}
                      icon={item.icon}
                      label={item.label}
                      active={isItemActive(pathname, item.key)}
                      onClick={() => setOpen(false)}
                      isMobile={true}
                    />
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.nav>
  );
};

export default TopNavigation; 