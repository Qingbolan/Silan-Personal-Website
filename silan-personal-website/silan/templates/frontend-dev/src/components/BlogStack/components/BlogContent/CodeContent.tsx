import React, { useState } from 'react';
import { BlogContent } from '../../types/blog';
import { useTheme } from '../../../ThemeContext';
import { useLanguage } from '../../../LanguageContext';
import { Copy, Check } from 'lucide-react';

interface CodeContentProps {
  item: BlogContent;
  index: number;
  isWideScreen: boolean;
}

export const CodeContent: React.FC<CodeContentProps> = ({ item, index, isWideScreen }) => {
  const { isDarkMode } = useTheme();
  const { language } = useLanguage();
  const [copied, setCopied] = useState(false);

  const handleCopyCode = async () => {
    try {
      await navigator.clipboard.writeText(item.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy code:', err);
    }
  };

  return (
    <figure className={`my-16 ${isWideScreen ? 'col-span-2' : ''} break-inside-avoid`}>
      <div className="bg-theme-surface-elevated rounded-xl overflow-hidden shadow-medium border border-theme-card-border">
        {/* Code Header */}
        <div className="flex items-center justify-between px-6 py-4 bg-theme-surface-secondary border-b border-theme-card-border">
          <div className="flex items-center gap-3">
            {/* Language Badge */}
            <div className="inline-flex items-center px-3 py-1 bg-theme-primary/10 rounded-full">
              <span className="text-xs font-semibold text-theme-primary uppercase tracking-wider font-mono">
                {item.language || 'TEXT'}
              </span>
            </div>
            
            {/* Listing Number */}
            <span className="text-xs text-theme-text-tertiary font-sans">
              Listing {index + 1}
            </span>
          </div>
          
          {/* Copy Button */}
          <button
            onClick={handleCopyCode}
            className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium 
                       text-theme-text-secondary hover:text-theme-text-primary 
                       hover:bg-theme-surface-secondary rounded-lg transition-all duration-200 
                       focus:outline-none focus:ring-2 focus:ring-theme-focus-ring 
                       focus:ring-offset-1 group"
            aria-label={language === 'en' ? 'Copy code to clipboard' : '复制代码到剪贴板'}
          >
            {copied ? (
              <>
                <Check size={14} className="text-success-500" />
                <span className="text-success-500 font-sans">
                  {language === 'en' ? 'Copied!' : '已复制!'}
                </span>
              </>
            ) : (
              <>
                <Copy size={14} className="group-hover:scale-110 transition-transform" />
                <span className="font-sans">
                  {language === 'en' ? 'Copy' : '复制'}
                </span>
              </>
            )}
          </button>
        </div>
        
        {/* Code Block */}
        <div className="relative">
          <pre className="p-6 overflow-x-auto text-sm leading-relaxed   
                          scrollbar-thin scrollbar-thumb-theme-accent/20 scrollbar-track-transparent"
               style={{
                 fontFamily: 'JetBrains Mono, Monaco, Menlo, "Ubuntu Mono", Consolas, monospace',
                 fontFeatureSettings: '"liga" 1, "calt" 1',
                 tabSize: 2
               }}>
            <code className={`block whitespace-pre font-mono ${
              isDarkMode ? 'text-gray-100' : 'text-gray-800'
            }`}
                  style={{
                    fontSize: '0.875rem',
                    lineHeight: '1.7'
                  }}>
              {item.content}
            </code>
          </pre>
          
          {/* Line Numbers (Optional Enhancement) */}
          <div className="absolute left-0 top-0 bottom-0 w-12 bg-theme-surface-secondary/50
                          border-r border-theme-card-border/50 pointer-events-none hidden lg:block">
            <div className="p-6 text-xs text-theme-text-tertiary font-mono leading-relaxed">
              {item.content.split('\n').map((_, i) => (
                <div key={i} className="text-right pr-3" style={{ lineHeight: '1.7' }}>
                  {i + 1}
                </div>
              ))}
            </div>
          </div>
        </div>
        
        {/* Caption */}
        {item.caption && (
          <figcaption className="p-6 bg-theme-surface-elevated border-t border-theme-card-border">
            <div className="text-center space-y-2">
              {/* Caption Text */}
              <p className="text-sm text-theme-text-secondary leading-relaxed max-w-2xl mx-auto font-normal"
                 style={{ 
                   fontFamily: 'Georgia, "Times New Roman", Charter, serif'
                 }}>
                {item.caption}
              </p>
            </div>
          </figcaption>
        )}
      </div>
    </figure>
  );
}; 