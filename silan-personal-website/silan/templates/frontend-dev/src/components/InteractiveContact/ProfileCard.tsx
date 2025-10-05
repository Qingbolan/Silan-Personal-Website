import React from 'react';
import { Card, Avatar, Button } from 'antd';
import { LogoutOutlined } from '@ant-design/icons';
import { useLanguage } from '../LanguageContext';
import { useAuth } from './AuthContext';

const ProfileCard: React.FC = () => {
  const { language } = useLanguage();
  const { user, logout } = useAuth();

  if (!user) return null;

  return (
    <Card
      className="card-interactive"
      style={{ borderRadius: '20px' }}
      bodyStyle={{ padding: '24px' }}
    >
      <div className="text-center space-y-4">
        <Avatar
          size={64}
          src={user.avatar}
          className="mx-auto shadow-theme-md"
        >
          {user.username.charAt(0).toUpperCase()}
        </Avatar>
        <div>
          <h3 className="font-bold text-theme-primary">{user.username}</h3>
          <p className="text-sm text-theme-tertiary truncate">{user.email}</p>
        </div>
        <Button
          type="default"
          icon={<LogoutOutlined />}
          onClick={logout}
          className="w-full rounded-xl"
        >
          {language === 'en' ? 'Sign Out' : '退出登录'}
        </Button>
      </div>
    </Card>
  );
};

export default ProfileCard;
