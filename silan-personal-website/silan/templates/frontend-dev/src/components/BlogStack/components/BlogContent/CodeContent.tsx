import React, { useMemo, useState, useRef, useEffect } from 'react';
import { BlogContent } from '../../types/blog';
import { useTheme } from '../../../ThemeContext';
import { useLanguage } from '../../../LanguageContext';
import { Copy, Check } from 'lucide-react';
import { basicSetup } from 'codemirror';
import { EditorView } from '@codemirror/view';
import { EditorState } from '@codemirror/state';
import { javascript } from '@codemirror/lang-javascript';
import { python } from '@codemirror/lang-python';
import { html } from '@codemirror/lang-html';
import { css } from '@codemirror/lang-css';
import { json } from '@codemirror/lang-json';
import { markdown } from '@codemirror/lang-markdown';
import { sql } from '@codemirror/lang-sql';
import { dracula } from '@uiw/codemirror-theme-dracula';
import { syntaxHighlighting, defaultHighlightStyle } from '@codemirror/language';

interface CodeContentProps {
  item: BlogContent;
  index: number;
  isWideScreen: boolean;
}

export const CodeContent: React.FC<CodeContentProps> = ({ item, index, isWideScreen }) => {
  const { isDarkMode } = useTheme();
  const { language } = useLanguage();
  const [copied, setCopied] = useState(false);
  const editorRef = useRef<HTMLDivElement>(null);
  const viewRef = useRef<EditorView | null>(null);

  // Normalize code content
  const code = useMemo(() => {
    let text = (item.content ?? '').replace(/^\uFEFF/, '');
    text = text.replace(/\r\n?/g, '\n');
    return text;
  }, [item.content]);

  const getLanguageExtension = (lang?: string) => {
    const s = (lang || '').toLowerCase();
    if (['js', 'javascript', 'node', 'jsx', 'ts', 'typescript', 'tsx'].includes(s)) {
      return javascript({ jsx: true, typescript: s.includes('ts') });
    }
    if (['py', 'python'].includes(s)) return python();
    if (['html', 'xml', 'markup'].includes(s)) return html();
    if (['css'].includes(s)) return css();
    if (['json'].includes(s)) return json();
    if (['md', 'markdown'].includes(s)) return markdown();
    if (['sql'].includes(s)) return sql();
    return javascript(); // default
  };

  useEffect(() => {
    if (!editorRef.current) return;

    // Clean up previous editor
    if (viewRef.current) {
      viewRef.current.destroy();
    }

    const extensions = [
      basicSetup,
      getLanguageExtension(item.language),
      syntaxHighlighting(defaultHighlightStyle, { fallback: true }),
      EditorView.editable.of(false),
      EditorView.lineWrapping,
      EditorState.readOnly.of(true),
    ];

    if (isDarkMode) {
      extensions.push(dracula);
    }

    const state = EditorState.create({
      doc: code,
      extensions,
    });

    const view = new EditorView({
      state,
      parent: editorRef.current,
    });

    viewRef.current = view;

    return () => {
      view.destroy();
    };
  }, [code, item.language, isDarkMode]);

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

        {/* CodeMirror Editor */}
        <div className="relative" ref={editorRef} />

        {/* Caption */}
        {item.caption && (
          <figcaption className="p-6 bg-theme-surface-elevated border-t border-theme-card-border">
            <div className="text-center space-y-2">
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
