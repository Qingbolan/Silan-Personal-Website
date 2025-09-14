"""Data validation utilities for the Silan application"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable

from ..core.exceptions import ValidationError


class DataValidator:
    """Utility class for data validation with comprehensive rules"""
    
    # Common regex patterns
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    URL_PATTERN = re.compile(r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$')
    GITHUB_USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$')
    SLUG_PATTERN = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address format"""
        if not email or not isinstance(email, str):
            return False
        return bool(DataValidator.EMAIL_PATTERN.match(email.strip()))
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""
        if not url or not isinstance(url, str):
            return False
        return bool(DataValidator.URL_PATTERN.match(url.strip()))
    
    @staticmethod
    def validate_github_username(username: str) -> bool:
        """Validate GitHub username format"""
        if not username or not isinstance(username, str):
            return False
        username = username.strip()
        return (
            len(username) <= 39 and  # GitHub username max length
            bool(DataValidator.GITHUB_USERNAME_PATTERN.match(username))
        )
    
    @staticmethod
    def validate_slug(slug: str) -> bool:
        """Validate URL slug format"""
        if not slug or not isinstance(slug, str):
            return False
        return bool(DataValidator.SLUG_PATTERN.match(slug.strip().lower()))
    
    @staticmethod
    def validate_required_string(value: Any, field_name: str, min_length: int = 1) -> str:
        """Validate required string field"""
        if not value or not isinstance(value, str):
            raise ValidationError(f"{field_name} is required and must be a string")
        
        value = value.strip()
        if len(value) < min_length:
            raise ValidationError(f"{field_name} must be at least {min_length} characters long")
        
        return value
    
    @staticmethod
    def validate_optional_string(value: Any, field_name: str, max_length: Optional[int] = None) -> Optional[str]:
        """Validate optional string field"""
        if value is None or value == "":
            return None
        
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} must be a string")
        
        value = value.strip()
        if max_length and len(value) > max_length:
            raise ValidationError(f"{field_name} must be no more than {max_length} characters long")
        
        return value if value else None
    
    @staticmethod
    def validate_integer(value: Any, field_name: str, minimum: Optional[int] = None, maximum: Optional[int] = None) -> int:
        """Validate integer field with optional range"""
        if not isinstance(value, int):
            try:
                value = int(value)
            except (ValueError, TypeError):
                raise ValidationError(f"{field_name} must be an integer")
        
        if minimum is not None and value < minimum:
            raise ValidationError(f"{field_name} must be at least {minimum}")
        
        if maximum is not None and value > maximum:
            raise ValidationError(f"{field_name} must be at most {maximum}")
        
        return value
    
    @staticmethod
    def validate_date_string(date_str: str, field_name: str, format_pattern: str = "%Y-%m-%d") -> str:
        """Validate date string format"""
        if not date_str or not isinstance(date_str, str):
            raise ValidationError(f"{field_name} is required and must be a date string")
        
        try:
            from datetime import datetime
            datetime.strptime(date_str, format_pattern)
            return date_str
        except ValueError:
            raise ValidationError(f"{field_name} must be in format {format_pattern}")
    
    @staticmethod
    def validate_file_path(path: Union[str, Path], field_name: str, must_exist: bool = True, is_directory: bool = False) -> Path:
        """Validate file or directory path"""
        if not path:
            raise ValidationError(f"{field_name} is required")
        
        if isinstance(path, str):
            path = Path(path)
        
        if must_exist and not path.exists():
            raise ValidationError(f"{field_name} path does not exist: {path}")
        
        if must_exist and is_directory and not path.is_dir():
            raise ValidationError(f"{field_name} must be a directory: {path}")
        
        if must_exist and not is_directory and not path.is_file():
            raise ValidationError(f"{field_name} must be a file: {path}")
        
        return path
    
    @staticmethod
    def validate_choice(value: Any, field_name: str, choices: List[Any]) -> Any:
        """Validate value is in allowed choices"""
        if value not in choices:
            choices_str = ", ".join([str(c) for c in choices])
            raise ValidationError(f"{field_name} must be one of: {choices_str}")
        return value
    
    @staticmethod
    def validate_list(value: Any, field_name: str, item_validator: Optional[Callable] = None, min_items: int = 0, max_items: Optional[int] = None) -> List[Any]:
        """Validate list field with optional item validation"""
        if not isinstance(value, list):
            raise ValidationError(f"{field_name} must be a list")
        
        if len(value) < min_items:
            raise ValidationError(f"{field_name} must have at least {min_items} items")
        
        if max_items and len(value) > max_items:
            raise ValidationError(f"{field_name} must have at most {max_items} items")
        
        if item_validator:
            validated_items = []
            for i, item in enumerate(value):
                try:
                    validated_items.append(item_validator(item))
                except ValidationError as e:
                    raise ValidationError(f"{field_name}[{i}]: {e.message}")
            return validated_items
        
        return value
    
    @staticmethod
    def validate_dict(value: Any, field_name: str, required_keys: Optional[List[str]] = None, optional_keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """Validate dictionary structure"""
        if not isinstance(value, dict):
            raise ValidationError(f"{field_name} must be a dictionary")
        
        if required_keys:
            for key in required_keys:
                if key not in value:
                    raise ValidationError(f"{field_name} missing required key: {key}")
        
        allowed_keys = set()
        if required_keys:
            allowed_keys.update(required_keys)
        if optional_keys:
            allowed_keys.update(optional_keys)
        
        if allowed_keys:
            for key in value.keys():
                if key not in allowed_keys:
                    raise ValidationError(f"{field_name} contains unknown key: {key}")
        
        return value


class ContentValidator(DataValidator):
    """Specialized validator for content-specific validation"""
    
    @staticmethod
    def validate_frontmatter(frontmatter_data: Dict[str, Any], content_type: str) -> Dict[str, Any]:
        """Validate frontmatter based on content type"""
        if content_type == "blog":
            return ContentValidator._validate_blog_frontmatter(frontmatter_data)
        elif content_type == "project":
            return ContentValidator._validate_project_frontmatter(frontmatter_data)
        elif content_type == "idea":
            return ContentValidator._validate_idea_frontmatter(frontmatter_data)
        elif content_type == "update":
            return ContentValidator._validate_update_frontmatter(frontmatter_data)
        else:
            raise ValidationError(f"Unknown content type: {content_type}")
    
    @staticmethod
    def _validate_blog_frontmatter(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate blog post frontmatter"""
        validated = {}
        
        # Required fields
        validated['title'] = DataValidator.validate_required_string(data.get('title'), 'title')
        validated['date'] = DataValidator.validate_date_string(data.get('date'), 'date')
        validated['slug'] = DataValidator.validate_required_string(data.get('slug'), 'slug')
        
        if not DataValidator.validate_slug(validated['slug']):
            raise ValidationError("slug must be URL-friendly (lowercase, hyphen-separated)")
        
        # Optional fields
        validated['description'] = DataValidator.validate_optional_string(data.get('description'), 'description')
        validated['excerpt'] = DataValidator.validate_optional_string(data.get('excerpt'), 'excerpt')
        validated['featured'] = bool(data.get('featured', False))
        validated['published'] = bool(data.get('published', True))
        
        # Tags and categories
        if 'tags' in data:
            validated['tags'] = DataValidator.validate_list(data['tags'], 'tags', 
                                                          lambda x: DataValidator.validate_required_string(x, 'tag'))
        
        if 'categories' in data:
            validated['categories'] = DataValidator.validate_list(data['categories'], 'categories',
                                                                lambda x: DataValidator.validate_required_string(x, 'category'))
        
        return validated
    
    @staticmethod
    def _validate_project_frontmatter(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate project frontmatter"""
        validated = {}
        
        # Required fields
        validated['title'] = DataValidator.validate_required_string(data.get('title'), 'title')
        validated['description'] = DataValidator.validate_required_string(data.get('description'), 'description')
        validated['status'] = DataValidator.validate_choice(
            data.get('status'), 'status', 
            ['active', 'completed', 'on-hold', 'cancelled']
        )
        
        # Optional fields
        validated['start_date'] = data.get('start_date')
        if validated['start_date']:
            validated['start_date'] = DataValidator.validate_date_string(validated['start_date'], 'start_date')
        
        validated['end_date'] = data.get('end_date')
        if validated['end_date']:
            validated['end_date'] = DataValidator.validate_date_string(validated['end_date'], 'end_date')
        
        # URLs
        if 'github_url' in data and data['github_url']:
            if not DataValidator.validate_url(data['github_url']):
                raise ValidationError("github_url must be a valid URL")
            validated['github_url'] = data['github_url']
        
        if 'demo_url' in data and data['demo_url']:
            if not DataValidator.validate_url(data['demo_url']):
                raise ValidationError("demo_url must be a valid URL")
            validated['demo_url'] = data['demo_url']
        
        # Technologies
        if 'technologies' in data:
            validated['technologies'] = DataValidator.validate_list(
                data['technologies'], 'technologies',
                lambda x: DataValidator.validate_required_string(x, 'technology')
            )
        
        return validated
    
    @staticmethod
    def _validate_idea_frontmatter(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate research idea frontmatter"""
        validated = {}
        
        # Required fields
        validated['title'] = DataValidator.validate_required_string(data.get('title'), 'title')
        validated['status'] = DataValidator.validate_choice(
            data.get('status'), 'status',
            ['draft', 'in-review', 'approved', 'implemented', 'rejected']
        )
        
        # Optional fields
        validated['description'] = DataValidator.validate_optional_string(data.get('description'), 'description')
        validated['priority'] = DataValidator.validate_choice(
            data.get('priority', 'medium'), 'priority',
            ['low', 'medium', 'high', 'critical']
        )
        
        if 'estimated_hours' in data:
            validated['estimated_hours'] = DataValidator.validate_integer(
                data['estimated_hours'], 'estimated_hours', minimum=1
            )
        
        return validated
    
    @staticmethod
    def _validate_update_frontmatter(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate update entry frontmatter"""
        validated = {}
        
        # Required fields
        validated['title'] = DataValidator.validate_required_string(data.get('title'), 'title')
        validated['date'] = DataValidator.validate_date_string(data.get('date'), 'date')
        validated['type'] = DataValidator.validate_choice(
            data.get('type'), 'type',
            ['project', 'work', 'education', 'research', 'publication', 'personal']
        )
        
        # Optional fields
        validated['description'] = DataValidator.validate_optional_string(data.get('description'), 'description')
        validated['impact'] = DataValidator.validate_choice(
            data.get('impact', 'medium'), 'impact',
            ['low', 'medium', 'high']
        )
        
        return validated