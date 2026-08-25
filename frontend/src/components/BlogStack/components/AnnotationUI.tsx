import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageCircle } from 'lucide-react';
import { SelectedText } from '../types/blog';
import { SelectionAnchor } from '../hooks/useAnnotations';
import { useLanguage } from '../../LanguageContext';

interface AnnotationUIProps {
  selectionMenu: SelectionAnchor | null;
  formAnchor: SelectionAnchor | null;
  showAnnotationForm: string | null;
  selectedText: SelectedText | null;
  newAnnotationText: string;
  onOpenForm: () => void;
  onSetNewAnnotationText: (text: string) => void;
  onAddUserAnnotation: (contentId: string) => void;
  onCancelAnnotation: () => void;
}

const POPOVER_WIDTH = 384; // 24rem
const VIEWPORT_GUTTER = 16;

// Medium-style two-step annotation UI, rendered once per article page:
//  1. `selectionMenu` — a small floating toolbar above the current text
//     selection. No backdrop, no modal, selection untouched (copy still
//     works). Hidden when the selection collapses or the page scrolls.
//  2. The composer — an anchored popover next to where the selection was,
//     so the annotated passage stays visible while writing. A transparent
//     click-catcher (not a blur) dismisses it.
export const AnnotationUI: React.FC<AnnotationUIProps> = ({
  selectionMenu,
  formAnchor,
  showAnnotationForm,
  selectedText,
  newAnnotationText,
  onOpenForm,
  onSetNewAnnotationText,
  onAddUserAnnotation,
  onCancelAnnotation,
}) => {
  const { language } = useLanguage();

  // Esc dismisses the composer (the toolbar disappears on its own when the
  // selection collapses, which Esc also triggers).
  useEffect(() => {
    if (!showAnnotationForm) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onCancelAnnotation();
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [showAnnotationForm, onCancelAnnotation]);

  const viewportW = typeof window === 'undefined' ? 1024 : window.innerWidth;
  const viewportH = typeof window === 'undefined' ? 768 : window.innerHeight;

  // Toolbar: centered above the selection, flipped below when too close to
  // the viewport top, horizontally clamped so it never clips off-screen.
  const toolbarStyle: React.CSSProperties | undefined = selectionMenu
    ? {
        position: 'fixed',
        left: Math.min(Math.max(selectionMenu.left, 64), viewportW - 64),
        top: selectionMenu.top > 56 ? selectionMenu.top - 44 : selectionMenu.bottom + 8,
        transform: 'translateX(-50%)',
        zIndex: 60,
      }
    : undefined;

  // Composer: below the anchor, flipped above when it would overflow the
  // viewport bottom, horizontally clamped to the gutter.
  const composerStyle: React.CSSProperties | undefined = formAnchor
    ? (() => {
        const width = Math.min(POPOVER_WIDTH, viewportW - VIEWPORT_GUTTER * 2);
        const left = Math.min(
          Math.max(formAnchor.left - width / 2, VIEWPORT_GUTTER),
          viewportW - width - VIEWPORT_GUTTER,
        );
        const estimatedHeight = 320;
        const fitsBelow = formAnchor.bottom + 8 + estimatedHeight <= viewportH;
        return fitsBelow
          ? { position: 'fixed', left, top: formAnchor.bottom + 8, width, zIndex: 56 }
          : { position: 'fixed', left, bottom: viewportH - formAnchor.top + 8, width, zIndex: 56 };
      })()
    : undefined;

  return (
    <>
      {/* Step 1 — floating toolbar on selection */}
      <AnimatePresence>
        {selectionMenu && !showAnnotationForm && toolbarStyle && (
          <motion.button
            key="annotation-toolbar"
            type="button"
            initial={{ opacity: 0, y: 4, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 4, scale: 0.95 }}
            transition={{ duration: 0.15, ease: 'easeOut' }}
            style={toolbarStyle}
            // mousedown must not collapse the selection before click fires.
            onMouseDown={(event) => event.preventDefault()}
            onClick={onOpenForm}
            className="flex items-center gap-1.5 rounded-full bg-theme-accent px-3 py-1.5
                       text-xs font-medium text-white shadow-lg
                       transition-colors hover:bg-theme-accent-hover"
          >
            <MessageCircle size={13} aria-hidden />
            {language === 'en' ? 'Annotate' : '批注'}
          </motion.button>
        )}
      </AnimatePresence>

      {/* Step 2 — anchored composer popover */}
      <AnimatePresence>
        {showAnnotationForm && formAnchor && composerStyle && (
          <>
            {/* Transparent click-catcher — dismisses without hiding the
                article behind a blur. */}
            <div
              className="fixed inset-0 z-[55]"
              onClick={onCancelAnnotation}
            />
            <motion.div
              key="annotation-composer"
              initial={{ opacity: 0, scale: 0.96, y: 6 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.96, y: 6 }}
              transition={{ duration: 0.18, ease: 'easeOut' }}
              style={composerStyle}
            >
              {/* Solid ds surface — the legacy `bg-theme-surface-elevated`
                  token resolves to `transparent` (the old modal hid that
                  behind a full-screen backdrop blur; this popover has no
                  blur, so it needs an opaque card). */}
              <div className="rounded-xl border border-ds-border bg-ds-surface-1 p-5 shadow-ds-3">
                {selectedText && selectedText.contentId === showAnnotationForm && (
                  <div className="mb-4 rounded-lg border border-theme-accent/20 bg-theme-accent/5 p-3">
                    <p className="mb-1 font-sans text-xs uppercase tracking-wider text-theme-tertiary">
                      {language === 'en' ? 'Selected Text' : '选中文本'}
                    </p>
                    <p className="text-sm italic leading-relaxed text-theme-secondary">
                      "{selectedText.text.substring(0, 80)}{selectedText.text.length > 80 ? '...' : ''}"
                    </p>
                  </div>
                )}

                <textarea
                  value={newAnnotationText}
                  onChange={(e) => onSetNewAnnotationText(e.target.value)}
                  placeholder={language === 'en' ? 'Write your note...' : '写下你的批注...'}
                  className="w-full resize-none rounded-lg border border-theme-card p-3
                             text-sm leading-relaxed text-theme-primary placeholder-theme-tertiary
                             ring-theme-primary transition-all duration-200
                             focus:border-transparent focus:outline-none focus:ring-2"
                  rows={4}
                  autoFocus
                  maxLength={500}
                />

                <div className="mt-4 flex items-center justify-between">
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={() => onAddUserAnnotation(showAnnotationForm)}
                      disabled={!newAnnotationText.trim()}
                      className="rounded-lg bg-theme-accent px-4 py-2 font-sans text-sm
                                 font-medium text-white ring-theme-primary transition-all
                                 duration-200 hover:bg-theme-accent-hover
                                 focus:outline-none focus:ring-2
                                 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      {language === 'en' ? 'Save' : '保存'}
                    </button>
                    <button
                      type="button"
                      onClick={onCancelAnnotation}
                      className="rounded-lg px-4 py-2 font-sans text-sm text-theme-secondary
                                 ring-theme-primary transition-all duration-200
                                 hover:bg-theme-hover hover:text-theme-primary
                                 focus:outline-none focus:ring-2"
                    >
                      {language === 'en' ? 'Cancel' : '取消'}
                    </button>
                  </div>
                  <p className="font-mono text-xs text-theme-tertiary opacity-70">
                    {newAnnotationText.length}
                  </p>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
};
