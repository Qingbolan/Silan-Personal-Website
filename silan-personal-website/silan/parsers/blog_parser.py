"""
Blog parser for extracting structured blog post information including
content analysis, categories, tags, series, and reading metrics.
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from .base_parser import BaseParser, ExtractedContent


class BlogParser(BaseParser):
    """
    Specialized parser for blog post content.
    
    Extracts blog metadata, content analysis, reading metrics, categories,
    tags, series information, and related posts with SEO optimization.
    """
    
    def __init__(self, content_dir):
        super().__init__(content_dir, logger_name="blog_parser")
    
    def _get_content_type(self) -> str:
        return 'blog_post'
    
    def _parse_content(self, post, extracted: ExtractedContent):
        """Parse blog post content and extract structured data"""
        metadata = post.metadata
        content = post.content
        
        # Add filename to metadata for prefix detection
        if hasattr(extracted, 'source_file') and extracted.source_file:
            filename = extracted.source_file.name
            metadata['filename'] = filename
            
            # folder_prefix should now be available from passed metadata
            # No need to manually detect from parent folder
        
        # Extract main blog post data
        blog_data = self._extract_blog_data(metadata, content)
        extracted.main_entity = blog_data
        
        # Extract categories and tags
        categories = self._extract_categories(metadata, content)
        tags = self._extract_tags(metadata, content)
        
        extracted.categories = categories
        extracted.tags = tags
        
        # Extract series information
        series_info = self._extract_series_info(metadata, content)
        
        # Extract content analysis
        content_analysis = self._analyze_content(content)
        
        # Extract related posts/references
        related_posts = self._extract_related_posts(content)
        
        # Store all extracted data
        extracted.metadata.update({
            'categories_data': [{'name': cat, 'slug': self._generate_slug(cat)} for cat in categories],
            'tags_data': [{'name': tag, 'slug': self._generate_slug(tag)} for tag in tags],
            'series': series_info,
            'content_analysis': content_analysis,
            'related_posts': related_posts,
            'sections': self._extract_sections(content)
        })
    
    def _extract_blog_data(self, metadata: Dict, content: str) -> Dict[str, Any]:
        """Extract main blog post information"""
        # Generate slug if not provided
        title = metadata.get('title', '')
        slug = metadata.get('slug', self._generate_slug(title))
        
        # Extract excerpt
        excerpt = metadata.get('excerpt', metadata.get('summary', ''))
        if not excerpt:
            excerpt = self._extract_excerpt(content)
        
        # Parse publication date
        pub_date = self._parse_publication_date(metadata)
        
        # Calculate reading metrics
        reading_metrics = self._calculate_reading_metrics(content)
        
        # Determine content type
        content_type = self._determine_content_type(metadata, content)
        
        # Extract featured image
        featured_image = self._extract_featured_image(metadata, content)
        
        # Extract series information for main entity
        series_info = self._extract_series_info(metadata, content)
        
        blog_data = {
            'title': title,
            'slug': slug,
            'excerpt': excerpt,
            'content': content,
            'content_type': content_type,
            'status': self._determine_status(metadata),
            'is_featured': metadata.get('featured', False),
            'featured_image_url': featured_image,
            'reading_time_minutes': reading_metrics['reading_time'],
            'view_count': metadata.get('views', 0),
            'like_count': metadata.get('likes', 0),
            'comment_count': 0,
            'published_at': pub_date,
            'series': series_info
        }
        
        return blog_data
    
    def _extract_categories(self, metadata: Dict, content: str) -> List[str]:
        """Extract blog categories"""
        categories = []
        
        # Get from metadata
        if 'categories' in metadata:
            if isinstance(metadata['categories'], list):
                categories.extend(metadata['categories'])
            else:
                categories.append(metadata['categories'])
        
        if 'category' in metadata:
            categories.append(metadata['category'])
        
        # Infer from content if no explicit categories
        if not categories:
            categories = self._infer_categories_from_content(content)
        
        return [cat.strip() for cat in categories if cat and cat.strip()]
    
    def _extract_tags(self, metadata: Dict, content: str) -> List[str]:
        """Extract blog tags"""
        tags = []
        
        # Get from metadata
        if 'tags' in metadata:
            if isinstance(metadata['tags'], list):
                tags.extend(metadata['tags'])
            else:
                tags.extend([tag.strip() for tag in metadata['tags'].split(',') if tag.strip()])
        
        # Extract hashtags from content
        hashtag_pattern = r'#(\w+)'
        hashtags = re.findall(hashtag_pattern, content)
        tags.extend(hashtags)
        
        # Infer additional tags from content
        inferred_tags = self._infer_tags_from_content(content)
        tags.extend(inferred_tags)
        
        # Remove duplicates and clean
        return list(set([tag.strip().lower() for tag in tags if tag and tag.strip()]))
    
    def _extract_series_info(self, metadata: Dict, content: str) -> Optional[Dict[str, Any]]:
        """Extract blog series information"""
        series_info = None
        
        # Check folder prefix for episode series
        folder_prefix = metadata.get('folder_prefix', '')
        if folder_prefix.startswith('episode.'):
            # Extract series info from episode folder name
            # Format: episode.series-name
            parts = folder_prefix.split('.')
            if len(parts) >= 2:
                series_name = parts[1].replace('-', ' ').title()
                
                # Try to extract part number from metadata first, then filename
                part_number = metadata.get('episode', None)
                if part_number is None or not isinstance(part_number, int):
                    part_number = 1
                    
                    # If no episode in metadata, try filename
                    filename = metadata.get('filename', '')
                    if filename:
                        try:
                            # Extract number from filename like "part1-getting-started.md" or "episode1.en.md"
                            match = re.search(r'(?:part|episode)(\d+)', filename)
                            if match:
                                part_number = int(match.group(1))
                        except:
                            pass
                
                series_info = {
                    'name': series_name,
                    'slug': self._generate_slug(series_name),
                    'part_number': part_number,
                    'description': metadata.get('series_description', '')
                }
        
        # Check filename for episode prefix (legacy support)
        filename = metadata.get('filename', '')
        if filename.startswith('episode.') and not series_info:
            # Extract series info from episode filename
            # Format: episode.series-name.part-number.md
            parts = filename.split('.')
            if len(parts) >= 3:
                series_name = parts[1].replace('-', ' ').title()
                part_number = 1
                try:
                    # Try to find part number in filename
                    for part in parts:
                        if part.isdigit():
                            part_number = int(part)
                            break
                except:
                    pass
                
                series_info = {
                    'name': series_name,
                    'slug': self._generate_slug(series_name),
                    'part_number': part_number,
                    'description': metadata.get('series_description', '')
                }
        
        # Check metadata for series (override filename if present)
        if 'series' in metadata:
            series_data = metadata['series']
            if isinstance(series_data, str):
                series_info = {
                    'name': series_data,
                    'slug': self._generate_slug(series_data),
                    'part_number': metadata.get('episode', metadata.get('part', 1)),
                    'description': ''
                }
            elif isinstance(series_data, dict):
                series_info = {
                    'name': series_data.get('name', ''),
                    'slug': self._generate_slug(series_data.get('name', '')),
                    'part_number': series_data.get('episode', series_data.get('part', metadata.get('episode', 1))),
                    'description': series_data.get('description', '')
                }
        
        # Look for series indicators in content
        if not series_info:
            series_patterns = [
                r'Part (\d+) of ([^.]+)',
                r'This is part (\d+) in the ([^.]+) series',
                r'Part (\d+): ([^.]+) Series'
            ]
            
            for pattern in series_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    part_num = int(match.group(1))
                    series_name = match.group(2).strip()
                    
                    series_info = {
                        'name': series_name,
                        'slug': self._generate_slug(series_name),
                        'part_number': part_num,
                        'description': f'Part {part_num} of {series_name}'
                    }
                    break
        
        return series_info
    
    def _analyze_content(self, content: str) -> Dict[str, Any]:
        """Perform comprehensive content analysis"""
        analysis = {}
        
        # Basic metrics
        word_count = len(content.split())
        char_count = len(content)
        paragraph_count = len([p for p in content.split('\n\n') if p.strip()])
        
        # Reading level analysis
        reading_level = self._calculate_reading_level(content)
        
        # Content structure analysis
        structure = self._analyze_content_structure(content)
        
        # Topic analysis
        topics = self._extract_topics(content)
        
        # Technical content analysis
        technical_analysis = self._analyze_technical_content(content)
        
        # Sentiment analysis (basic)
        sentiment = self._analyze_sentiment(content)
        
        analysis = {
            'word_count': word_count,
            'character_count': char_count,
            'paragraph_count': paragraph_count,
            'reading_level': reading_level,
            'structure': structure,
            'topics': topics,
            'technical_analysis': technical_analysis,
            'sentiment': sentiment,
            'readability_score': self._calculate_readability_score(content)
        }
        
        return analysis
    
    def _calculate_reading_metrics(self, content: str) -> Dict[str, int]:
        """Calculate reading time and word count"""
        words = content.split()
        word_count = len(words)
        
        # Average reading speed: 200-250 words per minute
        reading_time = max(1, word_count // 200)
        
        return {
            'word_count': word_count,
            'reading_time': reading_time
        }
    
    def _extract_excerpt(self, content: str) -> str:
        """Extract excerpt from content"""
        # Remove headers and get first substantial paragraph
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and len(line) > 50:
                # Truncate to reasonable length
                if len(line) > 200:
                    line = line[:197] + '...'
                return line
        
        # Fallback: first 200 characters
        clean_content = re.sub(r'#+\s*', '', content)
        clean_content = re.sub(r'\n+', ' ', clean_content)
        excerpt = clean_content.strip()[:200]
        
        if len(clean_content) > 200:
            excerpt += '...'
        
        return excerpt
    
    def _parse_publication_date(self, metadata: Dict) -> Optional[datetime]:
        """Parse publication date from metadata"""
        date_fields = ['published_at', 'publish_date', 'date', 'created_at']
        
        for field in date_fields:
            if field in metadata:
                date_str = metadata[field]
                if date_str:
                    parsed_date = self._parse_date(date_str)
                    if parsed_date:
                        return datetime.combine(parsed_date, datetime.min.time())
        
        return None
    
    def _determine_content_type(self, metadata: Dict, content: str) -> str:
        """Determine blog post content type that matches BlogContentType enum"""
        # 1. Check folder prefix for type detection (highest priority)
        folder_prefix = metadata.get('folder_prefix', '')
        if folder_prefix:
            if folder_prefix.startswith('vlog.'):
                return 'vlog'
            elif folder_prefix.startswith('blog.'):
                return 'article'
            elif folder_prefix.startswith('episode.'):
                return 'episode'  # Episodes are their own content type
            elif folder_prefix.startswith('tutorial.'):
                return 'tutorial'
            elif folder_prefix.startswith('podcast.'):
                return 'podcast'
        
        # 2. Check metadata explicitly specified type/content_type fields
        content_type_raw = metadata.get('type', metadata.get('content_type', ''))
        if content_type_raw:
            return self._map_to_valid_content_type(content_type_raw)
        
        # 3. Check filename prefix for type detection
        filename = metadata.get('filename', '')
        if filename:
            if filename.startswith('vlog.'):
                return 'vlog'
            elif filename.startswith('blog.'):
                return 'article'
            elif filename.startswith('episode.'):
                return 'episode'  # Episodes are their own content type
            elif filename.startswith('tutorial.'):
                return 'tutorial'
            elif filename.startswith('podcast.'):
                return 'podcast'

        # 2. Infer from content keywords
        content_lower = content.lower()
        indicator_map = {
            'article': [
                'review', 'comparison', 'vs', 'pros and cons', 'evaluation',
                'analysis', 'deep dive', 'investigation', 'study', 'research',
                'news', 'announcement', 'release', 'update', 'breaking',
                'opinion', 'thoughts', 'perspective', 'viewpoint',
                'case study', 'implementation', 'project', 'experience',
                'list of', 'top', 'best', 'worst', 'reasons'
            ],
            'podcast': ['podcast', 'audio', 'interview', 'conversation', 'q&a', 'questions'],
            'vlog': ['vlog', 'video', 'recording', 'demonstration'],
            'episode': ['episode', 'series', 'part', 'chapter', 'installment', 'continuation']
        }

        for enum_value, keywords in indicator_map.items():
            if any(keyword in content_lower for keyword in keywords):
                return enum_value

        # 3. Default fallback
        return 'article'

    def _map_to_valid_content_type(self, content_type: str) -> str:
        """Convert arbitrary content_type strings to valid BlogContentType enum members (lowercase)."""
        mapping = {
            'article': 'article',
            'blog': 'article',
            'vlog': 'vlog',
            'video': 'vlog',
            'episode': 'episode',
            'series': 'episode',
        }
        ct_lower = str(content_type).strip().lower()
        return mapping.get(ct_lower, ct_lower.lower())
    
    def _determine_status(self, metadata: Dict) -> str:
        """Determine blog post status"""
        status = metadata.get('status', '').lower()
        published = metadata.get('published', True)
        
        if status in ['draft', 'unpublished']:
            return 'draft'
        elif status in ['published', 'public']:
            return 'published'
        elif status in ['private']:
            return 'private'
        elif not published:
            return 'draft'
        else:
            return 'published'
    
    def _extract_featured_image(self, metadata: Dict, content: str) -> str:
        """Extract featured image URL"""
        # Check metadata first
        featured_fields = ['featured_image', 'featured_image_url', 'image', 'banner', 'thumbnail']
        
        for field in featured_fields:
            if field in metadata and metadata[field]:
                return metadata[field]
        
        # Look for first image in content
        images = self._extract_images(content)
        if images:
            return images[0]['image_url']
        
        return ''
    
    def _infer_categories_from_content(self, content: str) -> List[str]:
        """Infer categories from content analysis"""
        categories = []
        content_lower = content.lower()
        
        # Technology categories
        if any(tech in content_lower for tech in ['python', 'javascript', 'programming', 'code']):
            categories.append('Programming')
        
        if any(term in content_lower for term in ['machine learning', 'ai', 'neural network']):
            categories.append('Artificial Intelligence')
        
        if any(term in content_lower for term in ['web development', 'frontend', 'backend']):
            categories.append('Web Development')
        
        if any(term in content_lower for term in ['data science', 'analytics', 'visualization']):
            categories.append('Data Science')
        
        # General categories
        if any(term in content_lower for term in ['tutorial', 'how to', 'guide']):
            categories.append('Tutorial')
        
        if any(term in content_lower for term in ['review', 'comparison']):
            categories.append('Review')
        
        return categories
    
    def _infer_tags_from_content(self, content: str) -> List[str]:
        """Infer tags from content analysis"""
        tags = []
        
        # Technology tags
        tech_terms = [
            'python', 'javascript', 'react', 'vue', 'angular', 'django', 'flask',
            'tensorflow', 'pytorch', 'machine learning', 'deep learning',
            'docker', 'kubernetes', 'aws', 'azure', 'cloud', 'devops'
        ]
        
        content_lower = content.lower()
        for term in tech_terms:
            if term in content_lower:
                tags.append(term)
        
        # Extract technical acronyms
        acronyms = re.findall(r'\b[A-Z]{2,}\b', content)
        for acronym in acronyms:
            if len(acronym) <= 5:  # Reasonable acronym length
                tags.append(acronym.lower())
        
        return tags[:10]  # Limit to 10 inferred tags
    
    def _extract_topics(self, content: str) -> List[str]:
        """Extract main topics from content"""
        # This is a simplified topic extraction
        # In a real implementation, you might use NLP libraries like spaCy or NLTK
        
        # Extract nouns that appear frequently
        words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
        
        # Count word frequency
        word_freq = {}
        for word in words:
            if word not in ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'was', 'one', 'our', 'has', 'use']:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top words
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        topics = [word for word, freq in sorted_words[:10] if freq > 1]
        
        return topics
    
    def _analyze_technical_content(self, content: str) -> Dict[str, Any]:
        """Analyze technical aspects of content"""
        analysis = {
            'has_code_blocks': bool(re.search(r'```', content)),
            'code_languages': self._extract_code_languages(content),
            'has_math': bool(re.search(r'\$.*\$', content)),
            'technical_terms': self._extract_technical_terms(content),
            'complexity_level': self._assess_technical_complexity(content)
        }
        
        return analysis
    
    def _extract_code_languages(self, content: str) -> List[str]:
        """Extract programming languages from code blocks"""
        languages = []
        
        # Find code blocks with language specification
        code_block_pattern = r'```(\w+)'
        matches = re.findall(code_block_pattern, content)
        
        for match in matches:
            if match.lower() not in ['text', 'plain', 'output']:
                languages.append(match.lower())
        
        return list(set(languages))
    
    def _extract_technical_terms(self, content: str) -> List[str]:
        """Extract technical terms and jargon"""
        # This is a simplified implementation
        technical_patterns = [
            r'\b[A-Z]{2,}\b',  # Acronyms
            r'\b\w+(?:API|SDK|CLI|UI|UX|DB)\b',  # Technical suffixes
            r'\b(?:async|await|lambda|function|class|method|variable)\b'  # Programming terms
        ]
        
        terms = []
        for pattern in technical_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            terms.extend(matches)
        
        return list(set(terms))
    
    def _assess_technical_complexity(self, content: str) -> str:
        """Assess technical complexity level"""
        content_lower = content.lower()
        
        beginner_indicators = ['basic', 'introduction', 'beginner', 'getting started', 'simple']
        intermediate_indicators = ['implementation', 'configuration', 'setup', 'development']
        advanced_indicators = ['optimization', 'performance', 'architecture', 'scalability', 'algorithm']
        
        if any(indicator in content_lower for indicator in advanced_indicators):
            return 'advanced'
        elif any(indicator in content_lower for indicator in intermediate_indicators):
            return 'intermediate'
        elif any(indicator in content_lower for indicator in beginner_indicators):
            return 'beginner'
        else:
            return 'intermediate'
    
    def _analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """Perform basic sentiment analysis"""
        positive_words = ['great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'best', 'awesome']
        negative_words = ['bad', 'terrible', 'awful', 'worst', 'hate', 'horrible', 'disappointing']
        
        content_lower = content.lower()
        
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        if positive_count > negative_count:
            sentiment = 'positive'
        elif negative_count > positive_count:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'positive_score': positive_count,
            'negative_score': negative_count
        }
    
    def _calculate_reading_level(self, content: str) -> str:
        """Calculate reading difficulty level"""
        sentences = len(re.split(r'[.!?]+', content))
        words = len(content.split())
        
        if sentences == 0:
            return 'easy'
        
        avg_words_per_sentence = words / sentences
        
        if avg_words_per_sentence < 15:
            return 'easy'
        elif avg_words_per_sentence < 20:
            return 'medium'
        else:
            return 'hard'
    
    def _calculate_readability_score(self, content: str) -> float:
        """Calculate a simple readability score (0-100)"""
        sentences = len(re.split(r'[.!?]+', content))
        words = len(content.split())
        
        if sentences == 0 or words == 0:
            return 50.0
        
        avg_words_per_sentence = words / sentences
        
        # Simple scoring (inverted - lower words per sentence = higher score)
        score = max(0, 100 - (avg_words_per_sentence - 10) * 5)
        return min(100, score)
    
    def _analyze_content_structure(self, content: str) -> Dict[str, Any]:
        """Analyze content structure"""
        headers = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
        
        structure = {
            'header_count': len(headers),
            'header_levels': [len(header[0]) for header in headers],
            'has_introduction': self._has_introduction(content),
            'has_conclusion': self._has_conclusion(content),
            'list_count': len(re.findall(r'^\s*[-*+]\s+', content, re.MULTILINE)),
            'link_count': len(re.findall(r'\[([^\]]+)\]\([^)]+\)', content))
        }
        
        return structure
    
    def _has_introduction(self, content: str) -> bool:
        """Check if content has an introduction section"""
        intro_patterns = [
            r'##?\s*Introduction',
            r'##?\s*Overview',
            r'##?\s*Getting Started'
        ]
        
        for pattern in intro_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False
    
    def _has_conclusion(self, content: str) -> bool:
        """Check if content has a conclusion section"""
        conclusion_patterns = [
            r'##?\s*Conclusion',
            r'##?\s*Summary',
            r'##?\s*Final Thoughts',
            r'##?\s*Wrap[- ]?up'
        ]
        
        for pattern in conclusion_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False
    
    def _extract_related_posts(self, content: str) -> List[Dict[str, Any]]:
        """Extract references to related posts"""
        related_posts = []
        
        # Look for internal links that might be related posts
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        links = re.findall(link_pattern, content)
        
        for link_text, url in links:
            # Filter for internal links that look like blog posts
            if not url.startswith('http') and ('.md' in url or '/blog/' in url or '/post/' in url):
                related_posts.append({
                    'title': link_text,
                    'url': url,
                    'relationship_type': 'reference'
                })
        
        return related_posts
    
    def _extract_focus_keywords(self, content: str) -> List[str]:
        """Extract potential focus keywords"""
        # Get most frequent meaningful words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
        
        # Filter common words
        stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'was', 'one', 'our', 'has', 'use', 'this', 'that', 'with', 'from', 'they', 'she', 'her', 'him', 'his'}
        
        word_freq = {}
        for word in words:
            if word not in stop_words and len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return top 5 keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:5] if freq > 2]
    
    def _check_structured_data(self, content: str) -> bool:
        """Check if content has structured data markup"""
        # Look for JSON-LD or microdata
        return bool(re.search(r'application/ld\+json|itemscope|itemtype', content, re.IGNORECASE))
    
    def _validate_content(self, extracted: ExtractedContent):
        """Validate extracted blog content"""
        main_entity = extracted.main_entity
        
        # Check required fields
        if not main_entity.get('title'):
            extracted.validation_errors.append('Missing blog post title')
        
        if not main_entity.get('content'):
            extracted.validation_errors.append('Missing blog post content')
        
        if not main_entity.get('excerpt'):
            extracted.validation_warnings.append('Missing excerpt')
        
        if not extracted.categories:
            extracted.validation_warnings.append('No categories assigned')
        
        if not extracted.tags:
            extracted.validation_warnings.append('No tags assigned')
        
        # Validate content quality
        word_count = main_entity.get('word_count', 0)
        if word_count < 300:
            extracted.validation_warnings.append('Content may be too short for SEO')
        elif word_count > 3000:
            extracted.validation_warnings.append('Content may be too long - consider breaking into series')
        
        # Validate SEO
        title_length = len(main_entity.get('title', ''))
        if title_length > 60:
            extracted.validation_warnings.append('Title may be too long for SEO')
        elif title_length < 30:
            extracted.validation_warnings.append('Title may be too short for SEO')
        
        # Validate dates
        pub_date = main_entity.get('published_at')
        if pub_date and pub_date.date() > date.today():
            extracted.validation_warnings.append('Publication date is in the future')