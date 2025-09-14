import React from 'react';
import { Typography, Divider } from 'antd';

const { Text, Link } = Typography;

/**
 * Simple markdown renderer for inline elements
 * Handles: bold, italic, code, links
 */
export const renderMarkdownInline = (text: string): React.ReactNode => {
  if (!text || typeof text !== 'string') {
    return text;
  }

  // Split text into segments and process each one
  const segments: React.ReactNode[] = [];
  let currentIndex = 0;
  let segmentIndex = 0;

  // Regex patterns for markdown elements
  const patterns = [
    { 
      regex: /\*\*(.*?)\*\*/g, 
      render: (match: string, content: string, key: string) => (
        <Text strong key={key}>{content}</Text>
      )
    },
    { 
      regex: /\*(.*?)\*/g, 
      render: (match: string, content: string, key: string) => (
        <Text italic key={key}>{content}</Text>
      )
    },
    { 
      regex: /`([^`]+)`/g, 
      render: (match: string, content: string, key: string) => (
        <Text code key={key} style={{ 
          fontSize: '0.9em',
          background: 'var(--color-surface, #f5f5f5)',
          color: 'var(--color-primary, #0066FF)',
          padding: '2px 6px',
          borderRadius: '4px'
        }}>
          {content}
        </Text>
      )
    },
    { 
      regex: /\[([^\]]+)\]\(([^)]+)\)/g, 
      render: (match: string, linkText: string, url: string, key: string) => (
        <Link 
          key={key}
          href={url} 
          target={url.startsWith('http') ? '_blank' : '_self'}
          rel={url.startsWith('http') ? 'noopener noreferrer' : undefined}
          style={{
            color: 'var(--color-primary, #0066FF)',
            textDecoration: 'underline'
          }}
        >
          {linkText}
        </Link>
      )
    }
  ];

  // Find all matches in the text
  const allMatches: Array<{
    start: number;
    end: number;
    element: React.ReactNode;
  }> = [];

  patterns.forEach(pattern => {
    let match;
    const regex = new RegExp(pattern.regex.source, pattern.regex.flags);
    
    while ((match = regex.exec(text)) !== null) {
      const key = `segment-${segmentIndex++}`;
      let element: React.ReactNode;
      
      if (pattern.regex.source.includes('\\[')) {
        // Link pattern - has 3 groups (full, text, url)
        element = pattern.render(match[0], match[1], match[2], key);
      } else {
        // Other patterns - have 2 groups (full, content)
        element = pattern.render(match[0], match[1], key);
      }
      
      allMatches.push({
        start: match.index!,
        end: match.index! + match[0].length,
        element
      });
    }
  });

  // Sort matches by position
  allMatches.sort((a, b) => a.start - b.start);

  // Remove overlapping matches (prefer first occurrence)
  const validMatches = [];
  let lastEnd = -1;
  
  for (const match of allMatches) {
    if (match.start >= lastEnd) {
      validMatches.push(match);
      lastEnd = match.end;
    }
  }

  // Build the final result
  currentIndex = 0;
  validMatches.forEach(match => {
    // Add text before the match
    if (match.start > currentIndex) {
      const beforeText = text.slice(currentIndex, match.start);
      if (beforeText) {
        segments.push(beforeText);
      }
    }
    
    // Add the matched element
    segments.push(match.element);
    currentIndex = match.end;
  });

  // Add remaining text
  if (currentIndex < text.length) {
    const remainingText = text.slice(currentIndex);
    if (remainingText) {
      segments.push(remainingText);
    }
  }

  // If no matches found, return original text
  return segments.length > 0 ? segments : text;
};

/**
 * Check if text contains markdown formatting
 */
export const hasMarkdownFormatting = (text: string): boolean => {
  if (!text || typeof text !== 'string') return false;
  
  const patterns = [
    /\*\*.*?\*\*/,  // Bold
    /\*.*?\*/,      // Italic
    /`[^`]+`/,      // Code
    /\[.*?\]\(.*?\)/ // Links
  ];
  
  return patterns.some(pattern => pattern.test(text));
};