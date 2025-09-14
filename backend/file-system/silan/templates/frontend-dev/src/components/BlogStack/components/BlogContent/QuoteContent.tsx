import React from 'react';
import { BlogContent } from '../../types/blog';

interface QuoteContentProps {
  item: BlogContent;
}

export const QuoteContent: React.FC<QuoteContentProps> = ({ item }) => {

  return (
    <section className="my-16 break-inside-avoid">
      <div className="px-6">
        <div className="relative">
          {/* Decorative Quote Mark */}
          <div 
            className="absolute -top-8 transform -translate-x-1/2 text-8xl leading-none 
                       text-theme-accent/20 pointer-events-none select-none font-serif"
            aria-hidden="true"
          >
            "
          </div>
          
          {/* Quote Content */}
          <blockquote 
            className="relative z-10 text-center py-12 px-8"
          >
            <p className="text-lg sm:text-xl lg:text-2xl leading-relaxed text-theme-text-primary 
                         font-normal italic tracking-wide selection:bg-theme-accent/20 
                         max-w-3xl mx-auto"
               style={{
                 textRendering: 'optimizeLegibility',
                 WebkitFontSmoothing: 'antialiased',
                 MozOsxFontSmoothing: 'grayscale',
                 lineHeight: '1.6'
               }}>
              {item.content}
            </p>
          </blockquote>
        </div>
      </div>
    </section>
  );
}; 