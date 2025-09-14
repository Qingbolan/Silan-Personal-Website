import React from 'react';
import { Spin } from 'antd';
import { motion } from 'framer-motion';

interface LoadingSpinnerProps {
  size?: 'small' | 'default' | 'large';
  spinning?: boolean;
  tip?: string;
  children?: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'default',
  spinning = true,
  tip,
  children,
  className = '',
  style,
}) => {
  if (children) {
    return (
      <Spin 
        size={size} 
        spinning={spinning} 
        tip={tip}
        className={className}
        style={style}
      >
        {children}
      </Spin>
    );
  }

  return (
    <motion.div
      className={`flex items-center justify-center ${className}`}
      style={style}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <Spin size={size} tip={tip} />
    </motion.div>
  );
};

export default LoadingSpinner;