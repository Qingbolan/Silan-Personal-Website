import React, { useState, useEffect, useMemo, ReactNode, useCallback, useId } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence, useReducedMotion } from 'framer-motion';
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

const NavItem: React.FC<NavItemProps> = React.memo(({ to, icon, label, active, onClick, isMobile = false }) => {
  const { colors } = useTheme();
  const reduceMotion = useReducedMotion();
  
  return (
    <Link
      to={to}
      onClick={onClick}
      aria-current={active ? 'page' : undefined}
      className="relative group"
    >
      <motion.div
        className={`flex items-center justify-center xs:justify-start space-x-0 xs:space-x-2 sm:space-x-3 px-2 xs:px-3 sm:px-4 py-2 xs:py-2.5 sm:py-3 rounded-lg xs:rounded-xl ${active ? 'font-semibold' : 'font-medium'} transition-all duration-300 btn-touch ${
          isMobile 
            ? 'text-base xs:text-sm sm:text-base w-full min-h-[48px]' 
            : 'text-xs xs:text-sm min-h-[40px] xs:min-h-[44px]'
        }`}
        whileHover={reduceMotion ? undefined : { scale: 1.02, y: -1 }}
        whileTap={reduceMotion ? undefined : { scale: 0.98 }}
        style={{
          color: active ? colors.primary : colors.textSecondary,
          backgroundColor: active ? `${colors.primary}10` : 'transparent',
          boxShadow: active ? `0 4px 12px ${colors.primary}10` : 'none',
        }}
      >
        <motion.span 
          className="flex items-center justify-center"
          animate={reduceMotion ? undefined : { 
            color: active ? colors.primary : colors.textSecondary,
            scale: active ? 1.1 : 1 
          }}
          transition={reduceMotion ? undefined : { duration: 0.2 }}
        >
          {/* decorative icon */}
          {React.isValidElement(icon) ? React.cloneElement(icon as any, { 'aria-hidden': true, focusable: false }) : icon}
        </motion.span>
        <span className={isMobile ? 'block ml-2' : 'hidden xs:hidden sm:block'}>{label}</span>
      </motion.div>
      {/* Active dot indicator removed per request */}
    </Link>
  );
});

const ThemeToggle: React.FC = React.memo(() => {
  const { isDarkMode, toggleTheme, colors } = useTheme();
  const reduceMotion = useReducedMotion();
  
  return (
    <motion.button
      type="button"
      aria-label={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
      aria-pressed={isDarkMode}
      onClick={toggleTheme}
      className="p-2 xs:p-2.5 sm:p-3 rounded-lg xs:rounded-xl transition-all duration-300 relative overflow-hidden btn-touch flex items-center justify-center"
      style={{ 
        color: colors.textSecondary,
        backgroundColor: 'transparent'
      }}
      whileHover={reduceMotion ? undefined : { 
        scale: 1.05,
        backgroundColor: `${colors.textSecondary}10`,
        boxShadow: `0 4px 15px ${colors.textSecondary}15`
      }}
      whileTap={reduceMotion ? undefined : { scale: 0.95 }}
    >
      <AnimatePresence mode="wait">
        <motion.div
          key={isDarkMode ? 'sun' : 'moon'}
          initial={reduceMotion ? false : { rotate: -180, opacity: 0 }}
          animate={reduceMotion ? undefined : { rotate: 0, opacity: 1 }}
          exit={reduceMotion ? undefined : { rotate: 180, opacity: 0 }}
          transition={reduceMotion ? undefined : { duration: 0.3, ease: "easeInOut" }}
        >
          {isDarkMode ? <Sun aria-hidden focusable={false} size={16} className="xs:w-4 xs:h-4 sm:w-5 sm:h-5" /> : <Moon aria-hidden focusable={false} size={16} className="xs:w-4 xs:h-4 sm:w-5 sm:h-5" />}
        </motion.div>
      </AnimatePresence>
    </motion.button>
  );
});

const SearchBox: React.FC = React.memo(() => {
  const { colors } = useTheme();
  const { language } = useLanguage();
  const [searchValue, setSearchValue] = useState('');
  const [isSearchFocused, setIsSearchFocused] = useState(false);
  const inputRef = React.useRef<HTMLInputElement>(null);
  const reduceMotion = useReducedMotion();

  const searchId = useId();

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
      role="search"
      className="relative hidden md:block"
      whileHover={reduceMotion ? undefined : { scale: 1.01 }}
      transition={reduceMotion ? undefined : { duration: 0.2 }}
    >
      <div className="relative">
        <Search 
          aria-hidden
          focusable={false}
          size={16} 
          className="absolute left-3 top-1/2 transform -translate-y-1/2 transition-colors duration-200" 
          style={{ color: isSearchFocused ? colors.primary : colors.textTertiary }}
        />
        <input
          ref={inputRef}
          type="text"
          id={searchId}
          value={searchValue}
          onChange={(e) => setSearchValue(e.target.value)}
          onFocus={() => setIsSearchFocused(true)}
          onBlur={() => setIsSearchFocused(false)}
          placeholder={language === 'en' ? 'Search...' : '搜索...'}
          aria-label={language === 'en' ? 'Search' : '搜索'}
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
            type="button"
            aria-label={language === 'en' ? 'Clear search' : '清除搜索'}
            initial={reduceMotion ? false : { opacity: 0, scale: 0 }}
            animate={reduceMotion ? undefined : { opacity: 1, scale: 1 }}
            onClick={() => setSearchValue('')}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200"
            style={{ color: colors.textTertiary }}
          >
            <X aria-hidden focusable={false} size={14} />
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
              {typeof navigator !== 'undefined' && navigator.platform.includes('Mac') ? '⌘K' : 'Ctrl+K'}
            </kbd>
          </div>
        )}
      </div>
    </motion.div>
  );
});

