#!/usr/bin/env python3
"""
Development server for Proposal Master API
"""

import uvicorn
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

if __name__ == "__main__":
    # Try to use the working API first, fall back to main API
    try:
        from working_api import app
        print("Starting with working_api.py...")
    except ImportError:
        try:
            from src.api.main import app
            print("Starting with src/api/main.py...")
        except ImportError:
            print("Error: Could not import API application")
            sys.exit(1)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["src", "."],
        log_level="info"
    )
