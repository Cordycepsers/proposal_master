#!/usr/bin/env python3
"""
Simple API server startup script for testing.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    import uvicorn
    
    # Create minimal FastAPI app
    app = FastAPI(
        title="Proposal Master API",
        description="Proposal Master System API",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        return {"message": "Proposal Master API", "status": "running"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "api": "running"}
    
    if __name__ == "__main__":
        port = int(os.getenv('API_PORT', 8000))
        print(f"Starting simple API server on port {port}")
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
        
except Exception as e:
    print(f"Error starting API: {e}")
    import traceback
    traceback.print_exc()
