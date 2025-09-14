import React from 'react';
import { Image, Card, Tag, Typography } from 'antd';
import { PictureOutlined } from '@ant-design/icons';
import { BlogContent } from '../../types/blog';

const { Text, Paragraph } = Typography;

interface ImageContentProps {
  item: BlogContent;
  index: number;
  isWideScreen: boolean;
}

export const ImageContent: React.FC<ImageContentProps> = ({ item, index, isWideScreen }) => {
  const imageSrc = item.content.startsWith('/api/placeholder') 
    ? `https://via.placeholder.com/800x400/6366f1/ffffff?text=${encodeURIComponent(item.caption || 'Academic Figure')}`
    : item.content;

  const fallbackSrc = `https://via.placeholder.com/800x400/6366f1/ffffff?text=${encodeURIComponent('Figure Not Available')}`;

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
        {/* Image with Ant Design Image component */}
        <div className="relative overflow-hidden  -secondary">
          <Image
            src={imageSrc}
            alt={item.caption || 'Academic figure'}
            fallback={fallbackSrc}
            placeholder={
              <div className="flex items-center justify-center h-64 bg-gray-100">
                <PictureOutlined style={{ fontSize: '48px', color: '#d9d9d9' }} />
              </div>
            }
            preview={{
              mask: (
                <div className="flex flex-col items-center justify-center text-white">
                  <PictureOutlined style={{ fontSize: '24px', marginBottom: '8px' }} />
                  <Text style={{ color: 'white', fontSize: '14px' }}>预览</Text>
                </div>
              )
            }}
            style={{ 
              width: '100%',
              height: '400px',
              objectFit: 'cover'
            }}
            className="hover:scale-105 transition-transform duration-500"
          />
          
          {/* Subtle Overlay for Better Text Readability */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/5 to-transparent pointer-events-none"></div>
        </div>
        
        {/* Caption */}
        {item.caption && (
          <div className="p-6 bg-theme-surface-elevated">
            <div className="text-center space-y-2">
              {/* Figure Number Tag */}
              <Tag 
                color="blue" 
                className="mb-2"
                style={{
                  borderRadius: '16px',
                  fontWeight: 600,
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em'
                }}
              >
                Figure {index + 1}
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