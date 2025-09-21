---
title: "Silan Personal Website Usage Guide - Part 2: Content Management and Customization"
author: "Silan Hu"
date: "2024-07-16"
type: "blog"
series: "silan-website-usage-guide"
episode: 2
excerpt: "Deep dive into content management, customization options, and advanced features of the Silan Personal Website platform."
tags: ["tutorial", "content-management", "silan-website", "customization", "markdown"]
status: "published"
language: "en"
---

# Silan Personal Website Usage Guide - Part 2: Content Management and Customization

Now that you have your Silan Personal Website up and running, let's explore the powerful content management system and customization options that make this platform truly shine.

## Understanding the Content Architecture

### File-Based Content Management

The Silan platform uses a unique file-based approach that combines the simplicity of markdown with the power of a database-backed system:

```
api-test-portfolio/content/
├── blog/           # Blog posts and articles
├── ideas/          # Research ideas and concepts
├── projects/       # Portfolio projects
├── resume/         # Resume and CV information
└── updates/        # Timeline updates
```

### Content Types and Structure

Each content type follows a specific structure optimized for different use cases:

#### Blog Posts
```markdown
---
title: "Your Blog Title"
author: "Your Name"
date: "2024-07-16"
type: "blog"
series: "optional-series-name"
episode: 1
excerpt: "Brief description"
tags: ["tag1", "tag2"]
status: "published"
language: "en"
---

# Your Content Here
```

#### Project Documentation
```markdown
---
title: "Project Name"
type: "project"
status: "active"
technologies: ["React", "Go", "Python"]
demo_url: "https://example.com"
repository: "https://github.com/user/repo"
---

# Project Description
```

## Content Management with CLI

### Creating New Content

```bash
# Create a new blog post
silan init blog "Advanced React Patterns"

# Create a new project
silan init project "AI Chat Application"

# Create a new research idea
silan init idea "Quantum Machine Learning Framework"

# Create a timeline update
silan init update "2024 Q2 Milestone"
```

### Managing Content Lifecycle

```bash
# Check content status
silan status

# Sync content with database
silan sync content

# Validate content structure
silan validate

# Preview content before publishing
silan preview blog "your-blog-post"
```

### Advanced CLI Operations

```bash
# Batch operations
silan sync --type blog          # Sync only blog posts
silan sync --status published   # Sync only published content

# Content analysis
silan analyze content           # Generate content statistics
silan check links              # Verify external links

# Backup and restore
silan backup content           # Create content backup
silan restore backup.zip      # Restore from backup
```

## Customizing Your Website

### Personal Information Setup

Edit the resume section to reflect your professional profile:

```bash
# Edit personal information
cd api-test-portfolio/content/resume/
vim personal-info.md
```

```markdown
---
name: "Your Name"
title: "AI Researcher & Full Stack Developer"
email: "your.email@example.com"
location: "Your City, Country"
website: "https://yourwebsite.com"
---

# Professional Summary

Your professional summary here...

## Skills
- Programming: Python, JavaScript, Go, TypeScript
- AI/ML: TensorFlow, PyTorch, Scikit-learn
- Web: React, Node.js, Docker, Kubernetes
```

### Customizing the Frontend

#### Theming and Styling

```bash
# Navigate to frontend source
cd src/

# Key files for customization:
# - tailwind.config.js    : Tailwind CSS configuration
# - src/index.css         : Global styles
# - src/components/       : React components
```

#### Modifying the Color Scheme

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          500: '#3b82f6',
          900: '#1e3a8a',
        },
        secondary: {
          50: '#f8fafc',
          500: '#64748b',
          900: '#0f172a',
        }
      }
    }
  }
}
```

#### Adding Custom Components

```typescript
// src/components/custom/MyComponent.tsx
import React from 'react';

interface MyComponentProps {
  title: string;
  description: string;
}

export const MyComponent: React.FC<MyComponentProps> = ({ title, description }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-bold text-gray-800">{title}</h3>
      <p className="text-gray-600 mt-2">{description}</p>
    </div>
  );
};
```

### Backend Configuration

#### Database Configuration

```yaml
# backend/go-server/etc/backend-api.yaml
Name: backend-api
Host: 0.0.0.0
Port: 8080

DataSource: silan:password@tcp(mysql:3306)/silan_website?charset=utf8mb4&parseTime=true&loc=Local

Cache:
  - Host: redis:6379
    Pass: ""
    Type: node
```

#### API Customization

```go
// backend/go-server/internal/handler/custom/customhandler.go
package custom

import (
    "net/http"
    "github.com/zeromicro/go-zero/rest/httpx"
    "your-project/internal/logic/custom"
    "your-project/internal/svc"
)

