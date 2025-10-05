import React, { useState } from 'react';
import { Card, Form, Input, Button, message, Avatar, Upload } from 'antd';
import { UserOutlined, SaveOutlined, CameraOutlined } from '@ant-design/icons';
import { useLanguage } from '../LanguageContext';
import { useAuth } from './AuthContext';

const ProfileEditor: React.FC = () => {
  const [form] = Form.useForm();
  const [saving, setSaving] = useState(false);
  const { language } = useLanguage();
  const { user } = useAuth();

  const handleSubmit = async (values: any) => {
    setSaving(true);
    try {
      const response = await fetch('/api/v1/user/profile', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values),
        credentials: 'include',
      });

      if (!response.ok) throw new Error('Failed to update profile');

      message.success(language === 'en' ? 'Profile updated!' : '个人资料已更新！');
    } catch (error) {
      message.error(language === 'en' ? 'Failed to update profile' : '更新失败');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Card
      className="card-interactive"
      style={{ borderRadius: '20px' }}
      bodyStyle={{ padding: '32px' }}
    >
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-gradient-primary">
            <UserOutlined className="text-white text-2xl" />
          </div>
          <div>
            <h3 className="text-2xl font-bold text-theme-primary">
              {language === 'en' ? 'Edit Profile' : '编辑个人资料'}
            </h3>
            <p className="text-sm text-theme-tertiary">
              {language === 'en' ? 'Update your personal information' : '更新您的个人信息'}
            </p>
          </div>
        </div>

        {/* Avatar */}
        <div className="text-center">
          <Avatar size={100} src={user?.avatar} className="mb-4 shadow-theme-md">
            {user?.username.charAt(0).toUpperCase()}
          </Avatar>
          <Upload showUploadList={false}>
            <Button icon={<CameraOutlined />} type="dashed" className="rounded-xl">
              {language === 'en' ? 'Change Avatar' : '更换头像'}
            </Button>
          </Upload>
        </div>

        {/* Form */}
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            username: user?.username,
            title: user?.title,
            bio: user?.bio,
            website: user?.website,
            contact: user?.contact,
          }}
        >
          <Form.Item
            name="username"
            label={<span className="font-semibold text-theme-primary">{language === 'en' ? 'Username' : '用户名'}</span>}
          >
            <Input size="large" className="rounded-xl" />
          </Form.Item>

          <Form.Item
            name="title"
            label={<span className="font-semibold text-theme-primary">{language === 'en' ? 'Title' : '职位'}</span>}
          >
            <Input size="large" className="rounded-xl" placeholder={language === 'en' ? 'e.g. Software Engineer' : '例如：软件工程师'} />
          </Form.Item>

          <Form.Item
            name="bio"
            label={<span className="font-semibold text-theme-primary">{language === 'en' ? 'Bio' : '简介'}</span>}
          >
            <Input.TextArea rows={4} className="rounded-xl" />
          </Form.Item>

          <Form.Item
            name="website"
            label={<span className="font-semibold text-theme-primary">{language === 'en' ? 'Website' : '网站'}</span>}
          >
            <Input size="large" className="rounded-xl" />
          </Form.Item>

          <Form.Item
            name="contact"
            label={<span className="font-semibold text-theme-primary">{language === 'en' ? 'Contact' : '联系方式'}</span>}
          >
            <Input size="large" className="rounded-xl" />
          </Form.Item>

          <Button
            type="primary"
            htmlType="submit"
            size="large"
            icon={<SaveOutlined />}
            loading={saving}
            className="w-full rounded-xl font-semibold"
            style={{
              background: 'var(--color-gradientPrimary)',
              border: 'none',
            }}
          >
            {language === 'en' ? 'Save Changes' : '保存更改'}
          </Button>
        </Form>
      </div>
    </Card>
  );
};

export default ProfileEditor;
