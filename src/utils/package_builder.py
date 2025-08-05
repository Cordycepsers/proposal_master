"""
Package Builder Tool for the Automated RFP System.
Creates and manages Python packages with proper structure and configuration.
"""
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from ..utils.tools import Tool

logger = logging.getLogger(__name__)


class PackageBuilderTool(Tool):
    """Create and manage Python packages with proper structure and configuration."""
    
    name = "package_builder"
    description = "Create and manage Python packages with setup files, testing, and distribution"
    parameters = {
        "action": {
            "type": "string",
            "description": "Action to perform (create/test/build/publish/lint)",
            "required": True
        },
        "name": {
            "type": "string",
            "description": "Package name (required for create action)",
            "required": False
        },
        "version": {
            "type": "string",
            "description": "Package version",
            "required": False,
            "default": "0.1.0"
        },
        "author": {
            "type": "string",
            "description": "Package author",
            "required": False,
            "default": "Automated RFP System"
        },
        "description": {
            "type": "string",
            "description": "Package description",
            "required": False
        },
        "test_path": {
            "type": "string",
            "description": "Path to test directory or file",
            "required": False,
            "default": "tests/"
        },
        "output_dir": {
            "type": "string",
            "description": "Output directory for package creation",
            "required": False,
            "default": "."
        },
        "include_docs": {
            "type": "boolean",
            "description": "Include documentation structure",
            "required": False,
            "default": True
        },
        "include_ci": {
            "type": "boolean",
            "description": "Include CI/CD configuration",
            "required": False,
            "default": True
        }
    }

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute package builder action."""
        try:
            if action == "create":
                return self._create_package(**kwargs)
            elif action == "test":
                return self._run_tests(**kwargs)
            elif action == "build":
                return self._build_package(**kwargs)
            elif action == "publish":
                return self._publish_package(**kwargs)
            elif action == "lint":
                return self._lint_package(**kwargs)
            elif action == "structure":
                return self._analyze_structure(**kwargs)
            else:
                return {"error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Package builder action '{action}' failed: {e}")
            return {"error": str(e)}

    def _create_package(self, name: str, version: str = "0.1.0", 
                       author: str = "Automated RFP System", 
                       description: str = None, output_dir: str = ".",
                       include_docs: bool = True, include_ci: bool = True,
                       **kwargs) -> Dict[str, Any]:
        """Create a new Python package structure."""
        if not name:
            return {"error": "Package name is required for create action"}
        
        # Validate package name
        if not name.isidentifier() or not name.islower():
            return {"error": "Package name must be a valid Python identifier in lowercase"}
        
        package_dir = Path(output_dir) / name
        
        if package_dir.exists():
            return {"error": f"Package directory already exists: {package_dir}"}
        
        try:
            # Create package structure
            structure = self._create_package_structure(
                package_dir, name, version, author, description,
                include_docs, include_ci
            )
            
            return {
                "status": "success",
                "package_name": name,
                "package_dir": str(package_dir),
                "structure": structure,
                "message": f"Package '{name}' created successfully"
            }
            
        except Exception as e:
            return {"error": f"Failed to create package: {e}"}

    def _create_package_structure(self, package_dir: Path, name: str, 
                                 version: str, author: str, description: str,
                                 include_docs: bool, include_ci: bool) -> Dict[str, List[str]]:
        """Create the complete package directory structure."""
        structure = {"directories": [], "files": []}
        
        # Create main directories
        directories = [
            package_dir,
            package_dir / name,
            package_dir / "tests",
        ]
        
        if include_docs:
            directories.extend([
                package_dir / "docs",
                package_dir / "docs" / "source",
            ])
        
        if include_ci:
            directories.extend([
                package_dir / ".github",
                package_dir / ".github" / "workflows",
            ])
        
        # Create directories
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            structure["directories"].append(str(directory.relative_to(package_dir)))
        
        # Create files
        files_to_create = [
            ("setup.py", self._generate_setup_py(name, version, author, description)),
            ("pyproject.toml", self._generate_pyproject_toml(name, version, author, description)),
            ("requirements.txt", self._generate_requirements_txt()),
            ("requirements-dev.txt", self._generate_dev_requirements_txt()),
            ("README.md", self._generate_readme(name, description)),
            ("LICENSE", self._generate_license(author)),
            (".gitignore", self._generate_gitignore()),
            ("MANIFEST.in", self._generate_manifest()),
            (f"{name}/__init__.py", self._generate_init_py(version)),
            (f"{name}/main.py", self._generate_main_py(name)),
            ("tests/__init__.py", ""),
            ("tests/test_main.py", self._generate_test_main(name)),
            ("tests/conftest.py", self._generate_conftest()),
        ]
        
        if include_docs:
            files_to_create.extend([
                ("docs/conf.py", self._generate_sphinx_conf(name, author, version)),
                ("docs/index.rst", self._generate_sphinx_index(name, description)),
                ("docs/Makefile", self._generate_docs_makefile()),
                ("docs/requirements.txt", "sphinx\nsphinx-rtd-theme\n"),
            ])
        
        if include_ci:
            files_to_create.extend([
                (".github/workflows/ci.yml", self._generate_github_ci()),
                (".github/workflows/publish.yml", self._generate_github_publish()),
            ])
        
        # Write files
        for file_path, content in files_to_create:
            full_path = package_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding='utf-8')
            structure["files"].append(file_path)
        
        return structure

    def _run_tests(self, test_path: str = "tests/", **kwargs) -> Dict[str, Any]:
        """Run pytest with coverage reporting."""
        try:
            test_dir = Path(test_path)
            if not test_dir.exists():
                return {"error": f"Test directory not found: {test_path}"}
            
            # Run pytest with coverage
            cmd = [
                "python", "-m", "pytest",
                str(test_dir),
                "--cov=.",
                "--cov-report=term-missing",
                "--cov-report=json",
                "--cov-report=html",
                "-v"
            ]
            
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=test_dir.parent
            )
            
            # Parse coverage results
            coverage_data = self._parse_coverage_results(test_dir.parent)
            
            return {
                "status": "success" if result.returncode == 0 else "failed",
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "coverage": coverage_data,
                "test_path": str(test_dir)
            }
            
        except Exception as e:
            return {"error": f"Test execution failed: {e}"}

    def _build_package(self, **kwargs) -> Dict[str, Any]:
        """Build the package for distribution."""
        try:
            # Clean previous builds
            for build_dir in ["build", "dist", "*.egg-info"]:
                if Path(build_dir).exists():
                    if Path(build_dir).is_dir():
                        shutil.rmtree(build_dir)
                    else:
                        Path(build_dir).unlink()
            
            # Build source distribution and wheel
            cmd = ["python", "setup.py", "sdist", "bdist_wheel"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # List generated files
            dist_files = []
            if Path("dist").exists():
                dist_files = [str(f) for f in Path("dist").iterdir()]
            
            return {
                "status": "success" if result.returncode == 0 else "failed",
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "dist_files": dist_files
            }
            
        except Exception as e:
            return {"error": f"Package build failed: {e}"}

    def _publish_package(self, repository: str = "pypi", **kwargs) -> Dict[str, Any]:
        """Publish package to repository."""
        try:
            # Check if twine is available
            try:
                subprocess.run(["twine", "--version"], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                return {"error": "Twine is required for publishing. Install with: pip install twine"}
            
            # Upload to repository
            if repository == "test":
                cmd = ["twine", "upload", "--repository", "testpypi", "dist/*"]
            else:
                cmd = ["twine", "upload", "dist/*"]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            return {
                "status": "success" if result.returncode == 0 else "failed",
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "repository": repository
            }
            
        except Exception as e:
            return {"error": f"Package publishing failed: {e}"}

    def _lint_package(self, **kwargs) -> Dict[str, Any]:
        """Lint the package code."""
        try:
            # Run flake8, pylint, and black
            linting_results = {}
            
            # Flake8
            try:
                result = subprocess.run(
                    ["flake8", ".", "--count", "--statistics"],
                    capture_output=True, text=True
                )
                linting_results["flake8"] = {
                    "return_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            except FileNotFoundError:
                linting_results["flake8"] = {"error": "flake8 not installed"}
            
            # Black (check mode)
            try:
                result = subprocess.run(
                    ["black", ".", "--check", "--diff"],
                    capture_output=True, text=True
                )
                linting_results["black"] = {
                    "return_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            except FileNotFoundError:
                linting_results["black"] = {"error": "black not installed"}
            
            # isort (check mode)
            try:
                result = subprocess.run(
                    ["isort", ".", "--check-only", "--diff"],
                    capture_output=True, text=True
                )
                linting_results["isort"] = {
                    "return_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            except FileNotFoundError:
                linting_results["isort"] = {"error": "isort not installed"}
            
            return {
                "status": "success",
                "results": linting_results
            }
            
        except Exception as e:
            return {"error": f"Linting failed: {e}"}

    def _analyze_structure(self, **kwargs) -> Dict[str, Any]:
        """Analyze existing package structure."""
        try:
            cwd = Path.cwd()
            structure_analysis = {
                "has_setup_py": (cwd / "setup.py").exists(),
                "has_pyproject_toml": (cwd / "pyproject.toml").exists(),
                "has_requirements": (cwd / "requirements.txt").exists(),
                "has_tests": (cwd / "tests").exists() or (cwd / "test").exists(),
                "has_docs": (cwd / "docs").exists(),
                "has_ci": (cwd / ".github" / "workflows").exists(),
                "has_license": any((cwd / name).exists() for name in ["LICENSE", "LICENSE.txt", "LICENSE.md"]),
                "has_readme": any((cwd / name).exists() for name in ["README.md", "README.rst", "README.txt"]),
                "python_files": list(cwd.rglob("*.py")),
                "package_directories": []
            }
            
            # Find potential package directories
            for item in cwd.iterdir():
                if (item.is_dir() and 
                    (item / "__init__.py").exists() and
                    not item.name.startswith('.') and
                    item.name not in ['tests', 'test', 'docs', 'build', 'dist']):
                    structure_analysis["package_directories"].append(item.name)
            
            # Convert Path objects to strings for JSON serialization
            structure_analysis["python_files"] = [str(f) for f in structure_analysis["python_files"]]
            
            return {
                "status": "success",
                "structure": structure_analysis
            }
            
        except Exception as e:
            return {"error": f"Structure analysis failed: {e}"}

    def _parse_coverage_results(self, project_dir: Path) -> Dict[str, Any]:
        """Parse coverage results from JSON report."""
        coverage_file = project_dir / "coverage.json"
        if not coverage_file.exists():
            return {"error": "Coverage report not found"}
        
        try:
            import json
            with open(coverage_file) as f:
                coverage_data = json.load(f)
            
            return {
                "total_coverage": coverage_data.get("totals", {}).get("percent_covered", 0),
                "lines_covered": coverage_data.get("totals", {}).get("covered_lines", 0),
                "lines_total": coverage_data.get("totals", {}).get("num_statements", 0),
                "files": {
                    filename: {
                        "coverage": file_data.get("summary", {}).get("percent_covered", 0),
                        "missing_lines": file_data.get("missing_lines", [])
                    }
                    for filename, file_data in coverage_data.get("files", {}).items()
                }
            }
        except Exception as e:
            return {"error": f"Failed to parse coverage: {e}"}

    # Template generation methods
    def _generate_setup_py(self, name: str, version: str, author: str, description: str) -> str:
        """Generate setup.py content."""
        desc = description or f"A Python package: {name}"
        return f'''"""Setup configuration for {name}."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="{name}",
    version="{version}",
    author="{author}",
    author_email="contact@example.com",
    description="{desc}",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/yourusername/{name}",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={{
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "isort",
            "mypy",
        ],
        "docs": [
            "sphinx",
            "sphinx-rtd-theme",
        ],
    }},
    entry_points={{
        "console_scripts": [
            "{name}={name}.main:main",
        ],
    }},
)
'''

    def _generate_pyproject_toml(self, name: str, version: str, author: str, description: str) -> str:
        """Generate pyproject.toml content."""
        desc = description or f"A Python package: {name}"
        return f'''[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[project]
name = "{name}"
version = "{version}"
description = "{desc}"
readme = "README.md"
authors = [
    {{name = "{author}", email = "contact@example.com"}},
]
license = {{text = "MIT"}}
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]
requires-python = ">=3.8"
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=6.0",
    "pytest-cov",
    "black",
    "flake8",
    "isort",
    "mypy",
]
docs = [
    "sphinx",
    "sphinx-rtd-theme",
]

