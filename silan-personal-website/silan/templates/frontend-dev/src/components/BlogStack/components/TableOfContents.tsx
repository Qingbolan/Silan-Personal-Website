import React from 'react';
import { Anchor } from 'antd';
import type { AnchorLinkItemProps } from 'antd/es/anchor/Anchor';
import { Section } from '../types/blog';
interface TableOfContentsProps {
  sections: Section[];
  className?: string;
}

export const TableOfContents: React.FC<TableOfContentsProps> = ({
  sections,
  className = ''
}) => {
  // Convert sections to Ant Design Anchor items format with proper hierarchy
  const anchorItems: AnchorLinkItemProps[] = React.useMemo(() => {
    if (sections.length === 0) return [];
    
    // Use flat structure but with visual hierarchy via CSS
    return sections.map(section => ({
      key: section.id,
      href: `#${section.id}`,
      title: (
        <span 
          className={`simple-toc-item level-${section.level}`}
          title={section.title} // Tooltip for long titles
        >
          {section.title}
        </span>
      ),
    }));
  }, [sections]);

  if (sections.length === 0) {
    return null;
  }

  return (
    <div
      className={`simple-toc ${className}`}
      style={{
        position: 'relative',
        maxHeight: 'calc(100vh - 120px)', // 增加更多缓冲空间给顶部按钮和间距
        overflow: 'hidden' // 外层隐藏溢出
      }}
    >
      {/* TOC Content */}
      <div style={{
        maxHeight: 'calc(100vh - 160px)', // 与外层一致
        overflow: 'auto', // 内层可滚动
        paddingRight: '4px', // 为滚动条留出更多空间
      }}>
        <Anchor
          items={anchorItems}
          offsetTop={120}
          targetOffset={120}
          showInkInFixed={true}
          affix={false}
          bounds={10}
          className="simple-toc-anchor"
        />
      </div>
    </div>
  );
};