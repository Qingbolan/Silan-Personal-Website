import React from 'react';
import { motion } from 'framer-motion';
import { useTheme } from '../ThemeContext';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  text?: string;
  variant?: 'ring' | 'pulse' | 'dots';
  color?: 'primary' | 'secondary' | 'accent';
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  text,
  variant = 'ring',
  color = 'primary'
}) => {
  const { colors } = useTheme();

  const sizeClasses = {
    sm: 'w-6 h-6',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16'
  };

  const colorMap = {
    primary: colors.primary,
    secondary: colors.secondary,
    accent: colors.accent
  };

  const selectedColor = colorMap[color];

  const renderSpinner = () => {
    switch (variant) {
      case 'ring':
        return (
          <motion.div
            className={`${sizeClasses[size]} rounded-full relative`}
            style={{
              background: `conic-gradient(from 0deg, transparent, ${selectedColor}20, ${selectedColor})`,
            }}
            animate={{ rotate: 360 }}
            transition={{
              duration: 1,
              repeat: Infinity,
              ease: "linear"
            }}
          />
        );

      case 'pulse':
        return (
          <motion.div
            className={`${sizeClasses[size]} rounded-full`}
            style={{ backgroundColor: selectedColor }}
            animate={{
              scale: [1, 1.2, 1],
              opacity: [1, 0.5, 1]
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
        );

      case 'dots':
        return (
          <div className="flex space-x-1">
            {[0, 1, 2].map((index) => (
              <motion.div
                key={index}
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: selectedColor }}
                animate={{
                  scale: [1, 1.5, 1],
                  opacity: [0.3, 1, 0.3]
                }}
                transition={{
                  duration: 1,
                  repeat: Infinity,
                  delay: index * 0.2,
                  ease: "easeInOut"
                }}
              />
            ))}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="flex flex-col items-center justify-center space-y-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        className="relative"
      >
        {renderSpinner()}
        
        {/* Glow effect */}
        <motion.div
          className={`absolute inset-0 ${sizeClasses[size]} rounded-full opacity-20 blur-sm`}
          style={{ backgroundColor: selectedColor }}
          animate={{
            scale: [1, 1.1, 1],
            opacity: [0.2, 0.4, 0.2]
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
      </motion.div>
      
      {text && (
        <motion.p
          className="text-sm font-medium"
          style={{ color: colors.textSecondary }}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
        >
          {text}
        </motion.p>
      )}
    </div>
  );
}; 