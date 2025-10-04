"""Blog and episode synchronization helpers."""

from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from ....core.exceptions import DatabaseError
from ....models import (
    BlogPost,
    BlogPostTag,
    BlogTag,
    BlogCategory,
)


class BlogSyncMixin:
    """Blog-related synchronization utilities."""

    def _sync_blog_post(self, session: Session, content_data: Dict[str, Any], item: Dict[str, Any], content_hash: str = None) -> None:
        """Sync blog post to database"""
        try:
            # Handle both structured data and frontmatter-based data
            if 'frontmatter' in content_data:
                frontmatter = content_data.get('frontmatter', {})
                content = content_data.get('content', '')
            else:
                # Direct structured data from parsers
                frontmatter = content_data
                content = content_data.get('content', '')

            # Required fields
            title = frontmatter.get('title', 'Untitled')
            slug = frontmatter.get('slug', self._generate_slug(title))

            # Extract content_type from both locations
            content_type = content_data.get('content_type', frontmatter.get('content_type', frontmatter.get('type', 'article')))

            # Map content_type to valid database enum values
            content_type_mapping = {
                'article': 'article',
                'vlog': 'vlog', 
                'tutorial': 'tutorial',
                'podcast': 'podcast',
                # Handle variations
                'video': 'vlog',
                'howto': 'tutorial',
                'how-to': 'tutorial'
            }
            content_type = content_type_mapping.get(content_type.lower(), 'article')

            # Determine status more intelligently
            status = self._determine_blog_status(frontmatter, content_data)

            # Check if blog post exists
            existing_post = session.query(BlogPost).filter_by(slug=slug).first()

            if existing_post:
                # Update existing post only if content has changed
                from ....models.blog import BlogStatus, BlogContentType
                existing_post.title = title
                existing_post.content = content
                existing_post.excerpt = frontmatter.get('excerpt', frontmatter.get('summary', frontmatter.get('description', '')))
                existing_post.is_featured = frontmatter.get('featured', False)
                existing_post.content_type = BlogContentType(content_type.lower())
                existing_post.status = BlogStatus(status.lower())
                existing_post.updated_at = datetime.utcnow()

                # Handle view and like counts
                existing_post.view_count = frontmatter.get('views', existing_post.view_count)
                existing_post.like_count = frontmatter.get('likes', existing_post.like_count)

                if frontmatter.get('date'):
                    existing_post.published_at = self._parse_datetime(frontmatter['date'])

                # Content updated, the updated_at timestamp will be set automatically

                blog_post = existing_post
                self.sync_stats['updated_count'] += 1
            else:
                # Create new post
                from ....models.blog import BlogStatus, BlogContentType
                assert self.current_user_id is not None
                blog_post_data = {
                    'user_id': self.current_user_id,
                    'title': title,
                    'slug': slug,
                    'content': content,
                    'excerpt': frontmatter.get('excerpt', frontmatter.get('summary', frontmatter.get('description', ''))),
                    'is_featured': frontmatter.get('featured', False),
                    'content_type': BlogContentType(content_type.lower()),
                    'status': BlogStatus(status.lower()),
                    'view_count': frontmatter.get('views', 0),
                    'like_count': frontmatter.get('likes', 0),
                    'published_at': self._parse_datetime(frontmatter.get('date', datetime.utcnow()))
                }

                # New blog post will have created_at timestamp set automatically

                blog_post = BlogPost(**blog_post_data)
                session.add(blog_post)
                session.flush()  # Get the ID
                self.sync_stats['created_count'] += 1

            # Handle tags - check both frontmatter and top-level content_data
            tags_to_sync = None
            if 'tags' in frontmatter and frontmatter['tags']:
                tags_to_sync = frontmatter['tags']
            elif 'tags' in content_data and content_data['tags']:
                tags_to_sync = content_data['tags']

            if tags_to_sync:
                self._sync_blog_tags(session, blog_post, tags_to_sync)

            # Handle categories - check both frontmatter and top-level content_data
            categories_to_sync = None
            if 'categories' in frontmatter and frontmatter['categories']:
                categories_to_sync = frontmatter['categories']
            elif 'categories' in content_data and content_data['categories']:
                categories_to_sync = content_data['categories']

            if categories_to_sync:
                self._sync_blog_categories(session, blog_post, categories_to_sync)

            # Handle series - check both frontmatter and top-level content_data
            series_to_sync = None
            if 'series' in frontmatter and frontmatter['series']:
                series_to_sync = frontmatter['series']
            elif 'series' in content_data and content_data['series']:
                series_to_sync = content_data['series']

            if series_to_sync:
                self._sync_blog_series(session, blog_post, series_to_sync)

            # Handle translations - check if this content has language variants
            self._sync_blog_translations(session, blog_post, content_data, item)

        except Exception as e:
            raise DatabaseError(f"Failed to sync blog post: {e}")

    def _determine_blog_status(self, frontmatter: Dict[str, Any], content_data: Dict[str, Any]) -> str:
        """Determine blog post status intelligently"""
        # Check explicit status field
        status = frontmatter.get('status', content_data.get('status', '')).lower()

        # Check published field
        published = frontmatter.get('published', content_data.get('published', True))

        # Check if it's in drafts folder
        path = content_data.get('path', '')
        if 'drafts' in path.lower():
            return 'draft'

        # Status mapping
        if status in ['draft', 'unpublished', 'private']:
            return 'draft'
        elif status in ['published', 'public']:
            return 'published'
        elif status in ['archived']:
            return 'archived'
        elif not published:
            return 'draft'
        else:
            return 'published'

    def _sync_blog_series(self, session: Session, blog_post: BlogPost, series_data: Any) -> None:
        """Sync blog series information"""
        try:
            from ....models.blog import BlogSeries, BlogPost

            # Handle different series data formats
            if isinstance(series_data, dict):
                series_name = series_data.get('name', '')
                series_description = series_data.get('description', '')
                part_number = series_data.get('part', series_data.get('part_number', 1))
            elif isinstance(series_data, str):
                series_name = series_data
                series_description = ''
                part_number = 1
            else:
                return

            if not series_name:
                return

            # Generate series slug
            series_slug = self._generate_slug(series_name)

            # Get or create series
            series = session.query(BlogSeries).filter_by(slug=series_slug).first()
            if not series:
                series = BlogSeries(
                    title=series_name,
                    slug=series_slug,
                    description=series_description
                )
                session.add(series)
                session.flush()

            # Update blog post with series info
            blog_post.series_id = series.id
            blog_post.series_order = part_number

            # Update episode count for the series
            episode_count = session.query(BlogPost).filter_by(series_id=series.id).count()
            series.episode_count = episode_count

        except Exception as e:
            self.warning(f"Failed to sync blog series: {e}")

    def _sync_blog_tags(self, session: Session, blog_post: BlogPost, tags: List[str]) -> None:
        """Sync blog tags for a post"""
        # Clear existing tags
        session.query(BlogPostTag).filter_by(blog_post_id=blog_post.id).delete()

        for tag_name in tags:
            if not tag_name or not tag_name.strip():
                continue

            tag_name = tag_name.strip()
            generated_slug = self._generate_slug(tag_name)

            # Get or create tag - check both name and slug to avoid conflicts
            tag = session.query(BlogTag).filter_by(name=tag_name).first()
            if not tag:
                # Check if a tag with this slug already exists
                tag_by_slug = session.query(BlogTag).filter_by(slug=generated_slug).first()
                if tag_by_slug:
                    # Use existing tag with same slug
                    tag = tag_by_slug
                else:
                    # Create new tag
                    tag = BlogTag(
                        name=tag_name,
                        slug=generated_slug
                    )
                    session.add(tag)
                    session.flush()

            # Create association if not already exists
            existing_association = session.query(BlogPostTag).filter_by(
                blog_post_id=blog_post.id,
                blog_tag_id=tag.id
            ).first()

            if not existing_association:
                blog_post_tag = BlogPostTag(
                    blog_post_id=blog_post.id,
                    blog_tag_id=tag.id
                )
                session.add(blog_post_tag)

    def _sync_blog_categories(self, session: Session, blog_post: BlogPost, categories: List[str]) -> None:
        """Sync blog categories for a post"""
        if categories and categories[0]:
            category_name = categories[0].strip()  # Take first category
            generated_slug = self._generate_slug(category_name)

            # Get or create category - check both name and slug to avoid conflicts
            category = session.query(BlogCategory).filter_by(name=category_name).first()
            if not category:
                # Check if a category with this slug already exists
                category_by_slug = session.query(BlogCategory).filter_by(slug=generated_slug).first()
                if category_by_slug:
                    # Use existing category with same slug
                    category = category_by_slug
                else:
                    # Create new category
                    category = BlogCategory(
                        name=category_name,
                        slug=generated_slug
                    )
                    session.add(category)
                    session.flush()

            blog_post.category_id = category.id

    def _sync_blog_translations(self, session: Session, blog_post: BlogPost, content_data: Dict[str, Any], item: Dict[str, Any]) -> None:
        """Sync blog post translations for multi-language support"""
        try:
            # Check if this content has language information
            frontmatter = content_data.get('frontmatter', content_data)
            language = frontmatter.get('language', 'en')

            # If this is non-English content, handle it as a translation
            if language != 'en':
                # Import models
                from ....models.blog import BlogPostTranslation

                # Extract translation data
                title = frontmatter.get('title', '')
                excerpt = frontmatter.get('excerpt', frontmatter.get('summary', frontmatter.get('description', '')))
                content = content_data.get('content', '')

                if not title or not content:
                    return

                # Check if translation already exists
                existing_translation = session.query(BlogPostTranslation).filter_by(
                    blog_post_id=blog_post.id,
                    language_code=language
                ).first()

                if existing_translation:
                    # Update existing translation
                    existing_translation.title = title
                    existing_translation.excerpt = excerpt
                    existing_translation.content = content
                    self.debug(f"Updated {language} translation for blog post: {blog_post.slug}")
                else:
                    # Create new translation
                    translation = BlogPostTranslation(
                        blog_post_id=blog_post.id,
                        language_code=language,
                        title=title,
                        excerpt=excerpt,
                        content=content
                    )
                    session.add(translation)
                    self.debug(f"Created {language} translation for blog post: {blog_post.slug}")

        except Exception as e:
            self.warning(f"Failed to sync translations for blog post {blog_post.slug}: {e}")

    def _sync_blog_translation_only(self, session: Session, content_data: Dict[str, Any], item: Dict[str, Any]) -> None:
        """Sync only translation for a blog post (find corresponding English post)"""
        try:
            # Import models
            from ....models.blog import BlogPostTranslation

            frontmatter = content_data.get('frontmatter', content_data)
            language = frontmatter.get('language', 'en')

            if language == 'en':
                return  # This should not happen, but safety check

            item_name = item.get('name', '')
            if language in item_name:                
                # Try to find English post by matching folder pattern
                content_path = item.get('path', '')
                if content_path:
                    # Extract folder path and find English file
                    from pathlib import Path
                    path_obj = Path(content_path)
                    folder_path = path_obj.parent
                    english_file = folder_path / 'en.md'

                    if english_file.exists():
                        # Read English file to get its title for matching
                        import frontmatter as fm
                        with open(english_file, 'r', encoding='utf-8') as f:
                            english_post = fm.load(f)
                            english_title = english_post.metadata.get('title', '')
                            english_slug = english_post.metadata.get('slug', self._generate_slug(str(english_title)))

                            # Find the English blog post
                            english_blog_post = session.query(BlogPost).filter_by(slug=english_slug).first()
                            if not english_blog_post:
                                # Try to find by title
                                english_blog_post = session.query(BlogPost).filter_by(title=english_title).first()

                            if english_blog_post:
                                # Create or update translation
                                title = frontmatter.get('title', '')
                                excerpt = frontmatter.get('excerpt', frontmatter.get('summary', frontmatter.get('description', '')))
                                content = content_data.get('content', '')

                                existing_translation = session.query(BlogPostTranslation).filter_by(
                                    blog_post_id=english_blog_post.id,
                                    language_code=language
                                ).first()

                                if existing_translation:
                                    # Update existing translation
                                    existing_translation.title = title
                                    existing_translation.excerpt = excerpt
                                    existing_translation.content = content
                                    self.debug(f"Updated {language} translation for blog post: {english_blog_post.slug}")
                                else:
                                    # Create new translation
                                    translation = BlogPostTranslation(
                                        blog_post_id=english_blog_post.id,
                                        language_code=language,
                                        title=title,
                                        excerpt=excerpt,
                                        content=content
                                    )
                                    session.add(translation)
                                    self.debug(f"Created {language} translation for blog post: {english_blog_post.slug}")

                                session.commit()
                                return

                self.warning(f"Could not find corresponding English blog post for {language} translation: {item_name}")

        except Exception as e:
            self.warning(f"Failed to sync blog translation {item.get('name', '')}: {e}")

    def _sync_episode(self, session: Session, content_data: Dict[str, Any], item: Dict[str, Any], content_hash: str = None) -> None:
        """Sync episode content to database as specialized blog posts with series support"""
        try:
            # Extract episode data - episodes use parsed main_entity data
            main_entity = content_data.get('main_entity', {})
            frontmatter = content_data.get('frontmatter', {})
            content = main_entity.get('content', content_data.get('content', ''))

            # Episode-specific fields from parsed main_entity
            title = main_entity.get('title', 'Untitled Episode')
            slug = main_entity.get('slug', self._generate_slug(title))
            series_name = main_entity.get('series_name', '')
            episode_name = main_entity.get('episode_name', '')
            episode_number = main_entity.get('episode_number', 0)

            # Determine status
            status = self._determine_blog_status(frontmatter, content_data)

            # Check if episode exists
            existing_post = session.query(BlogPost).filter_by(slug=slug).first()

            if existing_post:
                # Update existing episode
                from ....models.blog import BlogStatus, BlogContentType
                existing_post.title = title
                existing_post.content = content
                existing_post.excerpt = main_entity.get('description', frontmatter.get('description', frontmatter.get('summary', '')))
                existing_post.is_featured = main_entity.get('is_featured', frontmatter.get('featured', False))
                existing_post.content_type = BlogContentType.EPISODE
                existing_post.status = BlogStatus(status.lower())
                existing_post.updated_at = datetime.utcnow()

                # Handle view and like counts
                existing_post.view_count = main_entity.get('view_count', frontmatter.get('views', existing_post.view_count))
                existing_post.like_count = main_entity.get('like_count', frontmatter.get('likes', existing_post.like_count))

                published_date = main_entity.get('published_date') or frontmatter.get('published_date')
                if published_date:
                    existing_post.published_at = self._parse_datetime(published_date)

                blog_post = existing_post
                self.sync_stats['updated_count'] += 1
            else:
                # Create new episode
                from ....models.blog import BlogStatus, BlogContentType
                assert self.current_user_id is not None
                published_date = main_entity.get('published_date') or frontmatter.get('published_date')
                blog_post = BlogPost(
                    user_id=self.current_user_id,
                    title=title,
                    slug=slug,
                    content=content,
                    excerpt=main_entity.get('description', frontmatter.get('description', frontmatter.get('summary', ''))),
                    is_featured=main_entity.get('is_featured', frontmatter.get('featured', False)),
                    content_type=BlogContentType.EPISODE,
                    status=BlogStatus(status.lower()),
                    view_count=main_entity.get('view_count', frontmatter.get('views', 0)),
                    like_count=main_entity.get('like_count', frontmatter.get('likes', 0)),
                    published_at=self._parse_datetime(published_date or datetime.utcnow())
                )
                session.add(blog_post)
                session.flush()  # Get the ID
                self.sync_stats['created_count'] += 1

            # Handle series information
            if series_name:
                self._sync_episode_series(session, blog_post, series_name, episode_number, frontmatter)

            # Handle tags and categories
            categories = content_data.get('categories', [])
            if not categories:
                categories = frontmatter.get('categories', [])
            if isinstance(categories, str):
                categories = [categories]

            # Add series as category
            if series_name and series_name not in categories:
                categories.append(series_name)

            if categories:
                self._sync_blog_categories(session, blog_post, categories)

            # Handle tags
            tags = content_data.get('tags', [])
            if not tags:
                tags = frontmatter.get('tags', [])
            if isinstance(tags, str):
                tags = [tags]

            # Add episode-specific tags
            if episode_name:
                tags.append(f"episode-{episode_name}")
            if series_name:
                tags.append(f"series-{series_name}")

            if tags:
                self._sync_blog_tags(session, blog_post, tags)

            self.debug(f"✅ Synced episode: {title}")

        except Exception as e:
            self.warning(f"Failed to sync episode {item.get('name', '')}: {e}")

    def _sync_episode_series(self, session: Session, blog_post: BlogPost, series_name: str, episode_number: int, frontmatter: Dict[str, Any]) -> None:
        """Handle series information for episodes"""
        try:
            from ....models.blog import BlogSeries, BlogSeriesTranslation

            # Find or create series
            existing_series = session.query(BlogSeries).filter_by(slug=self._generate_slug(series_name)).first()

            if not existing_series:
                # Create new series
                series = BlogSeries(
                    title=series_name.replace('-', ' ').title(),
                    slug=self._generate_slug(series_name),
                    description=frontmatter.get('series_description', f"Episodes from the {series_name} series"),
                    status="active"
                )
                session.add(series)
                session.flush()

                # Create English translation for series
                series_translation = BlogSeriesTranslation(
                    blog_series_id=series.id,
                    language_code='en',
                    title=series.title,
                    description=series.description
                )
                session.add(series_translation)
            else:
                series = existing_series

            # Associate blog post with series
            blog_post.series_id = series.id
            blog_post.episode_number = episode_number

            # Update series episode count
            episode_count = session.query(BlogPost).filter_by(series_id=series.id).count()
            series.episode_count = episode_count

        except Exception as e:
            self.warning(f"Failed to sync episode series {series_name}: {e}")
