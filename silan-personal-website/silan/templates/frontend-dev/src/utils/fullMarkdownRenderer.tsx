import React from 'react';
import { Typography, Divider } from 'antd';

const { Text, Link } = Typography;

/**
 * Complete markdown renderer for both inline and block elements
 * Handles: headers, bold, italic, code, links, lists, dividers, blockquotes, file trees
 */

/**
 * Detect if text contains file tree structure
 */
export const isFileTreeStructure = (text: string): boolean => {
  if (!text) return false;
  const treeChars = ['├─', '├──', '└─', '└──', '│', '┌─', '┐', '┘', '└', '├', '┤'];
  return treeChars.some(char => text.includes(char)) ||
         text.split('\n').some(line => /^[\s]*[├└│┌┐┘┤]/.test(line.trim()));
};

/**
 * Render file tree structure with proper styling
 */
export const FileTreeRenderer: React.FC<{ content: string }> = ({ content }) => {
  return (
    <div className="my-8 relative">
      <div className="bg-theme-surface-elevated rounded-xl overflow-hidden shadow-medium border border-theme-card-border">
        {/* Header */}
        <div className="flex items-center gap-3 px-6 py-4 bg-theme-surface-secondary border-b border-theme-card-border">
          <div className="inline-flex items-center px-3 py-1 bg-theme-primary/10 rounded-full">
            <span className="text-xs font-semibold text-theme-primary uppercase tracking-wider font-mono">
              FILE STRUCTURE
            </span>
          </div>
        </div>

        {/* Tree Content */}
        <div className="p-6">
          <pre className="font-mono text-sm leading-relaxed text-theme-text-primary overflow-x-auto"
               style={{
                 fontFamily: 'JetBrains Mono, Monaco, Menlo, "Ubuntu Mono", Consolas, monospace',
                 lineHeight: '1.6',
                 whiteSpace: 'pre'
               }}>
            {content.split('\n').map((line, index) => (
              <div key={index} className="hover:bg-theme-surface/20 px-2 py-1 -mx-2 rounded">
                {line || '\u00A0'} {/* Non-breaking space for empty lines */}
              </div>
            ))}
          </pre>
        </div>
      </div>
    </div>
  );
};

interface MarkdownBlock {
  type: 'paragraph' | 'list' | 'divider' | 'blockquote' | 'header';
  content: string | string[];
  level?: number;
  ordered?: boolean;
}

/**
 * Parse markdown text into blocks
 */
