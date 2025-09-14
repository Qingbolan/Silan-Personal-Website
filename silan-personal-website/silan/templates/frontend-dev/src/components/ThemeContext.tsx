import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';

// Vue.js inspired color scheme
const colorSchemes = {
  light: {
    // Primary colors - Vue green
    primary: '#42b883',         // Vue green
    primaryHover: '#369870',    // Darker Vue green
    primaryLight: '#f0f9ff',    // Very light green background
    
    // Secondary colors - Vue dark blue
    secondary: '#35495e',       // Vue dark blue
    secondaryHover: '#2c3e50',  // Darker Vue blue
    secondaryLight: '#f8fafc',  // Light gray
    
    // Background colors - Clean and minimal
    background: '#ffffff',       // Pure white
    backgroundSecondary: '#f8fafc',   // Very light gray
    backgroundTertiary: '#f1f5f9',    // Light gray
    
    // Text colors - High contrast
    textPrimary: '#2c3e50',     // Vue dark blue for text
    textSecondary: '#606266',   // Medium gray
    textTertiary: '#909399',    // Light gray
    
    // Accent colors
    accent: '#42b883',          // Vue green accent
    accentHover: '#369870',     // Darker Vue green
    
    // Status colors
    success: '#67c23a',         // Vue success green
    warning: '#e6a23c',         // Vue warning yellow
    error: '#f56c6c',           // Vue error red
    
    // Gradients - Vue style
    gradientPrimary: 'linear-gradient(135deg, #42b883 0%, #35495e 100%)',
    gradientSecondary: 'linear-gradient(135deg, #67c23a 0%, #42b883 100%)',
    gradientAccent: 'linear-gradient(135deg, #35495e 0%, #2c3e50 100%)',
    
    // Surface colors
    cardBackground: '#ffffff',
    cardBorder: '#ebeef5',      // Vue border gray
    surface: '#f8fafc',         
    surfaceSecondary: '#f1f5f9', 
    surfaceTertiary: '#ebeef5',  
    surfaceElevated: '#ffffff',
    
    // Interactive states
    hoverBackground: '#f1f5f9',
    activeBackground: '#ebeef5',
    focusRing: '#42b883',
    
    // Shadows
    shadowSm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    shadowMd: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    shadowLg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
    shadowXl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
  },
  dark: {
    // Primary colors - Vue green for dark
    primary: '#42b883',         // Vue green (same in dark)
    primaryHover: '#4fc08d',    // Lighter Vue green
    primaryLight: '#1a1a1a',    // Dark background
    
    // Secondary colors
    secondary: '#a0a8b7',       // Light gray for dark mode
    secondaryHover: '#c0c4cc',  // Lighter gray
    secondaryLight: '#35495e',  // Vue dark blue
    
    // Background colors - Vue dark theme
    background: '#1a1a1a',       // Very dark gray
    backgroundSecondary: '#2c2c2c', // Dark gray
    backgroundTertiary: '#35495e',  // Vue dark blue
    
    // Text colors - High contrast for dark
    textPrimary: '#ffffff',     // Pure white
    textSecondary: '#a0a8b7',   // Light gray
    textTertiary: '#909399',    // Medium gray
    
    // Accent colors
    accent: '#42b883',          // Vue green (consistent)
    accentHover: '#4fc08d',     // Lighter Vue green
    
    // Status colors
    success: '#67c23a',         // Vue success green
    warning: '#e6a23c',         // Vue warning yellow  
    error: '#f56c6c',           // Vue error red
    
    // Gradients - Vue dark style
    gradientPrimary: 'linear-gradient(135deg, #42b883 0%, #4fc08d 100%)',
    gradientSecondary: 'linear-gradient(135deg, #67c23a 0%, #42b883 100%)',
    gradientAccent: 'linear-gradient(135deg, #a0a8b7 0%, #909399 100%)',
    
    // Surface colors
    cardBackground: '#2c2c2c',   // Dark gray
    cardBorder: '#35495e',       // Vue dark blue
    surface: '#35495e',          // Vue dark blue
    surfaceSecondary: '#2c2c2c', // Dark gray
    surfaceTertiary: '#404040',  // Medium dark gray
    surfaceElevated: '#2c2c2c',
    
    // Interactive states
    hoverBackground: '#404040',
    activeBackground: '#35495e',
    focusRing: '#42b883',
    
    // Shadows for dark mode
    shadowSm: '0 1px 2px 0 rgb(0 0 0 / 0.3)',
    shadowMd: '0 4px 6px -1px rgb(0 0 0 / 0.4), 0 2px 4px -2px rgb(0 0 0 / 0.4)',
    shadowLg: '0 10px 15px -3px rgb(0 0 0 / 0.4), 0 4px 6px -4px rgb(0 0 0 / 0.4)',
    shadowXl: '0 20px 25px -5px rgb(0 0 0 / 0.4), 0 8px 10px -6px rgb(0 0 0 / 0.4)',
  }
};

