#!/usr/bin/env python3
"""
Working FastAPI application for Proposal Master System.

This is a simplified but functional API that demonstrates the core capabilities
including the working vector database integration.
"""

import sys
from pathlib import Path
import os
import asyncio
from typing import Dict, List, Any, Optional
import tempfile

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Import our working components
from src.core.vector_database import VectorDatabase, VectorIndexConfig, VectorDocument

# Pydantic models for API
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    min_similarity: float = 0.0

class SearchResponse(BaseModel):
    query: str
    results: List[Dict[str, Any]]
    total_results: int

class DocumentRequest(BaseModel):
    id: str
    content: str
    metadata: Dict[str, Any] = {}

class StatusResponse(BaseModel):
    status: str
    message: str
    details: Dict[str, Any] = {}

# Initialize FastAPI app
app = FastAPI(
    title="Proposal Master API",
    description="AI-Powered Proposal and RFP Response System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global vector database instance
vector_db: Optional[VectorDatabase] = None

async def get_vector_db() -> VectorDatabase:
    """Get or initialize the vector database"""
    global vector_db
    if vector_db is None:
        config = VectorIndexConfig()
        vector_db = VectorDatabase(config)
    return vector_db

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("🚀 Proposal Master API starting up...")
    await get_vector_db()
    print("✅ Vector database initialized")

@app.get("/", response_model=StatusResponse)
async def root():
    """Root endpoint with API information"""
    return StatusResponse(
        status="healthy",
        message="Proposal Master API is running",
        details={
            "version": "1.0.0",
            "docs": "/docs",
            "vector_search": "/api/v1/vector/search",
            "health": "/api/v1/health"
        }
    )

@app.get("/api/v1/health", response_model=StatusResponse)
async def health_check():
    """Health check endpoint"""
    db = await get_vector_db()
    stats = db.get_stats()
    
    return StatusResponse(
        status="healthy",
        message="All systems operational",
        details={
            "vector_db": {
                "total_documents": stats.get("total_documents", 0),
                "embedding_model": stats.get("embedding_model", "N/A"),
                "dimension": stats.get("dimension", 0)
            }
        }
    )

@app.post("/api/v1/vector/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """Search documents using semantic similarity"""
    try:
        db = await get_vector_db()
        results = await db.search(
            query=request.query,
            top_k=request.top_k,
            min_similarity=request.min_similarity
        )
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "id": result.document.id,
                "content": result.document.content,
                "similarity_score": result.similarity_score,
                "metadata": result.document.metadata,
                "rank": result.rank
            })
        
        return SearchResponse(
            query=request.query,
            results=formatted_results,
            total_results=len(formatted_results)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/api/v1/vector/documents", response_model=StatusResponse)
async def add_document(request: DocumentRequest):
    """Add a document to the vector database"""
    try:
        db = await get_vector_db()
        doc = VectorDocument(
            id=request.id,
            content=request.content,
            metadata=request.metadata
        )
        
        doc_id = await db.add_document(doc)
        
        return StatusResponse(
            status="success",
            message=f"Document added successfully",
            details={"document_id": doc_id}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add document: {str(e)}")

@app.get("/api/v1/vector/stats", response_model=Dict[str, Any])
async def get_vector_stats():
    """Get vector database statistics"""
    try:
        db = await get_vector_db()
        stats = db.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.get("/api/v1/demo/search")
async def demo_search():
    """Demo endpoint that shows pre-loaded search results"""
    try:
        # Add some demo documents if database is empty
        db = await get_vector_db()
        stats = db.get_stats()
        
        if stats.get("total_documents", 0) < 5:
            demo_docs = [
                VectorDocument(id="demo_1", content="FastAPI is a modern web framework for building APIs with Python", metadata={"type": "technology", "category": "web-framework"}),
                VectorDocument(id="demo_2", content="Vector databases enable semantic search and similarity matching for AI applications", metadata={"type": "database", "category": "ai"}),
                VectorDocument(id="demo_3", content="Proposal management systems help automate RFP responses and win more business", metadata={"type": "business", "category": "automation"}),
                VectorDocument(id="demo_4", content="Document analysis using NLP extracts key requirements from complex business documents", metadata={"type": "nlp", "category": "analysis"}),
                VectorDocument(id="demo_5", content="Competitive intelligence research helps companies position their proposals effectively", metadata={"type": "research", "category": "intelligence"}),
            ]
            
            for doc in demo_docs:
                await db.add_document(doc)
        
        # Perform demo searches
        demo_queries = [
            "API development framework",
            "business proposal automation", 
            "document analysis NLP",
            "competitive research"
        ]
        
        demo_results = {}
        for query in demo_queries:
            results = await db.search(query, top_k=2)
            demo_results[query] = [
                {
                    "id": r.document.id,
                    "content": r.document.content[:80] + "...",
                    "score": round(r.similarity_score, 3),
                    "type": r.document.metadata.get("type", "N/A")
                }
                for r in results
            ]
        
        return {
            "message": "Vector database demo search results",
            "total_documents": stats.get("total_documents", 0),
            "searches": demo_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo failed: {str(e)}")

def main():
    """Start the API server"""
    port = int(os.getenv("API_PORT", "8000"))
    print(f"🌟 Starting Proposal Master API on port {port}")
    print(f"📚 Documentation: http://localhost:{port}/docs")
    print(f"🔍 Demo: http://localhost:{port}/api/v1/demo/search")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        reload=False  # Disable reload to avoid import issues
    )

if __name__ == "__main__":
    main()
