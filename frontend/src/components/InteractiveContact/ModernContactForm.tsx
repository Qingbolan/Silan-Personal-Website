import React, { useState } from 'react';
import { Form, Input, Button, Switch, message, Card } from 'antd';
import { Send, Mail, User as UserIcon, Building2, Briefcase, Lock, Globe } from 'lucide-react';
import { useLanguage } from '../LanguageContext';
import { useAuth } from './AuthContext';

const { TextArea } = Input;

interface ModernContactFormProps {
  onSuccess?: () => void;
  onMessageTypeChange?: (type: 'general' | 'job') => void;
}

const ModernContactForm: React.FC<ModernContactFormProps> = ({ onSuccess, onMessageTypeChange }) => {
  const [form] = Form.useForm();
  const [messageType, setMessageType] = useState<'general' | 'job'>('general');
  const [isPublic, setIsPublic] = useState(true);
  const [consentLogo, setConsentLogo] = useState(false);
  const [emailVerified, setEmailVerified] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const { language } = useLanguage();
  const { user, isAuthenticated } = useAuth();

  const handleSubmit = async (values: any) => {
    if (messageType === 'job' && !emailVerified) {
      message.error(language === 'en' ? 'Please verify your company email' : '请验证您的公司邮箱');
      return;
    }

    setSubmitting(true);
    try {
      const response = await fetch('/api/v1/contact/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: messageType,
          author_name: user?.username || values.name,
          author_email: user?.email || values.email,
          subject: values.subject,
          message: values.message,
          company: values.company,
          company_email: values.company_email,
          position: values.position,
          send_resume: values.send_resume,
          isPublic,
          consentCompanyLogo: consentLogo,
        }),
        credentials: 'include',
      });

      if (!response.ok) throw new Error('Failed');

      message.success(language === 'en' ? 'Message sent successfully!' : '留言发送成功！');
      form.resetFields();
      setEmailVerified(false);
      onSuccess?.();
    } catch (error) {
      message.error(language === 'en' ? 'Failed to send message' : '发送失败');
    } finally {
      setSubmitting(false);
    }
  };

  const verifyEmail = async () => {
    const email = form.getFieldValue('company_email');
    if (!email) {
      message.error(language === 'en' ? 'Please enter company email' : '请输入公司邮箱');
      return;
    }

    try {
      const response = await fetch('/api/v1/auth/verify-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });

      if (response.ok) {
        setEmailVerified(true);
        message.success(language === 'en' ? 'Email verified!' : '邮箱验证成功！');
      } else {
        message.error(language === 'en' ? 'Verification failed' : '验证失败');
      }
    } catch (error) {
      message.error(language === 'en' ? 'Verification failed' : '验证失败');
    }
  };

  return (
    <div className="space-y-6">
      {/* Message Type Selector */}
      <div className="flex gap-3">
        <button
          type="button"
          onClick={() => {
            setMessageType('general');
            onMessageTypeChange?.('general');
          }}
          className={`flex-1 py-4 px-6 rounded-2xl font-medium transition-all duration-300 ${
            messageType === 'general'
              ? 'bg-gradient-primary text-white shadow-theme-lg scale-105'
              : 'bg-theme-surface-elevated text-theme-secondary hover:bg-theme-hover'
          }`}
        >
          <Mail className="inline-block mr-2" size={20} />
          {language === 'en' ? 'General Message' : '一般留言'}
        </button>
        <button
          type="button"
          onClick={() => {
            setMessageType('job');
            onMessageTypeChange?.('job');
          }}
          className={`flex-1 py-4 px-6 rounded-2xl font-medium transition-all duration-300 ${
            messageType === 'job'
              ? 'bg-gradient-primary text-white shadow-theme-lg scale-105'
              : 'bg-theme-surface-elevated text-theme-secondary hover:bg-theme-hover'
          }`}
        >
          <Briefcase className="inline-block mr-2" size={20} />
          {language === 'en' ? 'Job Opportunity' : '工作机会'}
        </button>
      </div>

      {/* Privacy Settings */}
      <Card className="bg-theme-surface-elevated border-0 rounded-2xl" bodyStyle={{ padding: '24px' }}>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg ${isPublic ? 'bg-theme-success-20' : 'bg-theme-surface'}`}>
                {isPublic ? <Globe size={20} className="text-theme-success" /> : <Lock size={20} className="text-theme-tertiary" />}
              </div>
              <div>
                <div className="font-semibold text-theme-primary">
                  {language === 'en' ? 'Display Publicly' : '公开展示'}
                </div>
                <div className="text-xs text-theme-tertiary">
                  {language === 'en'
                    ? 'Show this message on the public board after review'
                    : '审核后在公开留言板显示'}
                </div>
              </div>
            </div>
            <Switch checked={isPublic} onChange={setIsPublic} />
          </div>

          {messageType === 'job' && emailVerified && (
            <div className="flex items-center justify-between pt-4 border-t border-theme-card">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-theme-primary-20">
                  <Building2 size={20} className="text-theme-accent" />
                </div>
                <div>
                  <div className="font-semibold text-theme-primary">
                    {language === 'en' ? 'Display Company Logo' : '展示公司标识'}
                  </div>
                  <div className="text-xs text-theme-tertiary">
                    {language === 'en'
                      ? 'Allow showing company name and logo'
                      : '允许展示公司名称和 Logo'}
                  </div>
                </div>
              </div>
              <Switch checked={consentLogo} onChange={setConsentLogo} disabled={!isPublic} />
            </div>
          )}
        </div>
      </Card>

      {/* Form */}
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        className="space-y-4"
      >
        {/* Basic Info */}
        {!isAuthenticated && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Form.Item
              name="name"
              rules={[{ required: true, message: language === 'en' ? 'Name required' : '请输入姓名' }]}
            >
              <Input
                prefix={<UserIcon size={18} className="text-theme-tertiary" />}
                placeholder={language === 'en' ? 'Your Name' : '您的姓名'}
                size="large"
                className="rounded-xl"
              />
            </Form.Item>

            <Form.Item
              name="email"
              rules={[
                { required: true, message: language === 'en' ? 'Email required' : '请输入邮箱' },
                { type: 'email', message: language === 'en' ? 'Invalid email' : '邮箱格式不正确' },
              ]}
            >
              <Input
                prefix={<Mail size={18} className="text-theme-tertiary" />}
                placeholder={language === 'en' ? 'Your Email' : '您的邮箱'}
                size="large"
                className="rounded-xl"
              />
            </Form.Item>
          </div>
        )}

        {/* Job-specific fields */}
        {messageType === 'job' && (
          <div className="space-y-4 p-4 bg-theme-surface-elevated rounded-2xl">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Form.Item
                name="company"
                rules={[{ required: true, message: language === 'en' ? 'Company required' : '请输入公司名称' }]}
              >
                <Input
                  prefix={<Building2 size={18} className="text-theme-tertiary" />}
                  placeholder={language === 'en' ? 'Company Name' : '公司名称'}
                  size="large"
                  className="rounded-xl"
                />
              </Form.Item>

              <Form.Item
                name="position"
                rules={[{ required: true, message: language === 'en' ? 'Position required' : '请输入职位' }]}
              >
                <Input
                  prefix={<Briefcase size={18} className="text-theme-tertiary" />}
                  placeholder={language === 'en' ? 'Position' : '职位名称'}
                  size="large"
                  className="rounded-xl"
                />
              </Form.Item>
            </div>

            <Form.Item
              name="company_email"
              rules={[
                { required: true, message: language === 'en' ? 'Company email required' : '请输入公司邮箱' },
                { type: 'email' },
              ]}
            >
              <div className="flex gap-2">
                <Input
                  prefix={<Mail size={18} className="text-theme-tertiary" />}
                  placeholder={language === 'en' ? 'Company Email' : '公司邮箱'}
                  size="large"
                  className="rounded-xl flex-1"
                />
                <Button
                  type={emailVerified ? 'default' : 'primary'}
                  size="large"
                  onClick={verifyEmail}
                  disabled={emailVerified}
                  className="rounded-xl px-6"
                >
                  {emailVerified ? '✓ Verified' : 'Verify'}
                </Button>
              </div>
            </Form.Item>

            <Form.Item name="send_resume" valuePropName="checked">
              <div className="flex items-center gap-2 text-theme-secondary">
                <Switch disabled={!emailVerified} />
                <span>{language === 'en' ? 'Send my resume to this email' : '向此邮箱发送我的简历'}</span>
              </div>
            </Form.Item>
          </div>
        )}

        {/* Subject */}
        <Form.Item
          name="subject"
          rules={[{ required: true, message: language === 'en' ? 'Subject required' : '请输入主题' }]}
        >
          <Input
            placeholder={language === 'en' ? 'Subject' : '主题'}
            size="large"
            className="rounded-xl"
          />
        </Form.Item>

        {/* Message */}
        <Form.Item
          name="message"
          rules={[{ required: true, message: language === 'en' ? 'Message required' : '请输入留言内容' }]}
        >
          <TextArea
            placeholder={language === 'en' ? 'Your message...' : '您的留言...'}
            rows={6}
            className="rounded-xl"
          />
        </Form.Item>

        {/* Submit */}
        <Button
          type="primary"
          htmlType="submit"
          loading={submitting}
          size="large"
          icon={<Send size={20} />}
          className="w-full h-14 rounded-xl font-semibold text-lg"
          style={{
            background: 'var(--color-gradientPrimary)',
            border: 'none',
          }}
        >
          {language === 'en' ? 'Send Message' : '发送留言'}
        </Button>
      </Form>
    </div>
  );
};

export default ModernContactForm;
