import React from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';

interface ShimmerButtonProps extends Omit<HTMLMotionProps<"button">, 'children'> {
  children: React.ReactNode;
  className?: string;
  disabled?: boolean;
}

const ShimmerButton: React.FC<ShimmerButtonProps> = ({
  children,
  className = '',
  disabled = false,
  ...props
}) => {
  return (
    <motion.button
      className={`
        relative inline-flex items-center justify-center px-6 py-3
        font-medium transition-all duration-300 overflow-hidden
        group rounded-xl text-theme-primary border border-[var(--color-primary)20] bg-transparent
        hover:bg-[var(--color-primary)05] hover:border-[var(--color-primary)40]
        ${disabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}
        ${className}
      `}
      disabled={disabled}
      whileHover={!disabled ? { scale: 1.02 } : {}}
      whileTap={!disabled ? { scale: 0.98 } : {}}
      {...props}
    >
      {/* Shimmer effect */}
      <motion.div
        className="absolute inset-0 opacity-0 group-hover:opacity-100 bg-[linear-gradient(45deg,transparent_30%,var(--color-primary)30_50%,transparent_70%)]"
        initial={{ x: '-100%' }}
        whileHover={{
          x: '100%',
          transition: {
            duration: 0.6,
            ease: 'easeInOut',
          },
        }}
      />
      
      {/* Glow effect */}
      <motion.div
        className="absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 shadow-[0_0_20px_var(--color-primary)40]"
        initial={{ opacity: 0 }}
        whileHover={{ 
          opacity: 1,
          transition: { duration: 0.3 }
        }}
      />
      
      {/* Content */}
      <span className="relative z-10 flex items-center space-x-2">
        {children}
      </span>
    </motion.button>
  );
};

export default ShimmerButton; 