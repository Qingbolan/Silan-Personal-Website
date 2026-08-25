import { useState, useEffect } from 'react';
import { UserAnnotation, SelectedText } from '../types/blog';
import { getClientFingerprint } from '../../../utils/fingerprint';

// Viewport-anchored position of the current text selection. `top`/`bottom`
// are the selection rectangle edges; `left` is its horizontal center — the
// toolbar and the composer popover both anchor off these.
export interface SelectionAnchor {
  contentId: string;
  top: number;
  bottom: number;
  left: number;
}

export const useAnnotations = (postId?: string) => {
  const [userAnnotations, setUserAnnotations] = useState<Record<string, UserAnnotation>>({});
  const [showAnnotationForm, setShowAnnotationForm] = useState<string | null>(null);
  const [newAnnotationText, setNewAnnotationText] = useState('');
  const [selectedText, setSelectedText] = useState<SelectedText | null>(null);
  const [highlightedAnnotation, setHighlightedAnnotation] = useState<string | null>(null);
  // Two-step annotation UX (Medium-style): selecting text only floats a
  // small toolbar near the selection (`selectionMenu`); the composer opens
  // (`showAnnotationForm` + `formAnchor`) only after the user clicks it.
  const [selectionMenu, setSelectionMenu] = useState<SelectionAnchor | null>(null);
  const [formAnchor, setFormAnchor] = useState<SelectionAnchor | null>(null);

  // Load annotations from localStorage when component mounts
  useEffect(() => {
    if (postId) {
      const storageKey = `annotations_${postId}`;
      const storedAnnotations = localStorage.getItem(storageKey);
      if (storedAnnotations) {
        try {
          const parsed = JSON.parse(storedAnnotations);
          setUserAnnotations(parsed);
        } catch (error) {
          console.error('Failed to parse stored annotations:', error);
        }
      }
    }
  }, [postId]);

  // Save annotations to localStorage whenever userAnnotations changes
  useEffect(() => {
    if (postId && Object.keys(userAnnotations).length > 0) {
      const storageKey = `annotations_${postId}`;
      localStorage.setItem(storageKey, JSON.stringify(userAnnotations));
    }
  }, [userAnnotations, postId]);

  // Hide the floating toolbar when the selection collapses (click elsewhere,
  // Esc) or the page scrolls out from under it. The composer popover stays
  // open on selection loss — it is dismissed explicitly via Cancel / Save /
  // the click-catcher. Capture phase so inner scroll containers (the app's
  // #browser-window) count too.
  useEffect(() => {
    const onSelectionChange = () => {
      if (showAnnotationForm) return;
      const selection = window.getSelection();
      if (!selection || selection.isCollapsed || !selection.toString().trim()) {
        setSelectionMenu(null);
      }
    };
    const onScroll = () => setSelectionMenu(null);
    document.addEventListener('selectionchange', onSelectionChange);
    document.addEventListener('scroll', onScroll, true);
    return () => {
      document.removeEventListener('selectionchange', onSelectionChange);
      document.removeEventListener('scroll', onScroll, true);
    };
  }, [showAnnotationForm]);

  const handleTextSelection = () => {
    const selection = window.getSelection();
    if (!selection || !selection.toString().trim()) {
      return;
    }

    const selectedTextContent = selection.toString().trim();
    const range = selection.getRangeAt(0);

    // Find the content container by traversing up the DOM
    let element: Node | null = range.commonAncestorContainer;
    if (element.nodeType === Node.TEXT_NODE) {
      element = element.parentNode;
    }

    let contentId = '';
    let containerElement: Element | null = null;

    // Look for the content container with an ID
    while (element && element !== document.body) {
      if ((element as Element).id) {
        contentId = (element as Element).id;
        containerElement = element as Element;
        break;
      }
      element = element.parentNode;
    }

    if (!contentId || !containerElement) {
      console.warn('Could not find content container for selection');
      return;
    }

    // Calculate more precise text offsets
    const containerText = containerElement.textContent || '';

    // Use the range to get more accurate positioning
    const preCaretRange = range.cloneRange();
    preCaretRange.selectNodeContents(containerElement);
    preCaretRange.setEnd(range.startContainer, range.startOffset);
    const startOffset = preCaretRange.toString().length;
    const endOffset = startOffset + selectedTextContent.length;

    // Validate that the selected text matches what we expect
    const extractedText = containerText.substring(startOffset, endOffset);

    if (extractedText !== selectedTextContent) {
      // Fallback: use simple string search if positioning is off
      const fallbackStart = containerText.indexOf(selectedTextContent);
      if (fallbackStart !== -1) {
        setSelectedText({
          text: selectedTextContent,
          contentId,
          startOffset: fallbackStart,
          endOffset: fallbackStart + selectedTextContent.length
        });
      } else {
        console.warn('Could not accurately position selected text');
        return;
      }
    } else {
      setSelectedText({
        text: selectedTextContent,
        contentId,
        startOffset,
        endOffset
      });
    }

    // Only float the toolbar. The selection is left untouched so the user
    // can still copy; nothing modal opens until the toolbar is clicked.
    const rect = range.getBoundingClientRect();
    setSelectionMenu({
      contentId,
      top: rect.top,
      bottom: rect.bottom,
      left: rect.left + rect.width / 2,
    });
  };

  // The toolbar button was clicked — now open the composer, anchored where
  // the selection was. Clearing the selection is safe at this point: the
  // user explicitly chose to annotate instead of copy.
  const openAnnotationForm = () => {
    setSelectionMenu((menu) => {
      if (!menu) return null;
      setFormAnchor(menu);
      setShowAnnotationForm(menu.contentId);
      return null;
    });
    window.getSelection()?.removeAllRanges();
  };

  const addUserAnnotation = (contentId: string) => {
    if (!newAnnotationText.trim() || !selectedText) {
      return;
    }

    const annotationId = `${contentId}-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    const newAnnotation: UserAnnotation = {
      text: newAnnotationText.trim(),
      selectedText: selectedText.text,
      startOffset: selectedText.startOffset,
      endOffset: selectedText.endOffset,
      fingerprint: getClientFingerprint()
    };

    setUserAnnotations(prev => ({
      ...prev,
      [annotationId]: newAnnotation
    }));

    // Reset form state
    setNewAnnotationText('');
    setShowAnnotationForm(null);
    setSelectedText(null);
    setFormAnchor(null);
  };

  const removeUserAnnotation = (annotationId: string) => {
    setUserAnnotations(prev => {
      const newAnnotations = { ...prev };
      delete newAnnotations[annotationId];

      // Update localStorage immediately
      if (postId) {
        const storageKey = `annotations_${postId}`;
        if (Object.keys(newAnnotations).length === 0) {
          localStorage.removeItem(storageKey);
        } else {
          localStorage.setItem(storageKey, JSON.stringify(newAnnotations));
        }
      }

      return newAnnotations;
    });
  };

  const highlightAnnotation = (annotationId: string) => {
    setHighlightedAnnotation(annotationId);
    setTimeout(() => setHighlightedAnnotation(null), 2000);
  };

  const cancelAnnotation = () => {
    setShowAnnotationForm(null);
    setNewAnnotationText('');
    setSelectedText(null);
    setFormAnchor(null);
    setSelectionMenu(null);
  };

  // Clear all annotations for the current post
  const clearAllAnnotations = () => {
    setUserAnnotations({});
    if (postId) {
      const storageKey = `annotations_${postId}`;
      localStorage.removeItem(storageKey);
    }
  };

  return {
    userAnnotations,
    showAnnotationForm,
    newAnnotationText,
    selectedText,
    highlightedAnnotation,
    selectionMenu,
    formAnchor,
    setNewAnnotationText,
    setShowAnnotationForm,
    handleTextSelection,
    openAnnotationForm,
    addUserAnnotation,
    removeUserAnnotation,
    highlightAnnotation,
    cancelAnnotation,
    clearAllAnnotations
  };
};
