"""
Idea parser for extracting structured idea information including
feasibility analysis, implementation details, and collaboration requirements.

Supports both individual markdown files and folder-based idea structure
with research materials, notes, experiments, and references.
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from pathlib import Path
import yaml
from .base_parser import BaseParser, ExtractedContent


class IdeaParser(BaseParser):
    """
    Specialized parser for idea content.
    
    Extracts idea metadata, feasibility analysis, implementation requirements,
    collaboration needs, and business potential with detailed scoring.
    """
    
    def __init__(self, content_dir):
        super().__init__(content_dir, logger_name="idea_parser")
    
    def _get_content_type(self) -> str:
        return 'idea'
    
    def debug_motivation_extraction(self, file_path: Path) -> str:
        """Debug method to test motivation extraction"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract motivation section
            import re
            for level in ['##', '###', '####']:
                pattern = rf'\n{level}\s+Motivation\s*\n(.*?)(?=\n{level}\s+|\Z)'
                match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
                if match:
                    return match.group(1).strip()
            return ''
        except Exception as e:
            return f"Error: {e}"

    def parse_folder(self, folder_path: Path) -> Optional[ExtractedContent]:
        """
        Parse an idea folder structure with enhanced debugging.
        """
        try:
            # Look for main content file
            main_files = ['README.md', 'index.md', 'idea.md']
            main_file = None
            
            for filename in main_files:
                file_path = folder_path / filename
                if file_path.exists():
                    main_file = file_path
                    break
            
            if not main_file:
                self.error(f"No main content file found in {folder_path}")
                return None
            
            # Debug motivation extraction
            debug_motivation = self.debug_motivation_extraction(main_file)
            
            # Parse main content file
            extracted = self.parse_file(main_file)
            if not extracted:
                return None
            
            # Force set motivation if it was lost
            if not extracted.main_entity.get('motivation') and debug_motivation:
                extracted.main_entity['motivation'] = debug_motivation
            
            # Load idea configuration if exists
            config_file = folder_path / 'config.yaml'
            config_data = {}
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config_data = yaml.safe_load(f) or {}
                except Exception as e:
                    self.warning(f"Error reading config.yaml: {e}")
            
            # Enhance extracted data with folder structure
            self._enhance_with_folder_data(extracted, folder_path, config_data)
            
            # Final check - if motivation is still empty, force set it
            if not extracted.main_entity.get('motivation') and debug_motivation:
                extracted.main_entity['motivation'] = debug_motivation
            
            return extracted
            
        except Exception as e:
            self.error(f"Error parsing idea folder {folder_path}: {e}")
            return None
    
    def _enhance_with_folder_data(self, extracted: ExtractedContent, folder_path: Path, config_data: Dict):
        """Enhance extracted data with folder structure information"""
        
        # Update idea data with config
        if config_data:
            idea_data = extracted.main_entity
            
            # Handle nested config structure (config.yaml may have 'idea' key)
            if 'idea' in config_data:
                config_idea_data = config_data['idea']
            else:
                config_idea_data = config_data
            
            # Override with config data if available, but preserve motivation if already extracted
            for key, value in config_idea_data.items():
                if key in idea_data and value is not None:
                    # Don't override motivation if it was already extracted from content
                    if key == 'motivation' and idea_data.get('motivation'):
                        continue
                    idea_data[key] = value
            
            # Add folder-specific data to metadata (not main entity)
            extracted.metadata['folder_path'] = str(folder_path)
            extracted.metadata['config_data'] = config_data
        
        # Scan research folder
        research_data = self._scan_research_folder(folder_path / 'research')
        extracted.metadata['research_materials'] = research_data
        
        # Scan notes folder
        notes_data = self._scan_notes_folder(folder_path / 'notes')
        extracted.metadata['development_notes'] = notes_data
        
        # Scan experiments folder
        experiments_data = self._scan_experiments_folder(folder_path / 'experiments')
        extracted.metadata['experiments'] = experiments_data
        
        # Scan references folder
        references_data = self._scan_references_folder(folder_path / 'references')
        extracted.metadata['references'] = references_data
        
        # Scan prototypes folder
        prototypes_data = self._scan_prototypes_folder(folder_path / 'prototypes')
        extracted.metadata['prototypes'] = prototypes_data
        
        # Scan assets folder
        assets_data = self._scan_assets_folder(folder_path / 'assets')
        extracted.metadata['assets'] = assets_data
        if assets_data.get('images'):
            extracted.images.extend(assets_data['images'])
    
    def _scan_research_folder(self, research_folder: Path) -> Dict[str, Any]:
        """Scan research folder for research materials"""
        research_data = {
            'papers': [],
            'market_analysis': [],
            'competitive_analysis': [],
            'technical_research': []
        }
        
        if not research_folder.exists():
            return research_data
        
        for research_file in research_folder.rglob('*'):
            if research_file.is_file() and research_file.suffix.lower() in {'.md', '.txt', '.pdf', '.doc', '.docx'}:
                filename_lower = research_file.name.lower()
                
                file_data = {
                    'filename': research_file.name,
                    'path': str(research_file.relative_to(research_folder)),
                    'size': research_file.stat().st_size,
                    'modified': datetime.fromtimestamp(research_file.stat().st_mtime)
                }
                
                # Categorize research file
                if any(keyword in filename_lower for keyword in ['paper', 'article', 'journal']):
                    research_data['papers'].append(file_data)
                elif any(keyword in filename_lower for keyword in ['market', 'user', 'survey']):
                    research_data['market_analysis'].append(file_data)
                elif any(keyword in filename_lower for keyword in ['competitor', 'competitive', 'analysis']):
                    research_data['competitive_analysis'].append(file_data)
                else:
                    research_data['technical_research'].append(file_data)
        
        return research_data
    
    def _scan_notes_folder(self, notes_folder: Path) -> List[Dict[str, Any]]:
        """Scan notes folder for development notes"""
        notes = []
        
        if not notes_folder.exists():
            return notes
        
        for note_file in notes_folder.rglob('*.md'):
            if note_file.is_file():
                try:
                    # Read content for analysis
                    with open(note_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        summary = content[:200] + ('...' if len(content) > 200 else '')
                    
                    # Categorize note type
                    note_type = self._categorize_note_type(note_file.name, content)
                    
                    notes.append({
                        'filename': note_file.name,
                        'path': str(note_file.relative_to(notes_folder)),
                        'type': note_type,
                        'summary': summary,
                        'size': note_file.stat().st_size,
                        'modified': datetime.fromtimestamp(note_file.stat().st_mtime)
                    })
                except Exception:
                    continue
        
        return notes
    
    def _scan_experiments_folder(self, experiments_folder: Path) -> List[Dict[str, Any]]:
        """Scan experiments folder for experiment records"""
        experiments = []
        
        if not experiments_folder.exists():
            return experiments
        
        for exp_file in experiments_folder.rglob('*'):
            if exp_file.is_file():
                experiment_data = {
                    'filename': exp_file.name,
                    'path': str(exp_file.relative_to(experiments_folder)),
                    'type': self._classify_experiment_type(exp_file.name),
                    'size': exp_file.stat().st_size,
                    'modified': datetime.fromtimestamp(exp_file.stat().st_mtime)
                }
                
                # Try to extract experiment metadata from markdown files
                if exp_file.suffix.lower() == '.md':
                    try:
                        with open(exp_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            experiment_data['summary'] = content[:200] + ('...' if len(content) > 200 else '')
                    except Exception:
                        pass
                
                experiments.append(experiment_data)
        
        return experiments
    
    def _scan_references_folder(self, references_folder: Path) -> List[Dict[str, Any]]:
        """Scan references folder for reference materials"""
        references = []
        
        if not references_folder.exists():
            return references
        
        reference_exts = {'.md', '.txt', '.pdf', '.url', '.webloc'}
        
        for ref_file in references_folder.rglob('*'):
            if ref_file.is_file() and ref_file.suffix.lower() in reference_exts:
                ref_data = {
                    'filename': ref_file.name,
                    'path': str(ref_file.relative_to(references_folder)),
                    'type': self._classify_reference_type(ref_file.name),
                    'size': ref_file.stat().st_size,
                    'modified': datetime.fromtimestamp(ref_file.stat().st_mtime)
                }
                
                # Extract URL from .url files
                if ref_file.suffix.lower() == '.url':
                    try:
                        with open(ref_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            url_match = re.search(r'URL=(.+)', content)
                            if url_match:
                                ref_data['url'] = url_match.group(1).strip()
                    except Exception:
                        pass
                
                references.append(ref_data)
        
        return references
    
    def _scan_prototypes_folder(self, prototypes_folder: Path) -> List[Dict[str, Any]]:
        """Scan prototypes folder for prototype files"""
        prototypes = []
        
        if not prototypes_folder.exists():
            return prototypes
        
        for proto_file in prototypes_folder.rglob('*'):
            if proto_file.is_file():
                prototype_data = {
                    'filename': proto_file.name,
                    'path': str(proto_file.relative_to(prototypes_folder)),
                    'type': self._classify_prototype_type(proto_file.name),
                    'size': proto_file.stat().st_size,
                    'modified': datetime.fromtimestamp(proto_file.stat().st_mtime)
                }
                
                prototypes.append(prototype_data)
        
        return prototypes
    
    def _scan_assets_folder(self, assets_folder: Path) -> Dict[str, Any]:
        """Scan assets folder for images and media"""
        assets_data = {
            'images': [],
            'videos': [],
            'documents': []
        }
        
        if not assets_folder.exists():
            return assets_data
        
        # Image extensions
        image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp'}
        video_exts = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
        doc_exts = {'.pdf', '.doc', '.docx', '.ppt', '.pptx'}
        
        for asset_file in assets_folder.rglob('*'):
            if not asset_file.is_file():
                continue
            
            ext = asset_file.suffix.lower()
            
            if ext in image_exts:
                assets_data['images'].append({
                    'image_url': str(asset_file.relative_to(assets_folder)),
                    'alt_text': asset_file.stem.replace('-', ' ').replace('_', ' ').title(),
                    'caption': asset_file.stem.replace('-', ' ').replace('_', ' ').title(),
                    'image_type': self._classify_idea_image_type(asset_file.name),
                    'sort_order': len(assets_data['images']),
                    'file_size': asset_file.stat().st_size
                })
            elif ext in video_exts:
                assets_data['videos'].append({
                    'filename': asset_file.name,
                    'path': str(asset_file.relative_to(assets_folder)),
                    'size': asset_file.stat().st_size,
                    'modified': datetime.fromtimestamp(asset_file.stat().st_mtime)
                })
            elif ext in doc_exts:
                assets_data['documents'].append({
                    'filename': asset_file.name,
                    'path': str(asset_file.relative_to(assets_folder)),
                    'size': asset_file.stat().st_size,
                    'modified': datetime.fromtimestamp(asset_file.stat().st_mtime)
                })
        
        return assets_data
    
    def _categorize_note_type(self, filename: str, content: str) -> str:
        """Categorize development note type"""
        filename_lower = filename.lower()
        content_lower = content.lower()
        
        if any(keyword in filename_lower for keyword in ['meeting', 'discussion']):
            return 'meeting_notes'
        elif any(keyword in filename_lower for keyword in ['brainstorm', 'idea']):
            return 'brainstorming'
        elif any(keyword in filename_lower for keyword in ['tech', 'technical']):
            return 'technical_notes'
        elif any(keyword in filename_lower for keyword in ['design', 'ui', 'ux']):
            return 'design_notes'
        elif any(keyword in content_lower for keyword in ['todo', 'task', 'action']):
            return 'action_items'
        else:
            return 'general_notes'
    
    def _classify_experiment_type(self, filename: str) -> str:
        """Classify experiment type"""
        filename_lower = filename.lower()
        
        if any(keyword in filename_lower for keyword in ['prototype', 'proof', 'poc']):
            return 'proof_of_concept'
        elif any(keyword in filename_lower for keyword in ['user', 'usability', 'test']):
            return 'user_testing'
        elif any(keyword in filename_lower for keyword in ['performance', 'benchmark']):
            return 'performance_testing'
        elif any(keyword in filename_lower for keyword in ['a/b', 'ab', 'variant']):
            return 'ab_testing'
        else:
            return 'general_experiment'
    
    def _classify_reference_type(self, filename: str) -> str:
        """Classify reference type"""
        filename_lower = filename.lower()
        
        if any(keyword in filename_lower for keyword in ['paper', 'research', 'academic']):
            return 'academic_paper'
        elif any(keyword in filename_lower for keyword in ['tutorial', 'guide', 'howto']):
            return 'tutorial'
        elif any(keyword in filename_lower for keyword in ['blog', 'article']):
            return 'blog_article'
        elif any(keyword in filename_lower for keyword in ['video', 'youtube', 'vimeo']):
            return 'video_content'
        elif any(keyword in filename_lower for keyword in ['tool', 'software', 'library']):
            return 'tool_reference'
        else:
            return 'general_reference'
    
    def _classify_prototype_type(self, filename: str) -> str:
        """Classify prototype type"""
        ext = Path(filename).suffix.lower()
        filename_lower = filename.lower()
        
        if ext in ['.html', '.css', '.js']:
            return 'web_prototype'
        elif ext in ['.py', '.java', '.cpp', '.go']:
            return 'code_prototype'
        elif ext in ['.fig', '.sketch', '.psd', '.ai']:
            return 'design_prototype'
        elif ext in ['.blend', '.fbx', '.obj']:
            return '3d_prototype'
        elif any(keyword in filename_lower for keyword in ['wireframe', 'mockup']):
            return 'wireframe'
        else:
            return 'general_prototype'
    
    def _classify_idea_image_type(self, filename: str) -> str:
        """Classify idea image type"""
        filename_lower = filename.lower()
        
        if any(keyword in filename_lower for keyword in ['mockup', 'wireframe']):
            return 'mockup'
        elif any(keyword in filename_lower for keyword in ['diagram', 'flow', 'architecture']):
            return 'diagram'
        elif any(keyword in filename_lower for keyword in ['sketch', 'concept']):
            return 'concept_sketch'
        elif any(keyword in filename_lower for keyword in ['inspiration', 'reference']):
            return 'inspiration'
        else:
            return 'general_image'
    
    def _parse_content(self, post, extracted: ExtractedContent):
        """Parse idea content and extract structured data"""
        metadata = post.metadata
        content = post.content
        
        # Extract main idea data
        idea_data = self._extract_idea_data(metadata, content)
        extracted.main_entity = idea_data
        
        # Extract technologies and requirements
        technologies = self._extract_idea_technologies(metadata, content)
        extracted.technologies = technologies
        
        # Extract implementation details
        implementation = self._extract_implementation_details(content)
        
        # Extract feasibility analysis
        feasibility = self._analyze_feasibility(content)
        
        # Extract collaboration requirements
        collaboration = self._extract_collaboration_requirements(content)
        
        # Extract business analysis
        business_analysis = self._analyze_business_potential(content)
        
        # Extract market analysis
        market_analysis = self._analyze_market_potential(content)
        
        # Store all extracted data
        extracted.metadata.update({
            'implementation': implementation,
            'feasibility': feasibility,
            'collaboration': collaboration,
            'business_analysis': business_analysis,
            'market_analysis': market_analysis,
            'sections': self._extract_sections(content)
        })
    
    def _extract_idea_data(self, metadata: Dict, content: str) -> Dict[str, Any]:
        """Extract main idea information"""
        # Extract title from metadata or content
        title = metadata.get('title', '')
        if not title:
            # Extract title from first heading
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('# '):
                    title = line[2:].strip()
                    break
        
        slug = metadata.get('slug', self._generate_slug(title))
        
        # Extract abstract from metadata or content
        abstract = metadata.get('abstract', metadata.get('description', ''))
        if not abstract:
            # Look for Abstract section in content
            abstract_section = self._extract_section(content, 'Abstract')
            if abstract_section:
                # Take first paragraph of abstract section
                abstract = abstract_section.split('\n\n')[0].strip()
            elif title:
                # Fallback to a generated abstract
                abstract = f"An innovative idea focusing on {title.lower()}"
        
        # Extract motivation from content first, then fallback to metadata
        motivation = ''
        motivation_section = self._extract_section(content, 'Motivation')
        if motivation_section:
            motivation = motivation_section
        else:
            # Look for Problem section as alternative
            problem_section = self._extract_section(content, 'Problem')
            if problem_section:
                motivation = problem_section
            else:
                # Fallback to metadata
                motivation = metadata.get('motivation', '')
        
        # Extract problem statement
        problem_statement = self._extract_problem_statement(content)
        
        # Extract solution overview
        solution_overview = self._extract_solution_overview(content)
        
        # Calculate scores
        feasibility_score = self._calculate_feasibility_score(metadata, content)
        impact_score = self._calculate_impact_score(metadata, content)
        innovation_score = self._calculate_innovation_score(content)
        
        # Extract financial estimates
        financial_estimates = self._extract_financial_estimates(metadata, content)
        
        # Determine development stage
        development_stage = self._determine_development_stage(content)
        
        # Map collaboration and funding status properly
        collaboration_needed = metadata.get('collaboration_needed', metadata.get('collaborationOpen', False))
        if isinstance(collaboration_needed, str):
            collaboration_needed = collaboration_needed.lower() in ['true', 'yes', '1']
        
        funding_required = metadata.get('funding_required', False)
        if metadata.get('fundingStatus') == 'seeking':
            funding_required = True
        elif metadata.get('fundingStatus') == 'funded':
            funding_required = False
        
        # Parse duration from string like "6-8 months"
        duration_months = self._extract_duration_months(metadata.get('estimated_duration', ''))
        
        idea_data = {
            'title': title,
            'slug': slug,
            'abstract': abstract,
            'motivation': motivation, # Ensure motivation is preserved
            'methodology': solution_overview or self._extract_methodology(content),
            'expected_outcome': self._extract_expected_outcome(content),
            'status': self._map_idea_status(metadata.get('status', 'draft')),
            'estimated_duration_months': duration_months,
            'collaboration_needed': collaboration_needed,
            'funding_required': funding_required,
            'estimated_budget': financial_estimates.get('budget'),
            'required_resources': self._extract_required_resources_string(content),
            'is_public': metadata.get('is_public', True),  # Default to public for content-extracted ideas
            'view_count': 0,
            'like_count': 0,
            'priority': self._map_priority_level(feasibility_score, impact_score)
        }
        
        return idea_data
    
    def _extract_duration_months(self, duration_str: str) -> Optional[int]:
        """Extract duration in months from string like '6-8 months'"""
        if not duration_str:
            return None
        
        import re
        # Extract numbers from string like "6-8 months" or "12 months"
        numbers = re.findall(r'\d+', duration_str)
        if numbers:
            # If range like "6-8", take the average
            if len(numbers) >= 2:
                return (int(numbers[0]) + int(numbers[1])) // 2
            else:
                return int(numbers[0])
        return None
    
    def _extract_methodology(self, content: str) -> str:
        """Extract methodology from content"""
        # Look for Technical Approach or Implementation sections
        sections = ['technical approach', 'implementation', 'methodology', 'approach']
        for section in sections:
            section_content = self._extract_section(content, section)
            if section_content:
                return section_content[:500]  # Limit length
        return ''
    
    def _extract_expected_outcome(self, content: str) -> str:
        """Extract expected outcomes from content"""
        # Look for Expected Outcomes, Results, or Deliverables sections
        sections = ['expected outcomes', 'expected outcome', 'deliverables', 'results', 'impact metrics']
        for section in sections:
            section_content = self._extract_section(content, section)
            if section_content:
                return section_content[:500]  # Limit length
        return ''
    
    def _extract_required_resources_string(self, content: str) -> str:
        """Extract required resources from content as a string"""
        # Look for resources, requirements, or funding sections
        sections = ['funding requirements', 'resources', 'requirements', 'personnel', 'infrastructure']
        for section in sections:
            section_content = self._extract_section(content, section)
            if section_content:
                return section_content[:500]  # Limit length
        return ''
    
    def _extract_required_resources(self, content: str) -> str:
        """Extract required resources from content"""
        # Look for resources, requirements, or funding sections
        sections = ['funding requirements', 'resources', 'requirements', 'personnel', 'infrastructure']
        for section in sections:
            section_content = self._extract_section(content, section)
            if section_content:
                return section_content[:500]  # Limit length
        return ''
    
    def _map_priority_level(self, feasibility_score: float, impact_score: float):
        """Map scores to priority levels matching enum"""
        from silan.models.ideas import IdeaPriority
        
        avg_score = (feasibility_score + impact_score) / 2
        if avg_score >= 8.0:
            return IdeaPriority.HIGH
        elif avg_score >= 6.0:
            return IdeaPriority.MEDIUM
        else:
            return IdeaPriority.LOW
    
    def _map_idea_status(self, status: str):
        """Map status to IdeaStatus enum values"""
        from silan.models.ideas import IdeaStatus
        
        status_lower = status.lower()
        
        status_mapping = {
            'draft': IdeaStatus.DRAFT,
            'hypothesis': IdeaStatus.HYPOTHESIS, 
            'experimenting': IdeaStatus.EXPERIMENTING,
            'validating': IdeaStatus.VALIDATING,
            'published': IdeaStatus.PUBLISHED,
            'concluded': IdeaStatus.CONCLUDED
        }
        
        return status_mapping.get(status_lower, IdeaStatus.DRAFT)
    
    def _extract_idea_technologies(self, metadata: Dict, content: str) -> List[Dict[str, Any]]:
        """Extract technologies required for the idea"""
        technologies = []
        
        # Get from metadata
        tech_list = metadata.get('tech_stack', [])
        
        # Also try to get from nested technologies structure
        if 'technologies' in metadata:
            tech_dict = metadata['technologies']
            if isinstance(tech_dict, dict):
                # Flatten all technology lists from different categories
                for category, techs in tech_dict.items():
                    if isinstance(techs, list):
                        tech_list.extend(techs)
            elif isinstance(tech_dict, list):
                tech_list.extend(tech_dict)
        
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
                'required_expertise': self._assess_required_expertise(tech_name, content),
                'availability': self._assess_tech_availability(tech_name),
                'learning_curve': self._assess_learning_curve(tech_name),
                'cost_factor': self._assess_tech_cost(tech_name),
                'sort_order': i
            }
            
            technologies.append(tech_data)
        
        return technologies
    
    def _extract_tech_from_content(self, content: str) -> List[str]:
        """Extract technologies mentioned in idea content"""
        technologies = []
        
        # Look for technology sections
        tech_sections = [
            self._extract_section(content, 'Technology'),
            self._extract_section(content, 'Technical Requirements'),
            self._extract_section(content, 'Tech Stack'),
            self._extract_section(content, 'Implementation')
        ]
        
        tech_content = ' '.join([section for section in tech_sections if section])
        if not tech_content:
            tech_content = content
        
        # Extract using patterns
        tech_patterns = [
            r'\b(React|Vue|Angular|Svelte|Next\.js|Nuxt\.js)\b',
            r'\b(Python|JavaScript|TypeScript|Java|Go|Rust|PHP|Ruby|Swift|Kotlin)\b',
            r'\b(TensorFlow|PyTorch|Keras|Scikit-learn|OpenCV|Pandas|NumPy)\b',
            r'\b(MySQL|PostgreSQL|MongoDB|Redis|SQLite|Elasticsearch)\b',
            r'\b(Docker|Kubernetes|AWS|Azure|GCP|Heroku|Vercel|Netlify)\b',
            r'\b(Express|Flask|Django|Spring|Rails|Laravel|FastAPI)\b',
            r'\b(Blockchain|AI|Machine Learning|Deep Learning|IoT|AR|VR)\b'
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, tech_content, re.IGNORECASE)
            technologies.extend(matches)
        
        return list(set(technologies))
    
    def _extract_problem_statement(self, content: str) -> str:
        """Extract the problem statement from content"""
        problem_section = self._extract_section(content, 'Problem')
        if problem_section:
            return problem_section
        
        # Look for problem indicators in first few paragraphs
        paragraphs = content.split('\n\n')[:3]
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if any(indicator in paragraph.lower() for indicator in 
                   ['problem', 'issue', 'challenge', 'difficulty', 'pain point']):
                return paragraph
        
        return ''
    
    def _extract_solution_overview(self, content: str) -> str:
        """Extract the solution overview from content"""
        solution_sections = [
            self._extract_section(content, 'Solution'),
            self._extract_section(content, 'Approach'),
            self._extract_section(content, 'Overview'),
            self._extract_section(content, 'Concept')
        ]
        
        for section in solution_sections:
            if section:
                return section
        
        # Fallback to first substantial paragraph
        paragraphs = content.split('\n\n')
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if len(paragraph) > 100 and not paragraph.startswith('#'):
                return paragraph
        
        return ''
    
    def _extract_implementation_details(self, content: str) -> Dict[str, Any]:
        """Extract implementation details and requirements"""
        implementation = {
            'phases': self._extract_implementation_phases(content),
            'resources_needed': self._extract_required_resources_dict(content),
            'timeline': self._extract_timeline(content),
            'milestones': self._extract_milestones(content),
            'risks': self._extract_risks(content),
            'dependencies': self._extract_dependencies(content)
        }
        
        return implementation
    
    def _extract_implementation_phases(self, content: str) -> List[Dict[str, Any]]:
        """Extract implementation phases"""
        phases = []
        
        # Look for phase sections
        phase_section = self._extract_section(content, 'Implementation')
        if not phase_section:
            phase_section = self._extract_section(content, 'Phases')
        if not phase_section:
            phase_section = self._extract_section(content, 'Plan')
        
        if phase_section:
            # Look for numbered or bullet points
            phase_items = self._extract_list_items(phase_section)
            
            for i, item in enumerate(phase_items):
                phases.append({
                    'phase_number': i + 1,
                    'name': f'Phase {i + 1}',
                    'description': item,
                    'estimated_duration': self._extract_phase_duration(item),
                    'dependencies': []
                })
        
        return phases
    
    def _extract_required_resources_dict(self, content: str) -> Dict[str, List[str]]:
        """Extract required resources as a dictionary"""
        resources = {
            'human_resources': [],
            'technical_resources': [],
            'financial_resources': [],
            'other_resources': []
        }
        
        # Look for resource sections
        resource_section = self._extract_section(content, 'Resources')
        if not resource_section:
            resource_section = self._extract_section(content, 'Requirements')
        
        if resource_section:
            # Categorize resources
            items = self._extract_list_items(resource_section)
            
            for item in items:
                item_lower = item.lower()
                if any(keyword in item_lower for keyword in ['developer', 'designer', 'manager', 'team', 'person', 'expert']):
                    resources['human_resources'].append(item)
                elif any(keyword in item_lower for keyword in ['server', 'api', 'database', 'software', 'tool', 'platform']):
                    resources['technical_resources'].append(item)
                elif any(keyword in item_lower for keyword in ['budget', 'funding', 'cost', 'money', 'investment']):
                    resources['financial_resources'].append(item)
                else:
                    resources['other_resources'].append(item)
        
        return resources
    
    def _extract_timeline(self, content: str) -> Dict[str, Any]:
        """Extract project timeline"""
        timeline = {
            'total_duration': None,
            'start_date': None,
            'milestones': []
        }
        
        # Look for timeline indicators
        timeline_section = self._extract_section(content, 'Timeline')
        if timeline_section:
            # Extract duration
            duration_match = re.search(r'(\d+)\s*(months?|weeks?|years?)', timeline_section, re.IGNORECASE)
            if duration_match:
                timeline['total_duration'] = f"{duration_match.group(1)} {duration_match.group(2)}"
        
        return timeline
    
    def _extract_milestones(self, content: str) -> List[Dict[str, Any]]:
        """Extract project milestones"""
        milestones = []
        
        milestone_section = self._extract_section(content, 'Milestones')
        if milestone_section:
            milestone_items = self._extract_list_items(milestone_section)
            
            for i, item in enumerate(milestone_items):
                milestones.append({
                    'name': f'Milestone {i + 1}',
                    'description': item,
                    'target_date': None,
                    'dependencies': []
                })
        
        return milestones
    
    def _extract_risks(self, content: str) -> List[Dict[str, Any]]:
        """Extract project risks"""
        risks = []
        
        risk_section = self._extract_section(content, 'Risks')
        if not risk_section:
            risk_section = self._extract_section(content, 'Challenges')
        
        if risk_section:
            risk_items = self._extract_list_items(risk_section)
            
            for item in risk_items:
                risks.append({
                    'description': item,
                    'probability': self._assess_risk_probability(item),
                    'impact': self._assess_risk_impact(item),
                    'mitigation': ''
                })
        
        return risks
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract project dependencies"""
        dependencies = []
        
        dep_section = self._extract_section(content, 'Dependencies')
        if dep_section:
            dependencies = self._extract_list_items(dep_section)
        
        return dependencies
    
    def _analyze_feasibility(self, content: str) -> Dict[str, Any]:
        """Analyze idea feasibility"""
        feasibility = {
            'technical_feasibility': self._assess_technical_feasibility(content),
            'market_feasibility': self._assess_market_feasibility(content),
            'financial_feasibility': self._assess_financial_feasibility(content),
            'operational_feasibility': self._assess_operational_feasibility(content),
            'overall_score': 0.0
        }
        
        # Calculate overall score
        scores = [feasibility[key] for key in feasibility if key != 'overall_score' and isinstance(feasibility[key], (int, float))]
        if scores:
            feasibility['overall_score'] = sum(scores) / len(scores)
        
        return feasibility
    
    def _extract_collaboration_requirements(self, content: str) -> Dict[str, Any]:
        """Extract collaboration requirements"""
        collaboration = {
            'team_size_needed': self._estimate_team_size(content),
            'skills_needed': self._extract_required_skills(content),
            'roles_needed': self._extract_required_roles(content),
            'collaboration_type': self._determine_collaboration_type(content),
            'remote_friendly': self._assess_remote_feasibility(content)
        }
        
        return collaboration
    
    def _analyze_business_potential(self, content: str) -> Dict[str, Any]:
        """Analyze business potential"""
        business = {
            'monetization_potential': self._assess_monetization_potential(content),
            'scalability': self._assess_scalability(content),
            'competitive_advantage': self._extract_competitive_advantage(content),
            'target_users': self._extract_target_users(content),
            'business_model': self._extract_business_model(content)
        }
        
        return business
    
    def _analyze_market_potential(self, content: str) -> Dict[str, Any]:
        """Analyze market potential"""
        market = {
            'market_size': self._assess_market_size(content),
            'growth_potential': self._assess_growth_potential(content),
            'competition_level': self._assess_competition_level(content),
            'market_trends': self._extract_market_trends(content),
            'barriers_to_entry': self._extract_barriers_to_entry(content)
        }
        
        return market
    
    def _categorize_idea(self, content: str) -> str:
        """Categorize the idea"""
        content_lower = content.lower()
        
        categories = {
            'AI/ML': ['artificial intelligence', 'machine learning', 'ai', 'ml', 'neural network', 'deep learning'],
            'Web Development': ['web app', 'website', 'frontend', 'backend', 'full stack'],
            'Mobile App': ['mobile app', 'android', 'ios', 'react native', 'flutter'],
            'IoT': ['iot', 'internet of things', 'sensors', 'smart device'],
            'Blockchain': ['blockchain', 'cryptocurrency', 'smart contract', 'defi'],
            'Health Tech': ['health', 'medical', 'healthcare', 'fitness', 'wellness'],
            'Fintech': ['financial', 'banking', 'payment', 'fintech', 'investment'],
            'Education': ['education', 'learning', 'teaching', 'edtech', 'training'],
            'Gaming': ['game', 'gaming', 'entertainment', 'vr', 'ar'],
            'Social': ['social', 'community', 'networking', 'collaboration'],
            'Business': ['business', 'enterprise', 'b2b', 'saas', 'productivity'],
            'Environment': ['environment', 'sustainability', 'green', 'climate']
        }
        
        for category, keywords in categories.items():
            if any(keyword in content_lower for keyword in keywords):
                return category
        
        return 'Other'
    
    def _determine_development_stage(self, content: str) -> str:
        """Determine the development stage"""
        content_lower = content.lower()
        
        if any(keyword in content_lower for keyword in ['concept', 'idea', 'brainstorming', 'initial']):
            return 'concept'
        elif any(keyword in content_lower for keyword in ['research', 'analysis', 'planning', 'design']):
            return 'research'
        elif any(keyword in content_lower for keyword in ['prototype', 'mvp', 'proof of concept', 'demo']):
            return 'prototype'
        elif any(keyword in content_lower for keyword in ['development', 'building', 'coding', 'implementation']):
            return 'development'
        elif any(keyword in content_lower for keyword in ['testing', 'beta', 'trial', 'validation']):
            return 'testing'
        elif any(keyword in content_lower for keyword in ['launch', 'production', 'deployed', 'live']):
            return 'launched'
        else:
            return 'concept'
    
    def _extract_duration(self, metadata: Dict, content: str) -> Optional[int]:
        """Extract estimated duration in months"""
        # Check metadata first
        duration = metadata.get('estimated_duration_months')
        if duration:
            return int(duration)
        
        # Extract from content
        duration_patterns = [
            r'(\d+)\s*months?',
            r'(\d+)\s*weeks?',  # Convert to months
            r'(\d+)\s*years?'   # Convert to months
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                value = int(match.group(1))
                if 'week' in pattern:
                    return max(1, value // 4)  # Convert weeks to months
                elif 'year' in pattern:
                    return value * 12  # Convert years to months
                else:
                    return value
        
        return None
    
    def _needs_collaboration(self, content: str) -> bool:
        """Determine if collaboration is needed"""
        content_lower = content.lower()
        
        collaboration_indicators = [
            'team', 'collaboration', 'partner', 'co-founder', 'help needed',
            'looking for', 'seeking', 'need help', 'require assistance'
        ]
        
        return any(indicator in content_lower for indicator in collaboration_indicators)
    
    def _requires_funding(self, content: str) -> bool:
        """Determine if funding is required"""
        content_lower = content.lower()
        
        funding_indicators = [
            'funding', 'investment', 'budget', 'cost', 'money needed',
            'capital', 'financial support', 'investor', 'venture capital'
        ]
        
        return any(indicator in content_lower for indicator in funding_indicators)
    
    def _extract_financial_estimates(self, metadata: Dict, content: str) -> Dict[str, Optional[float]]:
        """Extract financial estimates"""
        estimates = {
            'budget': metadata.get('estimated_budget'),
            'revenue_potential': None
        }
        
        # Extract budget from content
        if not estimates['budget']:
            budget_patterns = [
                r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'budget[:\s]*\$?(\d+(?:,\d{3})*)',
                r'cost[:\s]*\$?(\d+(?:,\d{3})*)'
            ]
            
            for pattern in budget_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    budget_str = match.group(1).replace(',', '')
                    estimates['budget'] = float(budget_str)
                    break
        
        # Extract revenue potential
        revenue_patterns = [
            r'revenue[:\s]*\$?(\d+(?:,\d{3})*)',
            r'profit[:\s]*\$?(\d+(?:,\d{3})*)',
            r'earning potential[:\s]*\$?(\d+(?:,\d{3})*)'
        ]
        
        for pattern in revenue_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                revenue_str = match.group(1).replace(',', '')
                estimates['revenue_potential'] = float(revenue_str)
                break
        
        return estimates
    
    def _calculate_feasibility_score(self, metadata: Dict, content: str) -> float:
        """Calculate feasibility score (1-10)"""
        score = metadata.get('feasibility_score', 5.0)
        
        if score is None:
            # Calculate based on content analysis
            score = 5.0  # Base score
            
            content_lower = content.lower()
            
            # Positive factors
            if any(keyword in content_lower for keyword in ['simple', 'straightforward', 'proven', 'existing technology']):
                score += 1
            
            if any(keyword in content_lower for keyword in ['prototype', 'tested', 'validated']):
                score += 1
            
            # Negative factors
            if any(keyword in content_lower for keyword in ['complex', 'challenging', 'unproven', 'cutting-edge']):
                score -= 1
            
            if any(keyword in content_lower for keyword in ['research needed', 'experimental', 'theoretical']):
                score -= 1
        
        return max(1.0, min(10.0, float(score)))
    
    def _calculate_impact_score(self, metadata: Dict, content: str) -> float:
        """Calculate impact score (1-10)"""
        score = metadata.get('impact_score', 5.0)
        
        if score is None:
            score = 5.0  # Base score
            
            content_lower = content.lower()
            
            # High impact indicators
            if any(keyword in content_lower for keyword in ['revolutionary', 'game-changing', 'disrupting', 'transformative']):
                score += 2
            
            if any(keyword in content_lower for keyword in ['millions of users', 'global', 'widespread']):
                score += 1
            
            # Lower impact indicators
            if any(keyword in content_lower for keyword in ['niche', 'small market', 'limited scope']):
                score -= 1
        
        return max(1.0, min(10.0, float(score)))
    
    def _calculate_innovation_score(self, content: str) -> float:
        """Calculate innovation score (1-10)"""
        score = 5.0  # Base score
        content_lower = content.lower()
        
        # Innovation indicators
        if any(keyword in content_lower for keyword in ['novel', 'innovative', 'first-of-its-kind', 'breakthrough']):
            score += 2
        
        if any(keyword in content_lower for keyword in ['new approach', 'unique', 'original']):
            score += 1
        
        # Existing solution indicators
        if any(keyword in content_lower for keyword in ['similar to', 'based on existing', 'incremental improvement']):
            score -= 1
        
        return max(1.0, min(10.0, score))
    
    def _calculate_priority_level(self, feasibility: float, impact: float) -> str:
        """Calculate priority level based on feasibility and impact"""
        if feasibility >= 7 and impact >= 7:
            return 'high'
        elif feasibility >= 5 and impact >= 5:
            return 'medium'
        else:
            return 'low'
    
    # Additional helper methods for detailed analysis
    def _assess_technical_feasibility(self, content: str) -> float:
        """Assess technical feasibility (1-10)"""
        # Simplified implementation
        return 7.0
    
    def _assess_market_feasibility(self, content: str) -> float:
        """Assess market feasibility (1-10)"""
        return 6.0
    
    def _assess_financial_feasibility(self, content: str) -> float:
        """Assess financial feasibility (1-10)"""
        return 5.0
    
    def _assess_operational_feasibility(self, content: str) -> float:
        """Assess operational feasibility (1-10)"""
        return 6.0
    
    def _validate_content(self, extracted: ExtractedContent):
        """Validate extracted idea content"""
        main_entity = extracted.main_entity
        
        # Check required fields
        if not main_entity.get('title'):
            extracted.validation_errors.append('Missing idea title')
        
        if not main_entity.get('content'):
            extracted.validation_errors.append('Missing idea content')
        
        if not main_entity.get('problem_statement'):
            extracted.validation_warnings.append('Missing problem statement')
        
        if not main_entity.get('solution_overview'):
            extracted.validation_warnings.append('Missing solution overview')
        
        # Validate scores
        for score_field in ['feasibility_score', 'impact_score', 'innovation_score']:
            score = main_entity.get(score_field, 0)
            if score < 1 or score > 10:
                extracted.validation_errors.append(f'Invalid {score_field}: must be between 1-10')
        
        # Validate financial data
        budget = main_entity.get('estimated_budget')
        if budget is not None and budget < 0:
            extracted.validation_errors.append('Budget cannot be negative')
        
        # Validate duration
        duration = main_entity.get('estimated_duration_months')
        if duration is not None and duration <= 0:
            extracted.validation_errors.append('Duration must be positive')
    
    # Placeholder methods for complex analysis (would need ML/NLP in real implementation)
    def _extract_target_market(self, content: str) -> str:
        return 'General'
    
    def _assess_competition_level(self, content: str) -> str:
        return 'medium'
    
    def _assess_technical_complexity(self, content: str) -> str:
        return 'medium'
    
    def _estimate_team_size(self, content: str) -> int:
        return 3
    
    def _extract_required_skills(self, content: str) -> List[str]:
        return []
    
    def _extract_required_roles(self, content: str) -> List[str]:
        return []
    
    def _determine_collaboration_type(self, content: str) -> str:
        return 'team-based'
    
    def _assess_remote_feasibility(self, content: str) -> bool:
        return True
    
    def _assess_monetization_potential(self, content: str) -> str:
        return 'medium'
    
    def _assess_scalability(self, content: str) -> str:
        return 'medium'
    
    def _extract_competitive_advantage(self, content: str) -> str:
        return ''
    
    def _extract_target_users(self, content: str) -> str:
        return ''
    
    def _extract_business_model(self, content: str) -> str:
        return ''
    
    def _assess_market_size(self, content: str) -> str:
        return 'medium'
    
    def _assess_growth_potential(self, content: str) -> str:
        return 'medium'
    
    def _extract_market_trends(self, content: str) -> List[str]:
        return []
    
    def _extract_barriers_to_entry(self, content: str) -> List[str]:
        return []
    
    def _extract_phase_duration(self, item: str) -> Optional[str]:
        return None
    
    def _assess_risk_probability(self, item: str) -> str:
        return 'medium'
    
    def _assess_risk_impact(self, item: str) -> str:
        return 'medium'
    
    def _assess_required_expertise(self, tech_name: str, content: str) -> str:
        return 'intermediate'
    
    def _assess_tech_availability(self, tech_name: str) -> str:
        return 'available'
    
    def _assess_learning_curve(self, tech_name: str) -> str:
        return 'medium'
    
    def _assess_tech_cost(self, tech_name: str) -> str:
        return 'medium'