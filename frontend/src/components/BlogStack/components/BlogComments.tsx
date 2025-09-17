import React, { useState, useEffect } from 'react';
import { Card, Avatar, Button, Input, Form, Spin, Typography, Space, Tag, message, Popconfirm } from 'antd';
import { LikeOutlined, LikeFilled, MessageOutlined, DeleteOutlined, UserOutlined } from '@ant-design/icons';
import { useLanguage } from '../../LanguageContext';
import { useTheme } from '../../ThemeContext';
import { getClientFingerprint } from '../../../utils/fingerprint';

import { GoogleLogin, CredentialResponse } from '@react-oauth/google';

const { TextArea } = Input;
const { Text, Title } = Typography;

interface Comment {
  id: string;
  blog_post_id: string;
  parent_id?: string;
  author_name: string;
  author_avatar_url?: string;
  content: string;
  created_at: string;
  user_identity_id?: string;
  likes_count: number;
  is_liked_by_user: boolean;
  replies?: Comment[];
}

interface CurrentUser {
  id?: string;
  name?: string;
  email?: string;
  avatar_url?: string;
  provider?: string;
}


interface BlogCommentsProps {
  postId: string;
  postSlug?: string;
}

const BlogComments: React.FC<BlogCommentsProps> = ({ postId, postSlug }) => {
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
  const googleClientId = "423692235373-d2v539b53sm9cppehm4dqgnmjf8o7n23.apps.googleusercontent.com";

  const { language } = useLanguage();
  const { colors } = useTheme();
  const [comments, setComments] = useState<Comment[]>([]);
  const [replyingTo, setReplyingTo] = useState<string | null>(null);
  const [replyContent, setReplyContent] = useState('');
  const loginAvailable = Boolean(googleClientId);
  const loggedIn = Boolean(currentUser?.email || currentUser?.name);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [authorName, setAuthorName] = useState('');
  const [authorEmail, setAuthorEmail] = useState('');
  const [content, setContent] = useState('');
  const [total, setTotal] = useState(0);

  const isUUID = (s: string) => /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(s);

  const resolvePostId = async (): Promise<string | null> => {
    if (postId && isUUID(postId)) return postId;
    if (postSlug) {
      try {
        const resp = await fetch(`/api/v1/blog/posts/${postSlug}?lang=${language}`);
        if (resp.ok) {
          const b = await resp.json();
          if (b?.id && isUUID(b.id)) return b.id;
        }
      } catch {}
    }
    return postId || null;
  };

  const loadComments = async () => {
    try {
      setLoading(true);
      const pid = await resolvePostId();
      if (!pid) throw new Error('missing post id');

      // Build query parameters
      const params = new URLSearchParams({ lang: language });

      // Add fingerprint for like status
      try {
        const fingerprint = await getClientFingerprint();
        if (fingerprint) {
          params.append('fingerprint', fingerprint);
        }
      } catch (error) {
        console.warn('Failed to get fingerprint:', error);
      }

      // Add user identity if logged in
      if (currentUser?.id) {
        params.append('user_identity_id', currentUser.id);
      }

      const response = await fetch(`/api/v1/blog/posts/${pid}/comments?${params.toString()}`);
      if (response.ok) {
        const data = await response.json();
        setComments(data.comments || []);
        setTotal(data.total || 0);
      } else {
        const t = await response.text();
        console.error('Load comments failed:', response.status, t);
        setComments([]);
        setTotal(0);
      }
    } catch (error) {
      console.error('Failed to load comments:', error);
      setComments([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  // Google login -> verify with backend -> store user locally
  const authWithGoogle = async (idToken: string) => {
    if (!idToken) {
      message.error(language === 'en' ? 'Google credential missing' : '缺少 Google 登录凭证');
      return;
    }
    try {
      const resp = await fetch(`/api/v1/auth/google/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id_token: idToken }),
      });
      if (!resp.ok) {
        const t = await resp.text();
        throw new Error(t || `HTTP ${resp.status}`);
      }
      const user = await resp.json();
      setCurrentUser(user);
      try { localStorage.setItem('auth_user', JSON.stringify(user)); } catch {}
    } catch (e: any) {
      console.error('Google login failed:', e);
      message.error(language === 'en' ? 'Google login failed' : 'Google 登录失败');
    }
  };

  const submitComment = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!authorName.trim() || !content.trim()) return;
    let email = authorEmail.trim();
    if (currentUser && currentUser.email) {
      email = currentUser.email;
    } else {
      if (!email || email.length < 5 || !email.includes('@')) {
        message.error(language === 'en' ? 'Please enter a valid email' : '请输入有效的邮箱');
        return;
      }
    }

    try {
      setSubmitting(true);
      const fingerprint = await getClientFingerprint();

      const pid = await resolvePostId();
      if (!pid) throw new Error('missing post id');
      const response = await fetch(`/api/v1/blog/posts/${pid}/comments?lang=${language}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          author_name: (currentUser?.name || authorName).trim(),
          author_email: email,
          content: content.trim(),
          fingerprint,
          // Send user_identity_id if user is logged in
          user_identity_id: currentUser?.id || '',
          parent_id: replyingTo || '',
        }),
      });

      if (response.ok) {
        // Only clear name/email for anonymous users, not for logged-in users
        if (!currentUser) {
          setAuthorName('');
          setAuthorEmail('');
        }
        setContent(''); // Always clear content
        setReplyingTo(null);
        setReplyContent('');
        loadComments();
      } else {
        const errorData = await response.text();
        console.error('Failed to submit comment:', response.status, errorData);
        message.error(`Failed to submit comment: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      console.error('Failed to submit comment:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const submitReply = async (parentId: string) => {
    if (!replyContent.trim()) return;
    let email = authorEmail.trim();
    if (currentUser && currentUser.email) {
      email = currentUser.email;
    } else {
      if (!email || email.length < 5 || !email.includes('@')) {
        message.error(language === 'en' ? 'Please enter a valid email' : '请输入有效的邮箱');
        return;
      }
    }

    try {
      setSubmitting(true);
      const fingerprint = await getClientFingerprint();
      const pid = await resolvePostId();
      if (!pid) throw new Error('missing post id');

      const response = await fetch(`/api/v1/blog/posts/${pid}/comments?lang=${language}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          author_name: (currentUser?.name || authorName).trim(),
          author_email: email,
          content: replyContent.trim(),
          fingerprint,
          user_identity_id: currentUser?.id || '',
          parent_id: parentId,
        }),
      });

      if (response.ok) {
        setReplyContent('');
        setReplyingTo(null);
        loadComments();
      } else {
        const errorData = await response.text();
        console.error('Failed to submit reply:', response.status, errorData);
        message.error(`Failed to submit reply: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      console.error('Failed to submit reply:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const deleteComment = async (commentId: string) => {

    try {
      const response = await fetch(`/api/v1/blog/comments/${commentId}?lang=${language}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_identity_id: currentUser?.id || '',
          fingerprint: await getClientFingerprint(),
        }),
      });

      if (response.ok) {
        loadComments();
      } else {
        const errorData = await response.text();
        console.error('Failed to delete comment:', response.status, errorData);
        message.error(`Failed to delete comment: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      console.error('Failed to delete comment:', error);
    }
  };

  const likeComment = async (commentId: string) => {
    try {
      const fingerprint = await getClientFingerprint();
      const requestData: any = {
        lang: language
      };

      if (fingerprint) {
        requestData.fingerprint = fingerprint;
      }

      if (currentUser?.id) {
        requestData.user_identity_id = currentUser.id;
      }

      const response = await fetch(`/api/v1/blog/comments/${commentId}/like`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      if (response.ok) {
        const result = await response.json();

        // Update the specific comment in state
        setComments(prevComments => {
          const updateCommentInTree = (comments: Comment[]): Comment[] => {
            return comments.map(comment => {
              if (comment.id === commentId) {
                return {
                  ...comment,
                  likes_count: result.likes_count,
                  is_liked_by_user: result.is_liked_by_user
                };
              }

              if (comment.replies && comment.replies.length > 0) {
                return {
                  ...comment,
                  replies: updateCommentInTree(comment.replies)
                };
              }

              return comment;
            });
          };

          return updateCommentInTree(prevComments);
        });
      } else {
        const text = await response.text();
        console.error('Like failed:', response.status, text);
      }
    } catch (error) {
      console.error('Failed to like comment:', error);
    }
  };

  const renderComment = (comment: Comment, depth: number = 0): React.ReactNode => {
    const getDisplayName = (name: string) => {
      if (!name) return 'Anonymous';
      if (name.includes('@')) {
        return name.split('@')[0];
      }
      return name;
    };

    const displayName = getDisplayName(comment.author_name);
    const hasAvatar = comment.author_avatar_url;
    const canDelete = currentUser?.id && comment.user_identity_id === currentUser.id;

    return (
      <div key={comment.id} style={{ marginLeft: depth * 24 }}>
          <div className="flex items-start gap-3">
            <Avatar
              size={depth > 0 ? 32 : 40}
              src={hasAvatar ? comment.author_avatar_url : undefined}
              icon={!hasAvatar ? <UserOutlined /> : undefined}
              style={{
                backgroundColor: hasAvatar ? undefined : colors.primary,
                flexShrink: 0
              }}
            />

            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-2">
                <Space size="small">
                  <Text strong style={{ color: colors.textPrimary, fontSize: '14px' }}>
                    {displayName}
                  </Text>
                  {hasAvatar && (
                    <Tag color="blue" style={{ fontSize: '10px', margin: 0 }}>
                      {language === 'en' ? 'Verified' : '已验证'}
                    </Tag>
                  )}
                </Space>

                <Space size="small">
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {formatDate(comment.created_at)}
                  </Text>
                  {canDelete && (
                    <Popconfirm
                      title={language === 'en' ? 'Delete this comment?' : '确定要删除这条评论吗？'}
                      onConfirm={() => deleteComment(comment.id)}
                      okText={language === 'en' ? 'Yes' : '确定'}
                      cancelText={language === 'en' ? 'No' : '取消'}
                    >
                      <Button
                        type="text"
                        size="small"
                        danger
                        icon={<DeleteOutlined />}
                      />
                    </Popconfirm>
                  )}
                </Space>
              </div>

              <Text style={{ color: colors.textPrimary, fontSize: '14px', whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
                {comment.content}
              </Text>

              <div className="mt-3">
                <Space size="middle">
                  <Button
                    type="text"
                    size="small"
                    icon={comment.is_liked_by_user ? <LikeFilled /> : <LikeOutlined />}
                    onClick={() => likeComment(comment.id)}
                    style={{
                      color: comment.is_liked_by_user ? '#ff4d4f' : colors.textSecondary,
                      padding: '2px 8px',
                      height: 'auto'
                    }}
                  >
                    {comment.likes_count || 0}
                  </Button>

                  {loginAvailable && depth < 3 && (
                    <Button
                      type={replyingTo === comment.id ? "primary" : "text"}
                      size="small"
                      icon={<MessageOutlined />}
                      onClick={() => setReplyingTo(replyingTo === comment.id ? null : comment.id)}
                      style={{ padding: '2px 8px', height: 'auto' ,
                        color: replyingTo === comment.id ? colors.primary : colors.textSecondary
                      }}
                    >
                      {language === 'en' ? 'Reply' : '回复'}
                    </Button>
                  )}
                </Space>
              </div>

              {replyingTo === comment.id && (
                <Card
                  size="small"
                  className="mt-3"
                  style={{
                    backgroundColor: colors.surface,
                    borderColor: colors.cardBorder
                  }}
                >
                  <TextArea
                    placeholder={language === 'en' ? 'Write a reply...' : '写下您的回复...'}
                    value={replyContent}
                    onChange={(e) => setReplyContent(e.target.value)}
                    rows={2}
                    maxLength={500}
                    showCount
                    style={{
                      backgroundColor: colors.background,
                      borderColor: colors.cardBorder,
                      marginBottom: 12
                    }}
                  />
                  <Space>
                    <Button
                      type="primary"
                      size="small"
                      onClick={() => submitReply(comment.id)}
                      loading={submitting}
                      disabled={!replyContent.trim()}
                    >
                      {language === 'en' ? 'Reply' : '回复'}
                    </Button>
                    <Button
                      size="small"
                      onClick={() => { setReplyingTo(null); setReplyContent(''); }}
                    >
                      {language === 'en' ? 'Cancel' : '取消'}
                    </Button>
                  </Space>
                </Card>
              )}
            </div>
          </div>
        {comment.replies && comment.replies.length > 0 && (
          <div className="ml-2">
            {comment.replies.map(reply => renderComment(reply, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  useEffect(() => {
    loadComments();
  }, [postId, language]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString(language === 'zh' ? 'zh-CN' : 'en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };


  // Load current user from localStorage (placeholder until backend auth is ready)
  useEffect(() => {
    try {
      const raw = localStorage.getItem('auth_user');
      if (raw) {
        const u = JSON.parse(raw);
        if (u && (u.name || u.email)) setCurrentUser(u);
      }
    } catch {}
  }, []);

  // Sync name/email when currentUser changes so submit button enables
  useEffect(() => {
    if (currentUser) {
      if (currentUser.name) setAuthorName(currentUser.name);
      if (currentUser.email) setAuthorEmail(currentUser.email);
    }
  }, [currentUser]);

  // Hide the entire comments block when login is unavailable and there are no comments
  const shouldHide = !loginAvailable && !loggedIn && !loading && (comments.length === 0 || total === 0);

  if (shouldHide) {
    return null;
  }

  return (
    <div className="max-w-4xl mx-auto mt-8">
      <div>
        <Title level={4} style={{ color: colors.textPrimary, marginBottom: 16 }}>
          {language === 'en' ? 'Comments' : '评论'} ({total})
        </Title>

        {/* Auth status / Login */}
        <div className="mb-6">
          {currentUser ? (
            <div className="flex items-center justify-between">
              <Space>
                <Avatar
                  size={32}
                  src={currentUser.avatar_url}
                  icon={!currentUser.avatar_url ? <UserOutlined /> : undefined}
                />
                <Text type="secondary">
                  {language === 'en' ? 'Logged in as' : '已登录：'} {currentUser.name || currentUser.email}
                </Text>
              </Space>
              <Button
                size="small"
                onClick={() => { try { localStorage.removeItem('auth_user'); } catch {}; setCurrentUser(null); }}
              >
                {language === 'en' ? 'Logout' : '退出'}
              </Button>
            </div>
          ) : (
            googleClientId ? (
              <GoogleLogin
                onSuccess={(cred: CredentialResponse) => {
                  const id = cred?.credential;
                  if (id) {
                    authWithGoogle(id);
                  } else {
                    message.error(language === 'en' ? 'No credential received' : '未收到登录凭证');
                  }
                }}
                onError={() => {
                  message.error(language === 'en' ? 'Google login failed' : 'Google 登录失败');
                }}
              />
            ) : null
          )}
        </div>

        {/* Comment Form */}
        {loginAvailable ? (
          loggedIn ? (
            <Card
              size="small"
              className="mb-6"
              style={{
                backgroundColor: colors.background,
                borderColor: colors.cardBorder
              }}
            >
              <Form
                onFinish={() => submitComment()}
                layout="vertical"
              >
                {!currentUser && (
                  <Form.Item
                    name="email"
                    rules={[
                      { required: true, message: language === 'en' ? 'Please enter your email' : '请输入邮箱' },
                      { type: 'email', message: language === 'en' ? 'Please enter a valid email' : '请输入有效的邮箱' }
                    ]}
                  >
                    <Input
                      placeholder={language === 'en' ? 'Your email (for verification)' : '邮箱（用于验证）'}
                      value={authorEmail}
                      onChange={(e) => setAuthorEmail(e.target.value)}
                      maxLength={255}
                      style={{
                        backgroundColor: colors.background,
                        borderColor: colors.cardBorder
                      }}
                    />
                  </Form.Item>
                )}
                <Form.Item>
                  <TextArea
                    placeholder={language === 'en' ? 'Write a comment...' : '写下您的评论...'}
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    rows={3}
                    maxLength={500}
                    showCount
                    style={{
                      backgroundColor: colors.background,
                      borderColor: colors.cardBorder
                    }}
                  />
                </Form.Item>
                <Form.Item>
                  <Button
                    type="primary"
                    htmlType="submit"
                    loading={submitting}
                    disabled={
                      !(currentUser?.name || authorName.trim()) ||
                      (!currentUser && (!authorEmail.trim() || !authorEmail.includes('@'))) ||
                      !content.trim()
                    }
                  >
                    {language === 'en' ? 'Submit Comment' : '提交评论'}
                  </Button>
                </Form.Item>
              </Form>
            </Card>
          ) : (
            <Card size="small" className="mb-6">
              <Text type="secondary">
                {language === 'en' ? 'Please login to post a comment.' : '请先登录后再发表评论。'}
              </Text>
            </Card>
          )
        ) : null}

        {/* Comments List */}
        {loading ? (
          <div className="text-center py-8">
            <Spin size="large" />
            <div className="mt-2">
              <Text type="secondary">
                {language === 'en' ? 'Loading comments...' : '加载评论中...'}
              </Text>
            </div>
          </div>
        ) : comments.length === 0 ? (
          <div className="text-center py-8">
            <Text type="secondary">
              {language === 'en' ? 'No comments yet. Be the first to comment!' : '暂无评论，来发表第一条评论吧！'}
            </Text>
          </div>
        ) : (
          <div>
            {comments.filter(comment => !comment.parent_id).map(comment => renderComment(comment))}
          </div>
        )}
      </div>
    </div>
  );
};

export default BlogComments;