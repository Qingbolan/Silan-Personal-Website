import React from 'react';
import { List, Input, Button, Avatar, Typography, Divider } from 'antd';
import { UserOutlined } from '@ant-design/icons';
import { Comment } from '../types/blog';
import { useTheme } from '../../ThemeContext';
import { useLanguage } from '../../LanguageContext';

const { TextArea } = Input;
const { Title, Paragraph } = Typography;

interface BlogCommentsProps {
  comments: Comment[];
  newComment: string;
  onSetNewComment: (comment: string) => void;
  onAddComment: () => void;
}

export const BlogComments: React.FC<BlogCommentsProps> = ({
  comments,
  newComment,
  onSetNewComment,
  onAddComment
}) => {
  const { colors } = useTheme();
  const { language } = useLanguage();

  return (
    <section className="mt-32 pt-16">
      <Divider />
      
      <Title level={2} style={{ 
        textAlign: 'center',
        color: colors.textPrimary,
        fontFamily: 'Georgia, "Times New Roman", serif',
        fontWeight: 300
      }}>
        {language === 'en' ? 'Discussion' : '讨论'} ({comments.length})
      </Title>

      {/* Add Comment */}
      <div className="mb-16 max-w-4xl mx-auto">
        <TextArea
          value={newComment}
          onChange={(e) => onSetNewComment(e.target.value)}
          placeholder={language === 'en' ? 'Share your thoughts...' : '分享你的想法...'}
          rows={4}
          style={{
            borderRadius: '8px',
            fontFamily: 'Georgia, "Times New Roman", serif'
          }}
        />
        <Button
          type="primary"
          onClick={onAddComment}
          disabled={!newComment.trim()}
          className="mt-4"
          style={{ 
            borderRadius: '8px',
            fontFamily: 'Georgia, "Times New Roman", serif'
          }}
        >
          {language === 'en' ? 'Post Comment' : '发表评论'}
        </Button>
      </div>

      {/* Comments List */}
      <div className="max-w-4xl mx-auto">
        <List
          itemLayout="vertical"
          dataSource={comments}
          renderItem={(comment) => (
            <List.Item
              key={comment.id}
              style={{
                paddingLeft: '24px',
                borderLeft: `2px solid ${colors.cardBorder}`
              }}
            >
              <List.Item.Meta
                avatar={
                  <Avatar icon={<UserOutlined />}>
                    {comment.author[0]}
                  </Avatar>
                }
                title={
                  <span style={{ 
                    color: colors.textPrimary,
                    fontFamily: 'Georgia, "Times New Roman", serif',
                    fontWeight: 500
                  }}>
                    {comment.author}
                  </span>
                }
                description={
                  <span style={{ 
                    color: colors.textTertiary,
                    fontFamily: 'Georgia, "Times New Roman", serif'
                  }}>
                    {new Date(comment.timestamp).toLocaleDateString()}
                  </span>
                }
              />
              <Paragraph style={{ 
                color: colors.textSecondary,
                fontFamily: 'Georgia, "Times New Roman", serif',
                fontWeight: 300,
                marginTop: '8px'
              }}>
                {comment.content}
              </Paragraph>
            </List.Item>
          )}
        />
      </div>
    </section>
  );
}; 