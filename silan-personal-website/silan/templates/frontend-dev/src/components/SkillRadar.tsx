import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useTheme } from './ThemeContext';

interface SkillData {
  name: string;
  value: number;
  category: 'AI/ML' | 'Frontend' | 'Backend' | 'Research' | 'Tools';
}

const SkillRadar: React.FC = () => {
  const { colors } = useTheme();
  const [hoveredSkill, setHoveredSkill] = useState<string | null>(null);
  
  const skills: SkillData[] = [
    { name: 'Neural Networks', value: 95, category: 'AI/ML' },
    { name: 'Computer Vision', value: 90, category: 'AI/ML' },
    { name: 'LLMs', value: 88, category: 'AI/ML' },
    { name: 'React/TypeScript', value: 92, category: 'Frontend' },
    { name: 'Vue.js', value: 85, category: 'Frontend' },
    { name: 'Python/PyTorch', value: 95, category: 'Backend' },
    { name: 'Node.js/Go', value: 82, category: 'Backend' },
    { name: 'Research Writing', value: 88, category: 'Research' },
    { name: 'Data Analysis', value: 90, category: 'Research' },
    { name: 'Docker/Cloud', value: 80, category: 'Tools' },
    { name: 'Git/CI/CD', value: 85, category: 'Tools' }
  ];

  const centerX = 150;
  const centerY = 150;
  const radius = 120;
  
  const categoryColors = {
    'AI/ML': colors.primary,
    'Frontend': colors.success,
    'Backend': colors.secondary,
    'Research': colors.accent,
    'Tools': colors.warning
  };

  const getPointPosition = (index: number, value: number) => {
    const angle = (index * 2 * Math.PI) / skills.length - Math.PI / 2;
    const distance = (value / 100) * radius;
    return {
      x: centerX + Math.cos(angle) * distance,
      y: centerY + Math.sin(angle) * distance
    };
  };

  const getLabelPosition = (index: number) => {
    const angle = (index * 2 * Math.PI) / skills.length - Math.PI / 2;
    const distance = radius + 25;
    return {
      x: centerX + Math.cos(angle) * distance,
      y: centerY + Math.sin(angle) * distance
    };
  };

  // Generate radar grid circles
  const gridCircles = [20, 40, 60, 80, 100].map(percentage => (
    <circle
      key={percentage}
      cx={centerX}
      cy={centerY}
      r={(percentage / 100) * radius}
      fill="none"
      stroke={colors.cardBorder}
      strokeWidth="1"
      opacity="0.3"
    />
  ));

  // Generate radar grid lines
  const gridLines = skills.map((_, index) => {
    const angle = (index * 2 * Math.PI) / skills.length - Math.PI / 2;
    const endX = centerX + Math.cos(angle) * radius;
    const endY = centerY + Math.sin(angle) * radius;
    
    return (
      <line
        key={index}
        x1={centerX}
        y1={centerY}
        x2={endX}
        y2={endY}
        stroke={colors.cardBorder}
        strokeWidth="1"
        opacity="0.3"
      />
    );
  });

  // Generate skill polygon path
  const pathData = skills.map((skill, index) => {
    const point = getPointPosition(index, skill.value);
    return `${index === 0 ? 'M' : 'L'} ${point.x} ${point.y}`;
  }).join(' ') + ' Z';

  return (
    <div className="flex flex-col items-center p-6">
      <h3 className="text-xl font-semibold mb-4 text-theme-primary">
        Technical Expertise Radar
      </h3>
      
      <div className="relative">
        <svg width="300" height="300" viewBox="0 0 300 300">
          {/* Grid */}
          {gridCircles}
          {gridLines}
          
          {/* Skill polygon */}
          <motion.path
            d={pathData}
            fill={colors.primary}
            fillOpacity="0.1"
            stroke={colors.primary}
            strokeWidth="2"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 2, ease: "easeInOut" }}
          />
          
          {/* Skill points */}
          {skills.map((skill, index) => {
            const point = getPointPosition(index, skill.value);
            const isHovered = hoveredSkill === skill.name;
            
            return (
              <motion.circle
                key={skill.name}
                cx={point.x}
                cy={point.y}
                r={isHovered ? 8 : 5}
                fill={categoryColors[skill.category]}
                stroke="white"
                strokeWidth="2"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: index * 0.1, duration: 0.3 }}
                whileHover={{ scale: 1.5 }}
                onMouseEnter={() => setHoveredSkill(skill.name)}
                onMouseLeave={() => setHoveredSkill(null)}
                style={{ cursor: 'pointer' }}
              />
            );
          })}
          
          {/* Labels */}
          {skills.map((skill, index) => {
            const labelPos = getLabelPosition(index);
            const isHovered = hoveredSkill === skill.name;
            
            return (
              <text
                key={`label-${skill.name}`}
                x={labelPos.x}
                y={labelPos.y}
                textAnchor="middle"
                dominantBaseline="middle"
                fontSize={isHovered ? "12" : "10"}
                fill={isHovered ? categoryColors[skill.category] : colors.textSecondary}
                fontWeight={isHovered ? "600" : "400"}
                style={{ cursor: 'pointer' }}
                onMouseEnter={() => setHoveredSkill(skill.name)}
                onMouseLeave={() => setHoveredSkill(null)}
              >
                {skill.name}
              </text>
            );
          })}
        </svg>
        
        {/* Hover tooltip */}
        {hoveredSkill && (
          <motion.div
            className="absolute top-4 right-4 bg-theme-cardBackground border border-theme-cardBorder rounded-lg p-3 shadow-lg"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="text-sm font-semibold text-theme-primary">
              {hoveredSkill}
            </div>
            <div className="text-xs text-theme-secondary">
              Proficiency: {skills.find(s => s.name === hoveredSkill)?.value}%
            </div>
            <div className="text-xs text-theme-secondary">
              Category: {skills.find(s => s.name === hoveredSkill)?.category}
            </div>
          </motion.div>
        )}
      </div>
      
      {/* Legend */}
      <div className="mt-6 grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs">
        {Object.entries(categoryColors).map(([category, color]) => (
          <div key={category} className="flex items-center space-x-2">
            <div 
              className="w-3 h-3 rounded-full" 
              style={{ backgroundColor: color }}
            />
            <span className="text-theme-secondary">{category}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SkillRadar;