const LanguageToggle: React.FC = React.memo(() => {
  const { language, setLanguage } = useLanguage();
  const { colors } = useTheme();
  const reduceMotion = useReducedMotion();
  
  return (
    <motion.button
      type="button"
      aria-label={language === 'en' ? 'Switch language to Chinese' : '切换语言为英文'}
      onClick={() => setLanguage(language === 'en' ? 'zh' : 'en')}
      className="flex items-center justify-center xs:justify-start space-x-0 xs:space-x-1 sm:space-x-2 px-2 xs:px-3 py-2 xs:py-2.5 sm:py-3 font-medium rounded-lg xs:rounded-xl transition-all duration-300 text-xs xs:text-sm btn-touch"
      style={{ 
        color: colors.textSecondary,
        backgroundColor: 'transparent'
      }}
      whileHover={reduceMotion ? undefined : { 
        scale: 1.05,
        backgroundColor: `${colors.textSecondary}10`,
        boxShadow: `0 4px 15px ${colors.textSecondary}15`
      }}
      whileTap={reduceMotion ? undefined : { scale: 0.95 }}
    >
      <Globe aria-hidden focusable={false} size={14} className="xs:w-3.5 xs:h-3.5 sm:w-4 sm:h-4" />
      <span className="hidden xs:block font-semibold">
        {language === 'en' ? 'EN' : '中'}
      </span>
    </motion.button>
  );
});

