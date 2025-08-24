"""
Main FastAPI application for Proposal Master System.

This module sets up the FastAPI application with all routes, middleware,
and configuration for the Proposal Master API server.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any
import uvicorn
from pathlib import Path
import sys

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from .routes import (
    documents,
    analysis,
    requirements,
    risks,
    proposals,
    clients,
    research,
    health,
    vector,
    feedback,
    reporting
)

# Initialize logger
logger = logging.getLogger(__name__)
from ..utils.logging_config import setup_logging

# Setup logging
logger = setup_logging()

# Create FastAPI app
app = FastAPI(
    title="Proposal Master API",
    description="AI-powered proposal management and document analysis system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["Analysis"])
app.include_router(requirements.router, prefix="/api/v1/requirements", tags=["Requirements"])
app.include_router(risks.router, prefix="/api/v1/risks", tags=["Risk Assessment"])
app.include_router(proposals.router, prefix="/api/v1/proposals", tags=["Proposals"])
app.include_router(clients.router, prefix="/api/v1/clients", tags=["Client Management"])
app.include_router(research.router, prefix="/api/v1/research", tags=["Research"])
app.include_router(vector.router, prefix="/api/v1", tags=["Vector Database"])
app.include_router(feedback.router, prefix="/api/v1/feedback", tags=["Feedback"])
app.include_router(reporting.router, prefix="/api/v1/reporting", tags=["Reporting"])

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Proposal Master API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/api/v1/health"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Proposal Master API starting up...")
    # Initialize any necessary services here

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Proposal Master API shutting down...")
    # Clean up resources here

if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
