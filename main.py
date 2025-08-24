#!/usr/bin/env python3
"""
Proposal Master - AI-Powered Proposal Management System

This is the main entry point for the Proposal Master system.
"""

import sys
import os
import asyncio
import logging
from datetime import datetime
import argparse
import json

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.orchestrator_agent import OrchestratorAgent
from config.settings import settings

def setup_logging():
    """Setup logging configuration"""
    log_file = settings.LOG_FILE
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

async def main():
    """Main entry point for the smart proposal system"""
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    parser = argparse.ArgumentParser(description="Proposal Master - AI-Powered Proposal Management System")
    parser.add_argument("file_path", help="The path to the RFP document to process.")
    args = parser.parse_args()

    try:
        logger.info(f"System: {settings.SYSTEM_NAME}")
        logger.info(f"Version: {settings.VERSION}")
        logger.info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Initialize orchestrator agent
        orchestrator = OrchestratorAgent()
        logger.info("Orchestrator agent initialized")

        # Process the document through the orchestrator
        result = await orchestrator.process(args.file_path)
        
        if result["status"] == "success":
            logger.info("Process completed successfully!")
            print(json.dumps(result, indent=2))
        else:
            logger.error(f"Process failed: {result.get('message')}")

    except Exception as e:
        logger.error(f"System error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
