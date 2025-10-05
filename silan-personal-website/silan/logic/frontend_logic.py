"""
Frontend management logic for Silan CLI.
Handles template installation and frontend project management.
"""

import os
import shutil
import zipfile
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
import importlib.resources
from urllib.request import urlretrieve

from ..utils import ModernLogger


class FrontendLogic(ModernLogger):
    """Logic for managing frontend templates and projects"""

    def __init__(self):
        super().__init__(name="frontend", level="info")
        self.template_sources = {
            'static': 'templates/frontend-dist',
            'dev': 'templates/frontend-dev'
        }

    def install_frontend(self, dev_mode: bool = False, target_dir: Optional[str] = None) -> bool:
        """
        Install frontend templates to target directory

        Args:
            dev_mode: If True, install full development project. If False, install static build files
            target_dir: Target directory (defaults to current directory)

        Returns:
            bool: True if installation successful
        """
        try:
            current_dir = Path.cwd()
            target_path = Path(target_dir) if target_dir else current_dir

            if dev_mode:
                return self._install_dev_template(target_path)
            else:
                return self._install_static_template(target_path)

        except Exception as e:
            self.error(f"Frontend installation failed: {e}")
            return False

    def _install_static_template(self, target_path: Path) -> bool:
        """Install static build files for production deployment"""
        try:
            self.info("Installing static frontend files...")

            # Create static directory structure
            static_dir = target_path / "static"
            static_dir.mkdir(exist_ok=True)

            # Try to extract from package resources first
            if self._extract_from_package('static', static_dir):
                self.success(f"Static frontend installed to {static_dir}")
                return True

            # Fallback: create basic static structure
            return self._create_basic_static_structure(static_dir)

        except Exception as e:
            self.error(f"Failed to install static template: {e}")
            return False

    def _install_dev_template(self, target_path: Path) -> bool:
        """Install full development project template"""
        try:
            self.info("Installing development frontend template...")

            # Create project directory
            project_dir = target_path / "frontend"
            project_dir.mkdir(exist_ok=True)

            # Try to extract from package resources first
            if self._extract_from_package('dev', project_dir):
                self.success(f"Development frontend installed to {project_dir}")
                return True

            # Fallback: create basic development structure
            return self._create_basic_dev_structure(project_dir)

        except Exception as e:
            self.error(f"Failed to install dev template: {e}")
            return False

    def _extract_from_package(self, template_type: str, target_dir: Path) -> bool:
        """Extract template from package resources"""
        try:
            import silan

            # Get the template source path
            template_source = self.template_sources.get(template_type)
            if not template_source:
                return False

            # Try to access package resources
            try:
                if hasattr(importlib.resources, 'files'):
                    # Python 3.9+
                    package_files = importlib.resources.files('silan')
                    template_path = package_files / template_source

                    if template_path.exists():
                        self._copy_template_recursive(template_path, target_dir)
                        return True
                else:
                    # Python 3.8
                    with importlib.resources.path('silan', '') as package_path:
                        template_full_path = package_path / template_source
                        if template_full_path.exists():
                            shutil.copytree(template_full_path, target_dir, dirs_exist_ok=True)
                            return True
            except Exception as resource_error:
                self.debug(f"Package resource extraction failed: {resource_error}")
                return False

        except Exception as e:
            self.debug(f"Package extraction failed: {e}")
            return False

        return False

    def _copy_template_recursive(self, source_path, target_dir: Path):
        """Recursively copy template files from package resources"""
        if source_path.is_file():
            # Copy single file
            target_file = target_dir / source_path.name
            target_file.parent.mkdir(parents=True, exist_ok=True)
            target_file.write_bytes(source_path.read_bytes())
        elif source_path.is_dir():
            # Copy directory recursively
            target_subdir = target_dir / source_path.name
            target_subdir.mkdir(parents=True, exist_ok=True)

            for item in source_path.iterdir():
                self._copy_template_recursive(item, target_subdir)

    def _create_basic_static_structure(self, static_dir: Path) -> bool:
        """Create basic static file structure as fallback"""
        try:
            # Create basic HTML file
            index_html = static_dir / "index.html"
            index_html.write_text("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Silan Portfolio</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 40px; }
        .section { margin-bottom: 30px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Silan Portfolio</h1>
        <p>Personal portfolio website</p>
    </div>

    <div class="section">
        <h2>About</h2>
        <p>Welcome to your personal portfolio. Edit this file to customize your content.</p>
    </div>

    <div class="section">
        <h2>Projects</h2>
        <p>Your projects will be displayed here.</p>
    </div>

    <div class="section">
        <h2>Contact</h2>
        <p>Contact information goes here.</p>
    </div>
</body>
</html>""")

            # Create basic CSS file
            css_dir = static_dir / "css"
            css_dir.mkdir(exist_ok=True)
            style_css = css_dir / "style.css"
            style_css.write_text("""/* Silan Portfolio Styles */
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    background-color: #f9f9f9;
}

.header {
    text-align: center;
    padding: 40px 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 10px;
    margin-bottom: 40px;
}

.section {
    background: white;
    padding: 30px;
    margin-bottom: 30px;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

h1, h2 {
    margin-top: 0;
}

h2 {
    color: #667eea;
    border-bottom: 2px solid #667eea;
    padding-bottom: 10px;
}
""")

            self.success("Basic static structure created")
            return True

        except Exception as e:
            self.error(f"Failed to create basic static structure: {e}")
            return False

    def _create_basic_dev_structure(self, project_dir: Path) -> bool:
        """Create basic development project structure as fallback"""
        try:
            # Create package.json
            package_json = project_dir / "package.json"
            package_json.write_text("""{
  "name": "silan-portfolio",
  "version": "1.0.0",
  "description": "Silan Personal Portfolio Website",
  "main": "index.js",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.0.0",
    "typescript": "^5.0.0",
    "vite": "^4.4.0"
  }
}""")

            # Create vite.config.ts
            vite_config = project_dir / "vite.config.ts"
            vite_config.write_text("""import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true
  },
  build: {
    outDir: 'dist'
  }
})
""")

            # Create basic React app structure
            src_dir = project_dir / "src"
            src_dir.mkdir(exist_ok=True)

            # Create App.tsx
            app_tsx = src_dir / "App.tsx"
            app_tsx.write_text("""import React from 'react'