[project.scripts]
{name} = "{name}.main:main"

[project.urls]
Homepage = "https://github.com/yourusername/{name}"
Documentation = "https://github.com/yourusername/{name}#readme"
Repository = "https://github.com/yourusername/{name}.git"
"Bug Tracker" = "https://github.com/yourusername/{name}/issues"

[tool.setuptools.packages.find]
where = ["."]
include = ["{name}*"]

[tool.black]
line-length = 88
include = '\\.pyi?$'
extend-exclude = """
(
    dist
    | .eggs
    | .git
    | .mypy_cache
    | .pytest_cache
    | .venv
    | build
)
"""

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --cov={name} --cov-report=term-missing"

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
'''

    def _generate_requirements_txt(self) -> str:
        """Generate requirements.txt content."""
        return """# Production dependencies
# Add your project dependencies here
# Example:
# requests>=2.25.0
# pydantic>=1.8.0
"""

    def _generate_dev_requirements_txt(self) -> str:
        """Generate dev requirements.txt content."""
        return """# Development dependencies
pytest>=6.0
pytest-cov
black
flake8
isort
mypy
twine
build
"""

    def _generate_readme(self, name: str, description: str) -> str:
        """Generate README.md content."""
        desc = description or f"A Python package: {name}"
        return f'''# {name}

