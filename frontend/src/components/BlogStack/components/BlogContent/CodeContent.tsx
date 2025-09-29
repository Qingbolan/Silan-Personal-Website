import React, { useMemo, useState } from 'react';
import { BlogContent } from '../../types/blog';
import { useTheme } from '../../../ThemeContext';
import { useLanguage } from '../../../LanguageContext';
import { Copy, Check } from 'lucide-react';
import Prism from 'prismjs';
import 'prismjs/components/prism-clike';
import 'prismjs/components/prism-markup';
import 'prismjs/components/prism-bash';
import 'prismjs/components/prism-javascript';
import 'prismjs/components/prism-typescript';
import 'prismjs/components/prism-jsx';
import 'prismjs/components/prism-tsx';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-json';
import 'prismjs/components/prism-yaml';
import 'prismjs/components/prism-markdown';
import 'prismjs/components/prism-sql';
import 'prismjs/components/prism-ini';
import 'prismjs/components/prism-docker';
import 'prismjs/components/prism-powershell';

interface CodeContentProps {
  item: BlogContent;
  index: number;
  isWideScreen: boolean;
}

export const CodeContent: React.FC<CodeContentProps> = ({ item, index, isWideScreen }) => {
  const { isDarkMode } = useTheme();
  const { language } = useLanguage();
  const [copied, setCopied] = useState(false);

  // Normalize code content to avoid odd Unicode or BOM artifacts
  const code = useMemo(() => {
    let text = (item.content ?? '').replace(/^\uFEFF/, ''); // strip BOM
    // Normalize line endings
    text = text.replace(/\r\n?/g, '\n');
    return text;
  }, [item.content]);

  const mapLanguage = (lang?: string): string => {
    const s = (lang || '').toLowerCase();
    if (['bash', 'sh', 'shell'].includes(s)) return 'bash';
    if (['js', 'javascript', 'node'].includes(s)) return 'javascript';
    if (['ts', 'typescript'].includes(s)) return 'typescript';
    if (['jsx'].includes(s)) return 'jsx';
    if (['tsx'].includes(s)) return 'tsx';
    if (['py', 'python'].includes(s)) return 'python';
    if (['json'].includes(s)) return 'json';
    if (['yml', 'yaml'].includes(s)) return 'yaml';
    if (['md', 'markdown'].includes(s)) return 'markdown';
    if (['sql'].includes(s)) return 'sql';
    if (['ini', 'cfg', 'conf'].includes(s)) return 'ini';
    if (['docker', 'dockerfile'].includes(s)) return 'docker';
    if (['ps', 'ps1', 'powershell'].includes(s)) return 'powershell';
    if (['html', 'xml'].includes(s)) return 'markup';
    if (['css'].includes(s)) return 'css';
    return 'bash';
  };

  const langId = useMemo(() => mapLanguage(item.language), [item.language]);

  const handleCopyCode = async () => {
    try {
      await navigator.clipboard.writeText(code);
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
          <pre
            className="p-0 overflow-x-auto text-sm leading-relaxed scrollbar-thin scrollbar-thumb-theme-accent/20 scrollbar-track-transparent"
            aria-label={item.language || 'code'}
            style={{
              fontFamily: 'JetBrains Mono, Monaco, Menlo, "Ubuntu Mono", Consolas, monospace',
              fontVariantLigatures: 'none', // avoid unexpected ligatures
              tabSize: 2,
              margin: 0,
            }}
          >
            <code className={`language-${langId} ${isDarkMode ? 'text-gray-100' : 'text-gray-800'}`}>
              {/* Render per-line with Prism highlight to keep line numbers aligned */}
              {code.split('\n').map((line, i) => (
                <div key={i} className="flex items-start">
                  <span
                    className="select-none text-right w-10 pr-3 mr-2 text-xs text-theme-text-tertiary hidden lg:block"
                    style={{ lineHeight: '1.7' }}
                    aria-hidden
                  >
                    {i + 1}
                  </span>
                  <span
                    className="whitespace-pre block px-6 py-1"
                    style={{ lineHeight: '1.7' }}
                    dangerouslySetInnerHTML={{ __html: Prism.highlight(line || ' ', Prism.languages[langId] || Prism.languages.markup, langId) }}
                  />
                </div>
              ))}
            </code>
          </pre>
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
