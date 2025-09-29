import React from 'react';
import { useTheme } from './ThemeContext';
import LiquidEther from './ui/background/LiquidEther';
import DarkVeil from './ui/background/darkveil-canvas';

const Background: React.FC = () => {
  const { colors, isDarkMode } = useTheme();

  return (
    <div 
      className="fixed inset-0 pointer-events-none z-0 transition-colors duration-300 w-full h-full"
      style={{ backgroundColor: colors.background }}
    >
      {!isDarkMode && <LiquidEther />}
      {isDarkMode && <DarkVeil />}
    </div>
  );
};

export default Background;