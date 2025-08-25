#!/usr/bin/env python3
"""
Simple development API for Proposal Master
Works without vector database dependencies for frontend development
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import uvicorn
import json
from datetime import datetime
import uuid

# Create the FastAPI app
app = FastAPI(
    title="Proposal Master API - Development",
    description="Development API for Proposal Master frontend",
    version="1.0.0-dev"
)

# Configure CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative React dev server
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data stores
documents = []
proposals = []

# Models
class Document:
    def __init__(self, filename: str, content_type: str, size: int):
        self.id = str(uuid.uuid4())
        self.filename = filename
        self.content_type = content_type
        self.size = size
        self.upload_date = datetime.now().isoformat()
        self.status = "processed"
        self.analysis = {
            "key_requirements": ["Mock requirement 1", "Mock requirement 2"],
            "risk_level": "medium",
            "estimated_value": 150000
        }

class Proposal:
    def __init__(self, title: str, client: str, value: float):
        self.id = str(uuid.uuid4())
        self.title = title
        self.client = client
        self.value = value
        self.probability = 75.0
        self.status = "draft"
        self.created_date = datetime.now().isoformat()
        self.deadline = "2024-02-15"

# API Routes

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "proposal-master-dev-api",
        "version": "1.0.0-dev",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Proposal Master Development API",
        "docs": "/docs",
        "health": "/health"
    }

# Document endpoints
@app.get("/documents")
async def list_documents():
    """List all documents"""
    return {
        "documents": [doc.__dict__ for doc in documents],
        "total": len(documents)
    }

@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a document"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Create mock document
    doc = Document(
        filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
        size=len(await file.read())
    )
    documents.append(doc)
    
    return {
        "message": "File uploaded successfully",
        "document": doc.__dict__
    }

@app.post("/vector/search")
async def search_documents(query: dict):
    """Search documents (mock implementation)"""
    search_query = query.get("query", "")
    
    # Mock search results
    results = []
    for doc in documents:
        if search_query.lower() in doc.filename.lower():
            results.append({
                "document": doc.__dict__,
                "score": 0.85,
                "highlights": [f"Found '{search_query}' in document"]
            })
    
    return {
        "results": results,
        "query": search_query,
        "total": len(results)
    }

# Proposal endpoints
@app.get("/proposals")
async def list_proposals():
    """List all proposals"""
    return {
        "proposals": [prop.__dict__ for prop in proposals],
        "total": len(proposals)
    }

@app.post("/proposals")
async def create_proposal(proposal_data: dict):
    """Create a new proposal"""
    prop = Proposal(
        title=proposal_data.get("title", "New Proposal"),
        client=proposal_data.get("client", "Unknown Client"),
        value=proposal_data.get("value", 100000)
    )
    proposals.append(prop)
    
    return {
        "message": "Proposal created successfully",
        "proposal": prop.__dict__
    }

@app.get("/proposals/{proposal_id}")
async def get_proposal(proposal_id: str):
    """Get a specific proposal"""
    for prop in proposals:
        if prop.id == proposal_id:
            return {"proposal": prop.__dict__}
    
    raise HTTPException(status_code=404, detail="Proposal not found")

@app.put("/proposals/{proposal_id}")
async def update_proposal(proposal_id: str, proposal_data: dict):
    """Update a proposal"""
    for prop in proposals:
        if prop.id == proposal_id:
            if "title" in proposal_data:
                prop.title = proposal_data["title"]
            if "client" in proposal_data:
                prop.client = proposal_data["client"]
            if "value" in proposal_data:
                prop.value = proposal_data["value"]
            if "probability" in proposal_data:
                prop.probability = proposal_data["probability"]
            if "status" in proposal_data:
                prop.status = proposal_data["status"]
            
            return {
                "message": "Proposal updated successfully",
                "proposal": prop.__dict__
            }
    
    raise HTTPException(status_code=404, detail="Proposal not found")

# Research endpoint
@app.post("/research/conduct")
async def conduct_research(research_data: dict):
    """Conduct research (mock implementation)"""
    topic = research_data.get("topic", "Unknown topic")
    
    return {
        "topic": topic,
        "findings": [
            {
                "source": "Mock Industry Report",
                "summary": f"Market analysis shows growing demand for {topic}",
                "confidence": 0.85
            },
            {
                "source": "Competitor Analysis",
                "summary": f"Three main competitors identified in {topic} space",
                "confidence": 0.92
            }
        ],
        "recommendations": [
            f"Consider focusing on {topic} differentiation",
            "Competitive pricing strategy recommended"
        ]
    }

# System info endpoint
@app.get("/system/info")
async def system_info():
    """Get system information"""
    return {
        "documents_count": len(documents),
        "proposals_count": len(proposals),
        "uptime": "mock_uptime",
        "version": "1.0.0-dev",
        "environment": "development"
    }

if __name__ == "__main__":
    print("🚀 Starting Proposal Master Development API")
    print("📁 This is a simplified version for frontend development")
    print("🌐 API will be available at: http://localhost:8000")
    print("📚 Documentation at: http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