func CustomHandler(svcCtx *svc.ServiceContext) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        l := custom.NewCustomLogic(r.Context(), svcCtx)
        resp, err := l.Custom()
        if err != nil {
            httpx.Error(w, err)
        } else {
            httpx.OkJson(w, resp)
        }
    }
}
```

## Advanced Features

### Multi-Language Support

#### Setting Up Internationalization

```bash
# Create language files
cd src/i18n/locales/

# Add new language
cp en.json zh.json
```

```json
{
  "navigation": {
    "home": "首页",
    "blog": "博客",
    "projects": "项目",
    "resume": "简历"
  },
  "content": {
    "readMore": "阅读更多",
    "viewProject": "查看项目"
  }
}
```

#### Language-Specific Content

```markdown
---
title: "Project Title"
title_zh: "项目标题"
description: "English description"
description_zh: "中文描述"
language: "en"
---

# English Content

## 中文内容
```

### SEO Optimization

#### Meta Tags Configuration

```typescript
// src/utils/seo.ts
export const generateMetaTags = (content: ContentItem) => {
  return {
    title: `${content.title} | Silan Hu`,
    description: content.excerpt,
    keywords: content.tags.join(', '),
    'og:title': content.title,
    'og:description': content.excerpt,
    'og:image': content.image || '/default-og-image.jpg',
    'og:url': `https://silan.tech/${content.slug}`,
    'twitter:card': 'summary_large_image',
    'twitter:title': content.title,
    'twitter:description': content.excerpt,
  };
};
```

#### Structured Data

```typescript
// src/utils/structuredData.ts
export const generateBlogStructuredData = (post: BlogPost) => {
  return {
    '@context': 'https://schema.org',
    '@type': 'BlogPosting',
    headline: post.title,
    author: {
      '@type': 'Person',
      name: post.author,
    },
    datePublished: post.date,
    description: post.excerpt,
    url: `https://silan.tech/blog/${post.slug}`,
  };
};
```

### Performance Optimization

#### Image Optimization

```typescript
// src/components/OptimizedImage.tsx
import React from 'react';

interface OptimizedImageProps {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  className?: string;
}

export const OptimizedImage: React.FC<OptimizedImageProps> = ({
  src,
  alt,
  width,
  height,
  className
}) => {
  return (
    <img
      src={src}
      alt={alt}
      width={width}
      height={height}
      className={className}
      loading="lazy"
      decoding="async"
    />
  );
};
```

#### Code Splitting

```typescript
// src/views/LazyComponents.tsx
import { lazy } from 'react';

export const BlogStack = lazy(() => import('./BlogStack'));
export const ProjectGallery = lazy(() => import('./ProjectGallery'));
export const ResumeWebsite = lazy(() => import('./ResumeWebsite'));
```

## Content Publishing Workflow

### Development Workflow

```bash
# 1. Create content
silan init blog "My New Post"

# 2. Edit content
vim api-test-portfolio/content/blog/my-new-post.md

# 3. Preview locally
npm run dev

# 4. Sync with database
silan sync content

# 5. Verify changes
silan status
```

### Production Deployment

```bash
# 1. Build frontend
npm run build

# 2. Build backend
cd backend/go-server
go build -o backend backend.go

# 3. Deploy with Docker
docker-compose --profile production up -d

# 4. Verify deployment
curl -I https://silan.tech/api/health
```

## Best Practices

### Content Organization

1. **Use Clear Naming**: Use descriptive filenames and URLs
2. **Consistent Structure**: Follow the established frontmatter format
3. **Regular Backups**: Use `silan backup` regularly
4. **Version Control**: Keep content in Git for history tracking

### Performance Tips

1. **Optimize Images**: Use WebP format when possible
2. **Lazy Loading**: Implement lazy loading for images and components
3. **Caching**: Utilize Redis caching for frequently accessed content
4. **CDN**: Consider using a CDN for static assets

### Security Considerations

1. **Input Validation**: Always validate content inputs
2. **XSS Prevention**: Sanitize HTML content
3. **HTTPS**: Always use HTTPS in production
4. **Regular Updates**: Keep dependencies updated

## Troubleshooting

### Common Issues

**Content Not Syncing**
```bash
# Check sync status
silan status

# Force resync
silan sync --force

# Check logs
silan logs
```

**Frontend Build Issues**
```bash
# Clear cache
npm run clean

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

**Database Connection Issues**
```bash
# Check database status
docker-compose ps mysql

# Restart database
docker-compose restart mysql
```

## Next Steps

In Part 3, we'll explore:
- Advanced deployment strategies
- Monitoring and analytics
- Performance optimization
- Custom integrations

Continue with [Part 3: Advanced Features and Configuration](./part3-advanced-features.md)!

---

*Ready to make your website truly yours? The next part will cover advanced customization and deployment strategies.*