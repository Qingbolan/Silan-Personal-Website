# Database Design Document

## Silan-Personal-Website Website Database Schema

### Version: 1.0
### Date: 2025-01-07
### Author: Database Design Team

---

## 1. Overview

This document outlines the comprehensive database design for the Silan-Personal-Website website, following the Boyce-Codd Normal Form (BCNF) principles. The design supports multi-language content, user interactions, and all website functionalities including resume management, blog system, project portfolio, ideas management, and planning features.

## 2. Design Principles

### 2.1 Normalization (BCNF)
- All tables are normalized to Boyce-Codd Normal Form (BCNF)
- Every determinant is a candidate key
- Eliminates redundancy and maintains data integrity
- Ensures optimal query performance and storage efficiency

### 2.2 Multi-language Support
- Separate translation tables for content requiring localization
- Primary content in default language with translations linked via foreign keys
- Supports scalable addition of new languages

### 2.3 Audit Trail
- Created and updated timestamps on all major entities
- Soft deletion support where appropriate
- Version control for critical content

---

## 3. Core Entity Tables

### 3.1 Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    avatar_url VARCHAR(500),
    bio TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITH TIME ZONE
);
```

### 3.2 Languages Table
```sql
CREATE TABLE languages (
    code VARCHAR(5) PRIMARY KEY, -- e.g., 'en', 'zh'
    name VARCHAR(50) NOT NULL,
    native_name VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4. Resume/Profile Module

### 4.1 Personal Information
```sql
CREATE TABLE personal_info (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    full_name VARCHAR(200) NOT NULL,
    title VARCHAR(200) NOT NULL,
    current_status TEXT,
    phone VARCHAR(20),
    email VARCHAR(255),
    location VARCHAR(200),
    website VARCHAR(500),
    avatar_url VARCHAR(500),
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, is_primary) WHERE is_primary = TRUE
);

CREATE TABLE personal_info_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    personal_info_id UUID NOT NULL REFERENCES personal_info(id) ON DELETE CASCADE,
    language_code VARCHAR(5) NOT NULL REFERENCES languages(code),
    full_name VARCHAR(200),
    title VARCHAR(200),
    current_status TEXT,
    location VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(personal_info_id, language_code)
);
```

### 4.2 Social Links
```sql
CREATE TABLE social_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    personal_info_id UUID NOT NULL REFERENCES personal_info(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL, -- github, linkedin, twitter, etc.
    url VARCHAR(500) NOT NULL,
    display_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 4.3 Education
```sql
CREATE TABLE education (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    institution VARCHAR(200) NOT NULL,
    degree VARCHAR(200) NOT NULL,
    field_of_study VARCHAR(200),
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,
    gpa VARCHAR(10),
    location VARCHAR(200),
    institution_website VARCHAR(500),
    institution_logo_url VARCHAR(500),
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE education_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    education_id UUID NOT NULL REFERENCES education(id) ON DELETE CASCADE,
    language_code VARCHAR(5) NOT NULL REFERENCES languages(code),
    institution VARCHAR(200),
    degree VARCHAR(200),
    field_of_study VARCHAR(200),
    location VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(education_id, language_code)
);

CREATE TABLE education_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    education_id UUID NOT NULL REFERENCES education(id) ON DELETE CASCADE,
    detail_text TEXT NOT NULL,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE education_detail_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    education_detail_id UUID NOT NULL REFERENCES education_details(id) ON DELETE CASCADE,
    language_code VARCHAR(5) NOT NULL REFERENCES languages(code),
    detail_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(education_detail_id, language_code)
);
```

### 4.4 Work Experience
```sql
CREATE TABLE work_experience (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    company VARCHAR(200) NOT NULL,
    position VARCHAR(200) NOT NULL,
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,
    location VARCHAR(200),
    company_website VARCHAR(500),
    company_logo_url VARCHAR(500),
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE work_experience_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    work_experience_id UUID NOT NULL REFERENCES work_experience(id) ON DELETE CASCADE,
    language_code VARCHAR(5) NOT NULL REFERENCES languages(code),
    company VARCHAR(200),
    position VARCHAR(200),
    location VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(work_experience_id, language_code)
);

CREATE TABLE work_experience_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    work_experience_id UUID NOT NULL REFERENCES work_experience(id) ON DELETE CASCADE,
    detail_text TEXT NOT NULL,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE work_experience_detail_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    work_experience_detail_id UUID NOT NULL REFERENCES work_experience_details(id) ON DELETE CASCADE,
    language_code VARCHAR(5) NOT NULL REFERENCES languages(code),
    detail_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(work_experience_detail_id, language_code)
);
```

### 4.5 Skills
```sql
CREATE TABLE skill_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE skill_category_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_category_id UUID NOT NULL REFERENCES skill_categories(id) ON DELETE CASCADE,
    language_code VARCHAR(5) NOT NULL REFERENCES languages(code),
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(skill_category_id, language_code)
);

CREATE TABLE skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    skill_category_id UUID REFERENCES skill_categories(id),
    name VARCHAR(100) NOT NULL,
    proficiency_level INTEGER CHECK (proficiency_level >= 1 AND proficiency_level <= 5),
    years_of_experience INTEGER,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE skill_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    language_code VARCHAR(5) NOT NULL REFERENCES languages(code),
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(skill_id, language_code)
);
```

---

## 5. Research & Publications Module

### 5.1 Research Projects
```sql
CREATE TABLE research_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(300) NOT NULL,
    start_date DATE,
    end_date DATE,
    is_ongoing BOOLEAN DEFAULT FALSE,
    location VARCHAR(200),
    research_type VARCHAR(50), -- individual, collaboration, funded, etc.
    funding_source VARCHAR(200),
    funding_amount DECIMAL(12,2),
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE research_project_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    research_project_id UUID NOT NULL REFERENCES research_projects(id) ON DELETE CASCADE,
    language_code VARCHAR(5) NOT NULL REFERENCES languages(code),
    title VARCHAR(300) NOT NULL,
    location VARCHAR(200),
    research_type VARCHAR(50),
    funding_source VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(research_project_id, language_code)
);

