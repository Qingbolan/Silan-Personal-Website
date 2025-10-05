import React, { useState } from 'react';
import { Card, Button, Input, DatePicker, TimePicker, message, Tag } from 'antd';
import { Calendar, Clock, Send, Plus, X } from 'lucide-react';
import { useLanguage } from '../LanguageContext';
import { useAuth } from './AuthContext';
import dayjs, { Dayjs } from 'dayjs';

const MeetingScheduler: React.FC = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [note, setNote] = useState('');
  const [slots, setSlots] = useState<Array<{ date: Dayjs | null; time: Dayjs | null }>>([
    { date: null, time: null },
  ]);
  const [submitting, setSubmitting] = useState(false);
  const { language } = useLanguage();
  const { user, isAuthenticated } = useAuth();

  const addSlot = () => {
    if (slots.length < 5) {
      setSlots([...slots, { date: null, time: null }]);
    }
  };

  const removeSlot = (index: number) => {
    if (slots.length > 1) {
      setSlots(slots.filter((_, i) => i !== index));
    }
  };

  const updateSlot = (index: number, field: 'date' | 'time', value: Dayjs | null) => {
    const newSlots = [...slots];
    newSlots[index][field] = value;
    setSlots(newSlots);
  };

  const handleSubmit = async () => {
    const finalName = user?.username || name;
    const finalEmail = user?.email || email;

    if (!finalName || !finalEmail) {
      message.error(language === 'en' ? 'Please fill in name and email' : '请填写姓名和邮箱');
      return;
    }

    const validSlots = slots.filter(s => s.date && s.time);
    if (validSlots.length === 0) {
      message.error(language === 'en' ? 'Please provide at least one time slot' : '请至少提供一个时间段');
      return;
    }

    setSubmitting(true);
    try {
      const formattedSlots = validSlots.map(s => {
        const dateStr = s.date!.format('YYYY-MM-DD');
        const timeStr = s.time!.format('HH:mm');
        return `${dateStr} ${timeStr} (SGT)`;
      });

      await fetch('/api/v1/meetings/request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: finalName,
          email: finalEmail,
          slots: formattedSlots,
          note,
        }),
        credentials: 'include',
      });

      message.success(language === 'en' ? 'Meeting request sent!' : '会议请求已发送！');

      // Reset
      setName('');
      setEmail('');
      setNote('');
      setSlots([{ date: null, time: null }]);
    } catch (error) {
      message.error(language === 'en' ? 'Failed to send request' : '发送失败');
    } finally {
      setSubmitting(false);
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
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-3 rounded-xl bg-gradient-primary">
              <Calendar size={24} className="text-white" />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-theme-primary">
                {language === 'en' ? 'Schedule a Meeting' : '预约会议'}
              </h3>
              <p className="text-sm text-theme-tertiary">
                {language === 'en' ? 'Suggest your available times' : '提供您的可用时间'}
              </p>
            </div>
          </div>
        </div>

        {/* User Info (if not authenticated) */}
        {!isAuthenticated && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              placeholder={language === 'en' ? 'Your Name' : '您的姓名'}
              value={name}
              onChange={(e) => setName(e.target.value)}
              size="large"
              className="rounded-xl"
            />
            <Input
              type="email"
              placeholder={language === 'en' ? 'Your Email' : '您的邮箱'}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              size="large"
              className="rounded-xl"
            />
          </div>
        )}

        {/* Time Slots */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="font-semibold text-theme-primary">
              {language === 'en' ? 'Your Available Times' : '您的可用时间'}
            </label>
            <Button
              type="dashed"
              icon={<Plus size={16} />}
              onClick={addSlot}
              disabled={slots.length >= 5}
              className="rounded-xl"
            >
              {language === 'en' ? 'Add Slot' : '添加时间'}
            </Button>
          </div>

          {slots.map((slot, index) => (
            <div key={index} className="flex gap-3 items-center">
              <Tag className="px-3 py-1 rounded-lg bg-theme-primary text-white border-theme-primary">
                #{index + 1}
              </Tag>
              <DatePicker
                value={slot.date}
                onChange={(date) => updateSlot(index, 'date', date)}
                placeholder={language === 'en' ? 'Select Date' : '选择日期'}
                size="large"
                className="flex-1 rounded-xl"
                disabledDate={(current) => current && current < dayjs().startOf('day')}
              />
              <TimePicker
                value={slot.time}
                onChange={(time) => updateSlot(index, 'time', time)}
                placeholder={language === 'en' ? 'Select Time' : '选择时间'}
                format="HH:mm"
                size="large"
                className="flex-1 rounded-xl"
                minuteStep={15}
              />
              {slots.length > 1 && (
                <Button
                  danger
                  type="text"
                  icon={<X size={18} />}
                  onClick={() => removeSlot(index)}
                  className="rounded-xl"
                />
              )}
            </div>
          ))}

          <p className="text-xs text-theme-tertiary flex items-center gap-1">
            <Clock size={14} />
            {language === 'en'
              ? 'All times are in Singapore Time (SGT, UTC+8)'
              : '所有时间均为新加坡时间 (SGT, UTC+8)'}
          </p>
        </div>

        {/* Note */}
        <div>
          <label className="font-semibold text-theme-primary block mb-2">
            {language === 'en' ? 'Meeting Topic (Optional)' : '会议主题（可选）'}
          </label>
          <Input.TextArea
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder={language === 'en'
              ? 'What would you like to discuss?'
              : '您想讨论什么？'}
            rows={3}
            className="rounded-xl"
          />
        </div>

        {/* Submit */}
        <Button
          type="primary"
          size="large"
          icon={<Send size={20} />}
          loading={submitting}
          onClick={handleSubmit}
          className="w-full h-14 rounded-xl font-semibold text-lg"
          style={{
            background: 'var(--color-gradientPrimary)',
            border: 'none',
          }}
        >
          {language === 'en' ? 'Send Meeting Request' : '发送会议请求'}
        </Button>
      </div>
    </Card>
  );
};

export default MeetingScheduler;
