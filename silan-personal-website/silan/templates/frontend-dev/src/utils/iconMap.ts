// Icon mapping utility for dynamic icon loading
import React from 'react';
import {
  GraduationCap,
  Brain,
  Zap,
  Briefcase,
  Target,
  Calendar,
  TrendingUp,
  Code,
  Anchor,
  Heart,
  Smartphone,
  Droplets,
  LucideIcon
} from 'lucide-react';

// Type for icon names
export type IconName = 'GraduationCap' | 'Brain' | 'Zap' | 'Briefcase' | 'Target' | 'Calendar' | 'TrendingUp' | 'Code' | 'Anchor' | 'Heart' | 'Smartphone' | 'Droplets';

// Interface for icon props
export interface IconProps {
  size?: number;
  className?: string;
  color?: string;
}

// Interface for plan object - using import to avoid conflicts
import type { Plan as ProjectPlan, AnnualPlan } from '../types/api';
import type { Plan as IndexPlan } from '../types';

// Union type for plan objects
type PlanType = ProjectPlan | AnnualPlan | IndexPlan;

// Interface for plan display props
export interface PlanDisplayProps extends IconProps {
  onError?: (e: React.SyntheticEvent<HTMLImageElement, Event>) => void;
}

// Icon mapping
const iconMap: Record<string, LucideIcon> = {
  GraduationCap,
  Brain,
  Zap,
  Briefcase,
  Target,
  Calendar,
  TrendingUp,
  Code,
  Anchor,
  Heart,
  Smartphone,
  Droplets
};

/**
 * Get icon component by name
 * @param iconName - Name of the icon
 * @param props - Props to pass to icon component (size, color, etc.)
 * @returns React element or null
 */
export const getIcon = (iconName: IconName, props: IconProps = {}): React.ReactElement | null => {
  const IconComponent = iconMap[iconName];
  if (!IconComponent) {
    console.warn(`Icon "${iconName}" not found in iconMap`);
    return null;
  }
  return React.createElement(IconComponent, props);
};

/**
 * Get plan display element (icon or image)
 * @param plan - Plan object with icon and/or image properties (ProjectPlan, AnnualPlan, or IndexPlan)
 * @param props - Props for styling (size, className, etc.)
 * @returns React element or null
 */
export const getPlanDisplay = (plan: PlanType, props: PlanDisplayProps = {}): React.ReactElement | null => {
  const { size = 16, className = '' } = props;
  
  // Check if plan has image property and if it exists
  if ('image' in plan && plan.image) {
    const planName = 'nameZh' in plan ? plan.nameZh : ('name' in plan ? (plan as any).name : 'Plan');
    return React.createElement('img', {
      src: plan.image,
      alt: planName,
      className: `w-${size} h-${size} object-cover ${className}`,
      style: { width: size, height: size },
      onError: (e: React.SyntheticEvent<HTMLImageElement, Event>) => {
        // Fallback to icon if image fails to load
        const planId = 'id' in plan ? (plan as any).id : ('name' in plan ? (plan as any).name : 'unknown');
        console.warn(`Failed to load image for plan ${planId}, falling back to icon`);
        if ('icon' in plan && plan.icon && plan.icon in iconMap) {
          // Create a new img element with the icon as fallback
          const parent = e.currentTarget.parentNode;
          if (parent) {
            const IconComponent = iconMap[plan.icon];
            const iconElement = React.createElement(IconComponent, { size, className });
            // Replace the img with icon component
            parent.replaceChild(React.createElement('div', {}, iconElement) as any, e.currentTarget);
          }
        }
      }
    });
  }
  
  // Check if plan has icon property and if it exists in iconMap
  if ('icon' in plan && plan.icon && plan.icon in iconMap) {
    const IconComponent = iconMap[plan.icon];
    return React.createElement(IconComponent, { size, className });
  }
  
  // No valid icon or image found
  return null;
};

/**
 * Get available icon names
 * @returns Array of available icon names
 */
export const getAvailableIcons = (): IconName[] => {
  return Object.keys(iconMap) as IconName[];
};

export default iconMap; 