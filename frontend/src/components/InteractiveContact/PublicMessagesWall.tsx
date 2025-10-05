import React, { useEffect, useState } from 'react';
import { Card, Avatar, Tag, Empty, Button, Spin } from 'antd';
import { MessageSquare, Building2, Briefcase, ChevronDown, ChevronUp, TrendingUp } from 'lucide-react';
import { ContactMessage } from '../../types/contact';
import { useLanguage } from '../LanguageContext';

const PublicMessagesWall: React.FC = () => {
  const [messages, setMessages] = useState<ContactMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAll, setShowAll] = useState(false);
  const { language } = useLanguage();

  useEffect(() => {
    fetchMessages();
  }, []);

  const fetchMessages = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/contact/messages/public');
      if (response.ok) {
        const data = await response.json();
        setMessages(data.items || []);
      }
    } catch (error) {
      console.error('Failed to fetch messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const displayMessages = showAll ? messages : messages.slice(0, 6);
  const jobMessages = messages.filter(m => m.type === 'job').length;
  const companiesCount = new Set(messages.filter(m => m.company).map(m => m.company)).size;

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Header */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="text-center bg-theme-surface-elevated border-0" style={{ borderRadius: '16px' }}>
          <div className="flex flex-col items-center">
            <TrendingUp size={32} className="text-theme-accent mb-2" />
            <div className="text-3xl font-bold text-theme-primary">{messages.length}</div>
            <div className="text-sm text-theme-secondary">
              {language === 'en' ? 'Total Messages' : '总留言数'}
            </div>
          </div>
        </Card>

        <Card className="text-center bg-theme-surface-elevated border-0" style={{ borderRadius: '16px' }}>
          <div className="flex flex-col items-center">
            <Briefcase size={32} className="text-theme-accent mb-2" />
            <div className="text-3xl font-bold text-theme-primary">{jobMessages}</div>
            <div className="text-sm text-theme-secondary">
              {language === 'en' ? 'Job Opportunities' : '工作机会'}
            </div>
          </div>
        </Card>

        <Card className="text-center bg-theme-surface-elevated border-0" style={{ borderRadius: '16px' }}>
          <div className="flex flex-col items-center">
            <Building2 size={32} className="text-theme-success mb-2" />
            <div className="text-3xl font-bold text-theme-primary">{companiesCount}</div>
            <div className="text-sm text-theme-secondary">
              {language === 'en' ? 'Companies' : '家公司'}
            </div>
          </div>
        </Card>
      </div>

      {/* Messages Title */}
      <div className="flex items-center justify-between">
        <h3 className="text-2xl font-bold text-theme-primary flex items-center gap-3">
          <div className="p-2 rounded-xl bg-gradient-primary">
            <MessageSquare size={24} className="text-white" />
          </div>
          {language === 'en' ? 'Recent Messages' : '最新留言'}
        </h3>
      </div>

      {/* Messages Grid */}
      {displayMessages.length === 0 ? (
        <Card className="card-interactive" style={{ borderRadius: '20px' }}>
          <Empty
            image={<MessageSquare size={64} className="mx-auto text-theme-tertiary" />}
            description={
              <span className="text-theme-secondary">
                {language === 'en' ? 'No public messages yet' : '还没有公开留言'}
              </span>
            }
          />
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {displayMessages.map((msg) => (
            <Card
              key={msg.id}
              className="card-interactive"
              style={{ borderRadius: '20px' }}
              bodyStyle={{ padding: '20px' }}
            >
              <div className="space-y-3">
                {/* Author */}
                <div className="flex items-center gap-3">
                  <Avatar
                    size={48}
                    src={msg.author_avatar}
                    className="shadow-theme-md"
                  >
                    {msg.author_name.charAt(0).toUpperCase()}
                  </Avatar>
                  <div className="flex-1 min-w-0">
                    <div className="font-semibold text-theme-primary truncate">
                      {msg.author_name}
                    </div>
                    {msg.type === 'job' && msg.company && msg.consentCompanyLogo && (
                      <div className="text-xs text-theme-secondary flex items-center gap-1 truncate">
                        <Building2 size={12} />
                        {msg.company}
                      </div>
                    )}
                  </div>
                  {msg.type === 'job' && (
                    <Tag className="rounded-full px-3 bg-theme-warning text-white border-theme-warning">
                      <Briefcase size={12} className="inline mr-1" />
                      Job
                    </Tag>
                  )}
                </div>

                {/* Subject */}
                <div className="bg-theme-surface-elevated backdrop-blur-sm rounded-xl p-3">
                  <div className="font-semibold text-theme-primary mb-1 line-clamp-1">
                    {msg.subject}
                  </div>
                  <div className="text-sm text-theme-secondary line-clamp-2">
                    {msg.message}
                  </div>
                </div>

                {/* Position (for job type) */}
                {msg.type === 'job' && msg.position && (
                  <div className="flex items-center gap-2 text-theme-secondary text-sm">
                    <Briefcase size={14} />
                    <span className="truncate">{msg.position}</span>
                  </div>
                )}

                {/* Replies count */}
                {msg.replies && msg.replies.length > 0 && (
                  <div className="flex items-center gap-2 text-theme-tertiary text-xs">
                    <MessageSquare size={14} />
                    <span>
                      {msg.replies.length} {language === 'en' ? 'replies' : '条回复'}
                    </span>
                  </div>
                )}

                {/* Date */}
                <div className="text-xs text-theme-tertiary">
                  {new Date(msg.createdAt).toLocaleDateString()}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Show More/Less */}
      {messages.length > 6 && (
        <div className="text-center">
          <Button
            type="default"
            size="large"
            onClick={() => setShowAll(!showAll)}
            icon={showAll ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
            className="rounded-full px-8"
          >
            {showAll
              ? (language === 'en' ? 'Show Less' : '收起')
              : (language === 'en' ? `Show ${messages.length - 6} More` : `显示更多 ${messages.length - 6} 条`)}
          </Button>
        </div>
      )}
    </div>
  );
};

export default PublicMessagesWall;
