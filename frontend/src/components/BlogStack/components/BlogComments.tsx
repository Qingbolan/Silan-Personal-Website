import React, { useState, useEffect } from 'react';
import { useLanguage } from '../../LanguageContext';
import { useTheme } from '../../ThemeContext';
import { getClientFingerprint } from '../../../utils/fingerprint';

import { GoogleLogin, CredentialResponse } from '@react-oauth/google';

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

  // Debug environment variable loading
  console.log('🔧 [BlogComments] Environment variables check:');
  console.log('- import.meta.env:', (import.meta as any)?.env);
  console.log('- VITE_GOOGLE_CLIENT_ID:', googleClientId);
  console.log('- loginAvailable will be:', Boolean(googleClientId));

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
      alert(language === 'en' ? 'Google credential missing' : '缺少 Google 登录凭证');
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
      alert(language === 'en' ? 'Google login failed' : 'Google 登录失败');
    }
  };

  const submitComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!authorName.trim() || !content.trim()) return;
    let email = authorEmail.trim();
    if (currentUser && currentUser.email) {
      email = currentUser.email;
    } else {
      if (!email || email.length < 5 || !email.includes('@')) {
        alert(language === 'en' ? 'Please enter a valid email' : '请输入有效的邮箱');

        return;
      }
    }

    try {
      setSubmitting(true);
      const fingerprint = getClientFingerprint();

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
        alert(`Failed to submit comment: ${response.status} ${response.statusText}`);
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
        alert(language === 'en' ? 'Please enter a valid email' : '请输入有效的邮箱');
        return;
      }
    }

    try {
      setSubmitting(true);
      const fingerprint = getClientFingerprint();
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
        alert(`Failed to submit reply: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      console.error('Failed to submit reply:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const deleteComment = async (commentId: string) => {
    if (!confirm(language === 'en' ? 'Are you sure you want to delete this comment?' : '确定要删除这条评论吗？')) {
      return;
    }

    try {
      const response = await fetch(`/api/v1/blog/comments/${commentId}?lang=${language}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_identity_id: currentUser?.id || '',
          fingerprint: getClientFingerprint(),
        }),
      });

      if (response.ok) {
        loadComments();
      } else {
        const errorData = await response.text();
        console.error('Failed to delete comment:', response.status, errorData);
        alert(`Failed to delete comment: ${response.status} ${response.statusText}`);
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
    const marginLeft = depth * 20;

    return (
      <div key={comment.id} style={{ marginLeft: `${marginLeft}px` }}>
        <div
          className="border rounded-lg p-4 mb-4"
          style={{
            borderColor: colors.cardBorder,
            backgroundColor: colors.background,
          }}
        >
          <div className="flex items-start gap-3 mb-3">
            <div className="flex-shrink-0">
              {hasAvatar ? (
                <img
                  src={comment.author_avatar_url}
                  alt={displayName}
                  className="w-10 h-10 rounded-full object-cover border"
                  style={{ borderColor: colors.cardBorder }}
                  referrerPolicy="no-referrer"
                  onError={(e) => {
                    const target = e.target as HTMLImageElement;
                    target.style.display = 'none';
                    const fallback = target.nextElementSibling as HTMLElement;
                    if (fallback) fallback.style.display = 'flex';
                  }}
                />
              ) : null}
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-sm" style={{ color: colors.textPrimary }}>
                    {displayName}
                  </span>
                  {comment.author_avatar_url && (
                    <span className="text-xs px-2 py-0.5 rounded-full" style={{
                      backgroundColor: colors.surface,
                      color: colors.textSecondary
                    }}>
                      {language === 'en' ? 'Verified' : '已验证'}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs flex-shrink-0" style={{ color: colors.textSecondary }}>
                    {formatDate(comment.created_at)}
                  </span>
                  {canDelete && (
                    <button
                      onClick={() => deleteComment(comment.id)}
                      className="text-xs px-2 py-1 rounded hover:bg-red-100"
                      style={{ color: 'red' }}
                    >
                      {language === 'en' ? 'Delete' : '删除'}
                    </button>
                  )}
                </div>
              </div>

              <p style={{ color: colors.textPrimary }} className="whitespace-pre-wrap text-sm leading-relaxed mb-3">
                {comment.content}
              </p>

              <div className="flex items-center gap-3">
                {/* Like button */}
                <button
                  onClick={() => likeComment(comment.id)}
                  className="flex items-center gap-1 text-xs px-2 py-1 rounded hover:bg-gray-100"
                  style={{
                    color: comment.is_liked_by_user ? colors.primary : colors.textSecondary,
                    backgroundColor: comment.is_liked_by_user ? `${colors.primary}20` : 'transparent'
                  }}
                >
                  <span>{comment.is_liked_by_user ? '❤️' : '🤍'}</span>
                  <span>{comment.likes_count || 0}</span>
                </button>

                {/* Reply button */}
                {loginAvailable && depth < 3 && (
                  <button
                    onClick={() => setReplyingTo(replyingTo === comment.id ? null : comment.id)}
                    className="text-xs px-2 py-1 rounded"
                    style={{
                      backgroundColor: replyingTo === comment.id ? colors.primary : colors.surface,
                      color: replyingTo === comment.id ? 'white' : colors.textSecondary
                    }}
                  >
                    {language === 'en' ? 'Reply' : '回复'}
                  </button>
                )}
              </div>

              {replyingTo === comment.id && (
                <div className="mt-3 p-3 border rounded" style={{ borderColor: colors.cardBorder }}>
                  <textarea
                    placeholder={language === 'en' ? 'Write a reply...' : '写下您的回复...'}
                    value={replyContent}
                    onChange={(e) => setReplyContent(e.target.value)}
                    className="w-full px-3 py-2 rounded border resize-none mb-2"
                    style={{ borderColor: colors.cardBorder, backgroundColor: colors.background, color: colors.textPrimary }}
                    rows={2}
                    maxLength={500}
                  />
                  <div className="flex gap-2">
                    <button
                      onClick={() => submitReply(comment.id)}
                      disabled={submitting || !replyContent.trim()}
                      className="px-3 py-1 rounded text-sm font-medium disabled:opacity-50"
                      style={{ backgroundColor: colors.primary, color: 'white' }}
                    >
                      {submitting ? (language === 'en' ? 'Submitting...' : '提交中...') : (language === 'en' ? 'Reply' : '回复')}
                    </button>
                    <button
                      onClick={() => { setReplyingTo(null); setReplyContent(''); }}
                      className="px-3 py-1 rounded text-sm"
                      style={{ backgroundColor: colors.surface, color: colors.textSecondary }}
                    >
                      {language === 'en' ? 'Cancel' : '取消'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {comment.replies && comment.replies.length > 0 && (
          <div>
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

  // Debug hiding logic
  console.log('🔧 [BlogComments] Hide logic check:');
  console.log('- loginAvailable:', loginAvailable);
  console.log('- loggedIn:', loggedIn);
  console.log('- loading:', loading);
  console.log('- comments.length:', comments.length);
  console.log('- total:', total);
  console.log('- shouldHide:', shouldHide);

  if (shouldHide) {
    console.log('❌ [BlogComments] Component hidden due to shouldHide logic');
    return null;
  }

  return (
    <div className="max-w-4xl mx-auto mt-16">
      <div
        className="border rounded-xl p-6"
        style={{ borderColor: colors.cardBorder, backgroundColor: colors.surface }}
      >


        <h3 className="text-lg font-semibold mb-4" style={{ color: colors.textPrimary }}>
          {language === 'en' ? 'Comments' : '评论'} ({total})
        </h3>

        {/* Auth status / Login */}
        <div className="mb-4 flex items-center justify-between">
          {currentUser ? (
            <div className="flex items-center gap-3 text-sm" style={{ color: colors.textSecondary }}>
              {currentUser.avatar_url ? (
                <img
                  src={currentUser.avatar_url}
                  alt={currentUser.name || currentUser.email || 'avatar'}
                  className="w-8 h-8 rounded-full object-cover"
                  referrerPolicy="no-referrer"
                />
              ) : null}
              <div>
                {language === 'en' ? 'Logged in as' : '已登录：'} {currentUser.name || currentUser.email}
              </div>
              <button
                type="button"
                onClick={() => { try { localStorage.removeItem('auth_user'); } catch {}; setCurrentUser(null); }}
                className="px-2 py-1 rounded border"
                style={{ borderColor: colors.cardBorder, color: colors.textSecondary }}
              >
                {language === 'en' ? 'Logout' : '退出'}
              </button>
            </div>
          ) : (
            googleClientId ? (
              <GoogleLogin
                onSuccess={(cred: CredentialResponse) => {
                  const id = cred?.credential;
                  if (id) {
                    authWithGoogle(id);
                  } else {
                    alert(language === 'en' ? 'No credential received' : '未收到登录凭证');
                  }
                }}
                onError={() => {
                  alert(language === 'en' ? 'Google login failed' : 'Google 登录失败');
                }}
              />
            ) : null
          )}
        </div>

        {/* Comment Form */}
        {loginAvailable ? (
          loggedIn ? (
            <form onSubmit={submitComment} className="mb-6">
              {/* Hide email field when logged in */}
              {!currentUser && (
                <div className="mb-4">
                  <input
                    type="email"
                    placeholder={language === 'en' ? 'Your email (for verification)' : '邮箱（用于验证）'}
                    value={authorEmail}
                    onChange={(e) => setAuthorEmail(e.target.value)}
                    disabled={false}
                    className="w-full px-3 py-2 rounded border"
                    style={{ borderColor: colors.cardBorder, backgroundColor: colors.background, color: colors.textPrimary }}
                    maxLength={255}
                    required={!currentUser}
                  />
                </div>
              )}
              <div className="mb-4">
                <textarea
                  placeholder={language === 'en' ? 'Write a comment...' : '写下您的评论...'}
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  className="w-full px-3 py-2 rounded border resize-none"
                  style={{ borderColor: colors.cardBorder, backgroundColor: colors.background, color: colors.textPrimary }}
                  rows={3}
                  maxLength={500}
                  required
                />
              </div>
              <button
                type="submit"
                disabled={
                  submitting ||
                  !(currentUser?.name || authorName.trim()) ||
                  (!currentUser && (!authorEmail.trim() || !authorEmail.includes('@'))) ||
                  !content.trim()
                }
                className="px-4 py-2 rounded font-medium disabled:opacity-50"
                style={{ backgroundColor: colors.primary, color: 'white' }}
              >
                {submitting ? (language === 'en' ? 'Submitting...' : '提交中...') : (language === 'en' ? 'Submit Comment' : '提交评论')}
              </button>
            </form>
          ) : (
            <div className="mb-6 text-sm" style={{ color: colors.textSecondary }}>
              {language === 'en' ? 'Please login to post a comment.' : '请先登录后再发表评论。'}
            </div>
          )
        ) : null}

        {/* Comments List */}
        {loading ? (
          <div className="text-center py-4" style={{ color: colors.textSecondary }}>
            {language === 'en' ? 'Loading comments...' : '加载评论中...'}
          </div>
        ) : comments.length === 0 ? (
          <div className="text-center py-8" style={{ color: colors.textSecondary }}>
            {language === 'en' ? 'No comments yet. Be the first to comment!' : '暂无评论，来发表第一条评论吧！'}
          </div>
        ) : (
          <div className="space-y-4">
            {comments.filter(comment => !comment.parent_id).map(comment => renderComment(comment))}
          </div>
        )}
      </div>
    </div>
  );
};

export default BlogComments;