// src/components/ui/Button.tsx
import React from 'react';
import { Button as AntButton, ButtonProps as AntButtonProps } from 'antd';
import { motion } from 'framer-motion';

type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
type ButtonSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

interface CustomButtonProps {
  children: React.ReactNode;
  variant?: ButtonVariant;
  size?: ButtonSize;
  animate?: boolean;
  fullWidth?: boolean;
}

interface ButtonProps extends Omit<AntButtonProps, 'size' | 'type'>, CustomButtonProps {}

const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  className = '',
  animate = true,
  fullWidth = false,
  ...props
}) => {
  // Map custom variants to Ant Design types
  const getAntType = (): AntButtonProps['type'] => {
    switch (variant) {
      case 'primary':
        return 'primary';
      case 'secondary':
        return 'default';
      case 'outline':
        return 'default';
      case 'ghost':
        return 'text';
      case 'danger':
        return 'primary';
      default:
        return 'primary';
    }
  };

  // Map custom sizes to Ant Design sizes
  const getAntSize = (): AntButtonProps['size'] => {
    switch (size) {
      case 'xs':
      case 'sm':
        return 'small';
      case 'md':
        return 'middle';
      case 'lg':
      case 'xl':
        return 'large';
      default:
        return 'middle';
    }
  };

  const getDanger = (): boolean => {
    return variant === 'danger';
  };

  const getGhost = (): boolean => {
    return variant === 'outline' || variant === 'ghost';
  };

  const customStyles: React.CSSProperties = {
    width: fullWidth ? '100%' : undefined,
    borderRadius: '12px',
    fontWeight: 500,
    transition: 'all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
    ...(variant === 'secondary' && {
      background: 'var(--color-secondary)',
      borderColor: 'var(--color-secondary)',
      color: 'white',
    }),
  };

  const buttonElement = (
    <AntButton
      type={getAntType()}
      size={getAntSize()}
      disabled={disabled}
      loading={loading}
      danger={getDanger()}
      ghost={getGhost()}
      className={`${className} ${variant === 'secondary' ? 'ant-btn-secondary' : ''}`}
      style={customStyles}
      {...props}
    >
      {children}
    </AntButton>
  );

  if (animate && !disabled && !loading) {
    return (
      <motion.div
        whileHover={{ scale: 1.02, y: -1 }}
        whileTap={{ scale: 0.98 }}
        transition={{ duration: 0.2, ease: [0.25, 0.46, 0.45, 0.94] }}
        style={{ display: fullWidth ? 'block' : 'inline-block' }}
      >
        {buttonElement}
      </motion.div>
    );
  }

  return buttonElement;
};

export default Button;
