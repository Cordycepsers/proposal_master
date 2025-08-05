"""
Test Suite for Proposal Master System

This package contains comprehensive tests for all components of the 
Proposal Master AI-powered proposal management system.

Test Categories:
- Document Processing: PDF, DOCX, TXT, MD file handling
- AI Content Generation: Proposal writing and optimization
- Research Module: Web research and competitive intelligence
- Anti-Scraping: Request handling and protection mechanisms
- Proposal Workflow: End-to-end proposal lifecycle
- Collaboration: Multi-user and team features
- Export Functionality: Document generation and formatting
"""

import os
import sys

# Add project root to Python path for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

__version__ = "1.0.0"
__author__ = "Proposal Master Team"