CREATE TABLE research_project_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    research_project_id UUID NOT NULL REFERENCES research_projects(id) ON DELETE CASCADE,
    detail_text TEXT NOT NULL,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE research_project_detail_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    research_project_detail_id UUID NOT NULL REFERENCES research_project_details(id) ON DELETE CASCADE,
    language_code VARCHAR(5) NOT NULL REFERENCES languages(code),
    detail_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(research_project_detail_id, language_code)
);
```

### 5.2 Publications
```sql
CREATE TABLE publications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(500) NOT NULL,
    publication_type VARCHAR(50) NOT NULL, -- journal, conference, book, chapter, etc.
    journal_name VARCHAR(200),
    conference_name VARCHAR(200),
    volume VARCHAR(20),
    issue VARCHAR(20),
    pages VARCHAR(50),
    publication_date DATE,
    doi VARCHAR(100),
    isbn VARCHAR(20),
    url VARCHAR(500),
    pdf_url VARCHAR(500),
    citation_count INTEGER DEFAULT 0,
    is_peer_reviewed BOOLEAN DEFAULT FALSE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE publication_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    publication_id UUID NOT NULL REFERENCES publications(id) ON DELETE CASCADE,
    language_code VARCHAR(5) NOT NULL REFERENCES languages(code),
    title VARCHAR(500) NOT NULL,
    journal_name VARCHAR(200),
    conference_name VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(publication_id, language_code)
);

CREATE TABLE publication_authors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    publication_id UUID NOT NULL REFERENCES publications(id) ON DELETE CASCADE,
    author_name VARCHAR(200) NOT NULL,
    author_order INTEGER NOT NULL,
    is_corresponding BOOLEAN DEFAULT FALSE,
    affiliation VARCHAR(300),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(publication_id, author_order)
);
```

### 5.3 Awards & Achievements
```sql
CREATE TABLE awards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(300) NOT NULL,
    awarding_organization VARCHAR(200) NOT NULL,
    award_date DATE,
    award_type VARCHAR(50), -- scholarship, recognition, competition, etc.
    amount DECIMAL(12,2),
    description TEXT,
    certificate_url VARCHAR(500),
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE award_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    award_id UUID NOT NULL REFERENCES awards(id) ON DELETE CASCADE,
    language_code VARCHAR(5) NOT NULL REFERENCES languages(code),
    title VARCHAR(300) NOT NULL,
    awarding_organization VARCHAR(200) NOT NULL,
    award_type VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(award_id, language_code)
);
```

---

## 6. Project Portfolio Module

### 6.1 Projects
```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(300) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    description TEXT,
    project_type VARCHAR(50) NOT NULL, -- web, mobile, ai, research, etc.
    status VARCHAR(20) DEFAULT 'active', -- active, completed, paused, cancelled
    start_date DATE,
    end_date DATE,
    github_url VARCHAR(500),
    demo_url VARCHAR(500),
    documentation_url VARCHAR(500),
    thumbnail_url VARCHAR(500),
    is_featured BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT TRUE,
    view_count INTEGER DEFAULT 0,
    star_count INTEGER DEFAULT 0,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE project_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    language_code VARCHAR(5) NOT NULL REFERENCES languages(code),
    title VARCHAR(300) NOT NULL,
    description TEXT,
    project_type VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, language_code)
);
```

### 6.2 Project Details & Metadata
```sql
CREATE TABLE project_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    detailed_description TEXT,
    goals TEXT,
    challenges TEXT,
    solutions TEXT,
    lessons_learned TEXT,
    future_enhancements TEXT,
    license VARCHAR(50),
    version VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id)
);

CREATE TABLE project_detail_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_detail_id UUID NOT NULL REFERENCES project_details(id) ON DELETE CASCADE,
    language_code VARCHAR(5) NOT NULL REFERENCES languages(code),
    detailed_description TEXT,
    goals TEXT,
    challenges TEXT,
    solutions TEXT,
    lessons_learned TEXT,
    future_enhancements TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_detail_id, language_code)
);

CREATE TABLE project_technologies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    technology_name VARCHAR(100) NOT NULL,
    technology_type VARCHAR(50), -- frontend, backend, database, tool, etc.
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, technology_name)
);

CREATE TABLE project_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    image_url VARCHAR(500) NOT NULL,
    alt_text VARCHAR(200),
    caption TEXT,
    image_type VARCHAR(50), -- screenshot, diagram, logo, etc.
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE project_image_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_image_id UUID NOT NULL REFERENCES project_images(id) ON DELETE CASCADE,
    language_code VARCHAR(5) NOT NULL REFERENCES languages(code),
    alt_text VARCHAR(200),
    caption TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_image_id, language_code)
);
```

### 6.3 Project Relationships
```sql
CREATE TABLE project_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    target_project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL, -- depends_on, related_to, fork_of, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_project_id, target_project_id, relationship_type),
    CHECK(source_project_id != target_project_id)
);
```

---

## 7. Blog System Module

### 7.1 Blog Categories & Tags
```sql
CREATE TABLE blog_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    color VARCHAR(7), -- hex color code
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE blog_category_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    blog_category_id UUID NOT NULL REFERENCES blog_categories(id) ON DELETE CASCADE,
    language_code VARCHAR(5) NOT NULL REFERENCES languages(code),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(blog_category_id, language_code)
);

CREATE TABLE blog_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE blog_tag_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    blog_tag_id UUID NOT NULL REFERENCES blog_tags(id) ON DELETE CASCADE,
    language_code VARCHAR(5) NOT NULL REFERENCES languages(code),
    name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(blog_tag_id, language_code)
);
```

### 7.2 Blog Posts
```sql
CREATE TABLE blog_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(500) NOT NULL,
    slug VARCHAR(300) UNIQUE NOT NULL,
    excerpt TEXT,
    content TEXT NOT NULL,
    content_type VARCHAR(20) DEFAULT 'article', -- article, vlog, podcast, etc.
    status VARCHAR(20) DEFAULT 'draft', -- draft, published, archived
    is_featured BOOLEAN DEFAULT FALSE,
    featured_image_url VARCHAR(500),
    reading_time_minutes INTEGER,
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE blog_post_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    blog_post_id UUID NOT NULL REFERENCES blog_posts(id) ON DELETE CASCADE,
    language_code VARCHAR(5) NOT NULL REFERENCES languages(code),
    title VARCHAR(500) NOT NULL,
    excerpt TEXT,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(blog_post_id, language_code)
);

