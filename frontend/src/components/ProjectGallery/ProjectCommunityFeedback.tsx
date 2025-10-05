import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MessageSquare,
  Plus,
  Heart,
  Reply,
  Send,
  Lightbulb,
  Bug,
  HelpCircle
} from 'lucide-react';
import { Button, Input, Select, Checkbox, Tag, Popconfirm, message } from 'antd';
import { useLanguage } from '../LanguageContext';
import { Comment, Reply as ReplyType, CommunityStats } from '../../types/community';
import { getClientFingerprint } from '../../utils/fingerprint';
import {
  listProjectComments,
  createProjectComment,
  likeProjectComment,
  deleteProjectComment,
  type ProjectCommentData
} from '../../api/projects/projectApi';
import { GoogleLogin, CredentialResponse } from '@react-oauth/google';

const { TextArea } = Input;

interface ProjectCommunityFeedbackProps {
  projectId: string;
}

const ProjectCommunityFeedback: React.FC<ProjectCommunityFeedbackProps> = ({ projectId }) => {
  const getCurrentUser = (): { id?: string; name?: string; email?: string } | null => {
    try {
      const raw = localStorage.getItem('auth_user');
      if (!raw) return null;
      const u = JSON.parse(raw);
      if (u && (u.id || u.email || u.name)) return u;
    } catch {}
    return null;
  };

  const mapProjectToCommunity = (node: ProjectCommentData): Comment => ({
    id: node.id,
    author: node.author_name || 'User',
    avatar: node.author_avatar_url,
    content: node.content,
    timestamp: new Date(node.created_at),
    likes: node.likes_count,
    replies: (node.replies || []).map(mapProjectToCommunityReply),
    tags: [],
    type: (node.type as Comment['type']) || 'general',
    status: undefined,
    isAnonymous: !node.user_identity_id,
  });

  const mapProjectToCommunityReply = (node: ProjectCommentData): ReplyType => ({
    id: node.id,
    author: node.author_name || 'User',
    avatar: node.author_avatar_url,
    content: node.content,
    timestamp: new Date(node.created_at),
    likes: node.likes_count,
    isAnonymous: !node.user_identity_id,
  });

  const { language } = useLanguage();

  const [comments, setComments] = useState<Comment[]>([]);
  const [ownerMap, setOwnerMap] = useState<Record<string, string>>({});
  const [newComment, setNewComment] = useState('');
  const [filterType, setFilterType] = useState<'general' | Comment['type']>('general');
  const [isAnonymous, setIsAnonymous] = useState(false);
  const [showReplyForm, setShowReplyForm] = useState<string | null>(null);
  const [replyContent, setReplyContent] = useState('');
  const [stats, setStats] = useState<CommunityStats>({
    totalComments: 0,
    totalSuggestions: 0,
    resolvedSuggestions: 0,
    activeDiscussions: 0,
    contributors: 0
  });

  // Auth state
  const [currentUser, setCurrentUser] = useState<any>(null);
  useEffect(() => {
    try {
      const raw = localStorage.getItem('auth_user');
      if (raw) {
        const u = JSON.parse(raw);
        if (u && (u.id || u.email)) setCurrentUser(u);
      }
    } catch {}
  }, []);

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
    } catch (e) {
      console.error('Google login failed:', e);
      message.error(language === 'en' ? 'Google login failed' : 'Google 登录失败');
    }
  };

  // Load comments
  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      if (!projectId) return;

      try {
        const fp = getClientFingerprint();
        const user = getCurrentUser();
        const typesToLoad: Comment['type'][] = ['general', 'suggestion', 'question', 'bug-report'];
        const results = await Promise.all(
          typesToLoad.map(t => listProjectComments(projectId, t, fp, user?.id || undefined, language as 'en' | 'zh'))
        );
        const items: ProjectCommentData[] = results.flat();
        if (cancelled) return;

        // Build owner map for delete permission (user_identity based)
        const owners: Record<string, string> = {};
        const collectOwners = (nodes: ProjectCommentData[]) => {
          nodes.forEach(n => {
            if (n.user_identity_id) owners[n.id] = n.user_identity_id;
            if (n.replies && n.replies.length) collectOwners(n.replies);
          });
        };
        collectOwners(items);
        setOwnerMap(owners);

        const mapped = items.filter(Boolean).map(mapProjectToCommunity)
          .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
        setComments(mapped);
        updateStats(mapped);
      } catch (e) {
        console.warn('Failed to load project comments:', e);
      }
    };
    load();
    return () => { cancelled = true; };
  }, [projectId, language, filterType]);

  const updateStats = (commentsList: Comment[]) => {
    const totalComments = commentsList.length;
    const suggestions = commentsList.filter(c => c.type === 'suggestion');
    const resolved = suggestions.filter(s => s.status === 'resolved');
    const active = commentsList.filter(c => c.status !== 'resolved').length;
    const contributors = new Set(commentsList.map(c => c.author)).size;

    setStats({
      totalComments,
      totalSuggestions: suggestions.length,
      resolvedSuggestions: resolved.length,
      activeDiscussions: active,
      contributors
    });
  };

  const submitComment = async () => {
    if (!newComment.trim()) return;

    try {
      const fp = getClientFingerprint();
      const user = getCurrentUser();
      await createProjectComment(
        projectId,
        newComment.trim(),
        fp,
        {
          type: filterType,
          userIdentityId: user?.id,
          authorName: user?.name || (isAnonymous ? (language === 'en' ? 'Anonymous' : '匿名用户') : 'User'),
          authorEmail: user?.email || (isAnonymous ? 'anonymous@example.com' : ''),
          language: language as 'en' | 'zh',
        }
      );
      setNewComment('');

      // Reload comments
      const typesToLoad: Comment['type'][] = ['general', 'suggestion', 'question', 'bug-report'];
      const results = await Promise.all(
        typesToLoad.map(t => listProjectComments(projectId, t, fp, user?.id || undefined, language as 'en' | 'zh'))
      );
      const merged = results.flat().map(mapProjectToCommunity)
        .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
      setComments(merged);
      updateStats(merged);
    } catch (e) {
      console.error('Failed to create project comment:', e);
    }
  };

  const submitReply = async (commentId: string) => {
    if (!replyContent.trim()) return;

    try {
      const fp = getClientFingerprint();
      const user = getCurrentUser();
      const parent = comments.find(c => c.id === commentId);
      const parentType = parent?.type || 'general';

      await createProjectComment(
        projectId,
        replyContent.trim(),
        fp,
        {
          type: parentType,
          userIdentityId: user?.id,
          authorName: user?.name || (isAnonymous ? (language === 'en' ? 'Anonymous' : '匿名用户') : 'User'),
          authorEmail: user?.email || (isAnonymous ? 'anonymous@example.com' : ''),
          parentId: commentId,
          language: language as 'en' | 'zh',
        }
      );
      setReplyContent('');
      setShowReplyForm(null);

      // Reload comments
      const typesToLoad: Comment['type'][] = ['general', 'suggestion', 'question', 'bug-report'];
      const results = await Promise.all(
        typesToLoad.map(t => listProjectComments(projectId, t, fp, user?.id || undefined, language as 'en' | 'zh'))
      );
      const merged = results.flat().map(mapProjectToCommunity)
        .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
      setComments(merged);
      updateStats(merged);
    } catch (e) {
      console.error('Failed to create reply:', e);
    }
  };

  const likeComment = async (commentId: string) => {
    try {
      const fp = getClientFingerprint();
      const user = getCurrentUser();
      await likeProjectComment(commentId, fp, user?.id || undefined, language as 'en' | 'zh');

      // Reload comments
      const typesToLoad: Comment['type'][] = ['general', 'suggestion', 'question', 'bug-report'];
      const results = await Promise.all(
        typesToLoad.map(t => listProjectComments(projectId, t, fp, user?.id || undefined, language as 'en' | 'zh'))
      );
      const merged = results.flat().map(mapProjectToCommunity)
        .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
      setComments(merged);
      updateStats(merged);
    } catch (e) {
      console.error('Failed to like project comment:', e);
    }
  };

  const likeReply = async (_commentId: string, replyId: string) => {
    try {
      const fp = getClientFingerprint();
      const user = getCurrentUser();
      await likeProjectComment(replyId, fp, user?.id || undefined, language as 'en' | 'zh');

      // Reload comments
      const typesToLoad: Comment['type'][] = ['general', 'suggestion', 'question', 'bug-report'];
      const results = await Promise.all(
        typesToLoad.map(t => listProjectComments(projectId, t, fp, user?.id || undefined, language as 'en' | 'zh'))
      );
      const merged = results.flat().map(mapProjectToCommunity)
        .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
      setComments(merged);
      updateStats(merged);
    } catch (e) {
      console.error('Failed to like project reply:', e);
    }
  };

  const handleDeleteComment = async (commentId: string) => {
    try {
      const fp = getClientFingerprint();
      const user = getCurrentUser();
      await deleteProjectComment(commentId, { fingerprint: fp, userIdentityId: user?.id, language: language as 'en' | 'zh' });

      // Reload comments
      const typesToLoad: Comment['type'][] = ['general', 'suggestion', 'question', 'bug-report'];
      const results = await Promise.all(
        typesToLoad.map(t => listProjectComments(projectId, t, fp, user?.id || undefined, language as 'en' | 'zh'))
      );
      const merged = results.flat().map(mapProjectToCommunity)
        .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
      setComments(merged);
      updateStats(merged);
    } catch (e) {
      console.error('Failed to delete comment:', e);
    }
  };

  const handleDeleteReply = async (_commentId: string, replyId: string) => {
    try {
      const fp = getClientFingerprint();
      const user = getCurrentUser();
      await deleteProjectComment(replyId, { fingerprint: fp, userIdentityId: user?.id, language: language as 'en' | 'zh' });

      // Reload comments
      const typesToLoad: Comment['type'][] = ['general', 'suggestion', 'question', 'bug-report'];
      const results = await Promise.all(
        typesToLoad.map(t => listProjectComments(projectId, t, fp, user?.id || undefined, language as 'en' | 'zh'))
      );
      const merged = results.flat().map(mapProjectToCommunity)
        .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
      setComments(merged);
      updateStats(merged);
    } catch (e) {
      console.error('Failed to delete reply:', e);
    }
  };

  const updateCommentStatus = (commentId: string, status: Comment['status']) => {
    setComments(prev => prev.map(comment =>
      comment.id === commentId
        ? { ...comment, status }
        : comment
    ));
  };

  const filteredComments = comments.filter(comment =>
    comment.type === filterType
  );

  const typeIcons = {
    general: <MessageSquare size={16} />,
    suggestion: <Lightbulb size={16} />,
    question: <HelpCircle size={16} />,
    'bug-report': <Bug size={16} />
  };

  const formatRelativeTime = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return language === 'en' ? 'Just now' : '刚刚';
    if (minutes < 60) return language === 'en' ? `${minutes}m ago` : `${minutes}分钟前`;
    if (hours < 24) return language === 'en' ? `${hours}h ago` : `${hours}小时前`;
    return language === 'en' ? `${days}d ago` : `${days}天前`;
  };

  return (
    <div className="space-y-6">
      {/* Stats Overview */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-theme-card rounded-xl p-4 shadow-theme-md">
          <div className="text-2xl font-bold text-theme-primary">{stats.totalComments}</div>
          <div className="text-sm text-theme-secondary">
            {language === 'en' ? 'Total Messages' : '总留言数'}
          </div>
        </div>
        <div className="bg-theme-card rounded-xl p-4 shadow-theme-md">
          <div className="text-2xl font-bold text-theme-primary">{stats.totalSuggestions}</div>
          <div className="text-sm text-theme-secondary">
            {language === 'en' ? 'Suggestions' : '建议数'}
          </div>
        </div>
        <div className="bg-theme-card rounded-xl p-4 shadow-theme-md">
          <div className="text-2xl font-bold text-theme-primary">{stats.resolvedSuggestions}</div>
          <div className="text-sm text-theme-secondary">
            {language === 'en' ? 'Resolved' : '已解决'}
          </div>
        </div>
        <div className="bg-theme-card rounded-xl p-4 shadow-theme-md">
          <div className="text-2xl font-bold text-theme-primary">{stats.activeDiscussions}</div>
          <div className="text-sm text-theme-secondary">
            {language === 'en' ? 'Active' : '活跃讨论'}
          </div>
        </div>
        <div className="bg-theme-card rounded-xl p-4 shadow-theme-md">
          <div className="text-2xl font-bold text-theme-primary">{stats.contributors}</div>
          <div className="text-sm text-theme-secondary">
            {language === 'en' ? 'Contributors' : '参与者'}
          </div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap gap-2">
        {['general', 'suggestion', 'question', 'bug-report'].map((type) => (
          <button
            key={type}
            onClick={() => setFilterType(type as any)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
              filterType === type
                ? 'bg-theme-primary text-white'
                : 'bg-theme-surface text-theme-secondary hover:bg-theme-hover'
            }`}
          >
            <span className="text-sm">
              {type === 'general' && (language === 'en' ? 'General' : '一般')}
              {type === 'suggestion' && (language === 'en' ? 'Suggestions' : '建议')}
              {type === 'question' && (language === 'en' ? 'Questions' : '问题')}
              {type === 'bug-report' && (language === 'en' ? 'Bug Reports' : '错误报告')}
            </span>
          </button>
        ))}
      </div>

      {/* New Comment Form */}
      <div className="bg-theme-card rounded-xl p-6 shadow-theme-md">
        <h3 className="text-lg font-semibold mb-4 text-theme-primary flex items-center gap-2">
          <Plus size={20} />
          {language === 'en' ? 'Share Your Thoughts' : '分享您的想法'}
        </h3>

        {/* Auth */}
        <div className="mb-3 flex items-center justify-between">
          {currentUser ? (
            <div className="text-sm text-theme-secondary">
              {(language === 'en' ? 'Logged in as: ' : '已登录：')}
              <span className="text-theme-primary font-medium">{currentUser.name || currentUser.email}</span>
              <Button size="small" className="ml-3" onClick={() => { try { localStorage.removeItem('auth_user'); } catch {}; setCurrentUser(null); }}>
                {language === 'en' ? 'Logout' : '退出'}
              </Button>
            </div>
          ) : (
            <GoogleLogin onSuccess={(cred: CredentialResponse) => { const id = cred?.credential || ''; authWithGoogle(id); }} />
          )}
        </div>

        {/* Comment Input */}
        <TextArea
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder={language === 'en' ? 'Write your message...' : '写下您的留言...'}
          rows={4}
          style={{ borderRadius: '8px' }}
        />

        {/* Submit Options */}
        <div className="flex items-center justify-between mt-4">
          <Checkbox
            checked={isAnonymous}
            onChange={(e) => setIsAnonymous(e.target.checked)}
          >
            {language === 'en' ? 'Post anonymously' : '匿名发布'}
          </Checkbox>

          <Button
            type="primary"
            onClick={submitComment}
            disabled={!newComment.trim()}
            icon={<Send size={16} />}
            style={{ borderRadius: '8px' }}
          >
            {language === 'en' ? 'Submit' : '提交'}
          </Button>
        </div>
      </div>

      {/* Comments List */}
      <div className="space-y-4">
        <AnimatePresence>
          {filteredComments.map((comment) => (
            <motion.div
              key={comment.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="bg-theme-card rounded-xl p-6 shadow-theme-md"
            >
              {/* Comment Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  {comment.avatar ? (
                    <img src={comment.avatar} alt={comment.author} className="w-10 h-10 rounded-full object-cover" />
                  ) : (
                    <div className="w-10 h-10 bg-gradient-primary rounded-full flex items-center justify-center text-white font-semibold">
                      {comment.isAnonymous ? '?' : comment.author[0].toUpperCase()}
                    </div>
                  )}
                  <div>
                    <div className="font-medium text-theme-primary">{comment.author}</div>
                    <div className="text-sm text-theme-secondary">{formatRelativeTime(comment.timestamp)}</div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {typeIcons[comment.type]}
                  {comment.status && (
                    <Select
                      value={comment.status}
                      onChange={(value) => updateCommentStatus(comment.id, value as Comment['status'])}
                      size="small"
                      style={{ minWidth: '100px' }}
                      aria-label={language === 'en' ? 'Update status' : '更新状态'}
                      options={[
                        {
                          value: 'open',
                          label: (
                            <Tag color="blue">{language === 'en' ? 'Open' : '未解决'}</Tag>
                          ),
                        },
                        {
                          value: 'in-progress',
                          label: (
                            <Tag color="orange">{language === 'en' ? 'In Progress' : '处理中'}</Tag>
                          ),
                        },
                        {
                          value: 'resolved',
                          label: (
                            <Tag color="green">{language === 'en' ? 'Resolved' : '已解决'}</Tag>
                          ),
                        },
                      ]}
                    />
                  )}
                </div>
              </div>

              {/* Comment Content */}
              <div className="mb-4">
                <p className="text-theme-primary whitespace-pre-wrap">{comment.content}</p>
              </div>

              {/* Comment Actions */}
              <div className="flex items-center gap-4">
                <button
                  onClick={() => likeComment(comment.id)}
                  className="flex items-center gap-2 text-theme-secondary hover:text-red-500 transition-colors"
                >
                  <Heart size={16} />
                  <span className="text-sm">{comment.likes}</span>
                </button>

                <button
                  onClick={() => setShowReplyForm(showReplyForm === comment.id ? null : comment.id)}
                  className="flex items-center gap-2 text-theme-secondary hover:text-theme-primary transition-colors"
                >
                  <Reply size={16} />
                  <span className="text-sm">
                    {language === 'en' ? 'Reply' : '回复'} ({comment.replies.length})
                  </span>
                </button>

                {/* Delete (only for owner) */}
                {(() => {
                  const u = getCurrentUser();
                  const canDelete = Boolean(u?.id && ownerMap[comment.id] === u.id);
                  if (!canDelete) return null;
                  return (
                    <Popconfirm
                      title={language === 'en' ? 'Delete this comment?' : '确定要删除这条评论吗？'}
                      onConfirm={() => handleDeleteComment(comment.id)}
                      okText={language === 'en' ? 'Yes' : '确定'}
                      cancelText={language === 'en' ? 'No' : '取消'}
                    >
                      <button className="text-sm text-red-500 hover:text-red-600">
                        {language === 'en' ? 'Delete' : '删除'}
                      </button>
                    </Popconfirm>
                  );
                })()}
              </div>

              {/* Reply Form */}
              {showReplyForm === comment.id && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="mt-4 pt-4 border-t border-theme-surface"
                >
                  <TextArea
                    value={replyContent}
                    onChange={(e) => setReplyContent(e.target.value)}
                    placeholder={language === 'en' ? 'Write a reply...' : '写下回复...'}
                    rows={3}
                    style={{ borderRadius: '8px' }}
                  />
                  <div className="flex justify-end gap-2 mt-2">
                    <Button onClick={() => setShowReplyForm(null)}>
                      {language === 'en' ? 'Cancel' : '取消'}
                    </Button>
                    <Button
                      type="primary"
                      onClick={() => submitReply(comment.id)}
                      disabled={!replyContent.trim()}
                      style={{ borderRadius: '8px' }}
                    >
                      {language === 'en' ? 'Reply' : '回复'}
                    </Button>
                  </div>
                </motion.div>
              )}

              {/* Replies */}
              {comment.replies.length > 0 && (
                <div className="mt-4 pt-4 border-t border-theme-surface space-y-3">
                  {comment.replies.map((reply) => (
                    <div key={reply.id} className="flex gap-3">
                      {reply.avatar ? (
                        <img src={reply.avatar} alt={reply.author} className="w-8 h-8 rounded-full object-cover" />
                      ) : (
                        <div className="w-8 h-8 bg-gradient-secondary rounded-full flex items-center justify-center text-white text-sm font-semibold">
                          {reply.isAnonymous ? '?' : reply.author[0].toUpperCase()}
                        </div>
                      )}
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium text-theme-primary text-sm">{reply.author}</span>
                          <span className="text-xs text-theme-secondary">{formatRelativeTime(reply.timestamp)}</span>
                        </div>
                        <p className="text-sm text-theme-primary">{reply.content}</p>
                        <button
                          onClick={() => likeReply(comment.id, reply.id)}
                          className="flex items-center gap-1 mt-2 text-theme-secondary hover:text-red-500 transition-colors"
                        >
                          <Heart size={14} />
                          <span className="text-xs">{reply.likes}</span>
                        </button>

                        {/* Delete reply (only for owner) */}
                        {(() => {
                          const u = getCurrentUser();
                          const canDelete = Boolean(u?.id && ownerMap[reply.id] === u.id);
                          if (!canDelete) return null;
                          return (
                            <Popconfirm
                              title={language === 'en' ? 'Delete this reply?' : '确定要删除这条回复吗？'}
                              onConfirm={() => handleDeleteReply(comment.id, reply.id)}
                              okText={language === 'en' ? 'Yes' : '确定'}
                              cancelText={language === 'en' ? 'No' : '取消'}
                            >
                              <button className="text-xs text-red-500 hover:text-red-600 ml-3">
                                {language === 'en' ? 'Delete' : '删除'}
                              </button>
                            </Popconfirm>
                          );
                        })()}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {filteredComments.length === 0 && (
        <div className="text-center py-12 text-theme-secondary">
          <MessageSquare size={48} className="mx-auto mb-4 opacity-50" />
          <p>{language === 'en' ? 'No messages yet. Be the first to share your thoughts!' : '还没有留言，成为第一个分享想法的人吧！'}</p>
        </div>
      )}
    </div>
  );
};

export default ProjectCommunityFeedback;