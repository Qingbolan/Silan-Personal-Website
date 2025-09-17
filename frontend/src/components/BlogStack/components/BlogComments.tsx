import React, { useState, useEffect } from 'react';
import { useLanguage } from '../../LanguageContext';
import { useTheme } from '../../ThemeContext';
import { getClientFingerprint } from '../../../utils/fingerprint';

import { GoogleLogin, CredentialResponse } from '@react-oauth/google';

interface Comment {
  id: string;
  blog_post_id: string;
  author_name: string;
  author_avatar_url?: string;
  content: string;
  created_at: string;
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
      const response = await fetch(`/api/v1/blog/posts/${pid}/comments?lang=${language}`);
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
        }),
      });

      if (response.ok) {
        // Only clear name/email for anonymous users, not for logged-in users
        if (!currentUser) {
          setAuthorName('');
          setAuthorEmail('');
        }
        setContent(''); // Always clear content
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
            {comments.map((comment) => {
              // // Generate avatar fallback using first letter of name
              // const getAvatarFallback = (name: string) => {
              //   const colorIndex = name.charCodeAt(0) % colors_avatar.length;
              //   return {
              //     backgroundColor: colors_avatar[colorIndex],
              //     color: 'white',
              //     display: 'flex',
              //     alignItems: 'center',
              //     justifyContent: 'center',
              //     fontSize: '14px',
              //     fontWeight: 'bold'
              //   };
              // };

              // Clean up author name (remove email domain if it's an email)
              const getDisplayName = (name: string) => {
                if (!name) return 'Anonymous';
                // If it looks like an email, just use the part before @
                if (name.includes('@')) {
                  return name.split('@')[0];
                }
                return name;
              };

              const displayName = getDisplayName(comment.author_name);
              const hasAvatar = comment.author_avatar_url;

              return (
                <div
                  key={comment.id}
                  className="border rounded-lg p-4"
                  style={{
                    borderColor: colors.cardBorder,
                    backgroundColor: colors.background,
                  }}
                >
                  <div className="flex items-start gap-3 mb-3">
                    {/* Avatar - always show, either real image or fallback */}
                    <div className="flex-shrink-0">
                      {hasAvatar ? (
                        <img
                          src={comment.author_avatar_url}
                          alt={displayName}
                          className="w-10 h-10 rounded-full object-cover border"
                          style={{ borderColor: colors.cardBorder }}
                          referrerPolicy="no-referrer"
                          onError={(e) => {
                            // If image fails to load, replace with fallback
                            const target = e.target as HTMLImageElement;
                            target.style.display = 'none';
                            const fallback = target.nextElementSibling as HTMLElement;
                            if (fallback) fallback.style.display = 'flex';
                          }}
                        />
                      ) : null}
                    </div>

                    {/* Comment content */}
                    <div className="flex-1 min-w-0">
                      {/* Author name and timestamp */}
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
                        <span className="text-xs flex-shrink-0" style={{ color: colors.textSecondary }}>
                          {formatDate(comment.created_at)}
                        </span>
                      </div>

                      {/* Comment text */}
                      <p style={{ color: colors.textPrimary }} className="whitespace-pre-wrap text-sm leading-relaxed">
                        {comment.content}
                      </p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default BlogComments;