CREATE TABLE blog_post_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    blog_post_id UUID NOT NULL REFERENCES blog_posts(id) ON DELETE CASCADE,
    blog_category_id UUID NOT NULL REFERENCES blog_categories(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(blog_post_id, blog_category_id)
);

CREATE TABLE blog_post_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    blog_post_id UUID NOT NULL REFERENCES blog_posts(id) ON DELETE CASCADE,
    blog_tag_id UUID NOT NULL REFERENCES blog_tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(blog_post_id, blog_tag_id)
);
```

### 7.3 Blog Series
```sql
CREATE TABLE blog_series (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(300) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    description TEXT,
    thumbnail_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE blog_series_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    blog_series_id UUID NOT NULL REFERENCES blog_series(id) ON DELETE CASCADE,
    language_code VARCHAR(5) NOT NULL REFERENCES languages(code),
    title VARCHAR(300) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(blog_series_id, language_code)
);

CREATE TABLE blog_series_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    blog_series_id UUID NOT NULL REFERENCES blog_series(id) ON DELETE CASCADE,
    blog_post_id UUID NOT NULL REFERENCES blog_posts(id) ON DELETE CASCADE,
    episode_number INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(blog_series_id, blog_post_id),
    UNIQUE(blog_series_id, episode_number)
);
```

### 7.4 Blog Content Structure
```sql
CREATE TABLE blog_content_blocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    blog_post_id UUID NOT NULL REFERENCES blog_posts(id) ON DELETE CASCADE,
    block_type VARCHAR(50) NOT NULL, -- text, image, video, code, quote, etc.
    content TEXT NOT NULL,
    metadata JSONB, -- flexible metadata for different content types
    sort_order INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(blog_post_id, sort_order)
);

CREATE TABLE blog_content_block_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    blog_content_block_id UUID NOT NULL REFERENCES blog_content_blocks(id) ON DELETE CASCADE,
    language_code VARCHAR(5) NOT NULL REFERENCES languages(code),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(blog_content_block_id, language_code)
);
```

---

## 8. Ideas Management Module

### 8.1 Ideas
```sql
CREATE TABLE ideas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(300) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    abstract TEXT,
    motivation TEXT,
    methodology TEXT,
    expected_outcome TEXT,
    status VARCHAR(20) DEFAULT 'draft', -- draft, hypothesis, experimenting, validating, published, concluded
    priority VARCHAR(10) DEFAULT 'medium', -- low, medium, high, urgent
    estimated_duration_months INTEGER,
    required_resources TEXT,
    collaboration_needed BOOLEAN DEFAULT FALSE,
    funding_required BOOLEAN DEFAULT FALSE,
    estimated_budget DECIMAL(12,2),
    is_public BOOLEAN DEFAULT FALSE,
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE idea_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idea_id UUID NOT NULL REFERENCES ideas(id) ON DELETE CASCADE,
    language_code VARCHAR(5) NOT NULL REFERENCES languages(code),
    title VARCHAR(300) NOT NULL,
    abstract TEXT,
    motivation TEXT,
    methodology TEXT,
    expected_outcome TEXT,
    required_resources TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(idea_id, language_code)
);
```

### 8.2 Idea Categories & Tags
```sql
CREATE TABLE idea_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    color VARCHAR(7),
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE idea_category_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idea_category_id UUID NOT NULL REFERENCES idea_categories(id) ON DELETE CASCADE,
    language_code VARCHAR(5) NOT NULL REFERENCES languages(code),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(idea_category_id, language_code)
);

CREATE TABLE idea_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE idea_tag_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idea_tag_id UUID NOT NULL REFERENCES idea_tags(id) ON DELETE CASCADE,
    language_code VARCHAR(5) NOT NULL REFERENCES languages(code),
    name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(idea_tag_id, language_code)
);

CREATE TABLE idea_category_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idea_id UUID NOT NULL REFERENCES ideas(id) ON DELETE CASCADE,
    idea_category_id UUID NOT NULL REFERENCES idea_categories(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(idea_id, idea_category_id)
);

CREATE TABLE idea_tag_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idea_id UUID NOT NULL REFERENCES ideas(id) ON DELETE CASCADE,
    idea_tag_id UUID NOT NULL REFERENCES idea_tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(idea_id, idea_tag_id)
);
```

### 8.3 Idea Progress Tracking
```sql
CREATE TABLE idea_progress_updates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idea_id UUID NOT NULL REFERENCES ideas(id) ON DELETE CASCADE,
    update_title VARCHAR(200) NOT NULL,
    update_content TEXT NOT NULL,
    progress_percentage INTEGER CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    update_type VARCHAR(50), -- milestone, blocker, breakthrough, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE idea_progress_update_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idea_progress_update_id UUID NOT NULL REFERENCES idea_progress_updates(id) ON DELETE CASCADE,
    language_code VARCHAR(5) NOT NULL REFERENCES languages(code),
    update_title VARCHAR(200) NOT NULL,
    update_content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(idea_progress_update_id, language_code)
);
```

---

## 9. Planning & Goal Management Module

### 9.1 Annual Plans
```sql
CREATE TABLE annual_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    year INTEGER NOT NULL,
    title VARCHAR(300) NOT NULL,
    description TEXT,
    goals TEXT,
    success_metrics TEXT,
    status VARCHAR(20) DEFAULT 'active', -- active, completed, abandoned
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, year)
);

