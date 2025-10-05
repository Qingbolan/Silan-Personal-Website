import React from 'react';
import { Card, message } from 'antd';
import { GoogleLogin, CredentialResponse } from '@react-oauth/google';
import { LoginOutlined } from '@ant-design/icons';
import { useLanguage } from '../LanguageContext';
import { useAuth } from './AuthContext';

const LoginPanel: React.FC = () => {
  const { language } = useLanguage();
  const { loginWithGoogle } = useAuth();

  const handleGoogleLogin = async (credentialResponse: CredentialResponse) => {
    if (!credentialResponse.credential) {
      message.error(language === 'en' ? 'Login failed' : '登录失败');
      return;
    }

    try {
      await loginWithGoogle(credentialResponse.credential);
      message.success(language === 'en' ? 'Login successful!' : '登录成功！');
    } catch (error) {
      message.error(language === 'en' ? 'Login failed' : '登录失败');
    }
  };

  const handleGoogleError = () => {
    message.error(language === 'en' ? 'Login failed' : '登录失败');
  };

  return (
    <Card
      className="card-interactive"
      style={{ borderRadius: '20px' }}
      bodyStyle={{ padding: '24px' }}
    >
      <div className="text-center space-y-4">
        <div className="w-16 h-16 mx-auto rounded-full bg-gradient-primary flex items-center justify-center">
          <LoginOutlined className="text-white text-2xl" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-theme-primary mb-2">
            {language === 'en' ? 'Sign In' : '登录'}
          </h3>
          <p className="text-sm text-theme-tertiary mb-4">
            {language === 'en'
              ? 'Login to send messages and schedule meetings'
              : '登录以发送留言和预约会议'}
          </p>
        </div>
        <div className="flex justify-center">
          <GoogleLogin
            onSuccess={handleGoogleLogin}
            onError={handleGoogleError}
            useOneTap
            theme="outline"
            size="large"
          />
        </div>
      </div>
    </Card>
  );
};

export default LoginPanel;