interface ColorScheme {
  primary: string;
  primaryHover: string;
  primaryLight: string;
  secondary: string;
  secondaryHover: string;
  secondaryLight: string;
  background: string;
  backgroundSecondary: string;
  backgroundTertiary: string;
  textPrimary: string;
  textSecondary: string;
  textTertiary: string;
  accent: string;
  accentHover: string;
  success: string;
  warning: string;
  error: string;
  gradientPrimary: string;
  gradientSecondary: string;
  gradientAccent: string;
  cardBackground: string;
  cardBorder: string;
  surface: string;
  surfaceSecondary: string;
  surfaceTertiary: string;
  surfaceElevated: string;
  hoverBackground: string;
  activeBackground: string;
  focusRing: string;
  shadowSm: string;
  shadowMd: string;
  shadowLg: string;
  shadowXl: string;
}

interface ThemeContextType {
  isDarkMode: boolean;
  setIsDarkMode: (value: boolean) => void;
  toggleTheme: () => void;
  colors: ColorScheme;
}

interface ThemeProviderProps {
  children: ReactNode;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [isDarkMode, setIsDarkMode] = useState<boolean>(() => {
    // Check system preference first
    const systemPreference = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const savedMode = localStorage.getItem('darkMode');
    return savedMode ? JSON.parse(savedMode) : systemPreference;
  });

  const toggleTheme = () => {
    setIsDarkMode(prev => !prev);
  };

  const colors = colorSchemes[isDarkMode ? 'dark' : 'light'];

  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(isDarkMode));
    
    // Apply theme class to document
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    
    // Apply CSS custom properties for dynamic theming
    const root = document.documentElement;
    Object.entries(colors).forEach(([key, value]) => {
      root.style.setProperty(`--color-${key}`, value);
    });

    // Apply shadow CSS custom properties
    root.style.setProperty('--shadow-sm', colors.shadowSm);
    root.style.setProperty('--shadow-md', colors.shadowMd);
    root.style.setProperty('--shadow-lg', colors.shadowLg);
    root.style.setProperty('--shadow-xl', colors.shadowXl);

    // Apply futuristic design properties
    root.style.setProperty('--border-radius-sm', '0.5rem');
    root.style.setProperty('--border-radius-md', '0.75rem');
    root.style.setProperty('--border-radius-lg', '1rem');
    root.style.setProperty('--border-radius-xl', '1.5rem');
    root.style.setProperty('--transition-fast', '0.15s ease-out');
    root.style.setProperty('--transition-smooth', '0.3s ease-out');
    root.style.setProperty('--backdrop-blur', 'blur(10px)');
    
  }, [isDarkMode, colors]);

  // Listen for system theme changes
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e: MediaQueryListEvent) => {
      if (!localStorage.getItem('darkMode')) {
        setIsDarkMode(e.matches);
      }
    };
    
    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  const contextValue: ThemeContextType = {
    isDarkMode,
    setIsDarkMode,
    toggleTheme,
    colors
  };

  return (
    <ThemeContext.Provider value={contextValue}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}; 