CREATE TABLE annual_plan_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    annual_plan_id UUID NOT NULL REFERENCES annual_plans(id) ON DELETE CASCADE,
    language_code VARCHAR(5) NOT NULL REFERENCES languages(code),
    title VARCHAR(300) NOT NULL,
    description TEXT,
    goals TEXT,
    success_metrics TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(annual_plan_id, language_code)
);
```

### 9.2 Plan-Project Associations
```sql
CREATE TABLE plan_project_associations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    annual_plan_id UUID NOT NULL REFERENCES annual_plans(id) ON DELETE CASCADE,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    priority INTEGER DEFAULT 1,
    planned_start_date DATE,
    planned_end_date DATE,
    actual_start_date DATE,
    actual_end_date DATE,
    status VARCHAR(20) DEFAULT 'planned', -- planned, in_progress, completed, delayed, cancelled
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(annual_plan_id, project_id)
);

CREATE TABLE plan_idea_associations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    annual_plan_id UUID NOT NULL REFERENCES annual_plans(id) ON DELETE CASCADE,
    idea_id UUID NOT NULL REFERENCES ideas(id) ON DELETE CASCADE,
    priority INTEGER DEFAULT 1,
    planned_start_date DATE,
    planned_end_date DATE,
    status VARCHAR(20) DEFAULT 'planned',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(annual_plan_id, idea_id)
);
```

---

## 10. Activity & Timeline Module

### 10.1 Recent Updates
```sql
CREATE TABLE recent_updates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(300) NOT NULL,
    description TEXT,
    update_type VARCHAR(50) NOT NULL, -- project, education, experience, publication, award, etc.
    reference_type VARCHAR(50), -- what type of entity this references
    reference_id UUID, -- generic reference to any entity
    status VARCHAR(20) DEFAULT 'active', -- active, completed, archived
    priority VARCHAR(10) DEFAULT 'medium', -- low, medium, high
    is_featured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE recent_update_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recent_update_id UUID NOT NULL REFERENCES recent_updates(id) ON DELETE CASCADE,
    language_code VARCHAR(5) NOT NULL REFERENCES languages(code),
    title VARCHAR(300) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(recent_update_id, language_code)
);
```

### 10.2 Activity Log
```sql
CREATE TABLE activity_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    action VARCHAR(50) NOT NULL, -- create, update, delete, view, like, etc.
    entity_type VARCHAR(50) NOT NULL, -- project, blog_post, idea, etc.
    entity_id UUID NOT NULL, -- generic reference to any entity
    ip_address INET,
    user_agent TEXT,
    metadata JSONB, -- flexible metadata for different activities
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_activity_log_user_id ON activity_log(user_id);
CREATE INDEX idx_activity_log_created_at ON activity_log(created_at);
CREATE INDEX idx_activity_log_entity ON activity_log(entity_type, entity_id);
```

---

## 11. Interaction & Engagement Module

### 11.1 Likes & Reactions
```sql
CREATE TABLE reactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    entity_type VARCHAR(50) NOT NULL, -- project, blog_post, idea, etc.
    entity_id UUID NOT NULL, -- generic reference to any entity
    reaction_type VARCHAR(20) DEFAULT 'like', -- like, love, star, bookmark, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, entity_type, entity_id, reaction_type)
);

CREATE INDEX idx_reactions_entity ON reactions(entity_type, entity_id);
CREATE INDEX idx_reactions_user ON reactions(user_id);
```

### 11.2 Comments System
```sql
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    entity_type VARCHAR(50) NOT NULL, -- project, blog_post, idea, etc.
    entity_id UUID NOT NULL, -- generic reference to any entity
    parent_comment_id UUID REFERENCES comments(id),
    content TEXT NOT NULL,
    is_approved BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    like_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_comments_entity ON comments(entity_type, entity_id);
CREATE INDEX idx_comments_user ON comments(user_id);
CREATE INDEX idx_comments_parent ON comments(parent_comment_id);
```

### 11.3 Views & Analytics
```sql
CREATE TABLE page_views (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id), -- nullable for anonymous views
    entity_type VARCHAR(50) NOT NULL, -- project, blog_post, idea, etc.
    entity_id UUID NOT NULL, -- generic reference to any entity
    ip_address INET,
    user_agent TEXT,
    referrer VARCHAR(500),
    duration_seconds INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_page_views_entity ON page_views(entity_type, entity_id);
CREATE INDEX idx_page_views_created_at ON page_views(created_at);
```

---

## 12. File & Media Management Module

### 12.1 File Storage
```sql
CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    original_filename VARCHAR(500) NOT NULL,
    stored_filename VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_size INTEGER NOT NULL,
    file_hash VARCHAR(128) NOT NULL, -- SHA-256 hash
    alt_text VARCHAR(200),
    caption TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    download_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE file_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    language_code VARCHAR(5) NOT NULL REFERENCES languages(code),
    alt_text VARCHAR(200),
    caption TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(file_id, language_code)
);

CREATE INDEX idx_files_user_id ON files(user_id);
CREATE INDEX idx_files_hash ON files(file_hash);
```

### 12.2 Entity-File Associations
```sql
CREATE TABLE entity_file_associations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(50) NOT NULL, -- project, blog_post, idea, etc.
    entity_id UUID NOT NULL, -- generic reference to any entity
    file_id UUID NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    association_type VARCHAR(50) NOT NULL, -- thumbnail, gallery, attachment, etc.
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(entity_type, entity_id, file_id, association_type)
);

CREATE INDEX idx_entity_file_associations_entity ON entity_file_associations(entity_type, entity_id);
CREATE INDEX idx_entity_file_associations_file ON entity_file_associations(file_id);
```

---

## 13. Configuration & Settings Module

### 13.1 System Settings
```sql
CREATE TABLE system_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type VARCHAR(20) DEFAULT 'string', -- string, integer, boolean, json
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    setting_key VARCHAR(100) NOT NULL,
    setting_value TEXT,
    setting_type VARCHAR(20) DEFAULT 'string',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, setting_key)
);
```

---

## 14. Indexes & Performance Optimization

### 14.1 Essential Indexes
```sql
-- User authentication
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- Content discovery
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_is_featured ON projects(is_featured);
CREATE INDEX idx_projects_is_public ON projects(is_public);

CREATE INDEX idx_blog_posts_user_id ON blog_posts(user_id);
CREATE INDEX idx_blog_posts_status ON blog_posts(status);
CREATE INDEX idx_blog_posts_published_at ON blog_posts(published_at);
CREATE INDEX idx_blog_posts_is_featured ON blog_posts(is_featured);

