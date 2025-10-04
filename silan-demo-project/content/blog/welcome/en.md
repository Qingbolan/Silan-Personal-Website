---
title: "Welcome to test-fixed"
date: "2025-09-23"
slug: "welcome"
description: "Getting started with your new Silan project"
published: true
featured: true
tags:
  - welcome
  - getting-started
  - silan
categories:
  - announcements
---

# Welcome to Your New Silan Project! 🎉

Congratulations on setting up your new portfolio project with Silan Database Tools! This is your first blog post to help you get started.

## What is Silan?

Silan is a powerful content management system that bridges the gap between Markdown files and databases. It allows you to:

- Write content in Markdown with frontmatter
- Automatically sync to MySQL, PostgreSQL, or SQLite databases
- Manage projects, ideas, and blog posts efficiently
- Use templates for consistent content creation

## Getting Started

### 1. Configure Your Database

First, set up your database connection:

```bash
# Interactive configuration
silan db-config interactive

# Or set manually
silan db-config set --type sqlite --path portfolio.db
```

### 2. Sync Your Content

Sync this blog post and other content to your database:

```bash
silan db-sync --create-tables
```

### 3. Explore the Structure

Your project includes:

- **Blog posts** in `content/blog/`
- **Projects** in `content/projects/`
- **Ideas** in `content/ideas/`
- **Moments** in `content/moment/`
- **Episodes** in `content/episode/`

### 4. Create New Content

```bash
# Create a new project
silan project create "My Awesome Project"

# Create a new idea
silan idea create "Revolutionary Concept"

# Create an update
silan update create --title "Weekly Progress"
```

## Next Steps

1. **Customize your configuration** in `silan.yaml`
2. **Edit the sample project** in `content/projects/`
3. **Create your own content** using the templates
4. **Set up your database** for production use

## Need Help?

- Check the [documentation](https://github.com/silan/docs)
- Run `silan --help` for command reference
- Look at the sample files for examples

Happy writing! ✨

---

*This post was auto-generated during project initialization. Feel free to edit or delete it.*
