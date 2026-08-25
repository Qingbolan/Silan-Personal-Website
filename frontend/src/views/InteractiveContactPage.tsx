import React, { useCallback, useMemo, useState } from 'react';
import { Mail, Phone, MapPin, Aperture, Briefcase, Contact, ArrowRight, User } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../components/LanguageContext';
import { Seo } from '../components/Seo';
import {
  useAuth,
} from '../components/InteractiveContact';
import ModernContactForm from '../components/InteractiveContact/ModernContactForm';
import PublicMessagesWall from '../components/InteractiveContact/PublicMessagesWall';
import { fetchMoments } from '../api/moments/momentApi';
import { fetchPersonalInfo, fetchExpectations, type ExpectationItem } from '../api/home/resumeApi';
import { resolveSocialLink } from '../utils/socialPlatform';
import { canonicalInternalPath } from '../utils/navigation';
import { useRemoteResource } from '../hooks/useRemoteResource';
import {
  Card,
  CardContent,
  Tabs,
  Button,
  Divider,
  Alert,
  EmptyState,
  Skeleton,
} from '../components/ds';

const TAB_PANEL_STACK_CLASS = 'mt-4 grid auto-rows-max content-start gap-2';

/** A single tappable list row — title + one-line description. */
const ListRow: React.FC<{
  title: string;
  description: string;
  onClick?: () => void;
}> = ({ title, description, onClick }) => (
  <button
    type="button"
    onClick={onClick}
    className="group block h-auto w-full self-start rounded-ds-md border border-transparent bg-ds-surface-1 px-3 py-2.5 text-left transition-[background-color,border-color,transform] duration-ds-fast hover:border-ds-border hover:bg-ds-surface-2 active:scale-[0.99]"
  >
    <div className="line-clamp-1 text-ds-sm font-medium text-ds-fg group-hover:text-ds-primary">{title}</div>
    {description && <div className="mt-0.5 line-clamp-2 text-ds-xs leading-5 text-ds-fg-muted">{description}</div>}
  </button>
);

const PanelLoading: React.FC<{ label: string }> = ({ label }) => (
  <div className="space-y-2 py-1" aria-label={label}>
    {[0, 1, 2].map((item) => <Skeleton key={item} shape="block" className="h-14" />)}
  </div>
);

const PanelError: React.FC<{ title: string; retryLabel: string; onRetry: () => void }> = ({
  title,
  retryLabel,
  onRetry,
}) => (
  <Alert tone="error" title={title}>
    <Button variant="ghost" size="sm" className="mt-2" onClick={onRetry}>
      {retryLabel}
    </Button>
  </Alert>
);

const formatContactLocation = (value: string, language: string) => {
  const normalized = value
    .replace(/🇸🇬|🇨🇳/g, '')
    .replace(/,\s*(China|中国)/gi, '')
    .replace(/\s*\/\s*/g, ' · ')
    .replace(/\s+/g, ' ')
    .trim();

  if (/Singapore/i.test(normalized) && /Beijing/i.test(normalized)) {
    return language === 'zh' ? '新加坡 · 北京' : 'Singapore · Beijing';
  }
  return normalized;
};

const ContactIntro: React.FC<{
  language: string;
  isAuthenticated: boolean;
  username?: string;
}> = ({ language, isAuthenticated, username }) => {
  const zh = language === 'zh';
  const title = isAuthenticated
    ? (zh ? `欢迎回来，${username}。` : `Welcome back, ${username}.`)
    : (zh ? '来聊聊。' : "Let's connect.");

  return (
    <header className="mb-7 grid gap-7 border-b border-ds-border pb-7 sm:mb-10 sm:grid-cols-[minmax(0,1fr)_15rem] sm:items-end sm:pb-10 lg:mb-12 lg:grid-cols-[minmax(0,1fr)_18rem]">
      <div className="min-w-0">
        <p className="font-mono text-ds-2xs font-medium uppercase tracking-[0.17em] text-ds-primary">
          {zh ? '联系' : 'Contact'}
        </p>
        <h1 className="mt-3 max-w-[12ch] text-balance text-4xl font-semibold leading-[0.96] tracking-[-0.045em] text-ds-fg sm:text-5xl lg:text-6xl">
          {title}
        </h1>
        <p className="mt-4 max-w-[42rem] text-pretty text-ds-base leading-7 text-ds-fg-muted sm:text-ds-lg">
          {zh
            ? '欢迎研究合作、系统工程项目与有价值的技术交流。'
            : 'Research collaborations, systems work, and thoughtful technical conversations.'}
        </p>
      </div>

      <aside className="hidden border-l border-ds-border pl-5 sm:block">
        <p className="font-mono text-ds-2xs font-medium uppercase tracking-[0.14em] text-ds-fg-subtle">
          {zh ? '工作坐标' : 'Working coordinates'}
        </p>
        <p className="mt-2 text-ds-sm font-medium text-ds-fg">
          {zh ? '新加坡 · 北京' : 'Singapore · Beijing'}
        </p>
        <p className="mt-1 text-ds-xs leading-5 text-ds-fg-muted">
          {zh ? '通常会在几天内认真回复。' : 'Thoughtful replies, usually within a few days.'}
        </p>
      </aside>
    </header>
  );
};