CREATE INDEX idx_ideas_user_id ON ideas(user_id);
CREATE INDEX idx_ideas_status ON ideas(status);
CREATE INDEX idx_ideas_is_public ON ideas(is_public);

-- Search optimization
CREATE INDEX idx_projects_title_gin ON projects USING gin(to_tsvector('english', title));
CREATE INDEX idx_blog_posts_title_gin ON blog_posts USING gin(to_tsvector('english', title));
CREATE INDEX idx_ideas_title_gin ON ideas USING gin(to_tsvector('english', title));

-- Sorting and pagination
CREATE INDEX idx_projects_created_at ON projects(created_at DESC);
CREATE INDEX idx_blog_posts_created_at ON blog_posts(created_at DESC);
CREATE INDEX idx_ideas_created_at ON ideas(created_at DESC);

-- Translation lookups
CREATE INDEX idx_project_translations_project_id ON project_translations(project_id);
CREATE INDEX idx_blog_post_translations_blog_post_id ON blog_post_translations(blog_post_id);
CREATE INDEX idx_idea_translations_idea_id ON idea_translations(idea_id);
```

### 14.2 Composite Indexes
```sql
-- User-specific content queries
CREATE INDEX idx_projects_user_status ON projects(user_id, status);
CREATE INDEX idx_blog_posts_user_status ON blog_posts(user_id, status);
CREATE INDEX idx_ideas_user_status ON ideas(user_id, status);

-- Public content queries
CREATE INDEX idx_projects_public_featured ON projects(is_public, is_featured);
CREATE INDEX idx_blog_posts_status_published ON blog_posts(status, published_at);
CREATE INDEX idx_ideas_public_status ON ideas(is_public, status);

-- Translation queries
CREATE INDEX idx_translations_entity_lang ON project_translations(project_id, language_code);
CREATE INDEX idx_blog_translations_entity_lang ON blog_post_translations(blog_post_id, language_code);
CREATE INDEX idx_idea_translations_entity_lang ON idea_translations(idea_id, language_code);
```

---

## 15. Data Integrity & Constraints

### 15.1 Custom Constraints
```sql
-- Ensure end dates are after start dates
ALTER TABLE education ADD CONSTRAINT check_education_dates 
    CHECK (end_date IS NULL OR start_date IS NULL OR end_date >= start_date);

ALTER TABLE work_experience ADD CONSTRAINT check_work_experience_dates 
    CHECK (end_date IS NULL OR start_date IS NULL OR end_date >= start_date);

ALTER TABLE projects ADD CONSTRAINT check_project_dates 
    CHECK (end_date IS NULL OR start_date IS NULL OR end_date >= start_date);

ALTER TABLE research_projects ADD CONSTRAINT check_research_dates 
    CHECK (end_date IS NULL OR start_date IS NULL OR end_date >= start_date);

-- Ensure only one primary personal info per user
CREATE UNIQUE INDEX idx_personal_info_primary 
    ON personal_info(user_id) WHERE is_primary = TRUE;

-- Ensure valid email formats
ALTER TABLE users ADD CONSTRAINT check_email_format 
    CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- Ensure valid URLs
ALTER TABLE social_links ADD CONSTRAINT check_url_format 
    CHECK (url ~* '^https?://[^\s/$.?#].[^\s]*$');

-- Ensure valid priority values
ALTER TABLE ideas ADD CONSTRAINT check_priority_values 
    CHECK (priority IN ('low', 'medium', 'high', 'urgent'));

-- Ensure valid status values
ALTER TABLE projects ADD CONSTRAINT check_project_status 
    CHECK (status IN ('active', 'completed', 'paused', 'cancelled'));

ALTER TABLE blog_posts ADD CONSTRAINT check_blog_post_status 
    CHECK (status IN ('draft', 'published', 'archived'));

ALTER TABLE ideas ADD CONSTRAINT check_idea_status 
    CHECK (status IN ('draft', 'hypothesis', 'experimenting', 'validating', 'published', 'concluded'));
```

### 15.2 Triggers for Automated Updates
```sql
-- Auto-update updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to all tables with updated_at column
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_blog_posts_updated_at BEFORE UPDATE ON blog_posts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ideas_updated_at BEFORE UPDATE ON ideas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add triggers for other tables with updated_at columns...

-- Auto-update tag usage counts
CREATE OR REPLACE FUNCTION update_tag_usage_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE blog_tags SET usage_count = usage_count + 1 WHERE id = NEW.blog_tag_id;
        UPDATE idea_tags SET usage_count = usage_count + 1 WHERE id = NEW.idea_tag_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE blog_tags SET usage_count = usage_count - 1 WHERE id = OLD.blog_tag_id;
        UPDATE idea_tags SET usage_count = usage_count - 1 WHERE id = OLD.idea_tag_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_blog_tag_usage AFTER INSERT OR DELETE ON blog_post_tags
    FOR EACH ROW EXECUTE FUNCTION update_tag_usage_count();

CREATE TRIGGER update_idea_tag_usage AFTER INSERT OR DELETE ON idea_tag_assignments
    FOR EACH ROW EXECUTE FUNCTION update_tag_usage_count();
```

---

## 16. Database Views for Common Queries

### 16.1 Content Summary Views
```sql
-- Complete project information with translations
CREATE VIEW project_summary AS
SELECT 
    p.id,
    p.user_id,
    p.title,
    p.slug,
    p.description,
    p.project_type,
    p.status,
    p.start_date,
    p.end_date,
    p.github_url,
    p.demo_url,
    p.thumbnail_url,
    p.is_featured,
    p.is_public,
    p.view_count,
    p.star_count,
    p.created_at,
    p.updated_at,
    pt.language_code,
    COALESCE(pt.title, p.title) as localized_title,
    COALESCE(pt.description, p.description) as localized_description,
    COALESCE(pt.project_type, p.project_type) as localized_project_type
FROM projects p
LEFT JOIN project_translations pt ON p.id = pt.project_id;

