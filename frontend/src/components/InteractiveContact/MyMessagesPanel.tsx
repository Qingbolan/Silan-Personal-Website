import React, { useEffect, useState } from 'react';
import { Card, Empty, Tag, Avatar, Collapse, Input, Button, message as antdMessage } from 'antd';
import { MessageSquare, Mail, Briefcase, Send } from 'lucide-react';
import { ContactMessage } from '../../types/contact';
import { useLanguage } from '../LanguageContext';
import { useAuth } from './AuthContext';

const { Panel } = Collapse;

const MyMessagesPanel: React.FC = () => {
  const [messages, setMessages] = useState<ContactMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [replyText, setReplyText] = useState<{ [key: string]: string }>({});
  const { language } = useLanguage();
  const { user } = useAuth();

  useEffect(() => {
    fetchMyMessages();
  }, []);

  const fetchMyMessages = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/contact/messages/my', {
        credentials: 'include',
      });
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

  const handleReply = async (messageId: string) => {
    if (!replyText[messageId]?.trim()) return;

    try {
      const response = await fetch(`/api/v1/contact/messages/${messageId}/reply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: replyText[messageId] }),
        credentials: 'include',
      });

      if (!response.ok) throw new Error('Failed to reply');

      antdMessage.success(language === 'en' ? 'Reply sent!' : '回复已发送！');
      setReplyText({ ...replyText, [messageId]: '' });
      fetchMyMessages();
    } catch (error) {
      antdMessage.error(language === 'en' ? 'Failed to send reply' : '回复失败');
    }
  };

  if (loading) {
    return <div className="text-center py-12 text-theme-secondary">{language === 'en' ? 'Loading...' : '加载中...'}</div>;
  }

  if (messages.length === 0) {
    return (
      <Empty
        image={<Mail size={64} className="mx-auto text-theme-tertiary" />}
        description={
          <span className="text-theme-secondary">
            {language === 'en' ? 'No messages yet' : '还没有留言'}
          </span>
        }
      />
    );
  }

  return (
    <div className="space-y-4">
      {messages.map((msg) => (
        <Card
          key={msg.id}
          className="card-interactive"
          style={{ borderRadius: '16px' }}
          bodyStyle={{ padding: '20px' }}
        >
          <div className="space-y-3">
            {/* Header */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Avatar size={40} src={msg.author_avatar}>
                  {msg.author_name.charAt(0).toUpperCase()}
                </Avatar>
                <div>
                  <div className="font-semibold text-theme-primary">{msg.author_name}</div>
                  <div className="text-xs text-theme-tertiary">
                    {new Date(msg.createdAt).toLocaleString()}
                  </div>
                </div>
              </div>
              <div className="flex gap-2">
                {msg.type === 'job' && (
                  <Tag className="rounded-full bg-theme-accent text-white border-theme-accent">
                    <Briefcase size={12} className="inline mr-1" />
                    Job
                  </Tag>
                )}
                <Tag
                  className={`rounded-full ${
                    msg.status === 'replied'
                      ? 'bg-theme-success text-white border-theme-success'
                      : msg.status === 'read'
                        ? 'bg-theme-primary text-white border-theme-primary'
                        : 'bg-theme-surface-elevated text-theme-secondary border-theme-card'
                  }`}
                >
                  {msg.status}
                </Tag>
                {msg.isPublic && (
                  <Tag className="rounded-full bg-theme-primary text-white border-theme-primary">
                    Public
                  </Tag>
                )}
              </div>
            </div>

            {/* Content */}
            <div className="bg-theme-surface-elevated p-4 rounded-xl">
              <div className="font-semibold text-theme-primary mb-2">{msg.subject}</div>
              <div className="text-theme-secondary text-sm">{msg.message}</div>
            </div>

            {/* Job Info */}
            {msg.type === 'job' && (msg.company || msg.position) && (
              <div className="flex gap-4 text-sm text-theme-secondary">
                {msg.company && (
                  <span>
                    <Briefcase size={14} className="inline mr-1" />
                    {msg.company}
                  </span>
                )}
                {msg.position && <span>{msg.position}</span>}
              </div>
            )}

            {/* Replies */}
            {msg.replies && msg.replies.length > 0 && (
              <div className="mt-4 space-y-2">
                <div className="font-semibold text-theme-primary text-sm flex items-center gap-2">
                  <MessageSquare size={16} />
                  {language === 'en' ? 'Replies' : '回复'}
                </div>
                {msg.replies.map((reply) => (
                  <div
                    key={reply.id}
                    className={`p-3 rounded-xl ${
                      reply.isFromOwner ? 'bg-theme-primary-20' : 'bg-theme-surface-elevated'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <Avatar size={24} src={reply.author_avatar}>
                        {reply.author_name.charAt(0).toUpperCase()}
                      </Avatar>
                      <span className="text-xs font-semibold text-theme-primary">
                        {reply.author_name}
                      </span>
                      {reply.isFromOwner && (
                        <Tag className="text-xs bg-theme-primary text-white border-theme-primary">
                          Silan
                        </Tag>
                      )}
                      <span className="text-xs text-theme-tertiary ml-auto">
                        {new Date(reply.createdAt).toLocaleString()}
                      </span>
                    </div>
                    <div className="text-sm text-theme-secondary">{reply.content}</div>
                  </div>
                ))}
              </div>
            )}

            {/* Reply Input */}
            <div className="flex gap-2 mt-4">
              <Input
                placeholder={language === 'en' ? 'Add a reply...' : '添加回复...'}
                value={replyText[msg.id] || ''}
                onChange={(e) => setReplyText({ ...replyText, [msg.id]: e.target.value })}
                onPressEnter={() => handleReply(msg.id)}
                className="rounded-xl"
              />
              <Button
                type="primary"
                icon={<Send size={16} />}
                onClick={() => handleReply(msg.id)}
                className="rounded-xl"
              >
                {language === 'en' ? 'Reply' : '回复'}
              </Button>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
};

export default MyMessagesPanel;