const Logo: React.FC = React.memo(() => {
  const { colors } = useTheme();
  const reduceMotion = useReducedMotion();
  
  return (
    <Link to="/" aria-label="Home" className="flex items-center space-x-2 xs:space-x-3 group">
      <motion.div
        className="relative flex items-center justify-center w-6 h-6 xs:w-9 xs:h-9 sm:w-10 sm:h-10 rounded-lg xs:rounded-xl overflow-hidden"
        style={{
          boxShadow: `0 4px 20px ${colors.primary}25`,
        }}
        whileHover={reduceMotion ? undefined : { 
          scale: 1.05,
          boxShadow: `0 6px 25px ${colors.primary}35`,
        }}
        whileTap={reduceMotion ? undefined : { scale: 0.95 }}
        transition={reduceMotion ? undefined : { duration: 0.2 }}
      >
        <img src="/image.png" alt="Silan Hu" className="w-full h-full object-contain" />
        <motion.div
          className="absolute inset-0 bg-white opacity-0"
          whileHover={reduceMotion ? undefined : { opacity: 0.1 }}
          transition={reduceMotion ? undefined : { duration: 0.2 }}
        />
      </motion.div>
      <div className="hidden xs:block">
        <motion.div 
          className="text-lg text-nowrap font-bold tracking-tight leading-tight"
          style={{ color: colors.textPrimary }}
          whileHover={reduceMotion ? undefined : { scale: 1.02 }}
          transition={reduceMotion ? undefined : { duration: 0.2 }}
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
});

const MobileSearchBox: React.FC = React.memo(() => {
  const { colors } = useTheme();
  const { language } = useLanguage();
  const [focused, setFocused] = useState(false);
  const mobileSearchId = useId();

  return (
    <div className="md:hidden mb-4">
      <div className="relative">
        <Search
          aria-hidden
          focusable={false}
          size={16}
          className="absolute left-3 top-1/2 transform -translate-y-1/2 transition-colors duration-200"
          style={{ color: colors.textTertiary }}
        />
        <input
          id={mobileSearchId}
          type="text"
          placeholder={language === 'en' ? 'Search...' : '搜索...'}
          aria-label={language === 'en' ? 'Search' : '搜索'}
          className="w-full pl-10 pr-4 py-3 rounded-xl text-sm transition-all duration-300 focus:outline-none border"
          style={{
            backgroundColor: colors.surface,
            color: colors.textPrimary,
            borderColor: focused ? colors.primary : colors.cardBorder,
            boxShadow: focused
              ? `0 0 0 3px ${colors.primary}15, 0 4px 12px ${colors.primary}10`
              : `0 2px 4px ${colors.shadowSm}`,
          }}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
        />
      </div>
    </div>
  );
});

const TopNavigation: React.FC = () => {
  const [open, setOpen] = useState<boolean>(false);
  // const [scrolled, setScrolled] = useState<boolean>(false);
  const { pathname } = useLocation();
  const { language } = useLanguage();
  const { colors, isDarkMode } = useTheme();
  const reduceMotion = useReducedMotion();

  // Close mobile menu on route change
  useEffect(() => setOpen(false), [pathname]);

  const items = useMemo(() => NAV_ITEMS(language), [language]);
  
  const isItemActive = useCallback((currentPath: string, itemPath: string): boolean => {
    if (itemPath === '/') return currentPath === '/';
    return currentPath === itemPath || currentPath.startsWith(itemPath + '/');
  }, []);

  return (
    <motion.nav
      aria-label="Primary"
      className="fixed top-0 left-0 right-0 z-50 transition-all duration-300 fluent-glass"
      initial={reduceMotion ? false : { y: -100, opacity: 0 }}
      animate={reduceMotion ? undefined : { y: 0, opacity: 1 }}
      transition={reduceMotion ? undefined : { duration: 0.6, ease: "easeOut" }}
      style={{
        // Frosted glass background with subtle tint
        backgroundColor: isDarkMode ? 'rgba(26, 26, 26, 0.50)' : 'rgba(255, 255, 255, 0.70)',
        backdropFilter: 'blur(10px)',
        WebkitBackdropFilter: 'blur(10px)',
        borderBottom: `1px solid ${colors.cardBorder}80`,
      }}
    >
      {/* Removed: bottom gradient line (replaced by border) */}
      
      <div className="mx-auto px-3 xs:px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 xs:h-18 sm:h-20">
          {/* Logo */}
          <Logo />
    
          {/* Right side - All controls and navigation */}
          <div className="flex items-center space-x-1 lg:space-x-2">
            {/* Search Box */}
            <SearchBox />

            {/* Desktop Navigation - Hide on mobile/tablet, show on desktop */}
            <ul className="hidden lg:flex items-center space-x-1 xl:space-x-1 list-none p-0 m-0" role="list">
              {items.map(item => (
                <li key={item.key} role="listitem">
                  <NavItem
                    to={item.key}
                    icon={item.icon}
                    label={item.label}
                    active={isItemActive(pathname, item.key)}
                  />
                </li>
              ))}
            </ul>

            {/* Controls */}
            <div className="flex items-center space-x-1">
              <LanguageToggle />
              <ThemeToggle />
              
              {/* Mobile Menu Button - Show on tablet and smaller */}
              <motion.button
                className="lg:hidden p-2 xs:p-2.5 sm:p-3 rounded-lg xs:rounded-xl ml-1 xs:ml-2 relative overflow-hidden btn-touch flex items-center justify-center"
                type="button"
                aria-label={open ? (language === 'en' ? 'Close menu' : '关闭菜单') : (language === 'en' ? 'Open menu' : '打开菜单')}
                aria-expanded={open}
                aria-controls="mobile-navigation"
                onClick={() => setOpen(prev => !prev)}
                style={{ 
                  color: colors.textSecondary,
                  backgroundColor: 'transparent'
                }}
                whileHover={reduceMotion ? undefined : { 
                  backgroundColor: `${colors.textSecondary}10`,
                  boxShadow: `0 4px 15px ${colors.textSecondary}15`
                }}
                whileTap={reduceMotion ? undefined : { scale: 0.95 }}
              >
                <AnimatePresence mode="wait">
                  <motion.div
                    key={open ? 'close' : 'menu'}
                    initial={reduceMotion ? false : { rotate: -90, opacity: 0 }}
                    animate={reduceMotion ? undefined : { rotate: 0, opacity: 1 }}
                    exit={reduceMotion ? undefined : { rotate: 90, opacity: 0 }}
                    transition={reduceMotion ? undefined : { duration: 0.2 }}
                  >
                    {open ? <X aria-hidden focusable={false} size={20} className="xs:w-5 xs:h-5 sm:w-6 sm:h-6" /> : <Menu aria-hidden focusable={false} size={20} className="xs:w-5 xs:h-5 sm:w-6 sm:h-6" />}
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
              id="mobile-navigation"
              className="lg:hidden overflow-hidden"
              initial={reduceMotion ? false : { height: 0, opacity: 0 }}
              animate={reduceMotion ? undefined : { height: 'auto', opacity: 1 }}
              exit={reduceMotion ? undefined : { height: 0, opacity: 0 }}
              transition={reduceMotion ? undefined : { duration: 0.3, ease: "easeInOut" }}
            >
              <div className="py-4 xs:py-6 space-y-1 xs:space-y-2">
                {/* Mobile Search */}
                <motion.div
                  initial={reduceMotion ? false : { x: -20, opacity: 0 }}
                  animate={reduceMotion ? undefined : { x: 0, opacity: 1 }}
                  transition={reduceMotion ? undefined : { delay: 0, duration: 0.3 }}
                >
                  <MobileSearchBox />
                </motion.div>

                {items.map((item, index) => (
                  <motion.div
                    key={item.key}
                    initial={reduceMotion ? false : { x: -20, opacity: 0 }}
                    animate={reduceMotion ? undefined : { x: 0, opacity: 1 }}
                    transition={reduceMotion ? undefined : { delay: (index + 1) * 0.1, duration: 0.3 }}
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
