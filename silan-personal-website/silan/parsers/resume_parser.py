"""
Resume parser for extracting structured personal information, education, 
experience, publications, and other resume-related data.
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from .base_parser import BaseParser, ExtractedContent


class ResumeParser(BaseParser):
    """
    Specialized parser for resume/CV content.
    
    Extracts personal information, education, work experience, publications,
    awards, skills, and other resume-related data with high accuracy.
    """
    
    def __init__(self, content_dir):
        super().__init__(content_dir, logger_name="resume_parser")
    
    def _get_content_type(self) -> str:
        return 'resume'
    
    def _parse_content(self, post, extracted: ExtractedContent):
        """Parse resume content and extract structured data"""
        metadata = post.metadata
        content = post.content
        
        # Extract personal information
        personal_info = self._extract_personal_info(metadata, content)
        extracted.main_entity = personal_info
        
        # Extract social links
        social_links = self._extract_social_links(metadata)
        
        # Extract education from content
        education_data = self._extract_education(content)
        education_data = self._enhance_education_with_metadata(education_data, metadata)
        
        # Extract work experience
        experience_data = self._extract_work_experience(content)
        experience_data = self._enhance_experience_with_metadata(experience_data, metadata)
        
        # Extract publications
        publications_data = self._extract_publications(content)
        
        # Extract awards
        awards_data = self._extract_awards(content)
        
        # Extract skills and technologies
        skills_data = self._extract_skills(content)
        technologies = self._parse_technologies(skills_data.get('technologies', []))
        
        # Extract research experience
        research_data = self._extract_research_experience(content)
        
        # Extract recent updates with structured format
        recent_updates = self._extract_recent_updates(content)
        
        # Include structured data in main_entity for database sync
        personal_info.update({
            'social_links': social_links,
            'education': education_data,
            'experience': experience_data,
            'publications': publications_data,
            'awards': awards_data,
            'skills': skills_data,
            'research': research_data,
            'recent_updates': recent_updates
        })
        
        # Store all extracted data in metadata as well for other uses
        extracted.metadata.update({
            'social_links': social_links,
            'education': education_data,
            'experience': experience_data,
            'publications': publications_data,
            'awards': awards_data,
            'skills': skills_data,
            'research': research_data,
            'recent_updates': recent_updates
        })
        
        extracted.technologies = technologies
    
    def _extract_personal_info(self, metadata: Dict, content: str) -> Dict[str, Any]:
        """Extract personal information from metadata and content"""
        # Extract title from content or metadata
        title = self._extract_professional_title(content) or metadata.get('title', '')
        
        personal_info = {
            'full_name': metadata.get('name', ''),
            'title': title,
            'current_status': metadata.get('current', ''),
            'phone': metadata.get('phone', ''),
            'email': metadata.get('email', ''),
            'location': metadata.get('location', ''),
            'website': metadata.get('website', ''),
            'avatar_url': self._extract_avatar_url(metadata, content),
            'is_primary': True
        }
        
        # Extract contact information if structured
        if 'contacts' in metadata:
            for contact in metadata['contacts']:
                contact_type = contact.get('type', '').lower()
                if contact_type == 'email' and not personal_info['email']:
                    personal_info['email'] = contact.get('value', '')
                elif contact_type == 'phone' and not personal_info['phone']:
                    personal_info['phone'] = contact.get('value', '')
                elif contact_type == 'location' and not personal_info['location']:
                    personal_info['location'] = contact.get('value', '')
        
        return personal_info
    
    def _extract_social_links(self, metadata: Dict) -> List[Dict[str, Any]]:
        """Extract social media links"""
        social_links = []
        
        if 'socialLinks' in metadata:
            for i, link in enumerate(metadata['socialLinks']):
                social_link = {
                    'platform': link.get('type', ''),
                    'url': link.get('url', ''),
                    'display_name': link.get('display_name', self._extract_username_from_url(link.get('url', ''))),
                    'is_active': True,
                    'sort_order': i
                }
                social_links.append(social_link)
        
        return social_links
    
    def _extract_avatar_url(self, metadata: Dict, content: str) -> str:
        """Extract avatar/profile photo URL"""
        # Check metadata first
        avatar_fields = ['avatar_url', 'avatar', 'photo', 'profile_photo', 'image']
        for field in avatar_fields:
            if field in metadata and metadata[field]:
                return metadata[field]
        
        # Look for images in content that might be profile photos
        images = self._extract_images(content)
        for img in images:
            alt_text = img.get('alt_text', '').lower()
            url = img.get('image_url', '')
            
            # Check if image looks like a profile photo
            if any(keyword in alt_text for keyword in ['profile', 'avatar', 'photo', 'headshot']):
                return url
            
            # If it's the first image and small, might be profile photo
            if url and len(images) <= 2:
                return url
        
        return ''
    
    def _extract_bio(self, content: str) -> str:
        """Extract bio/summary from content"""
        # Look for the first paragraph after the name
        lines = content.split('\n')
        in_header = True
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip headers and name
            if line.startswith('#') or line.startswith('**'):
                in_header = False
                continue
            
            # If we're past the header and find a substantial paragraph
            if not in_header and len(line) > 20 and not line.startswith('-'):
                return line
        
        return ''
    
    def _extract_professional_title(self, content: str) -> str:
        """Extract professional title from content"""
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for bold text that might be a title
            if line.startswith('**') and line.endswith('**'):
                title = line.strip('*').strip()
                # Check if it looks like a professional title
                if any(keyword in title.lower() for keyword in 
                       ['engineer', 'developer', 'researcher', 'scientist', 'analyst', 
                        'manager', 'lead', 'architect', 'consultant', 'specialist']):
                    return title
        
        return 'Professional'
    
    def _extract_education(self, content: str) -> List[Dict[str, Any]]:
        """Extract education information with detailed parsing"""
        education_data = []
        
        # Find education section
        education_section = self._extract_section(content, 'Education')
        if not education_section:
            return education_data
        
        # Parse education entries by looking for ### headers
        entries = re.split(r'\n###\s+', education_section)
        
        for entry in entries:
            if not entry.strip():
                continue
            
            education_record = self._parse_education_entry(entry)
            if education_record:
                education_data.append(education_record)
        
        return education_data
    
    def _enhance_education_with_metadata(self, education_data: List[Dict], metadata: Dict) -> List[Dict]:
        """Add logos and websites from metadata to education records"""
        education_logos = metadata.get('education_logos', {})
        education_websites = metadata.get('education_websites', {})
        
        for edu in education_data:
            # First priority: Check for directly specified logo key
            if '_logo_key' in edu:
                logo_key = edu['_logo_key']
                if logo_key in education_logos:
                    edu['institution_logo_url'] = education_logos[logo_key]
                # Remove the temporary key
                del edu['_logo_key']
            else:
                # Fallback to automatic matching
                institution = edu.get('institution', '').lower()
                
                # Try to match logos automatically
                for key, logo_url in education_logos.items():
                    if key.lower() in institution or any(keyword in institution for keyword in key.lower().split('_')):
                        edu['institution_logo_url'] = logo_url
                        break
            
            # Handle websites (only auto-match if not directly specified)
            if not edu.get('institution_website'):
                institution = edu.get('institution', '').lower()
                
                for key, website_url in education_websites.items():
                    if key.lower() in institution or any(keyword in institution for keyword in key.lower().split('_')):
                        edu['institution_website'] = website_url
                        break
        
        return education_data
    
    def _parse_education_entry(self, entry: str) -> Optional[Dict[str, Any]]:
        """Parse a single education entry"""
        lines = entry.strip().split('\n')
        if not lines:
            return None
        
        # First line is the institution
        institution = lines[0].strip('#').strip()
        
        education_record = {
            'institution': institution,
            'degree': '',
            'field_of_study': '',
            'start_date': None,
            'end_date': None,
            'is_current': False,
            'gpa': None,
            'location': '',
            'institution_website': '',
            'institution_logo_url': '',
            'sort_order': 0
        }
        
        description_lines = []
        
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            
            # Parse direct metadata (Logo, Website)
            if line.startswith('*Logo*:'):
                logo_key = line.replace('*Logo*:', '').strip()
                education_record['_logo_key'] = logo_key
            elif line.startswith('*Website*:'):
                website_url = line.replace('*Website*:', '').strip()
                education_record['institution_website'] = website_url
            
            # Parse degree (usually in bold)
            elif line.startswith('**') and line.endswith('**'):
                degree_text = line.strip('*').strip()
                education_record['degree'] = degree_text
                
                # Extract field of study if present
                if '(' in degree_text and ')' in degree_text:
                    field_match = re.search(r'\(([^)]+)\)', degree_text)
                    if field_match:
                        education_record['field_of_study'] = field_match.group(1)
            
            # Parse dates (usually in italic)
            elif line.startswith('*') and not line.startswith('**'):
                date_text = line.strip('*').strip()
                
                # Skip if it's metadata we've already handled
                if date_text.startswith('Logo:') or date_text.startswith('Website:'):
                    continue
                
                # Check if it's a date range
                if any(year in date_text for year in ['20', '19']) or 'Future' in date_text:
                    start_date, end_date = self._parse_date_range(date_text)
                    education_record['start_date'] = start_date
                    education_record['end_date'] = end_date
                    education_record['is_current'] = 'Future' in date_text or end_date is None
                else:
                    # Might be location
                    education_record['location'] = date_text
            
            # Parse GPA
            elif 'GPA' in line or 'gpa' in line.lower():
                gpa_match = re.search(r'GPA:?\s*(\d+\.?\d*(?:/\d+\.?\d*)?)', line, re.IGNORECASE)
                if gpa_match:
                    education_record['gpa'] = gpa_match.group(1)
                elif '/' in line and any(char.isdigit() for char in line):
                    # Extract GPA-like pattern
                    gpa_pattern = re.search(r'(\d+\.?\d*/\d+\.?\d*)', line)
                    if gpa_pattern:
                        education_record['gpa'] = gpa_pattern.group(1)
            
            # Parse honors and achievements (add to description)
            elif line.startswith('- '):
                description_lines.append(line.strip('- ').strip())
            
            else:
                # Other descriptive content
                if line and not line.startswith('#'):
                    description_lines.append(line)
        
        # Store details for education details table
        education_record['details'] = [detail.strip() for detail in description_lines if detail.strip()]
        
        return education_record
    
    def _extract_work_experience(self, content: str) -> List[Dict[str, Any]]:
        """Extract work experience with detailed parsing"""
        experience_data = []
        
        # Find work experience section
        work_section = self._extract_section(content, 'Work Experience')
        if not work_section:
            return experience_data
        
        # Parse experience entries
        entries = re.split(r'\n###\s+', work_section)
        
        for entry in entries:
            if not entry.strip():
                continue
            
            experience_record = self._parse_experience_entry(entry)
            if experience_record:
                experience_data.append(experience_record)
        
        return experience_data
    
    def _parse_experience_entry(self, entry: str) -> Optional[Dict[str, Any]]:
        """Parse a single work experience entry"""
        lines = entry.strip().split('\n')
        if not lines:
            return None
        
        # First line is the company
        company = lines[0].strip('#').strip()
        
        experience_record = {
            'company': company,
            'position': '',
            'start_date': None,
            'end_date': None,
            'is_current': False,
            'location': '',
            'company_website': '',
            'company_logo_url': '',
            'sort_order': 0
        }
        
        description_lines = []
        
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            
            # Parse direct metadata (Logo, Website)
            if line.startswith('*Logo*:'):
                logo_key = line.replace('*Logo*:', '').strip()
                # We'll use this in the enhancement phase
                experience_record['_logo_key'] = logo_key
            elif line.startswith('*Website*:'):
                website_url = line.replace('*Website*:', '').strip()
                experience_record['company_website'] = website_url
            
            # Parse position (usually in bold)
            elif line.startswith('**') and line.endswith('**'):
                experience_record['position'] = line.strip('*').strip()
            
            # Parse dates and location (usually in italic)
            elif line.startswith('*') and not line.startswith('**'):
                date_text = line.strip('*').strip()
                
                # Skip if it's metadata we've already handled
                if date_text.startswith('Logo:') or date_text.startswith('Website:'):
                    continue
                
                # Check if it's a date range
                if any(year in date_text for year in ['20', '19']) or 'Now' in date_text:
                    start_date, end_date = self._parse_date_range(date_text)
                    experience_record['start_date'] = start_date
                    experience_record['end_date'] = end_date
                    experience_record['is_current'] = 'Now' in date_text or end_date is None
                else:
                    # Might be location
                    experience_record['location'] = date_text
            
            # Parse achievements (add to description)
            elif line.startswith('- '):
                description_lines.append(line.strip('- ').strip())
            
            else:
                # Other descriptive content
                if line and not line.startswith('#'):
                    description_lines.append(line)
        
        # Store details for experience details table
        experience_record['details'] = [detail.strip() for detail in description_lines if detail.strip()]
        
        return experience_record
    
    def _extract_publications(self, content: str) -> List[Dict[str, Any]]:
        """Extract publications with detailed parsing"""
        publications = []
        
        # Find publications section
        pub_section = self._extract_section(content, 'Publications')
        if not pub_section:
            return publications
        
        # Parse numbered publications
        pub_pattern = r'(\d+)\.\s+(.+?)(?=\n\d+\.|$)'
        matches = re.finditer(pub_pattern, pub_section, re.DOTALL)
        
        for match in matches:
            pub_text = match.group(2).strip()
            publication_record = self._parse_publication_entry(pub_text)
            if publication_record:
                publications.append(publication_record)
        
        return publications
    
    def _parse_publication_entry(self, pub_text: str) -> Optional[Dict[str, Any]]:
        """Parse a single publication entry"""
        # Extract authors first (usually at the beginning)
        authors = self._extract_authors(pub_text)
        
        # Extract title - look for text in quotes or after authors
        title = ''
        
        # Pattern 1: Title in quotes
        quote_match = re.search(r'"([^"]+)"', pub_text)
        if quote_match:
            title = quote_match.group(1).strip()
        else:
            # Pattern 2: Title after authors, before journal/venue
            # Remove authors from beginning
            pub_text_no_authors = pub_text
            if authors:
                for author in authors:
                    pub_text_no_authors = pub_text_no_authors.replace(author, '', 1)
            
            # Clean up and look for title
            pub_text_no_authors = re.sub(r'^[,.\s]+', '', pub_text_no_authors)
            
            # Extract until journal indicators or year
            title_match = re.search(r'^([^.(]+?)(?:\s+(?:In|Proceedings|Journal|\(\d{4}\)|$))', pub_text_no_authors)
            if title_match:
                title = title_match.group(1).strip()
            else:
                # Fallback: take first reasonable chunk
                title_parts = pub_text_no_authors.split('.')
                if len(title_parts) > 0:
                    title = title_parts[0].strip()
        
        # If title is still suspicious (too short, looks like author name), use fallback
        if len(title) < 10 or re.match(r'^[A-Z][a-z]+,?\s*[A-Z]\.?$', title):
            title = "Publication title needs manual review"
        
        # Extract year
        year_match = re.search(r'\((\d{4})\)', pub_text)
        year = int(year_match.group(1)) if year_match else None
        
        # Extract journal/venue - look for various patterns
        journal = ''
        venue_patterns = [
            r'In\s+([^,.(]+)',
            r'Proceedings of\s+([^,.(]+)',
            r'Journal of\s+([^,.(]+)',
            r'([A-Z][^,.(]*(?:Conference|Workshop|Symposium|Journal)[^,.(]*)',
        ]
        
        for pattern in venue_patterns:
            venue_match = re.search(pattern, pub_text, re.IGNORECASE)
            if venue_match:
                journal = venue_match.group(1).strip()
                break
        
        # Extract DOI if present
        doi_match = re.search(r'doi:?\s*([^\s]+)', pub_text, re.IGNORECASE)
        doi = doi_match.group(1) if doi_match else ''
        
        publication_record = {
            'title': title,
            'authors': authors,  # Keep as list for separate table handling
            'journal_name': journal,
            'publication_type': self._determine_publication_type(pub_text),
            'publication_date': date(year, 1, 1) if year else None,
            'doi': doi,
            'is_peer_reviewed': True,
            'sort_order': 0
        }
        
        return publication_record
    
    def _extract_authors(self, pub_text: str) -> List[str]:
        """Extract authors from publication text"""
        # Clean up the text first - remove any leading numbering or whitespace
        clean_text = re.sub(r'^\d+\.\s*', '', pub_text).strip()
        
        # Look for author patterns at the beginning of the text
        author_patterns = [
            # Pattern 1: Authors before quoted title
            r'^([^"]+?)(?:\s*")',
            # Pattern 2: Authors before "In" or "Proceedings"  
            r'^([^."]+?)(?:\s+(?:In\s|Proceedings))',
            # Pattern 3: Authors before year in parentheses
            r'^([^."(]+?)(?:\s*\(\d{4}\))',
            # Pattern 4: Authors ending with period before title
            r'^([A-Z][^."]+?)\.\s*[A-Z"]',
            # Pattern 5: General pattern - text before journal/venue indicators
            r'^([^."]+?)(?:\s+(?:Communications|Journal|Proceedings|PeerJ|SPIE))',
        ]
        
        for pattern in author_patterns:
            match = re.search(pattern, clean_text, re.IGNORECASE)
            if match:
                authors_text = match.group(1).strip()
                
                # Remove common prefixes that might be included
                authors_text = re.sub(r'^(and|&)\s+', '', authors_text).strip()
                
                # Split by common separators
                authors = []
                
                # Try different separators in order of preference
                if ' and ' in authors_text:
                    authors = [author.strip() for author in authors_text.split(' and ')]
                elif ', ' in authors_text and not '.' in authors_text.split(',')[0]:
                    # Only split by comma if first part doesn't contain period (avoid splitting initials)
                    authors = [author.strip() for author in authors_text.split(',')]
                elif ' & ' in authors_text:
                    authors = [author.strip() for author in authors_text.split(' & ')]
                else:
                    # Single author or couldn't split
                    authors = [authors_text]
                
                # Clean up author names and filter out invalid ones
                cleaned_authors = []
                for author in authors:
                    author = author.strip()
                    
                    # Skip if empty or too short
                    if not author or len(author) < 2:
                        continue
                        
                    # Skip common false positives
                    if (author.lower().startswith(('in ', 'proceedings', 'journal', 'vol ')) or
                        author.isdigit() or
                        len(author.split()) > 6):  # Too many words, probably not an author
                        continue
                    
                    # Clean up punctuation
                    author = re.sub(r'[,;]$', '', author).strip()
                    
                    if author:
                        cleaned_authors.append(author)
                
                if cleaned_authors:
                    return cleaned_authors
        
        return []
    
    def _determine_publication_type(self, pub_text: str) -> str:
        """Determine publication type from text"""
        text_lower = pub_text.lower()
        
        if 'conference' in text_lower or 'proceedings' in text_lower:
            return 'conference'
        elif 'journal' in text_lower or 'transactions' in text_lower:
            return 'journal'
        elif 'workshop' in text_lower:
            return 'workshop'
        elif 'arxiv' in text_lower or 'preprint' in text_lower:
            return 'preprint'
        else:
            return 'journal'
    
    def _extract_awards(self, content: str) -> List[Dict[str, Any]]:
        """Extract awards and achievements"""
        awards = []
        
        # Find awards section
        awards_section = self._extract_section(content, 'Awards')
        if not awards_section:
            return awards
        
        # Parse award entries
        award_lines = awards_section.split('\n')
        
        for line in award_lines:
            if line.strip().startswith('- '):
                award_text = line.strip('- ').strip()
                award_record = self._parse_award_entry(award_text)
                if award_record:
                    awards.append(award_record)
        
        return awards
    
    def _parse_award_entry(self, award_text: str) -> Optional[Dict[str, Any]]:
        """Parse a single award entry"""
        # Extract date
        date_match = re.search(r'(\w+\s+\d{4})', award_text)
        award_date = None
        
        if date_match:
            try:
                award_date = datetime.strptime(date_match.group(1), '%b %Y').date()
            except ValueError:
                try:
                    award_date = datetime.strptime(date_match.group(1), '%B %Y').date()
                except ValueError:
                    pass
        
        # Extract title (remove date)
        title = re.sub(r'^\w+\s+\d{4}\s+', '', award_text).strip()
        
        # Extract organization if present
        org_match = re.search(r'by\s+([^,]+)', title)
        organization = org_match.group(1).strip() if org_match else ''
        
        if org_match:
            title = title.replace(org_match.group(0), '').strip()
        
        award_record = {
            'title': title,
            'awarding_organization': organization,
            'award_date': award_date,
            'description': award_text,
            'certificate_url': '',
            'sort_order': 0
        }
        
        return award_record
    
    def _extract_skills(self, content: str) -> Dict[str, Any]:
        """Extract skills and technologies"""
        skills_data = {
            'technologies': [],
            'programming_languages': [],
            'frameworks': [],
            'tools': [],
            'soft_skills': []
        }
        
        # Find skills section
        skills_section = self._extract_section(content, 'Skills')
        if not skills_section:
            return skills_data
        
        # Parse skills by category
        lines = skills_section.split('\n')
        
        for line in lines:
            if ':' in line:
                category_raw, technologies_raw = line.split(':', 1)
                category = category_raw.strip('- **').lower()
                technologies = [tech.strip() for tech in technologies_raw.split(',')]
                
                if 'programming' in category or 'language' in category:
                    skills_data['programming_languages'].extend(technologies)
                elif 'technolog' in category or 'framework' in category:
                    skills_data['frameworks'].extend(technologies)
                elif 'tool' in category:
                    skills_data['tools'].extend(technologies)
                else:
                    skills_data['technologies'].extend(technologies)
        
        # Combine all for main technologies list
        all_techs = (skills_data['programming_languages'] + 
                    skills_data['frameworks'] + 
                    skills_data['tools'] + 
                    skills_data['technologies'])
        
        skills_data['technologies'] = list(set(all_techs))
        
        return skills_data
    
    def _extract_research_experience(self, content: str) -> List[Dict[str, Any]]:
        """Extract research experience"""
        research_data = []
        
        # Find research section
        research_section = self._extract_section(content, 'Research Experience')
        if not research_section:
            return research_data
        
        # Parse research entries
        entries = re.split(r'\n###\s+', research_section)
        
        for entry in entries:
            if not entry.strip():
                continue
            
            research_record = self._parse_research_entry(entry)
            if research_record:
                research_data.append(research_record)
        
        return research_data
    
    def _parse_research_entry(self, entry: str) -> Optional[Dict[str, Any]]:
        """Parse a single research entry"""
        lines = entry.strip().split('\n')
        if not lines:
            return None
        
        # First line is the research title
        title = lines[0].strip('#').strip()
        
        research_record = {
            'title': title,
            'start_date': None,
            'end_date': None,
            'is_ongoing': False,
            'location': '',
            'research_type': 'individual',
            'funding_source': '',
            'funding_amount': None,
            'sort_order': 0
        }
        
        description_lines = []
        
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            
            # Parse location and dates
            if line.startswith('*') and not line.startswith('**'):
                info = line.strip('*').strip()
                
                # Check if it's a date range
                if any(year in info for year in ['20', '19']):
                    start_date, end_date = self._parse_date_range(info)
                    research_record['start_date'] = start_date
                    research_record['end_date'] = end_date
                    research_record['is_ongoing'] = end_date is None
                else:
                    # Probably location
                    research_record['location'] = info
            
            else:
                description_lines.append(line)
        
        # Store description as details array for ResearchProjectDetail table
        description_text = '\n'.join(description_lines).strip()
        research_record['details'] = [description_text] if description_text else []
        
        return research_record
    
    def _extract_username_from_url(self, url: str) -> str:
        """Extract username from social media URL"""
        if not url:
            return ''
        
        # Common patterns for extracting usernames
        patterns = [
            r'github\.com/([^/]+)',
            r'linkedin\.com/in/([^/]+)',
            r'twitter\.com/([^/]+)',
            r'instagram\.com/([^/]+)',
            r'facebook\.com/([^/]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return ''
    
    def _validate_content(self, extracted: ExtractedContent):
        """Validate extracted resume content"""
        # Check for required fields
        main_entity = extracted.main_entity
        
        if not main_entity.get('full_name'):
            extracted.validation_errors.append('Missing full name')
        
        if not main_entity.get('email'):
            extracted.validation_warnings.append('Missing email address')
        
        if not extracted.metadata.get('education'):
            extracted.validation_warnings.append('No education information found')
        
        if not extracted.metadata.get('experience'):
            extracted.validation_warnings.append('No work experience found')
        
        # Validate date ranges
        for edu in extracted.metadata.get('education', []):
            if edu.get('start_date') and edu.get('end_date'):
                if edu['start_date'] > edu['end_date']:
                    extracted.validation_errors.append(
                        f'Invalid date range in education: {edu["institution"]}'
                    )
        
        for exp in extracted.metadata.get('experience', []):
            if exp.get('start_date') and exp.get('end_date'):
                if exp['start_date'] > exp['end_date']:
                    extracted.validation_errors.append(
                        f'Invalid date range in experience: {exp["company"]}'
                    )
    
    def _enhance_experience_with_metadata(self, experience_data: List[Dict], metadata: Dict) -> List[Dict]:
        """Add logos and websites from metadata to experience records"""
        experience_logos = metadata.get('experience_logos', {})
        experience_websites = metadata.get('experience_websites', {})
        
        for exp in experience_data:
            # First priority: Check for directly specified logo key
            if '_logo_key' in exp:
                logo_key = exp['_logo_key']
                if logo_key in experience_logos:
                    exp['company_logo_url'] = experience_logos[logo_key]
                # Remove the temporary key
                del exp['_logo_key']
            else:
                # Fallback to automatic matching
                company = exp.get('company', '').lower()
                description = ' '.join(exp.get('details', [])).lower()
                search_text = f"{company} {description}"
                
                # Try to match logos automatically
                for key, logo_url in experience_logos.items():
                    key_lower = key.lower()
                    if (key_lower in company or 
                        key_lower in description or 
                        any(keyword in search_text for keyword in key_lower.split('_'))):
                        exp['company_logo_url'] = logo_url
                        break
            
            # Handle websites (only auto-match if not directly specified)
            if not exp.get('company_website'):
                company = exp.get('company', '').lower()
                description = ' '.join(exp.get('details', [])).lower()
                search_text = f"{company} {description}"
                
                for key, website_url in experience_websites.items():
                    key_lower = key.lower()
                    if (key_lower in company or 
                        key_lower in description or 
                        any(keyword in search_text for keyword in key_lower.split('_'))):
                        exp['company_website'] = website_url
                        break
        
        return experience_data
    
    def _extract_recent_updates(self, content: str) -> List[Dict[str, Any]]:
        """Extract structured recent updates"""
        recent_updates = []
        
        # Find recent updates section
        updates_section = self._extract_section(content, 'Recent Updates')
        if not updates_section:
            return recent_updates
        
        # Parse update entries by looking for ### headers
        entries = re.split(r'\n###\s+', updates_section)
        
        for entry in entries:
            if not entry.strip():
                continue
            
            update_record = self._parse_recent_update_entry(entry)
            if update_record:
                recent_updates.append(update_record)
        
        return recent_updates
    
    def _parse_recent_update_entry(self, entry: str) -> Optional[Dict[str, Any]]:
        """Parse a single recent update entry"""
        lines = entry.strip().split('\n')
        if not lines:
            return None
        
        # First line is the title with type
        title_line = lines[0].strip('#').strip()
        
        update_record = {
            'id': '',
            'type': '',
            'title': title_line,
            'description': '',
            'date': '',
            'tags': [],
            'status': '',
            'priority': ''
        }
        
        description_lines = []
        
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            
            # Parse metadata fields
            if line.startswith('*ID*:'):
                update_record['id'] = line.replace('*ID*:', '').strip()
            elif line.startswith('*Type*:'):
                update_record['type'] = line.replace('*Type*:', '').strip()
            elif line.startswith('*Date*:'):
                update_record['date'] = line.replace('*Date*:', '').strip()
            elif line.startswith('*Status*:'):
                update_record['status'] = line.replace('*Status*:', '').strip()
            elif line.startswith('*Priority*:'):
                update_record['priority'] = line.replace('*Priority*:', '').strip()
            elif line.startswith('*Tags*:'):
                tags_text = line.replace('*Tags*:', '').strip()
                update_record['tags'] = [tag.strip() for tag in tags_text.split(',')]
            else:
                # Description content
                description_lines.append(line)
        
        update_record['description'] = '\n'.join(description_lines).strip()
        
        # Extract clean title (remove type prefix if present)
        if ':' in update_record['title']:
            update_record['title'] = update_record['title'].split(':', 1)[1].strip()
        
        return update_record