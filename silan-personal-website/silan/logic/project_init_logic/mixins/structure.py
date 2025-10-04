"""Structure creation helpers for project initialization."""



class ProjectStructureMixin:
    """Create directories, sample files, and supportive resources."""

    def _create_project_root(self) -> None:
        """Create project root directory"""
        self.file_ops.ensure_directory(self.project_root)
        self.directory_created(str(self.project_root))

    def _create_content_directories(self) -> None:
        """Create content directory structure"""
        for dir_path in self.content_dirs:
            full_path = self.project_root / dir_path
            self.file_ops.ensure_directory(full_path)
            self.directory_created(str(full_path))

    def _create_template_directories(self) -> None:
        """Create template directory structure"""
        for dir_path in self.template_dirs:
            full_path = self.project_root / dir_path
            self.file_ops.ensure_directory(full_path)
            self.directory_created(str(full_path))

    def _create_config_directories(self) -> None:
        """Create configuration directory structure"""
        for dir_path in self.config_dirs:
            full_path = self.project_root / dir_path
            self.file_ops.ensure_directory(full_path)
            self.directory_created(str(full_path))

    def _create_configuration_files(self) -> None:
        """Create main configuration files"""
        # Create silan.yaml
        config_content = self._generate_silan_config()
        config_path = self.project_root / 'silan.yaml'
        self.file_ops.write_file(config_path, config_content)
        self.file_created(str(config_path))

        # Create README.md
        readme_content = self._generate_readme()
        readme_path = self.project_root / 'README.md'
        self.file_ops.write_file(readme_path, readme_content)
        self.file_created(str(readme_path))

    def _create_sample_content(self) -> None:
        """Create sample content files with proper directory structure"""
        # Sample blog post with directory structure
        self._create_sample_blog_post()

        # Sample project with directory structure
        self._create_sample_project()

        # Sample idea with directory structure
        self._create_sample_idea()

        # Sample moment with directory structure
        self._create_sample_moment()

        # Sample episode series with directory structure
        self._create_sample_episode()

        # Sample resume with directory structure
        self._create_sample_resume()

        # Sample templates
        self._create_sample_templates()

        # Create collection-level cache files
        self._create_collection_cache_files()

    def _create_sample_blog_post(self) -> None:
        """Create sample blog post with proper structure"""
        # Create blog directory
        blog_dir = self.project_root / 'content' / 'blog' / 'welcome'
        self.file_ops.ensure_directory(blog_dir)
        self.directory_created(str(blog_dir))

        # Create blog content file
        blog_content = self._generate_sample_blog_post()
        blog_path = blog_dir / 'en.md'
        self.file_ops.write_file(blog_path, blog_content)
        self.file_created(str(blog_path))

        # Create blog .silan-cache
        blog_config = self._generate_blog_config()
        config_path = blog_dir / '.silan-cache'
        self.file_ops.write_file(config_path, blog_config)
        self.file_created(str(config_path))

    def _create_sample_project(self) -> None:
        """Create sample project with proper structure"""
        # Create project directory
        project_dir = self.project_root / 'content' / 'projects' / 'sample-project'
        self.file_ops.ensure_directory(project_dir)
        self.directory_created(str(project_dir))

        # Create project content file
        project_content = self._generate_sample_project()
        project_path = project_dir / 'README.md'
        self.file_ops.write_file(project_path, project_content)
        self.file_created(str(project_path))

        # Create project .silan-cache
        project_config = self._generate_project_config()
        config_path = project_dir / '.silan-cache'
        self.file_ops.write_file(config_path, project_config)
        self.file_created(str(config_path))

        # Create LICENSE file
        license_content = self._generate_license()
        license_path = project_dir / 'LICENSE'
        self.file_ops.write_file(license_path, license_content)
        self.file_created(str(license_path))

        # Create docs directory and structure file
        docs_dir = project_dir / 'docs'
        self.file_ops.ensure_directory(docs_dir)
        self.directory_created(str(docs_dir))

        structure_content = self._generate_structure_doc()
        structure_path = docs_dir / 'STRUCTURE.md'
        self.file_ops.write_file(structure_path, structure_content)
        self.file_created(str(structure_path))

    def _create_sample_idea(self) -> None:
        """Create sample idea with proper structure"""
        # Create idea directory
        idea_dir = self.project_root / 'content' / 'ideas' / 'ai-content-optimizer'
        self.file_ops.ensure_directory(idea_dir)
        self.directory_created(str(idea_dir))

        # Create idea content file
        idea_content = self._generate_sample_idea()
        idea_path = idea_dir / 'README.md'
        self.file_ops.write_file(idea_path, idea_content)
        self.file_created(str(idea_path))

        # Create idea .silan-cache
        idea_config = self._generate_idea_config()
        config_path = idea_dir / '.silan-cache'
        self.file_ops.write_file(config_path, idea_config)
        self.file_created(str(config_path))

        # Create references file
        references_content = self._generate_idea_references()
        references_path = idea_dir / 'REFERENCES.md'
        self.file_ops.write_file(references_path, references_content)
        self.file_created(str(references_path))

        # Create research notes
        notes_content = self._generate_idea_notes()
        notes_path = idea_dir / 'NOTES.md'
        self.file_ops.write_file(notes_path, notes_content)
        self.file_created(str(notes_path))

        # Create timeline file
        timeline_content = self._generate_idea_timeline()
        timeline_path = idea_dir / 'TIMELINE.md'
        self.file_ops.write_file(timeline_path, timeline_content)
        self.file_created(str(timeline_path))

    def _create_sample_moment(self) -> None:
        """Create sample moment with proper structure"""
        # Create moment directory
        moment_dir = self.project_root / 'content' / 'moment' / 'project-kickoff'
        self.file_ops.ensure_directory(moment_dir)
        self.directory_created(str(moment_dir))

        # Create moment content file
        moment_content = self._generate_sample_moment()
        moment_path = moment_dir / 'en.md'
        self.file_ops.write_file(moment_path, moment_content)
        self.file_created(str(moment_path))

        # Create moment .silan-cache
        moment_config = self._generate_moment_config()
        config_path = moment_dir / '.silan-cache'
        self.file_ops.write_file(config_path, moment_config)
        self.file_created(str(config_path))

    def _create_sample_episode(self) -> None:
        """Create sample episode series with proper structure"""
        # Create episode directory for project tutorial series
        episode_dir = self.project_root / 'content' / 'episode' / 'portfolio-tutorial-series'
        self.file_ops.ensure_directory(episode_dir)
        self.directory_created(str(episode_dir))

        # Create episode 1
        episode1_content = self._generate_sample_episode1()
        episode1_path = episode_dir / 'episode-01-setup.md'
        self.file_ops.write_file(episode1_path, episode1_content)
        self.file_created(str(episode1_path))

        # Create episode 2
        episode2_content = self._generate_sample_episode2()
        episode2_path = episode_dir / 'episode-02-content.md'
        self.file_ops.write_file(episode2_path, episode2_content)
        self.file_created(str(episode2_path))

        # Create episode .silan-cache
        episode_config = self._generate_episode_config()
        config_path = episode_dir / '.silan-cache'
        self.file_ops.write_file(config_path, episode_config)
        self.file_created(str(config_path))

        # Create series overview
        overview_content = self._generate_episode_overview()
        overview_path = episode_dir / 'README.md'
        self.file_ops.write_file(overview_path, overview_content)
        self.file_created(str(overview_path))

    def _create_sample_resume(self) -> None:
        """Create sample resume with proper structure"""
        # Resume should be directly in content/resume/ not in a subdirectory
        resume_dir = self.project_root / 'content' / 'resume'

        # Create resume content file (resume.md)
        resume_content = self._generate_sample_resume()
        resume_path = resume_dir / 'resume.md'
        self.file_ops.write_file(resume_path, resume_content)
        self.file_created(str(resume_path))

        # Create resume .silan-cache for content-specific metadata
        resume_config = self._generate_resume_item_config()
        config_path = resume_dir / '.silan-cache-resume'  # Different name to avoid collision with collection cache
        self.file_ops.write_file(config_path, resume_config)
        self.file_created(str(config_path))

    def _create_sample_templates(self) -> None:
        """Create sample template files"""
        # Blog template
        blog_template = self._generate_blog_template()
        blog_template_path = self.project_root / 'templates' / 'blog' / 'default.md'
        self.file_ops.write_file(blog_template_path, blog_template)
        self.file_created(str(blog_template_path))

        # Project template
        project_template = self._generate_project_template()
        project_template_path = self.project_root / 'templates' / 'projects' / 'default.md'
        self.file_ops.write_file(project_template_path, project_template)
        self.file_created(str(project_template_path))

        # Ideas template
        ideas_template = self._generate_ideas_template()
        ideas_template_path = self.project_root / 'templates' / 'ideas' / 'default.md'
        self.file_ops.write_file(ideas_template_path, ideas_template)
        self.file_created(str(ideas_template_path))

        # Moment template
        moment_template = self._generate_moment_template()
        moment_template_path = self.project_root / 'templates' / 'moment' / 'default.md'
        self.file_ops.write_file(moment_template_path, moment_template)
        self.file_created(str(moment_template_path))

        # Episode template
        episode_template = self._generate_episode_template()
        episode_template_path = self.project_root / 'templates' / 'episode' / 'default.md'
        self.file_ops.write_file(episode_template_path, episode_template)
        self.file_created(str(episode_template_path))

        # Resume template
        resume_template = self._generate_resume_template()
        resume_template_path = self.project_root / 'templates' / 'resume' / 'default.md'
        self.file_ops.write_file(resume_template_path, resume_template)
        self.file_created(str(resume_template_path))

    def _create_collection_cache_files(self) -> None:
        """Create collection-level .silan-cache files for each content type"""
        content_types = ['blog', 'projects', 'ideas', 'moment', 'episode', 'resume']

        for content_type in content_types:
            collection_dir = self.project_root / 'content' / content_type
            cache_file = collection_dir / '.silan-cache'

            cache_content = self._generate_collection_cache(content_type)
            self.file_ops.write_file(cache_file, cache_content)
            self.file_created(str(cache_file))

    def _create_backend_support(self) -> None:
        """Create backend configuration and support files"""
        # Backend directory
        backend_dir = self.project_root / 'backend'
        self.file_ops.ensure_directory(backend_dir)
        self.directory_created(str(backend_dir))

        # Backend config
        backend_config = self._generate_backend_config()
        backend_config_path = backend_dir / '.silan-cache'
        self.file_ops.write_file(backend_config_path, backend_config)
        self.file_created(str(backend_config_path))

        # Environment example
        env_content = self._generate_env_example()
        env_path = self.project_root / '.env.example'
        self.file_ops.write_file(env_path, env_content)
        self.file_created(str(env_path))

    def _create_additional_files(self) -> None:
        """Create additional project files"""
        # .gitignore
        gitignore_content = self._generate_gitignore()
        gitignore_path = self.project_root / '.gitignore'
        self.file_ops.write_file(gitignore_path, gitignore_content)
        self.file_created(str(gitignore_path))

