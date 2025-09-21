---
title: "Silan Personal Website Usage Guide - Part 1: Getting Started"
author: "Silan Hu"
date: "2024-07-16"
type: "blog"
series: "silan-website-usage-guide"
episode: 1
excerpt: "Learn how to set up and get started with the Silan Personal Website platform - a comprehensive guide for AI professionals and developers."
tags: ["tutorial", "getting-started", "silan-website", "setup", "personal-branding"]
status: "published"
language: "en"
---

# Silan Personal Website Usage Guide - Part 1: Getting Started

Welcome to the comprehensive usage guide for the Silan Personal Website platform! This series will walk you through every aspect of setting up, customizing, and maintaining your professional online presence using this cutting-edge full-stack platform.

## What is Silan Personal Website?

The Silan Personal Website is a modern, full-stack platform designed specifically for AI professionals, researchers, and developers who need a sophisticated yet maintainable online presence. It combines:

- **Modern Frontend**: React 18 with TypeScript, Tailwind CSS, and Framer Motion
- **High-Performance Backend**: Go-Zero microservices with Python CLI tools
- **Intelligent Content Management**: File-based system with automated synchronization
- **Professional Features**: Multi-language support, SEO optimization, and responsive design

## Prerequisites

Before we start, ensure you have the following installed:

```bash
# Required software
- Node.js 18+ and npm
- Go 1.23+
- Python 3.9+
- Docker and Docker Compose
- Git
```

## Step 1: Repository Setup

### Clone the Repository

```bash
git clone https://github.com/Qingbolan/AIPro-Resume.git
cd AIPro-Resume
```

### Explore the Project Structure

```bash
# View the main directory structure
ls -la

# Key directories to understand:
# - src/                 : Frontend React application
# - backend/file-system/ : Python CLI tools
# - backend/go-server/   : Go backend services
# - api-test-portfolio/  : Content management system
```

## Step 2: Frontend Setup

### Install Dependencies

```bash
# Install frontend dependencies
npm install

# This will install all React, TypeScript, and styling dependencies
```

### Configure Development Environment

```bash
# Create environment file (if needed)
cp .env.example .env

# Edit the .env file with your configuration
```

### Start Development Server

```bash
# Start the development server
npm run dev

# Your application will be available at http://localhost:5173
```

### Verify Frontend Installation

Open your browser and navigate to `http://localhost:5173`. You should see:

- ✅ Clean, modern interface
- ✅ Responsive design
- ✅ Navigation menu
- ✅ Sample content

## Step 3: Backend Services Setup

### Python CLI Tools Setup

```bash
# Navigate to the Python backend
cd backend/file-system

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install CLI tool in development mode
pip install -e .
```

### Test Python CLI

```bash
# Test the CLI installation
silan --help

# You should see available commands like:
# - init: Initialize new content
# - sync: Synchronize content with database
# - status: Check system status
```

### Go Backend Setup

```bash
# Navigate to Go backend
cd backend/go-server

# Install Go dependencies
go mod download

# Build the application
go build -o backend backend.go

# Run the backend server
./backend
```

## Step 4: Content Management Setup

### Understanding Content Structure

```bash
# Navigate to content directory
cd api-test-portfolio/content

# Content is organized into:
# - blog/     : Blog posts and articles
# - ideas/    : Research ideas and concepts
# - projects/ : Portfolio projects
# - resume/   : Resume and CV information
# - updates/  : Timeline updates
```

### Initialize Your Content

```bash
# Use the CLI to initialize new content
silan init project "My First Project"
silan init blog "My First Blog Post"
silan init idea "My Research Idea"
```

### Synchronize Content

```bash
# Sync content with the database
silan sync content

# Check synchronization status
silan status
```

## Step 5: Docker Setup (Recommended)

### Using Docker Compose

```bash
# Navigate to backend directory
cd backend/go-server

# Start all services with Docker
docker-compose up -d

# This will start:
# - MySQL database
# - Redis cache
# - Go backend server
# - Monitoring tools (optional)
```

### Verify Docker Services

```bash
# Check running containers
docker-compose ps

# View logs
docker-compose logs

# Access services:
# - Backend API: http://localhost:8080
# - Database: localhost:3306
# - Redis: localhost:6379
```

## Step 6: Verification and Testing

### Test the Complete Stack

1. **Frontend**: http://localhost:5173
2. **Backend API**: http://localhost:8080/api/health
3. **Content Management**: Use `silan status` command

### Common Commands

```bash
# Development workflow
npm run dev                    # Start frontend
./backend/go-server/backend   # Start backend
silan sync content            # Sync content
silan status                  # Check status

# Production build
npm run build                 # Build frontend
go build -o backend          # Build backend
```

## Troubleshooting

### Common Issues and Solutions

**Port Already in Use**
```bash
# Check what's using the port
lsof -i :5173
lsof -i :8080

# Kill the process or change port in configuration
```

**Database Connection Issues**
```bash
# Check Docker containers
docker-compose ps

# Restart database
docker-compose restart mysql
```

**Python CLI Not Found**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall CLI
pip install -e .
```

## Next Steps

Congratulations! You've successfully set up the Silan Personal Website platform. In the next part of this series, we'll cover:

- **Part 2**: Content Management and Customization
- **Part 3**: Advanced Features and Configuration
- **Part 4**: Deployment and Production Setup

### What You've Accomplished

- ✅ Set up development environment
- ✅ Installed frontend and backend dependencies
- ✅ Configured content management system
- ✅ Tested complete application stack
- ✅ Learned basic CLI commands

### Resources

- **Demo**: https://silan.tech
- **Repository**: https://github.com/Qingbolan/AIPro-Resume
- **Documentation**: Check the README.md file
- **Community**: Join discussions on GitHub

Ready to dive deeper? Continue with [Part 2: Content Management and Customization](./part2-content-management.md)!

---

*Have questions or need help? Feel free to open an issue on the GitHub repository or reach out to the community.*