export const parseMarkdownBlocks = (text: string): MarkdownBlock[] => {
  if (!text || typeof text !== 'string') return [];
  
  const lines = text.split('\n');
  const blocks: MarkdownBlock[] = [];
  let currentBlock: MarkdownBlock | null = null;
  let listItems: string[] = [];
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmedLine = line.trim();
    
    // Skip empty lines
    if (!trimmedLine) {
      // End current list if we have one
      if (currentBlock?.type === 'list' && listItems.length > 0) {
        blocks.push({ 
          ...currentBlock, 
          content: listItems 
        });
        currentBlock = null;
        listItems = [];
      }
      continue;
    }
    
    // Divider (--- or ***)
    if (trimmedLine === '---' || trimmedLine === '***' || trimmedLine === '___') {
      // End current list
      if (currentBlock?.type === 'list' && listItems.length > 0) {
        blocks.push({ 
          ...currentBlock, 
          content: listItems 
        });
        listItems = [];
      }
      
      blocks.push({
        type: 'divider',
        content: ''
      });
      currentBlock = null;
      continue;
    }
    
    // Headers (# ## ### etc)
    const headerMatch = trimmedLine.match(/^(#{1,6})\s+(.*)$/);
    if (headerMatch) {
      // End current list
      if (currentBlock?.type === 'list' && listItems.length > 0) {
        blocks.push({ 
          ...currentBlock, 
          content: listItems 
        });
        listItems = [];
      }
      
      blocks.push({
        type: 'header',
        content: headerMatch[2],
        level: headerMatch[1].length
      });
      currentBlock = null;
      continue;
    }
    
    // Blockquotes (> text)
    const quoteMatch = trimmedLine.match(/^>\s*(.*)$/);
    if (quoteMatch) {
      // End current list
      if (currentBlock?.type === 'list' && listItems.length > 0) {
        blocks.push({ 
          ...currentBlock, 
          content: listItems 
        });
        listItems = [];
      }
      
      blocks.push({
        type: 'blockquote',
        content: quoteMatch[1]
      });
      currentBlock = null;
      continue;
    }
    
    // Unordered list (- * +)
    const unorderedMatch = trimmedLine.match(/^[-*+]\s+(.*)$/);
    if (unorderedMatch) {
      if (currentBlock?.type !== 'list' || currentBlock?.ordered !== false) {
        // End previous list if different type
        if (currentBlock?.type === 'list' && listItems.length > 0) {
          blocks.push({ 
            ...currentBlock, 
            content: listItems 
          });
        }
        currentBlock = { type: 'list', content: [], ordered: false };
        listItems = [];
      }
      listItems.push(unorderedMatch[1]);
      continue;
    }
    
    // Ordered list (1. 2. etc)
    const orderedMatch = trimmedLine.match(/^\d+\.\s+(.*)$/);
    if (orderedMatch) {
      if (currentBlock?.type !== 'list' || currentBlock?.ordered !== true) {
        // End previous list if different type
        if (currentBlock?.type === 'list' && listItems.length > 0) {
          blocks.push({ 
            ...currentBlock, 
            content: listItems 
          });
        }
        currentBlock = { type: 'list', content: [], ordered: true };
        listItems = [];
      }
      listItems.push(orderedMatch[1]);
      continue;
    }
    
    // Regular paragraph
    // End current list
    if (currentBlock?.type === 'list' && listItems.length > 0) {
      blocks.push({ 
        ...currentBlock, 
        content: listItems 
      });
      listItems = [];
      currentBlock = null;
    }
    
    blocks.push({
      type: 'paragraph',
      content: trimmedLine
    });
  }
  
  // Add final list if exists
  if (currentBlock?.type === 'list' && listItems.length > 0) {
    blocks.push({ 
      ...currentBlock, 
      content: listItems 
    });
  }
  
  return blocks;
};

/**
 * Render inline markdown elements within text
 */
export const renderInlineMarkdown = (text: string): React.ReactNode => {
  if (!text || typeof text !== 'string') return text;
  
  // First handle line breaks - convert single \n to <br>
  const textWithBreaks = text.replace(/\n/g, '<LINEBREAK>');
  
  const segments: React.ReactNode[] = [];
  let currentIndex = 0;
  let segmentIndex = 0;

  // Regex patterns for markdown elements (order matters!)
  const patterns = [
    { 
      regex: /\*\*(.*?)\*\*/g, 
      render: (match: string, content: string, key: string) => (
        <Text strong key={key} style={{ fontWeight: 600 }}>{content}</Text>
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
    },
    {
      regex: /~~(.*?)~~/g,
      render: (match: string, content: string, key: string) => (
        <Text delete key={key}>{content}</Text>
      )
    },
    {
      regex: /<LINEBREAK>/g,
      render: (match: string, content: string, key: string) => (
        <br key={key} />
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
    
    while ((match = regex.exec(textWithBreaks)) !== null) {
      const key = `segment-${segmentIndex++}`;
      let element: React.ReactNode;
      
      if (pattern.regex.source.includes('\\\\[')) {
        // Link pattern - has 3 groups (full, text, url)
        element = pattern.render(match[0], match[1], match[2], key);
      } else if (pattern.regex.source.includes('LINEBREAK')) {
        // Line break pattern - no content group
        element = pattern.render(match[0], '', key);
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
      const beforeText = textWithBreaks.slice(currentIndex, match.start);
      if (beforeText) {
        segments.push(beforeText);
      }
    }
    
    // Add the matched element
    segments.push(match.element);
    currentIndex = match.end;
  });

  // Add remaining text
  if (currentIndex < textWithBreaks.length) {
    const remainingText = textWithBreaks.slice(currentIndex);
    if (remainingText) {
      segments.push(remainingText);
    }
  }

  // If no matches found, return original text
  if (segments.length === 0) return text;
  if (segments.length === 1) return segments[0];
  
  // Add keys to segments if returning array
  const segmentsWithKeys = segments.map((segment, index) => 
    React.isValidElement(segment) ? React.cloneElement(segment, { key: segment.key || `seg-${index}` }) : 
    typeof segment === 'string' ? <span key={`text-seg-${index}`}>{segment}</span> : segment
  );
  
  return segmentsWithKeys;
};

/**
 * Render a complete markdown block
 */
export const renderMarkdownBlock = (block: MarkdownBlock, index: number): React.ReactNode => {
  const key = `block-${index}`;
  
  switch (block.type) {
    case 'header':
      const HeaderTag = `h${Math.min(block.level || 1, 6)}` as keyof JSX.IntrinsicElements;
      const fontSize = {
        1: '2rem',
        2: '1.5rem', 
        3: '1.25rem',
        4: '1.125rem',
        5: '1rem',
        6: '0.875rem'
      }[block.level || 1];
      
      return React.createElement(HeaderTag, {
        key,
        style: {
          fontSize,
          fontWeight: block.level === 1 ? 700 : block.level === 2 ? 600 : 500,
          color: 'var(--color-text-primary, #1f2937)',
          marginTop: '1.5rem',
          marginBottom: '1rem',
          lineHeight: 1.3
        }
      }, renderInlineMarkdown(block.content as string));
    
    case 'divider':
      return (
        <Divider 
          key={key} 
          style={{ 
            margin: '2rem 0',
            borderColor: 'var(--color-border, #e5e7eb)'
          }} 
        />
      );
    
    case 'blockquote':
      return (
        <div 
          key={key}
          style={{
            borderLeft: '4px solid var(--color-primary, #0066FF)',
            paddingLeft: '1rem',
            margin: '1rem 0',
            background: 'var(--color-surface, #f9fafb)',
            padding: '1rem',
            borderRadius: '0.5rem'
          }}
        >
          <Text italic style={{ color: 'var(--color-text-secondary, #6b7280)' }}>
            {renderInlineMarkdown(block.content as string)}
          </Text>
        </div>
      );
    
    case 'list':
      const items = (block.content as string[]).map((item, itemIndex) => (
        <li key={`item-${itemIndex}`} style={{ marginBottom: '0.25rem' }}>
          {renderInlineMarkdown(item)}
        </li>
      ));
      
      if (block.ordered) {
        return (
          <ol key={key} style={{ 
            margin: '1rem 0', 
            paddingLeft: '1.5rem',
            color: 'var(--color-text-primary, #1f2937)'
          }}>
            {items}
          </ol>
        );
      } else {
        return (
          <ul key={key} style={{ 
            margin: '1rem 0', 
            paddingLeft: '1.5rem',
            color: 'var(--color-text-primary, #1f2937)',
            listStyleType: 'disc'
          }}>
            {items}
          </ul>
        );
      }
    
    case 'paragraph':
    default:
      return (
        <p key={key} style={{ 
          margin: '1rem 0',
          color: 'var(--color-text-primary, #1f2937)',
          lineHeight: 1.7
        }}>
          {renderInlineMarkdown(block.content as string)}
        </p>
      );
  }
};

/**
 * Render complete markdown text with all features
 */
export const renderFullMarkdown = (text: string): React.ReactNode => {
  if (!text || typeof text !== 'string') return text;
  
  const blocks = parseMarkdownBlocks(text);
  
  if (blocks.length === 0) {
    return renderInlineMarkdown(text);
  }
  
  return (
    <div>
      {blocks.map((block, index) => renderMarkdownBlock(block, index))}
    </div>
  );
};

/**
 * Process plain text to handle line breaks
 */
export const processPlainTextWithBreaks = (text: string): React.ReactNode => {
  if (!text || typeof text !== 'string') return text;
  
  // Split by line breaks and create elements
  const lines = text.split('\n');
  
  if (lines.length === 1) {
    return text;
  }
  
  const elements: React.ReactNode[] = [];
  
  lines.forEach((line, index) => {
    if (index > 0) {
      elements.push(<br key={`br-${index}`} />);
    }
    if (line) {
      elements.push(<span key={`line-${index}`}>{line}</span>);
    }
  });
  
  return elements;
};

/**
 * Check if text contains any markdown formatting
 */
export const hasCompleteMarkdownFormatting = (text: string): boolean => {
  if (!text || typeof text !== 'string') return false;
  
  const patterns = [
    /\*\*.*?\*\*/,          // Bold
    /\*.*?\*/,              // Italic  
    /`[^`]+`/,              // Code
    /\[.*?\]\(.*?\)/,       // Links
    /^#{1,6}\s+/m,          // Headers
    /^[-*+]\s+/m,           // Unordered lists
    /^\d+\.\s+/m,           // Ordered lists
    /^>\s+/m,               // Blockquotes
    /^---$|^\*\*\*$|^___$/m, // Dividers
    /~~.*?~~/               // Strikethrough
  ];
  
  return patterns.some(pattern => pattern.test(text));
};