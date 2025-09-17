import React from 'react';
import { Breadcrumb } from 'antd';
import { Home, BookOpen, Play, List, Folder } from 'lucide-react';
import { BlogData } from '../types/blog';
import { useLanguage } from '../../LanguageContext';
import type { BreadcrumbProps as AntBreadcrumbProps } from 'antd';

interface BreadcrumbProps {
  post: BlogData;
  onBack: () => void;
  onFilterByCategory?: (category: string) => void;
}

export const BlogBreadcrumb: React.FC<BreadcrumbProps> = ({ post, onBack, onFilterByCategory }) => {
  const { language } = useLanguage();
  const isSeries = Boolean(post.seriesId);

  const getContentTypeInfo = () => {
    switch (post.type) {
      case 'vlog':
        return {
          icon: <Play size={14} className="text-red-500" />,
          label: isSeries
            ? (language === 'en' ? 'Video Series' : '视频系列')
            : (language === 'en' ? 'Vlog' : '视频博客'),
          category: language === 'en' ? 'Videos' : '视频',
          filterKey: 'vlog'
        };
      case 'tutorial':
        return {
          icon: <BookOpen size={14} className="text-green-500" />,
          label: isSeries
            ? (language === 'en' ? 'Tutorial Series' : '教程系列')
            : (language === 'en' ? 'Tutorial' : '教程'),
          category: language === 'en' ? 'Tutorials' : '教程',
          filterKey: 'tutorial'
        };
      case 'podcast':
        return {
          icon: <Play size={14} className="text-orange-500" />,
          label: isSeries
            ? (language === 'en' ? 'Podcast Series' : '播客系列')
            : (language === 'en' ? 'Podcast' : '播客'),
          category: language === 'en' ? 'Podcasts' : '播客',
          filterKey: 'podcast'
        };
      case 'article':
      default:
        return {
          icon: <BookOpen size={14} className="text-theme-500" />,
          label: isSeries
            ? (language === 'en' ? 'Article Series' : '文章系列')
            : (language === 'en' ? 'Article' : '文章'),
          category: language === 'en' ? 'Articles' : '文章',
          filterKey: 'article'
        };
    }
  };

  const handleCategoryClick = () => {
    if (onFilterByCategory) {
      onFilterByCategory(contentInfo.filterKey);
    } else {
      onBack(); // Fallback to normal back behavior
    }
  };

  const contentInfo = getContentTypeInfo();

  // 构建面包屑项
  const breadcrumbItems: AntBreadcrumbProps['items'] = [
    {
      title: (
        <button
          onClick={onBack}
          className="flex items-center gap-1.5 hover:text-theme-primary transition-colors text-theme-secondary"
        >
          <Home size={14} />
          <span className="hidden sm:inline">{language === 'en' ? 'Blog' : '博客'}</span>
        </button>
      ),
    },
    {
      title: (
        <button
          onClick={handleCategoryClick}
          className="flex items-center gap-1.5 hover:text-theme-primary transition-colors text-theme-secondary"
        >
          {contentInfo.icon}
          {isSeries && <List size={12} className="text-purple-500" />}
          <span className="hidden md:inline">{contentInfo.category}</span>
          <span className="md:hidden">{contentInfo.label}</span>
        </button>
      ),
    }
  ];

  // 如果是系列，添加系列级别
  if (isSeries && post.seriesTitle) {
    breadcrumbItems.push({
      title: (
        <button
          onClick={handleCategoryClick}
          className="flex items-center gap-1.5 hover:text-theme-primary transition-colors text-theme-secondary"
        >
          <Folder size={14} className="text-purple-500" />
          <span className="truncate max-w-[120px] sm:max-w-[180px]">
            {language === 'zh' && post.seriesTitleZh ? post.seriesTitleZh : post.seriesTitle}
          </span>
        </button>
      ),
    });
  }

  // 当前文章/剧集
  breadcrumbItems.push({
    title: (
      <span className="text-theme-primary font-medium flex items-center gap-1.5">
        {post.episodeNumber && (
          <span className="text-xs bg-theme-primary/10 text-theme-primary px-1.5 py-0.5 rounded">
            {language === 'en' ? `EP${post.episodeNumber}` : `第${post.episodeNumber}集`}
          </span>
        )}
        <span className="truncate max-w-[200px] sm:max-w-[300px]">
          {language === 'zh' && post.titleZh ? post.titleZh : post.title}
        </span>
      </span>
    ),
  });

  return (
    <Breadcrumb
      items={breadcrumbItems}
      className="blog-breadcrumb"
      separator="/"
    />
  );
}; 