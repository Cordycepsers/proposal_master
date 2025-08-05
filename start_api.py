#!/usr/bin/env python3
"""
API Server Startup Script

This script starts the Proposal Master API server with proper configuration
and environment setup.
"""

import os
import sys
from pathlib import Path
import uvicorn
import logging

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.logging_config import setup_logging

def main():
    """Start the API server."""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Server configuration
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "true").lower() == "true"
    log_level = os.getenv("API_LOG_LEVEL", "info").lower()
    
    logger.info(f"Starting Proposal Master API server on {host}:{port}")
    logger.info(f"Reload: {reload}, Log Level: {log_level}")
    
    # Start the server
    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
        access_log=True
    )

if __name__ == "__main__":
    main()