{desc}

## Installation

```bash
pip install {name}
```

## Quick Start

```python
from {name} import main

# Example usage
main.hello_world()
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/{name}.git
cd {name}

# Install in development mode
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
isort .
```

### Linting

```bash
flake8 .
mypy .
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
'''

    def _generate_license(self, author: str) -> str:
        """Generate MIT License content."""
        year = datetime.now().year
        return f'''MIT License

Copyright (c) {year} {author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

    def _generate_gitignore(self) -> str:
        """Generate .gitignore content."""
        return '''# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# celery beat schedule file
celerybeat-schedule

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
'''

    def _generate_manifest(self) -> str:
        """Generate MANIFEST.in content."""
        return '''include README.md
include LICENSE
include requirements.txt
include requirements-dev.txt
recursive-include docs *.rst *.py *.md
recursive-exclude * __pycache__
recursive-exclude * *.py[co]
'''

    def _generate_init_py(self, version: str) -> str:
        """Generate __init__.py content."""
        return f'''"""Package initialization."""

__version__ = "{version}"
__author__ = "Automated RFP System"
__email__ = "contact@example.com"

from .main import main, hello_world

__all__ = ["main", "hello_world", "__version__"]
'''

    def _generate_main_py(self, name: str) -> str:
        """Generate main.py content."""
        return f'''"""Main module for {name}."""

import logging

logger = logging.getLogger(__name__)


def hello_world(name: str = "World") -> str:
    """Return a greeting message.
    
    Args:
        name: Name to greet
        
    Returns:
        Greeting message
    """
    message = f"Hello, {{name}}! Welcome to {name}."
    logger.info(message)
    return message


def main() -> None:
    """Main entry point."""
    print(hello_world())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
'''

    def _generate_test_main(self, name: str) -> str:
        """Generate test_main.py content."""
        return f'''"""Tests for {name}.main module."""

import pytest
from {name}.main import hello_world, main


def test_hello_world_default():
    """Test hello_world with default parameter."""
    result = hello_world()
    assert "Hello, World!" in result
    assert "{name}" in result


def test_hello_world_custom_name():
    """Test hello_world with custom name."""
    result = hello_world("Alice")
    assert "Hello, Alice!" in result
    assert "{name}" in result


def test_main_runs_without_error():
    """Test that main function runs without error."""
    # This is a basic smoke test
    main()  # Should not raise any exceptions


@pytest.mark.parametrize("name,expected", [
    ("Bob", "Hello, Bob!"),
    ("", "Hello, !"),
    ("123", "Hello, 123!"),
])
def test_hello_world_parametrized(name, expected):
    """Test hello_world with various inputs."""
    result = hello_world(name)
    assert expected in result
'''

    def _generate_conftest(self) -> str:
        """Generate conftest.py content."""
        return '''"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {
        "test_string": "Hello, World!",
        "test_number": 42,
        "test_list": [1, 2, 3, 4, 5],
    }


@pytest.fixture(scope="session")
def setup_test_environment():
    """Set up test environment (runs once per test session)."""
    # Setup code here
    yield  # This is where the testing happens
    # Teardown code here
'''

    def _generate_sphinx_conf(self, name: str, author: str, version: str) -> str:
        """Generate Sphinx conf.py content."""
        return f'''"""Sphinx configuration."""

import os
import sys
sys.path.insert(0, os.path.abspath('..'))

# Project information
project = '{name}'
copyright = '2025, {author}'
author = '{author}'
version = '{version}'
release = '{version}'

# General configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# HTML output
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Intersphinx mapping
intersphinx_mapping = {{
    'python': ('https://docs.python.org/3', None),
}}

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
'''

    def _generate_sphinx_index(self, name: str, description: str) -> str:
        """Generate Sphinx index.rst content."""
        desc = description or f"A Python package: {name}"
        return f'''Welcome to {name}'s documentation!
{'=' * (len(name) + 31)}

{desc}

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   api
   contributing

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
'''

    def _generate_docs_makefile(self) -> str:
        """Generate docs Makefile content."""
        return '''# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD  ?= sphinx-build
SOURCEDIR    = .
BUILDDIR     = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
'''

    def _generate_github_ci(self) -> str:
        """Generate GitHub Actions CI workflow."""
        return '''name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10", "3.11"]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
    
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
    
    - name: Format check with black
      run: |
        black --check .
    
    - name: Import sort check with isort  
      run: |
        isort --check-only .
    
    - name: Type check with mypy
      run: |
        mypy .
      continue-on-error: true
    
    - name: Test with pytest
      run: |
        pytest --cov=. --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
'''

    def _generate_github_publish(self) -> str:
        """Generate GitHub Actions publish workflow."""
        return '''name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build package
      run: |
        python -m build
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: |
        twine upload dist/*
'''