-- Complete blog post information with translations
CREATE VIEW blog_post_summary AS
SELECT 
    bp.id,
    bp.user_id,
    bp.title,
    bp.slug,
    bp.excerpt,
    bp.content_type,
    bp.status,
    bp.is_featured,
    bp.featured_image_url,
    bp.reading_time_minutes,
    bp.view_count,
    bp.like_count,
    bp.comment_count,
    bp.published_at,
    bp.created_at,
    bp.updated_at,
    bpt.language_code,
    COALESCE(bpt.title, bp.title) as localized_title,
    COALESCE(bpt.excerpt, bp.excerpt) as localized_excerpt,
    COALESCE(bpt.content, bp.content) as localized_content
FROM blog_posts bp
LEFT JOIN blog_post_translations bpt ON bp.id = bpt.blog_post_id;

-- Complete idea information with translations
CREATE VIEW idea_summary AS
SELECT 
    i.id,
    i.user_id,
    i.title,
    i.slug,
    i.abstract,
    i.status,
    i.priority,
    i.collaboration_needed,
    i.funding_required,
    i.is_public,
    i.view_count,
    i.like_count,
    i.created_at,
    i.updated_at,
    it.language_code,
    COALESCE(it.title, i.title) as localized_title,
    COALESCE(it.abstract, i.abstract) as localized_abstract,
    COALESCE(it.motivation, i.motivation) as localized_motivation
FROM ideas i
LEFT JOIN idea_translations it ON i.id = it.idea_id;
```

### 16.2 Analytics Views
```sql
-- User activity summary
CREATE VIEW user_activity_summary AS
SELECT 
    u.id as user_id,
    u.username,
    u.email,
    COUNT(DISTINCT p.id) as project_count,
    COUNT(DISTINCT bp.id) as blog_post_count,
    COUNT(DISTINCT i.id) as idea_count,
    SUM(p.view_count) as total_project_views,
    SUM(bp.view_count) as total_blog_views,
    SUM(i.view_count) as total_idea_views,
    MAX(u.last_login_at) as last_activity
FROM users u
LEFT JOIN projects p ON u.id = p.user_id
LEFT JOIN blog_posts bp ON u.id = bp.user_id
LEFT JOIN ideas i ON u.id = i.user_id
GROUP BY u.id, u.username, u.email;

-- Popular content view
CREATE VIEW popular_content AS
SELECT 
    'project' as content_type,
    id as content_id,
    title,
    slug,
    view_count,
    created_at
FROM projects
WHERE is_public = true
UNION ALL
SELECT 
    'blog_post' as content_type,
    id as content_id,
    title,
    slug,
    view_count,
    created_at
FROM blog_posts
WHERE status = 'published'
UNION ALL
SELECT 
    'idea' as content_type,
    id as content_id,
    title,
    slug,
    view_count,
    created_at
FROM ideas
WHERE is_public = true
ORDER BY view_count DESC, created_at DESC;
```

---

## 17. Security Considerations

### 17.1 Row Level Security (RLS)
```sql
-- Enable RLS on sensitive tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE blog_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE ideas ENABLE ROW LEVEL SECURITY;

-- Users can only see/modify their own data
CREATE POLICY user_own_data ON users
    FOR ALL
    TO authenticated_user
    USING (id = current_user_id());

-- Projects visibility policy
CREATE POLICY project_visibility ON projects
    FOR SELECT
    TO authenticated_user
    USING (is_public = true OR user_id = current_user_id());

CREATE POLICY project_modification ON projects
    FOR INSERT, UPDATE, DELETE
    TO authenticated_user
    USING (user_id = current_user_id());

-- Blog posts visibility policy
CREATE POLICY blog_post_visibility ON blog_posts
    FOR SELECT
    TO authenticated_user
    USING (status = 'published' OR user_id = current_user_id());

CREATE POLICY blog_post_modification ON blog_posts
    FOR INSERT, UPDATE, DELETE
    TO authenticated_user
    USING (user_id = current_user_id());

-- Ideas visibility policy
CREATE POLICY idea_visibility ON ideas
    FOR SELECT
    TO authenticated_user
    USING (is_public = true OR user_id = current_user_id());

CREATE POLICY idea_modification ON ideas
    FOR INSERT, UPDATE, DELETE
    TO authenticated_user
    USING (user_id = current_user_id());
```

### 17.2 Audit Triggers
```sql
-- Create audit table for tracking changes
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name VARCHAR(50) NOT NULL,
    record_id UUID NOT NULL,
    action VARCHAR(10) NOT NULL, -- INSERT, UPDATE, DELETE
    old_values JSONB,
    new_values JSONB,
    user_id UUID,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Generic audit trigger function
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (table_name, record_id, action, new_values, user_id)
        VALUES (TG_TABLE_NAME, NEW.id, 'INSERT', to_jsonb(NEW), current_user_id());
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (table_name, record_id, action, old_values, new_values, user_id)
        VALUES (TG_TABLE_NAME, NEW.id, 'UPDATE', to_jsonb(OLD), to_jsonb(NEW), current_user_id());
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (table_name, record_id, action, old_values, user_id)
        VALUES (TG_TABLE_NAME, OLD.id, 'DELETE', to_jsonb(OLD), current_user_id());
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

-- Apply audit triggers to important tables
CREATE TRIGGER audit_users AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_projects AFTER INSERT OR UPDATE OR DELETE ON projects
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_blog_posts AFTER INSERT OR UPDATE OR DELETE ON blog_posts
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_ideas AFTER INSERT OR UPDATE OR DELETE ON ideas
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();
```

---

## 18. Data Migration & Seeding

### 18.1 Initial Data Setup
```sql
-- Insert default languages
INSERT INTO languages (code, name, native_name) VALUES
('en', 'English', 'English'),
('zh', 'Chinese', '中文');

-- Insert default blog categories
INSERT INTO blog_categories (name, slug, description, color) VALUES
('Technology', 'technology', 'Posts about technology and programming', '#3b82f6'),
('AI & Machine Learning', 'ai-ml', 'Posts about artificial intelligence and machine learning', '#8b5cf6'),
('Web Development', 'web-dev', 'Posts about web development', '#10b981'),
('Personal', 'personal', 'Personal thoughts and experiences', '#f59e0b'),
('Tutorial', 'tutorial', 'Step-by-step tutorials and guides', '#ef4444'),
('Research', 'research', 'Research papers and academic content', '#6366f1');

