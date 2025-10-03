---
title: "Episode 1: Setting Up Your Portfolio Project"
series: "Portfolio Tutorial Series"
episode_number: 1
date: "2025-09-23"
type: "episode"
duration: "15 minutes"
difficulty: "beginner"
tags:
  - "tutorial"
  - "setup"
  - "portfolio"
next_episode: "episode-02-content.md"
---

# Episode 1: Setting Up Your Portfolio Project

Welcome to the Portfolio Tutorial Series! In this first episode, we'll set up everything you need to start building your professional portfolio using Silan.

## What You'll Learn

By the end of this episode, you'll have:
- ✅ Silan installed and configured
- ✅ A new portfolio project initialized
- ✅ Basic understanding of the project structure
- ✅ Your first content piece created

## Prerequisites

- Basic command line knowledge
- Python 3.8+ installed
- Text editor of choice

## Step 1: Install Silan

First, let's install the Silan CLI tool:

```bash
pip install silan-cli
```

Verify the installation:

```bash
silan --version
```

## Step 2: Initialize Your Portfolio

Create a new directory for your portfolio and initialize it:

```bash
mkdir my-portfolio
cd my-portfolio
silan init
```

This creates the complete project structure with:
- Content directories (blog, projects, ideas, moment, episode)
- Template files for consistent formatting
- Configuration files
- Sample content to get you started

## Step 3: Explore the Structure

Let's look at what was created:

```bash
tree -L 3
```

You should see:
```
my-portfolio/
├── content/
│   ├── blog/
│   ├── projects/
│   ├── ideas/
│   ├── moment/
│   └── episode/
├── templates/
├── silan.yaml
└── README.md
```

## Step 4: Create Your First Project

Now let's create your first project entry:

```bash
silan new project hello-world --title "My First Project" --description "Learning to use Silan for portfolio management"
```

This creates a new project with proper structure and configuration.

## Step 5: Preview Your Content

Check what was created:

```bash
ls content/projects/hello-world/
```

You'll see:
- `README.md` - Main project description
- `.silan-cache` - Project metadata and configuration
- `LICENSE` - Project license file

## What's Next?

In the next episode, we'll learn how to:
- Customize your project content
- Add rich media and documentation
- Configure project metadata
- Set up project relationships

## Quick Exercise

Before moving to Episode 2, try this:
1. Open `content/projects/hello-world/README.md`
2. Replace the placeholder content with a real project description
3. Update the project status in `.silan-cache`
4. Add some tags that describe your project

## Troubleshooting

**Command not found**: Make sure Silan is properly installed and in your PATH
**Permission errors**: Check that you have write permissions in your current directory
**Missing directories**: Re-run `silan init` to recreate the project structure

## Resources

- [Silan Documentation](https://docs.silan.dev)
- [Project Template Examples](https://github.com/silan/examples)
- [Community Forum](https://forum.silan.dev)

---

**Next**: [Episode 2: Creating Rich Content](episode-02-content.md)

**Estimated Time**: 15 minutes
**Difficulty**: Beginner
