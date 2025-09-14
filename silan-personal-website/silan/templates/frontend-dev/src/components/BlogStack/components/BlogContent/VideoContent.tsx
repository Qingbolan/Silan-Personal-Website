import React from 'react';
import { Card, Tag, Typography, Alert } from 'antd';
import { PlayCircleOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import { BlogContent } from '../../types/blog';
import { useLanguage } from '../../../LanguageContext';

const { Paragraph } = Typography;

interface VideoContentProps {
  item: BlogContent;
  index: number;
  isWideScreen: boolean;
}

export const VideoContent: React.FC<VideoContentProps> = ({ item, index, isWideScreen }) => {
  const { language } = useLanguage();

  return (
    <figure className={`my-16 ${isWideScreen ? 'col-span-2' : ''} break-inside-avoid`}>
      <Card
        className="overflow-hidden shadow-medium"
        bodyStyle={{ padding: 0 }}
        style={{ 
          borderRadius: '12px',
          backgroundColor: 'var(--color-surface-elevated, white)',
          borderColor: 'var(--color-card-border, rgba(229, 231, 235, 1))'
        }}
      >
        {/* Video Container */}
        <div className="relative overflow-hidden  -secondary">
          <video
            controls
            className="w-full h-auto focus:outline-none"
            style={{ 
              aspectRatio: '16/9',
              maxHeight: '400px'
            }}
            poster={item.content.startsWith('/api/placeholder') 
              ? `https://via.placeholder.com/800x400/6366f1/ffffff?text=${encodeURIComponent('Academic Video Preview')}`
              : undefined
            }
            preload="metadata"
            onError={(e) => {
              // Show fallback content on video error
              const videoElement = e.target as HTMLVideoElement;
              const container = videoElement.parentElement;
              if (container) {
                container.innerHTML = `
                  <div class="flex items-center justify-center h-64 bg-gray-100">
                    <div class="text-center p-8">
                      <div class="text-4xl mb-4 text-gray-400">⚠️</div>
                      <p class="text-gray-600 text-sm font-medium">
                        ${language === 'en' ? 'Video could not be loaded' : '视频无法加载'}
                      </p>
                    </div>
                  </div>
                `;
              }
            }}
          >
            <source src={item.content} type="video/mp4" />
            <source src={item.content.replace('.mp4', '.webm')} type="video/webm" />
            
            {/* Fallback Content for unsupported browsers */}
            <div className="absolute inset-0 flex items-center justify-center  -secondary">
              <Alert
                message={language === 'en' ? 'Video Playback Not Supported' : '不支持视频播放'}
                description={
                  language === 'en' 
                    ? 'Your browser does not support the video tag. Please try updating your browser or use a different device.'
                    : '您的浏览器不支持视频播放。请尝试更新浏览器或使用其他设备。'
                }
                type="warning"
                icon={<ExclamationCircleOutlined />}
                showIcon
                className="max-w-md"
              />
            </div>
          </video>
          
          {/* Play button overlay for better UX */}
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 pointer-events-none">
            <PlayCircleOutlined 
              style={{ 
                fontSize: '64px', 
                color: 'rgba(255, 255, 255, 0.8)',
                filter: 'drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3))'
              }} 
            />
          </div>
        </div>
        
        {/* Caption */}
        {item.caption && (
          <div className="p-6 bg-theme-surface-elevated">
            <div className="text-center space-y-2">
              {/* Video Number Tag */}
              <Tag 
                color="orange" 
                className="mb-2"
                style={{
                  borderRadius: '16px',
                  fontWeight: 600,
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em'
                }}
                icon={<PlayCircleOutlined />}
              >
                Video {index + 1}
              </Tag>
              
              {/* Caption Text */}
              <Paragraph 
                className="text-center max-w-2xl mx-auto"
                style={{ 
                  fontFamily: 'Georgia, "Times New Roman", Charter, serif',
                  fontSize: '14px',
                  lineHeight: '1.6',
                  color: 'var(--color-text-secondary, #6b7280)',
                  marginBottom: 0
                }}
              >
                {item.caption}
              </Paragraph>
            </div>
          </div>
        )}
      </Card>
    </figure>
  );
}; 