import './App.css'

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Silan Portfolio</h1>
        <p>Welcome to your personal portfolio website</p>
      </header>

      <main>
        <section className="about">
          <h2>About</h2>
          <p>This is your about section. Customize it with your information.</p>
        </section>

        <section className="projects">
          <h2>Projects</h2>
          <p>Your projects will be displayed here.</p>
        </section>

        <section className="contact">
          <h2>Contact</h2>
          <p>Add your contact information here.</p>
        </section>
      </main>
    </div>
  )
}

export default App
""")

            # Create App.css
            app_css = src_dir / "App.css"
            app_css.write_text(""".App {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.App-header {
  text-align: center;
  padding: 40px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 10px;
  margin-bottom: 40px;
}

section {
  background: white;
  padding: 30px;
  margin-bottom: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

h1, h2 {
  margin-top: 0;
}

h2 {
  color: #667eea;
  border-bottom: 2px solid #667eea;
  padding-bottom: 10px;
}

body {
  margin: 0;
  background-color: #f9f9f9;
}
""")

            # Create main.tsx
            main_tsx = src_dir / "main.tsx"
            main_tsx.write_text("""import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
""")

            # Create index.css
            index_css = src_dir / "index.css"
            index_css.write_text("""* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}
""")

            # Create index.html
            index_html = project_dir / "index.html"
            index_html.write_text("""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Silan Portfolio</title>
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.tsx"></script>
</body>
</html>
""")

            # Create README.md
            readme = project_dir / "README.md"
            readme.write_text("""# Silan Portfolio

A personal portfolio website built with React and TypeScript.

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## Customization

- Edit `src/App.tsx` to modify the main content
- Customize styles in `src/App.css`
- Add new components in the `src` directory

## Deployment

After building, the `dist` directory contains all static files ready for deployment.
""")

            self.success("Basic development structure created")
            return True

        except Exception as e:
            self.error(f"Failed to create basic dev structure: {e}")
            return False