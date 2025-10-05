import React, { useEffect, useState } from 'react';
import { Card, Tabs } from 'antd';
import { Mail, Phone, MapPin, Github, Linkedin, Globe, Lightbulb, Briefcase } from 'lucide-react';
import { useTheme } from '../components/ThemeContext';
import { useLanguage } from '../components/LanguageContext';
import {
  AuthProvider,
  useAuth,
  LoginPanel,
  ProfileCard,
} from '../components/InteractiveContact';
import ModernContactForm from '../components/InteractiveContact/ModernContactForm';
import PublicMessagesWall from '../components/InteractiveContact/PublicMessagesWall';

const InteractiveContactPageContent: React.FC = () => {
  const { colors } = useTheme();
  const { language } = useLanguage();
  const { isAuthenticated, user } = useAuth();
  const [activeTab, setActiveTab] = useState('thoughts');

  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  useEffect(() => {
    const root = document.documentElement;
    Object.entries(colors).forEach(([key, value]) => {
      root.style.setProperty(`--color-${key}`, value);
    });
  }, [colors]);

  const contactInfo = [
    {
      icon: <Mail size={18} />,
      title: language === 'en' ? 'Email' : '邮箱',
      value: 'silan.hu@u.nus.edu',
      href: 'mailto:silan.hu@u.nus.edu',
    },
    {
      icon: <Phone size={18} />,
      title: language === 'en' ? 'Phone' : '电话',
      value: '+65 8698 6181',
      href: 'tel:+6586986181',
    },
    {
      icon: <MapPin size={18} />,
      title: language === 'en' ? 'Location' : '位置',
      value: 'Singapore',
      href: 'https://maps.google.com/?q=Singapore',
    },
  ];

  const socialLinks = [
    { icon: <Github size={18} />, label: 'GitHub', href: 'https://github.com/Qingbolan' },
    { icon: <Linkedin size={18} />, label: 'LinkedIn', href: 'https://linkedin.com/in/Qingbolan' },
    { icon: <Globe size={18} />, label: 'Website', href: 'https://silan.tech' },
  ];

  // Mock data for recent thoughts
  const recentThoughts = [
    { id: 1, title: 'Knowledge Forest: 行为即知识资产', description: language === 'en' ? 'Building a knowledge management system' : '构建知识管理系统' },
    { id: 2, title: 'EasyRemote: 下一代算力互联', description: language === 'en' ? 'Next-gen computing connectivity' : '下一代算力互联' },
    { id: 3, title: 'GEM: 在生成引擎中做营销', description: language === 'en' ? 'Marketing in generative engines' : '在生成引擎中做营销' },
  ];

  // Mock data for expected jobs
  const expectedJobs = [
    { id: 1, title: 'Agent 数据库 / 行为版本存储', company: language === 'en' ? 'AI Infrastructure' : 'AI基础设施' },
    { id: 2, title: 'Go/Python 分布式系统落地', company: language === 'en' ? 'Distributed Systems' : '分布式系统' },
    { id: 3, title: '评测平台共建 / 论文共著', company: language === 'en' ? 'Research & Development' : '研发' },
  ];

  return (
    <div className="min-h-screen py-20">
      <div className="max-w-7xl mx-auto px-4">
        {/* Hero Header */}
        <div className="text-center mb-16">
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            {isAuthenticated
              ? (language === 'en' ? `Hi, ${user?.username}!` : `你好，${user?.username}！`)
              : (language === 'en' ? "Let's Connect" : '联系我')
            }
          </h1>
          <p className="text-xl md:text-2xl max-w-3xl mx-auto text-theme-secondary font-light">
            {language === 'en'
              ? 'Open to collaborations, job opportunities, and interesting conversations'
              : '开放合作、工作机会和有趣的对话'}
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Contact Form */}
          <div className="space-y-6">
            {/* Contact Form Card */}
            <Card
              className="card-interactive"
              style={{ borderRadius: '20px' }}
              bodyStyle={{ padding: '32px' }}
            >
              <ModernContactForm
                onMessageTypeChange={(type) => {
                  setActiveTab(type === 'general' ? 'thoughts' : 'jobs');
                }}
              />
            </Card>

            {/* Contact Info */}
            <Card
              className="card-interactive"
              style={{ borderRadius: '20px' }}
              bodyStyle={{ padding: '24px' }}
            >
              <h3 className="text-lg font-bold text-theme-primary mb-4">
                {language === 'en' ? 'Quick Contact' : '快速联系'}
              </h3>
              <div className="space-y-2">
                {contactInfo.map((item, index) => (
                  <a
                    key={index}
                    href={item.href}
                    target={item.href.startsWith('http') ? '_blank' : undefined}
                    rel="noopener noreferrer"
                    className="flex items-center gap-3 p-3 rounded-xl bg-theme-surface hover:bg-theme-surface-elevated transition-all group"
                  >
                    <div className="p-2 rounded-lg bg-theme-primary-20 text-theme-accent group-hover:scale-110 transition-transform">
                      {item.icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-xs text-theme-tertiary mb-0.5">{item.title}</div>
                      <div className="text-sm text-theme-primary font-semibold truncate">
                        {item.value}
                      </div>
                    </div>
                  </a>
                ))}
              </div>

              {/* Social Links */}
              <div className="mt-6 pt-4 border-t border-theme-card">
                <h4 className="text-sm font-semibold text-theme-secondary mb-3">
                  {language === 'en' ? 'Social Media' : '社交媒体'}
                </h4>
                <div className="grid grid-cols-3 gap-2">
                  {socialLinks.map((social, index) => (
                    <a
                      key={index}
                      href={social.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex flex-col items-center gap-2 p-3 rounded-xl bg-theme-surface hover:bg-gradient-primary hover:text-white transition-all duration-300 group"
                    >
                      <div className="group-hover:scale-110 transition-transform">
                        {social.icon}
                      </div>
                      <span className="text-xs font-medium">{social.label}</span>
                    </a>
                  ))}
                </div>
              </div>
            </Card>

            {/* Auth Card */}
            {isAuthenticated ? (
              <ProfileCard />
            ) : (
              <LoginPanel />
            )}
          </div>

          {/* Right Column - Content Display */}
          <div className="space-y-6">
            <Card
              className="card-interactive"
              style={{ borderRadius: '20px' }}
              bodyStyle={{ padding: '32px' }}
            >
              <Tabs
                activeKey={activeTab}
                onChange={setActiveTab}
                items={[
                  {
                    key: 'thoughts',
                    label: (
                      <span className="flex items-center gap-2">
                        <Lightbulb size={18} />
                        {language === 'en' ? 'Recent Thoughts' : '最新想法'}
                      </span>
                    ),
                    children: (
                      <div className="space-y-4">
                        {recentThoughts.map((thought) => (
                          <div
                            key={thought.id}
                            className="p-4 rounded-xl bg-theme-surface-elevated hover:shadow-theme-md transition-all cursor-pointer"
                          >
                            <h4 className="font-semibold text-theme-primary mb-1">
                              {thought.title}
                            </h4>
                            <p className="text-sm text-theme-secondary">
                              {thought.description}
                            </p>
                          </div>
                        ))}
                      </div>
                    ),
                  },
                  {
                    key: 'jobs',
                    label: (
                      <span className="flex items-center gap-2">
                        <Briefcase size={18} />
                        {language === 'en' ? 'Expected Jobs' : '期待职位'}
                      </span>
                    ),
                    children: (
                      <div className="space-y-4">
                        {expectedJobs.map((job) => (
                          <div
                            key={job.id}
                            className="p-4 rounded-xl bg-theme-surface-elevated hover:shadow-theme-md transition-all cursor-pointer"
                          >
                            <h4 className="font-semibold text-theme-primary mb-1">
                              {job.title}
                            </h4>
                            <p className="text-sm text-theme-secondary">
                              {job.company}
                            </p>
                          </div>
                        ))}
                      </div>
                    ),
                  },
                ]}
              />
            </Card>

            {/* Public Messages Wall */}
            <Card
              className="card-interactive"
              style={{ borderRadius: '20px' }}
              bodyStyle={{ padding: '32px' }}
            >
              <PublicMessagesWall />
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

const InteractiveContactPage: React.FC = () => {
  return (
    <AuthProvider>
      <InteractiveContactPageContent />
    </AuthProvider>
  );
};

export default InteractiveContactPage;
