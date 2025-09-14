import React from 'react';
import { useTheme } from './ThemeContext';

const SimpleBackground: React.FC = () => {
  const { colors } = useTheme();

  return (
    <div 
      className="fixed inset-0 pointer-events-none z-0 transition-colors duration-300"
      style={{ backgroundColor: colors.background }}
    />
  );
};

export default SimpleBackground;