-- Insert default idea categories
INSERT INTO idea_categories (name, slug, description, color) VALUES
('Research', 'research', 'Academic research ideas', '#8b5cf6'),
('Product', 'product', 'Product development ideas', '#10b981'),
('Technology', 'technology', 'Technology innovation ideas', '#3b82f6'),
('Education', 'education', 'Educational project ideas', '#f59e0b'),
('Open Source', 'open-source', 'Open source project ideas', '#6366f1'),
('Startup', 'startup', 'Startup and business ideas', '#ef4444');

-- Insert default project types
INSERT INTO system_settings (setting_key, setting_value, setting_type, description, is_public) VALUES
('project_types', '["Web Application", "Mobile App", "Desktop Application", "API/Backend", "Machine Learning", "Research", "Tool/Utility", "Game", "Library/Framework", "Other"]', 'json', 'Available project types', true),
('content_types', '["article", "vlog", "podcast", "tutorial", "case-study", "news", "interview", "review"]', 'json', 'Available blog content types', true),
('skill_levels', '["Beginner", "Intermediate", "Advanced", "Expert", "Master"]', 'json', 'Available skill proficiency levels', true);
```

### 18.2 Sample Data Functions
```sql
-- Function to create sample user data
CREATE OR REPLACE FUNCTION create_sample_user_data(sample_user_id UUID)
RETURNS VOID AS $$
BEGIN
    -- Create sample personal info
    INSERT INTO personal_info (user_id, full_name, title, current_status, phone, email, location, is_primary)
    VALUES (sample_user_id, 'Silan Hu', 'AI Researcher & Full Stack Developer', 'Looking for PhD position in CS(AI)', '+65 86986181', 'silan.hu@example.com', 'Singapore', true);

    -- Create sample education
    INSERT INTO education (user_id, institution, degree, field_of_study, start_date, end_date, is_current, location, sort_order)
    VALUES 
    (sample_user_id, 'National University of Singapore', 'Master of Computing', 'Artificial Intelligence', '2024-08-01', '2025-12-31', true, 'Singapore', 1),
    (sample_user_id, 'Macau University of Science and Technology', 'Bachelor of Science', 'Computer Science', '2020-09-01', '2024-06-30', false, 'Macau', 2);

    -- Create sample projects
    INSERT INTO projects (user_id, title, slug, description, project_type, status, github_url, demo_url, is_featured, is_public, sort_order)
    VALUES 
    (sample_user_id, 'AI Resume Builder', 'ai-resume-builder', 'An intelligent resume builder powered by AI', 'Web Application', 'active', 'https://github.com/example/ai-resume', 'https://demo.example.com', true, true, 1),
    (sample_user_id, 'Knowledge Graph System', 'knowledge-graph', 'A knowledge graph system for educational content', 'Research', 'completed', 'https://github.com/example/kg-system', null, true, true, 2);

    -- Create sample blog posts
    INSERT INTO blog_posts (user_id, title, slug, excerpt, content, status, is_featured, published_at)
    VALUES 
    (sample_user_id, 'Getting Started with AI in Education', 'ai-education-intro', 'An introduction to applying AI in educational contexts', 'Full blog post content here...', 'published', true, CURRENT_TIMESTAMP - INTERVAL '1 month'),
    (sample_user_id, 'Building Knowledge Graphs with Neo4j', 'neo4j-knowledge-graphs', 'A comprehensive guide to building knowledge graphs', 'Full blog post content here...', 'published', false, CURRENT_TIMESTAMP - INTERVAL '2 weeks');

    -- Create sample ideas
    INSERT INTO ideas (user_id, title, slug, abstract, status, priority, is_public)
    VALUES 
    (sample_user_id, 'Personalized Learning Path Generator', 'personalized-learning-paths', 'An AI system that generates personalized learning paths based on student preferences and performance', 'hypothesis', 'high', true),
    (sample_user_id, 'Automated Code Review Assistant', 'code-review-assistant', 'An AI-powered tool that assists in code reviews by identifying patterns and suggesting improvements', 'draft', 'medium', true);

    RAISE NOTICE 'Sample data created for user %', sample_user_id;
END;
$$ language 'plpgsql';
```

---

## 19. Performance Optimization Strategies

### 19.1 Query Optimization
```sql
-- Materialized views for expensive queries
CREATE MATERIALIZED VIEW mv_user_content_stats AS
SELECT 
    u.id as user_id,
    u.username,
    COUNT(DISTINCT p.id) as project_count,
    COUNT(DISTINCT bp.id) as published_blog_count,
    COUNT(DISTINCT i.id) as public_idea_count,
    SUM(p.view_count) as total_project_views,
    SUM(bp.view_count) as total_blog_views,
    SUM(i.view_count) as total_idea_views,
    MAX(GREATEST(p.updated_at, bp.updated_at, i.updated_at)) as last_content_update
FROM users u
LEFT JOIN projects p ON u.id = p.user_id AND p.is_public = true
LEFT JOIN blog_posts bp ON u.id = bp.user_id AND bp.status = 'published'
LEFT JOIN ideas i ON u.id = i.user_id AND i.is_public = true
GROUP BY u.id, u.username;

-- Create index on materialized view
CREATE INDEX idx_mv_user_content_stats_user_id ON mv_user_content_stats(user_id);

-- Refresh materialized view function
CREATE OR REPLACE FUNCTION refresh_user_content_stats()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_user_content_stats;
END;
$$ language 'plpgsql';

-- Schedule refresh (would be done via cron job in production)
-- SELECT cron.schedule('refresh-stats', '0 */4 * * *', 'SELECT refresh_user_content_stats();');
```

### 19.2 Caching Strategy
```sql
-- Popular content cache table
CREATE TABLE popular_content_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_type VARCHAR(50) NOT NULL,
    content_id UUID NOT NULL,
    title VARCHAR(500) NOT NULL,
    slug VARCHAR(300) NOT NULL,
    view_count INTEGER NOT NULL,
    cache_key VARCHAR(200) NOT NULL,
    cached_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP + INTERVAL '1 hour',
    UNIQUE(cache_key)
);