const InteractiveContactPageContent: React.FC = () => {
  const { language } = useLanguage();
  const { isAuthenticated, user } = useAuth();
  const [activeTab, setActiveTab] = useState('contact');
  const [refreshKey, setRefreshKey] = useState(0);
  const navigate = useNavigate();

  // The three tab bodies are independent resources. A failure in moments,
  // for example, must not erase the email/social facts from personal_info.
  const loadThoughts = useCallback(
    async () => (await fetchMoments(language)).slice(0, 3).map((moment) => ({
      id: moment.slug || moment.id,
      title: moment.title,
      description: moment.description || '',
    })),
    [language],
  );
  const loadJobs = useCallback(() => fetchExpectations(language), [language]);
  const loadContactProfile = useCallback(() => fetchPersonalInfo(language), [language]);

  const thoughtsResource = useRemoteResource('recent-thoughts', loadThoughts);
  const jobsResource = useRemoteResource<ExpectationItem[]>('expected-jobs', loadJobs);
  const contactResource = useRemoteResource('contact-profile', loadContactProfile);

  const recentThoughts = thoughtsResource.data ?? [];
  const expectedJobs = jobsResource.data ?? [];

  const contactInfo = useMemo(() => {
    const profile = contactResource.data;
    if (!profile) return [];
    return [
      profile.email && { type: 'email', value: profile.email },
      profile.phone && { type: 'phone', value: profile.phone },
      profile.location && { type: 'location', value: profile.location },
    ].filter(Boolean).map((entry) => {
      const { type, value } = entry as { type: string; value: string };
      const displayValue = type === 'location' ? formatContactLocation(value, language) : value;
      return {
        icon: type === 'email' ? <Mail size={18} /> : type === 'phone' ? <Phone size={18} /> : <MapPin size={18} />,
        title: type === 'email' ? (language === 'en' ? 'Email' : '邮箱') : type === 'phone' ? (language === 'en' ? 'Phone' : '电话') : (language === 'en' ? 'Location' : '位置'),
        value: displayValue,
        href: type === 'email' ? `mailto:${value}` : type === 'phone' ? `tel:${value.replace(/\s+/g, '')}` : `https://maps.google.com/?q=${encodeURIComponent(value)}`,
      };
    });
  }, [contactResource.data, language]);

  const socialLinks = useMemo(
    () => (contactResource.data?.social_links ?? []).map((social) => {
      const { icon, label } = resolveSocialLink(social.url, social.platform);
      return { icon, label, href: social.url };
    }),
    [contactResource.data],
  );

  return (
    <div className="min-h-screen pb-32 pt-8 sm:pb-20 sm:pt-12 lg:pt-16">
      <Seo
        title={language === 'en' ? 'Contact' : '联系'}
        description={
          language === 'en'
            ? 'Get in touch with Silan Hu — email, social links and a public message board.'
            : '联系胡思蓝 —— 邮箱、社交链接与公开留言板。'
        }
        path="/contact"
        lang={language as 'en' | 'zh'}
      />
      <div className="mx-auto max-w-6xl px-4 sm:px-8">
        <ContactIntro
          language={language}
          isAuthenticated={isAuthenticated}
          username={user?.username}
        />

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,1.08fr)_minmax(20rem,0.92fr)] lg:gap-8 [&>*]:self-start">
          {/* Left — contact form. */}
          <Card variant="outline" padding="none" className="overflow-hidden">
            <CardContent className="p-4 sm:p-5">
              <header className="mb-4 flex items-start justify-between gap-4 border-b border-ds-border pb-4">
                <div>
                  <p className="font-mono text-ds-2xs font-medium uppercase tracking-[0.14em] text-ds-primary">
                    {language === 'en' ? 'Message / 01' : '留言 / 01'}
                  </p>
                  <h2 className="mt-1 text-ds-lg font-semibold tracking-[-0.015em] text-ds-fg">
                    {language === 'en' ? 'Send a note' : '发送留言'}
                  </h2>
                </div>
                <p className="max-w-32 text-right text-ds-xs leading-5 text-ds-fg-subtle">
                  {language === 'en' ? 'Private by default' : '默认仅你我可见'}
                </p>
              </header>
              <ModernContactForm
                onMessageSent={() => {
                  setRefreshKey((prev) => prev + 1);
                }}
              />
            </CardContent>
          </Card>

          {/* Right — tabbed content. */}
          <Card variant="outline" padding="none" className="overflow-hidden">
            <CardContent className="p-4 sm:p-5">
              <header className="mb-4">
                <p className="font-mono text-ds-2xs font-medium uppercase tracking-[0.14em] text-ds-primary">
                  {language === 'en' ? 'Context / 02' : '更多信息 / 02'}
                </p>
                <h2 className="mt-1 text-ds-lg font-semibold tracking-[-0.015em] text-ds-fg">
                  {language === 'en' ? 'More ways to connect' : '更多联系线索'}
                </h2>
              </header>
              <Tabs
                value={activeTab}
                onChange={setActiveTab}
                appearance="pill"
                size="sm"
                fullWidth
                items={[
                  {
                    value: 'contact',
                    icon: <Contact />,
                    label: language === 'en' ? 'Contact' : '联系',
                  },
                  {
                    value: 'jobs',
                    icon: <Briefcase />,
                    label: language === 'en' ? 'Roles' : '职位',
                  },
                  {
                    value: 'thoughts',
                    icon: <Aperture />,
                    label: language === 'en' ? 'Moments' : '瞬间',
                  },
                ]}
              />

              {/* Recent thoughts. */}
              {activeTab === 'thoughts' && (
                <div className={TAB_PANEL_STACK_CLASS}>
                  {thoughtsResource.status === 'loading' ? (
                    <PanelLoading label={language === 'en' ? 'Loading recent moments' : '正在加载最新瞬间'} />
                  ) : thoughtsResource.status === 'error' ? (
                    <PanelError
                      title={language === 'en' ? 'Recent moments could not be loaded' : '最新瞬间加载失败'}
                      retryLabel={language === 'en' ? 'Try again' : '重试'}
                      onRetry={thoughtsResource.reload}
                    />
                  ) : recentThoughts.length === 0 ? (
                    <EmptyState
                      icon={<Aperture />}
                      title={language === 'en' ? 'No public moments yet' : '还没有公开瞬间'}
                      description={language === 'en' ? 'Published moments will appear here.' : '公开后的瞬间会显示在这里。'}
                    />
                  ) : (
                    recentThoughts.map((thought) => (
                      <ListRow
                        key={thought.id}
                        title={thought.title}
                        description={thought.description}
                        onClick={() => navigate(`/moments?id=${encodeURIComponent(thought.id)}`)}
                      />
                    ))
                  )}
                  <div className="flex justify-end pt-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      trailingIcon={<ArrowRight />}
                      onClick={() => navigate(canonicalInternalPath('/moments'))}
                    >
                      {language === 'en' ? 'Show More Moments' : '查看更多瞬间'}
                    </Button>
                  </div>
                </div>
              )}

              {/* Expected jobs. */}
              {activeTab === 'jobs' && (
                <div className={TAB_PANEL_STACK_CLASS}>
                  {jobsResource.status === 'loading' ? (
                    <PanelLoading label={language === 'en' ? 'Loading preferred roles' : '正在加载期待职位'} />
                  ) : jobsResource.status === 'error' ? (
                    <PanelError
                      title={language === 'en' ? 'Preferred roles could not be loaded' : '期待职位加载失败'}
                      retryLabel={language === 'en' ? 'Try again' : '重试'}
                      onRetry={jobsResource.reload}
                    />
                  ) : expectedJobs.length === 0 ? (
                    <EmptyState
                      icon={<Briefcase />}
                      title={language === 'en' ? 'No role preferences published' : '尚未发布职位偏好'}
                      description={language === 'en' ? 'Current role preferences are maintained in the résumé.' : '当前职位偏好由简历内容维护。'}
                    />
                  ) : (
                    expectedJobs.map((job) => (
                      <ListRow
                        key={job.id}
                        title={job.title}
                        description={job.description}
                        onClick={() => navigate('/')}
                      />
                    ))
                  )}
                  <div className="flex justify-end pt-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      leadingIcon={<User />}
                      trailingIcon={<ArrowRight />}
                      onClick={() => navigate('/')}
                    >
                      {language === 'en' ? 'Who Am I' : '关于我'}
                    </Button>
                  </div>
                </div>
              )}

              {/* Quick contact. */}
              {activeTab === 'contact' && (
                <div className="mt-4 grid auto-rows-max content-start gap-3">
                  {contactResource.status === 'loading' ? (
                    <PanelLoading label={language === 'en' ? 'Loading contact information' : '正在加载联系信息'} />
                  ) : contactResource.status === 'error' ? (
                    <PanelError
                      title={language === 'en' ? 'Contact information could not be loaded' : '联系信息加载失败'}
                      retryLabel={language === 'en' ? 'Try again' : '重试'}
                      onRetry={contactResource.reload}
                    />
                  ) : contactInfo.length === 0 && socialLinks.length === 0 ? (
                    <EmptyState
                      icon={<Contact />}
                      title={language === 'en' ? 'No public contact details' : '暂无公开联系信息'}
                      description={language === 'en' ? 'Use the message form to get in touch.' : '可以使用留言表单与我联系。'}
                    />
                  ) : (
                    <>
                  {/* Contact info rows. */}
                  <div className="space-y-1">
                    {contactInfo.map((item, index) => (
                      <a
                        key={index}
                        href={item.href}
                        target={item.href.startsWith('http') ? '_blank' : undefined}
                        rel="noopener noreferrer"
                        className="flex items-center gap-3 rounded-ds-md px-3 py-2.5 transition-colors duration-ds-fast hover:bg-ds-surface-2"
                      >
                        <span className="text-ds-primary [&_svg]:size-[18px]">
                          {item.icon}
                        </span>
                        <span className="min-w-0 flex-1">
                          <span className="block text-ds-2xs text-ds-fg-subtle">
                            {item.title}
                          </span>
                          <span className="block truncate text-ds-sm font-medium text-ds-fg">
                            {item.value}
                          </span>
                        </span>
                      </a>
                    ))}
                  </div>

                  {/* Social links. */}
                  {socialLinks.length > 0 && <Divider />}
                  {socialLinks.length > 0 && <div>
                    <h4 className="mb-2 text-ds-2xs font-medium uppercase tracking-[0.08em] text-ds-fg-subtle">
                      {language === 'en' ? 'Social Media' : '社交媒体'}
                    </h4>
                    <div className="grid grid-cols-3 gap-2">
                      {socialLinks.map((social, index) => (
                        <a
                          key={index}
                          href={social.href}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex flex-col items-center gap-1.5 rounded-ds-md border border-ds-border bg-ds-surface-1 px-2.5 py-3 text-ds-fg-muted transition-colors duration-ds-fast hover:border-ds-primary/30 hover:bg-ds-primary-soft hover:text-ds-primary [&_svg]:size-[18px]"
                        >
                          {social.icon}
                          <span className="text-ds-2xs font-medium">{social.label}</span>
                        </a>
                      ))}
                    </div>
                  </div>}
                    </>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Public messages wall — full width. */}
        <div className="mt-12 sm:mt-16">
          <PublicMessagesWall key={refreshKey} />
        </div>
      </div>
    </div>
  );
};

const InteractiveContactPage: React.FC = () => {
  return <InteractiveContactPageContent />;
};

export default InteractiveContactPage;
