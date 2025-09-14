"""
Update parser for extracting structured information from individual update markdown files.

This parser handles the new file-based update system where each update is stored
as an individual markdown file organized by year/month structure.
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from pathlib import Path
from .base_parser import BaseParser, ExtractedContent


class UpdateParser(BaseParser):
    """
    Specialized parser for update content.
    
    Extracts update metadata, content analysis, impact assessment,
    and related project information from individual markdown files.
    """
    
    def __init__(self, content_dir):
        super().__init__(content_dir, logger_name="update_parser")
    
    def _get_content_type(self) -> str:
        return 'update'
    
    def _parse_content(self, post, extracted: ExtractedContent):
        """Parse update content and extract structured data"""
        metadata = post.metadata
        content = post.content
        
        # Extract main update data
        update_data = self._extract_update_data(metadata, content, extracted.file_path)
        extracted.main_entity = update_data
        
        # Extract technologies mentioned
        technologies = self._extract_update_technologies(metadata, content)
        extracted.technologies = technologies
        
        # Extract related projects
        related_projects = self._extract_related_projects(content)
        
        # Extract achievements and metrics
        achievements = self._extract_achievements(content)
        
        # Extract next steps and plans
        next_steps = self._extract_next_steps(content)
        
        # Store all extracted data
        extracted.metadata.update({
            'related_projects': related_projects,
            'achievements': achievements,
            'next_steps': next_steps,
            'sections': self._extract_sections(content)
        })
    
    def _extract_update_data(self, metadata: Dict, content: str, file_path: str) -> Dict[str, Any]:
        """Extract main update information"""
        # Extract date from filename if not in metadata
        update_date = self._extract_date_from_filename(file_path)
        if not update_date and metadata.get('date'):
            update_date = self._parse_date(metadata.get('date'))
        
        # Generate title if not provided
        title = metadata.get('title', '')
        if not title:
            title = self._generate_title_from_content(content)
        
        # Generate slug from filename or title
        slug = self._extract_slug_from_filename(file_path)
        if not slug:
            slug = self._generate_slug(title)
        
        # Extract summary from content if not in metadata
        summary = metadata.get('summary', metadata.get('description', ''))
        if not summary:
            summary = self._extract_summary_from_content(content)
        
        # Determine update type
        update_type = self._determine_update_type(metadata, content)
        
        # Calculate impact score
        impact_score = self._calculate_impact_score(content)
        
        # Extract metrics
        metrics = self._extract_update_metrics(content)
        
        update_data = {
            'title': title,
            'slug': slug,
            'summary': summary,
            'content': content,
            'update_date': update_date or date.today(),
            'update_type': update_type,
            'impact_score': impact_score,
            'is_major': metadata.get('major', False) or impact_score > 7.0,
            'is_public': metadata.get('public', True),
            'view_count': 0,
            'sort_order': self._calculate_sort_order(update_date),
            'metrics': metrics
        }
        
        return update_data
    
    def _extract_date_from_filename(self, file_path: str) -> Optional[date]:
        """Extract date from filename like '2024-01-15-project-milestone.md'"""
        file_path = Path(file_path)
        filename = file_path.stem
        
        # Try different date patterns
        date_patterns = [
            r'^(\d{4})-(\d{2})-(\d{2})',  # YYYY-MM-DD at start
            r'(\d{4})(\d{2})(\d{2})',     # YYYYMMDD
            r'(\d{2})-(\d{2})-(\d{4})',   # MM-DD-YYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, filename)
            if match:
                try:
                    if pattern.startswith('^(\d{4})'):  # YYYY-MM-DD
                        year, month, day = match.groups()
                        return date(int(year), int(month), int(day))
                    elif pattern == r'(\d{4})(\d{2})(\d{2})':  # YYYYMMDD
                        year, month, day = match.groups()
                        return date(int(year), int(month), int(day))
                    else:  # MM-DD-YYYY
                        month, day, year = match.groups()
                        return date(int(year), int(month), int(day))
                except ValueError:
                    continue
        
        # Try to extract from path structure (year/month folders)
        path_parts = file_path.parts
        if len(path_parts) >= 2:
            try:
                # Look for year in path
                year = None
                month = None
                
                for part in path_parts:
                    if re.match(r'^\d{4}$', part):  # Year folder
                        year = int(part)
                    elif re.match(r'^\d{2}-\w+$', part):  # Month folder like "01-january"
                        month = int(part.split('-')[0])
                
                if year and month:
                    return date(year, month, 1)  # First day of month
            except ValueError:
                pass
        
        return None
    
    def _extract_slug_from_filename(self, file_path: str) -> str:
        """Extract slug from filename"""
        filename = Path(file_path).stem
        
        # Remove date prefix if present
        filename = re.sub(r'^\d{4}-\d{2}-\d{2}-?', '', filename)
        filename = re.sub(r'^\d{8}-?', '', filename)
        
        return filename or 'update'
    
    def _generate_title_from_content(self, content: str) -> str:
        """Generate title from first header or content"""
        lines = content.split('\n')
        
        # Look for first header
        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                title = re.sub(r'^#+\s*', '', line).strip()
                if title:
                    return title
        
        # Use first substantial line
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and len(line) > 10:
                return line[:50] + ('...' if len(line) > 50 else '')
        
        return 'Update'
    
    def _extract_summary_from_content(self, content: str) -> str:
        """Extract summary from content"""
        # Look for summary section
        summary_section = self._extract_section(content, 'Summary')
        if summary_section:
            return summary_section[:200]
        
        # Use first paragraph after any headers
        lines = content.split('\n')
        in_content = False
        
        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                in_content = True
                continue
            
            if in_content and line and len(line) > 20:
                return line[:200] + ('...' if len(line) > 200 else '')
        
        # Fallback to first substantial line
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and len(line) > 20:
                return line[:200] + ('...' if len(line) > 200 else '')
        
        return ''
    
    def _determine_update_type(self, metadata: Dict, content: str) -> str:
        """Determine the type of update"""
        update_type = metadata.get('type', '').lower()
        
        # Use metadata if provided
        type_mapping = {
            'milestone': 'milestone',
            'achievement': 'achievement', 
            'progress': 'progress',
            'release': 'release',
            'announcement': 'announcement',
            'insight': 'insight',
            'learning': 'learning',
            'reflection': 'reflection'
        }
        
        if update_type in type_mapping:
            return type_mapping[update_type]
        
        # Analyze content for type indicators
        content_lower = content.lower()
        
        type_indicators = {
            'milestone': ['milestone', 'completed', 'finished', 'achieved', 'reached'],
            'achievement': ['achievement', 'success', 'accomplished', 'won', 'awarded'],
            'progress': ['progress', 'working on', 'developing', 'building', 'implementing'],
            'release': ['release', 'launched', 'deployed', 'published', 'version'],
            'announcement': ['announcing', 'excited to share', 'pleased to announce'],
            'insight': ['learned', 'insight', 'discovered', 'realized', 'understanding'],
            'learning': ['learning', 'studying', 'exploring', 'researching'],
            'reflection': ['reflection', 'looking back', 'thoughts on', 'retrospective']
        }
        
        for update_type, indicators in type_indicators.items():
            if any(indicator in content_lower for indicator in indicators):
                return update_type
        
        return 'progress'  # Default
    
    def _calculate_impact_score(self, content: str) -> float:
        """Calculate impact score based on content analysis"""
        score = 5.0  # Base score
        content_lower = content.lower()
        
        # High impact indicators
        high_impact_indicators = [
            'major milestone', 'breakthrough', 'significant progress', 'completed project',
            'published', 'launched', 'deployed', 'achieved goal', 'major achievement'
        ]
        
        # Medium impact indicators
        medium_impact_indicators = [
            'progress', 'milestone', 'improvement', 'update', 'development',
            'implementation', 'learning', 'insight'
        ]
        
        # Low impact indicators
        low_impact_indicators = [
            'minor update', 'small fix', 'quick note', 'brief update'
        ]
        
        # Calculate score
        for indicator in high_impact_indicators:
            if indicator in content_lower:
                score += 2.0
        
        for indicator in medium_impact_indicators:
            if indicator in content_lower:
                score += 1.0
        
        for indicator in low_impact_indicators:
            if indicator in content_lower:
                score -= 1.0
        
        # Content length factor
        if len(content) > 1000:
            score += 1.0
        elif len(content) < 200:
            score -= 1.0
        
        # Number of sections
        sections = self._extract_sections(content)
        if len(sections) > 3:
            score += 0.5
        
        return max(1.0, min(10.0, score))
    
    def _calculate_sort_order(self, update_date: Optional[date]) -> int:
        """Calculate sort order based on date (newer = higher)"""
        if not update_date:
            return 0
        
        # Use YYYYMMDD format for sorting
        return int(update_date.strftime('%Y%m%d'))
    
    def _extract_update_technologies(self, metadata: Dict, content: str) -> List[Dict[str, Any]]:
        """Extract technologies mentioned in the update"""
        technologies = []
        
        # Get from metadata
        tech_list = metadata.get('technologies', metadata.get('tech', []))
        
        # Extract from content
        tech_from_content = self._extract_tech_from_content(content)
        
        # Combine and process
        all_techs = list(set(tech_list + tech_from_content))
        
        for i, tech in enumerate(all_techs):
            if not tech or not tech.strip():
                continue
            
            tech_name = tech.strip()
            category = self._categorize_technology(tech_name)
            
            tech_data = {
                'technology_name': tech_name,
                'technology_type': category,
                'sort_order': i
            }
            
            technologies.append(tech_data)
        
        return technologies
    
    def _extract_tech_from_content(self, content: str) -> List[str]:
        """Extract technologies mentioned in update content"""
        technologies = []
        
        # Technology patterns for updates
        tech_patterns = [
            r'\b(React|Vue|Angular|Svelte|Next\.js|Nuxt\.js|Gatsby)\b',
            r'\b(Python|JavaScript|TypeScript|Java|Go|Rust|PHP|Ruby|Swift|Kotlin|C\+\+|C#)\b',
            r'\b(TensorFlow|PyTorch|Keras|Scikit-learn|OpenCV|Pandas|NumPy|Matplotlib)\b',
            r'\b(MySQL|PostgreSQL|MongoDB|Redis|SQLite|Elasticsearch|DynamoDB)\b',
            r'\b(Docker|Kubernetes|AWS|Azure|GCP|Heroku|Vercel|Netlify)\b',
            r'\b(Express|Flask|Django|Spring|Rails|Laravel|FastAPI|Node\.js)\b',
            r'\b(Git|GitHub|GitLab|Jenkins|CI/CD|DevOps)\b'
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            technologies.extend(matches)
        
        return list(set(technologies))
    
    def _extract_related_projects(self, content: str) -> List[str]:
        """Extract related project mentions"""
        projects = []
        
        # Look for project mentions
        project_patterns = [
            r'working on\s+([A-Z][A-Za-z\s]+?)(?:\s|$|\.)',
            r'project\s+([A-Z][A-Za-z\s]+?)(?:\s|$|\.)',
            r'building\s+([A-Z][A-Za-z\s]+?)(?:\s|$|\.)',
            r'developing\s+([A-Z][A-Za-z\s]+?)(?:\s|$|\.)'
        ]
        
        for pattern in project_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                project_name = match.strip()
                if len(project_name) > 3 and project_name not in projects:
                    projects.append(project_name)
        
        return projects[:5]  # Limit to 5 projects
    
    def _extract_achievements(self, content: str) -> List[Dict[str, Any]]:
        """Extract achievements from content"""
        achievements = []
        
        # Look for achievement sections
        achievement_section = self._extract_section(content, 'Achievements')
        if not achievement_section:
            achievement_section = self._extract_section(content, 'Accomplishments')
        if not achievement_section:
            achievement_section = self._extract_section(content, 'Completed')
        
        if achievement_section:
            achievement_items = self._extract_list_items(achievement_section)
            
            for item in achievement_items:
                achievements.append({
                    'description': item,
                    'category': self._categorize_achievement(item)
                })
        
        # Also look for achievement indicators in main content
        achievement_patterns = [
            r'(?:completed|finished|achieved|accomplished|delivered)\s+([^.!?]+)',
            r'(?:successfully|finally|managed to)\s+([^.!?]+)'
        ]
        
        for pattern in achievement_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                achievement_text = match.strip()
                if len(achievement_text) > 10:
                    achievements.append({
                        'description': achievement_text,
                        'category': self._categorize_achievement(achievement_text)
                    })
        
        return achievements[:10]  # Limit to 10 achievements
    
    def _extract_next_steps(self, content: str) -> List[str]:
        """Extract next steps and future plans"""
        next_steps = []
        
        # Look for next steps sections
        sections = ['Next Steps', 'Future Plans', 'TODO', 'Upcoming', 'Plans']
        
        for section_name in sections:
            section_content = self._extract_section(content, section_name)
            if section_content:
                steps = self._extract_list_items(section_content)
                next_steps.extend(steps)
        
        # Also look for future indicators in main content
        future_patterns = [
            r'(?:next|plan to|will|going to|intend to)\s+([^.!?]+)',
            r'(?:upcoming|future|planned)\s+([^.!?]+)'
        ]
        
        for pattern in future_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                step_text = match.strip()
                if len(step_text) > 10:
                    next_steps.append(step_text)
        
        return next_steps[:10]  # Limit to 10 next steps
    
    def _extract_update_metrics(self, content: str) -> Dict[str, Any]:
        """Extract metrics from update content"""
        metrics = {}
        
        # Look for metrics section
        metrics_section = self._extract_section(content, 'Metrics')
        if not metrics_section:
            metrics_section = self._extract_section(content, 'Progress')
        if not metrics_section:
            metrics_section = content
        
        # Extract common metrics
        metric_patterns = {
            'completion_percentage': [
                r'(\d+)%\s*(?:complete|done|finished)',
                r'(\d+)%\s*progress'
            ],
            'lines_of_code': [
                r'(\d+)\s*(?:lines?\s*of\s*code|LOC)',
                r'(\d+)\s*lines?\s*written'
            ],
            'commits': [
                r'(\d+)\s*commits?',
                r'(\d+)\s*commits?\s*(?:made|added)'
            ],
            'hours_worked': [
                r'(\d+)\s*hours?\s*(?:worked|spent)',
                r'(\d+)h\s*(?:worked|spent)'
            ],
            'issues_closed': [
                r'(\d+)\s*(?:issues?|bugs?)\s*(?:closed|fixed|resolved)'
            ]
        }
        
        for metric_name, patterns in metric_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, metrics_section, re.IGNORECASE)
                if match:
                    metrics[metric_name] = int(match.group(1))
                    break
        
        return metrics
    
    def _categorize_achievement(self, achievement_text: str) -> str:
        """Categorize achievement type"""
        text_lower = achievement_text.lower()
        
        categories = {
            'development': ['coded', 'developed', 'built', 'implemented', 'programmed'],
            'learning': ['learned', 'studied', 'mastered', 'understood'],
            'milestone': ['milestone', 'completed', 'finished', 'delivered'],
            'collaboration': ['worked with', 'collaborated', 'team', 'meeting'],
            'research': ['researched', 'analyzed', 'investigated', 'explored'],
            'writing': ['wrote', 'documented', 'article', 'blog'],
            'presentation': ['presented', 'demo', 'showcase', 'talked']
        }
        
        for category, indicators in categories.items():
            if any(indicator in text_lower for indicator in indicators):
                return category
        
        return 'general'
    
    def _validate_content(self, extracted: ExtractedContent):
        """Validate extracted update content"""
        main_entity = extracted.main_entity
        
        # Check required fields
        if not main_entity.get('title'):
            extracted.validation_errors.append('Missing update title')
        
        if not main_entity.get('summary'):
            extracted.validation_warnings.append('Missing update summary')
        
        if not main_entity.get('update_date'):
            extracted.validation_errors.append('Missing update date')
        
        # Validate content quality
        content = main_entity.get('content', '')
        if len(content) < 50:
            extracted.validation_warnings.append('Update content is very short')
        
        # Check for meaningful content
        if not any(section for section in extracted.metadata.get('sections', {}).values()):
            extracted.validation_warnings.append('No structured sections found') 