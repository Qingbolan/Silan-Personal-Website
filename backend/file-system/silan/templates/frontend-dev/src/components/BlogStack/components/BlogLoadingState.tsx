import React from 'react';
import { motion } from 'framer-motion';
import { BookOpen } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Spin, Alert, Button } from 'antd';
import { useTheme } from '../../ThemeContext';
import { useLanguage } from '../../LanguageContext';

interface BlogLoadingStateProps {
  loading: boolean;
  error?: boolean;
}

export const BlogLoadingState: React.FC<BlogLoadingStateProps> = ({ loading, error }) => {
  const navigate = useNavigate();
  const { colors } = useTheme();
  const { language } = useLanguage();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <Spin 
            size="large" 
            tip={language === 'en' ? 'Loading article...' : '加载文章中...'}
            indicator={
              <BookOpen 
                size={32} 
                className="animate-pulse" 
                style={{ color: colors.accent }} 
              />
            }
          >
            <div style={{ minHeight: '200px' }} />
          </Spin>
        </motion.div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <Alert
            message={language === 'en' ? 'Article Not Found' : '文章未找到'}
            description={language === 'en' ? 'The requested article could not be found.' : '无法找到请求的文章。'}
            type="error"
            showIcon
            action={
              <Button 
                type="primary" 
                onClick={() => navigate(-1)}
                style={{ borderRadius: '8px' }}
              >
                {language === 'en' ? 'Go Back' : '返回'}
              </Button>
            }
            style={{ 
              maxWidth: '400px',
              fontFamily: 'Georgia, "Times New Roman", serif'
            }}
          />
        </motion.div>
      </div>
    );
  }

  return null;
}; 