-- Function to update popular content cache
CREATE OR REPLACE FUNCTION update_popular_content_cache()
RETURNS VOID AS $$
BEGIN
    -- Clear expired cache entries
    DELETE FROM popular_content_cache WHERE expires_at < CURRENT_TIMESTAMP;
    
    -- Update cache with fresh data
    INSERT INTO popular_content_cache (content_type, content_id, title, slug, view_count, cache_key)
    SELECT 
        'project' as content_type,
        id as content_id,
        title,
        slug,
        view_count,
        'popular_projects' as cache_key
    FROM projects 
    WHERE is_public = true 
    ORDER BY view_count DESC, created_at DESC 
    LIMIT 10
    ON CONFLICT (cache_key) DO UPDATE SET
        cached_at = CURRENT_TIMESTAMP,
        expires_at = CURRENT_TIMESTAMP + INTERVAL '1 hour';
END;
$$ language 'plpgsql';
```

---

## 20. Backup & Recovery Strategy

### 20.1 Backup Procedures
```sql
-- Full database backup (to be run via pg_dump)
-- pg_dump -h localhost -U username -d database_name -f backup_$(date +%Y%m%d_%H%M%S).sql

-- Incremental backup using WAL-E or similar tools
-- wal-e backup-push /var/lib/postgresql/data

-- Point-in-time recovery setup
-- archive_mode = on
-- archive_command = 'wal-e wal-push %p'
-- wal_level = replica
```

### 20.2 Data Retention Policies
```sql
-- Clean up old activity logs (keep 1 year)
DELETE FROM activity_log WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '1 year';

-- Clean up old page views (keep 6 months)
DELETE FROM page_views WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '6 months';

-- Clean up old audit logs (keep 2 years)
DELETE FROM audit_log WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '2 years';

-- Archive old blog posts (move to archive table)
CREATE TABLE archived_blog_posts (LIKE blog_posts INCLUDING ALL);

-- Function to archive old content
CREATE OR REPLACE FUNCTION archive_old_content()
RETURNS VOID AS $$
BEGIN
    -- Move old draft blog posts to archive
    INSERT INTO archived_blog_posts 
    SELECT * FROM blog_posts 
    WHERE status = 'draft' AND created_at < CURRENT_TIMESTAMP - INTERVAL '2 years';
    
    DELETE FROM blog_posts 
    WHERE status = 'draft' AND created_at < CURRENT_TIMESTAMP - INTERVAL '2 years';
    
    RAISE NOTICE 'Archived old content';
END;
$$ language 'plpgsql';
```

---

## 21. Monitoring & Maintenance

### 21.1 Health Check Views
```sql
-- Database health check view
CREATE VIEW db_health_check AS
SELECT 
    'table_sizes' as check_type,
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Active connections view
CREATE VIEW active_connections AS
SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    client_port,
    backend_start,
    state,
    query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY backend_start;

-- Slow queries view
CREATE VIEW slow_queries AS
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements
ORDER BY total_time DESC;
```

### 21.2 Maintenance Functions
```sql
-- Vacuum and analyze all tables
CREATE OR REPLACE FUNCTION maintain_database()
RETURNS VOID AS $$
DECLARE
    table_name TEXT;
BEGIN
    FOR table_name IN
        SELECT tablename FROM pg_tables WHERE schemaname = 'public'
    LOOP
        EXECUTE 'VACUUM ANALYZE ' || table_name;
    END LOOP;
    
    RAISE NOTICE 'Database maintenance completed';
END;
$$ language 'plpgsql';

-- Update statistics for query planner
CREATE OR REPLACE FUNCTION update_statistics()
RETURNS VOID AS $$
BEGIN
    ANALYZE;
    RAISE NOTICE 'Statistics updated';
END;
$$ language 'plpgsql';
```

---

## 22. Migration Path

### 22.1 From Current Mock Data
```sql
-- Migration script to convert current mock data to database
CREATE OR REPLACE FUNCTION migrate_mock_data()
RETURNS VOID AS $$
BEGIN
    -- This would be implemented based on the actual mock data structure
    -- in the API files. The migration would:
    
    -- 1. Create default user account
    -- 2. Import resume data (education, experience, skills, etc.)
    -- 3. Import project data
    -- 4. Import blog post data
    -- 5. Import idea data
    -- 6. Import plan data
    -- 7. Set up relationships between entities
    
    RAISE NOTICE 'Mock data migration completed';
END;
$$ language 'plpgsql';
```

### 22.2 Version Control
```sql
-- Database version tracking
CREATE TABLE db_versions (
    id SERIAL PRIMARY KEY,
    version VARCHAR(20) NOT NULL,
    description TEXT,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial version
INSERT INTO db_versions (version, description) VALUES ('1.0.0', 'Initial database schema');
```

---

## 23. Conclusion

This comprehensive database design provides a robust foundation for the Silan-Personal-Website website with the following key features:

### ✅ **Normalization (BCNF)**
- All tables are properly normalized to Boyce-Codd Normal Form
- Eliminates data redundancy and ensures data integrity
- Optimizes storage and query performance

### ✅ **Multi-language Support**
- Comprehensive i18n support through translation tables
- Scalable design for adding new languages
- Maintains referential integrity across languages

### ✅ **Comprehensive Coverage**
- Supports all website features: resume, projects, blog, ideas, planning
- Includes user management, file handling, and analytics
- Provides interaction features like comments, likes, and views

### ✅ **Performance Optimized**
- Strategic indexing for fast queries
- Materialized views for expensive operations
- Efficient caching strategies

### ✅ **Security & Audit**
- Row-level security policies
- Comprehensive audit trail
- Data integrity constraints

### ✅ **Scalability**
- Designed for growth with proper indexing
- Efficient query patterns
- Horizontal scaling considerations

### ✅ **Maintainability**
- Clear documentation and comments
- Automated maintenance functions
- Version control and migration support

This design provides a solid foundation that can evolve with the website's needs while maintaining performance, security, and data integrity.

---

*End of Database Design Document*