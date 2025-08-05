"""
Vector Database API Routes

This module provides REST API endpoints for vector database operations,
including semantic search, document indexing, and similarity analysis.
"""

from typing import List, Dict, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.database import get_db
from src.services.vector_integration import VectorIntegrationService, create_vector_integration_service
from src.models.core import TenderOpportunity, Proposal, WonBid, ProjectDocumentation

router = APIRouter(prefix="/vector", tags=["vector-database"])

# Pydantic models for API
class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query text")
    top_k: int = Field(10, ge=1, le=100, description="Number of results to return")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters to apply")

class SearchResponse(BaseModel):
    query: str
    results_count: int
    execution_time_ms: float
    results: List[Dict[str, Any]]

class TenderRecommendationResponse(BaseModel):
    tender_id: int
    similar_won_bids: int
    winning_patterns: List[Dict[str, Any]]
    relevant_documentation: List[Dict[str, Any]]
    recommendations: List[str]

class IndexingResponse(BaseModel):
    success: bool
    indexed_documents: int
    document_ids: List[str]
    message: str

class DatabaseStatsResponse(BaseModel):
    total_documents: int
    total_vectors: int
    dimension: int
    index_type: str
    embedding_model: str
    is_initialized: bool

# Dependency to get vector integration service
def get_vector_service() -> VectorIntegrationService:
    """Get vector integration service instance"""
    # In production, this should be a singleton or dependency injection
    return create_vector_integration_service()

@router.get("/stats", response_model=DatabaseStatsResponse)
async def get_vector_database_stats(
    vector_service: VectorIntegrationService = Depends(get_vector_service)
):
    """Get vector database statistics"""
    try:
        stats = vector_service.vector_db.get_stats()
        return DatabaseStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.post("/search/tenders", response_model=SearchResponse)
async def search_tenders(
    request: SearchRequest,
    vector_service: VectorIntegrationService = Depends(get_vector_service)
):
    """Search for similar tender opportunities using semantic search"""
    import time
    start_time = time.time()
    
    try:
        results = await vector_service.semantic_search_tenders(
            query=request.query,
            top_k=request.top_k,
            filters=request.filters
        )
        
        # Format results
        formatted_results = []
        for tender, similarity_score in results:
            formatted_results.append({
                "id": tender.id,
                "title": tender.title,
                "organization": tender.organization,
                "category": tender.category,
                "status": tender.status.value,
                "deadline": tender.deadline.isoformat() if tender.deadline else None,
                "budget_range": {
                    "min": float(tender.budget_min) if tender.budget_min else None,
                    "max": float(tender.budget_max) if tender.budget_max else None
                },
                "similarity_score": similarity_score,
                "country": tender.country,
                "region": tender.region
            })
        
        execution_time = (time.time() - start_time) * 1000
        
        return SearchResponse(
            query=request.query,
            results_count=len(formatted_results),
            execution_time_ms=execution_time,
            results=formatted_results
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/search/won-bids", response_model=SearchResponse)
async def search_won_bids(
    request: SearchRequest,
    vector_service: VectorIntegrationService = Depends(get_vector_service)
):
    """Search for similar won bids for pattern analysis"""
    import time
    start_time = time.time()
    
    try:
        results = await vector_service.find_similar_won_bids(
            query=request.query,
            top_k=request.top_k
        )
        
        # Format results
        formatted_results = []
        for won_bid, similarity_score in results:
            formatted_results.append({
                "id": won_bid.id,
                "project_title": won_bid.project_title,
                "client_organization": won_bid.client_organization,
                "project_value": float(won_bid.project_value) if won_bid.project_value else None,
                "contract_duration": won_bid.contract_duration,
                "success_score": float(won_bid.success_score) if won_bid.success_score else None,
                "similarity_score": similarity_score,
                "winning_factors": won_bid.winning_factors,
                "contract_start_date": won_bid.contract_start_date.isoformat() if won_bid.contract_start_date else None
            })
        
        execution_time = (time.time() - start_time) * 1000
        
        return SearchResponse(
            query=request.query,
            results_count=len(formatted_results),
            execution_time_ms=execution_time,
            results=formatted_results
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Won bid search failed: {str(e)}")

@router.post("/search/documentation", response_model=SearchResponse)
async def search_project_documentation(
    request: SearchRequest,
    doc_type: Optional[str] = Query(None, description="Filter by document type"),
    organization: Optional[str] = Query(None, description="Filter by organization"),
    vector_service: VectorIntegrationService = Depends(get_vector_service)
):
    """Search project documentation using semantic similarity"""
    import time
    start_time = time.time()
    
    try:
        results = await vector_service.search_project_documentation(
            query=request.query,
            top_k=request.top_k,
            doc_type=doc_type,
            organization=organization
        )
        
        # Format results
        formatted_results = []
        for project_doc, similarity_score in results:
            formatted_results.append({
                "id": project_doc.id,
                "title": project_doc.title,
                "document_type": project_doc.document_type,
                "organization": project_doc.organization,
                "region": project_doc.region,
                "sector": project_doc.sector,
                "summary": project_doc.summary,
                "relevance_score": float(project_doc.relevance_score) if project_doc.relevance_score else None,
                "similarity_score": similarity_score,
                "document_date": project_doc.document_date.isoformat() if project_doc.document_date else None,
                "tags": project_doc.tags
            })
        
        execution_time = (time.time() - start_time) * 1000
        
        return SearchResponse(
            query=request.query,
            results_count=len(formatted_results),
            execution_time_ms=execution_time,
            results=formatted_results
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Documentation search failed: {str(e)}")

@router.get("/recommendations/tender/{tender_id}", response_model=TenderRecommendationResponse)
async def get_tender_recommendations(
    tender_id: int,
    top_k: int = Query(5, ge=1, le=20, description="Number of similar items to analyze"),
    vector_service: VectorIntegrationService = Depends(get_vector_service)
):
    """Get comprehensive recommendations for a tender based on historical patterns"""
    try:
        recommendations = await vector_service.get_recommendations_for_tender(
            tender_id=tender_id,
            top_k=top_k
        )
        
        return TenderRecommendationResponse(**recommendations)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")

@router.post("/index/tender/{tender_id}", response_model=IndexingResponse)
async def index_tender(
    tender_id: int,
    db: AsyncSession = Depends(get_db),
    vector_service: VectorIntegrationService = Depends(get_vector_service)
):
    """Index a specific tender opportunity in the vector database"""
    try:
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        # Get tender with requirements
        stmt = select(TenderOpportunity).options(
            selectinload(TenderOpportunity.requirements)
        ).where(TenderOpportunity.id == tender_id)
        result = await db.execute(stmt)
        tender = result.scalar_one_or_none()
        
        if not tender:
            raise HTTPException(status_code=404, detail=f"Tender {tender_id} not found")
        
        # Index the tender
        document_ids = await vector_service.index_tender_opportunity(tender)
        
        return IndexingResponse(
            success=True,
            indexed_documents=len(document_ids),
            document_ids=document_ids,
            message=f"Successfully indexed tender {tender_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")

@router.post("/index/proposal/{proposal_id}", response_model=IndexingResponse)
async def index_proposal(
    proposal_id: int,
    db: AsyncSession = Depends(get_db),
    vector_service: VectorIntegrationService = Depends(get_vector_service)
):
    """Index a specific proposal in the vector database"""
    try:
        from sqlalchemy import select
        
        # Get proposal
        stmt = select(Proposal).where(Proposal.id == proposal_id)
        result = await db.execute(stmt)
        proposal = result.scalar_one_or_none()
        
        if not proposal:
            raise HTTPException(status_code=404, detail=f"Proposal {proposal_id} not found")
        
        # Index the proposal
        document_ids = await vector_service.index_proposal(proposal)
        
        return IndexingResponse(
            success=True,
            indexed_documents=len(document_ids),
            document_ids=document_ids,
            message=f"Successfully indexed proposal {proposal_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")

@router.post("/index/won-bid/{won_bid_id}", response_model=IndexingResponse)
async def index_won_bid(
    won_bid_id: int,
    db: AsyncSession = Depends(get_db),
    vector_service: VectorIntegrationService = Depends(get_vector_service)
):
    """Index a specific won bid in the vector database"""
    try:
        from sqlalchemy import select
        
        # Get won bid
        stmt = select(WonBid).where(WonBid.id == won_bid_id)
        result = await db.execute(stmt)
        won_bid = result.scalar_one_or_none()
        
        if not won_bid:
            raise HTTPException(status_code=404, detail=f"Won bid {won_bid_id} not found")
        
        # Index the won bid
        document_ids = await vector_service.index_won_bid(won_bid)
        
        return IndexingResponse(
            success=True,
            indexed_documents=len(document_ids),
            document_ids=document_ids,
            message=f"Successfully indexed won bid {won_bid_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")

@router.post("/index/project-doc/{doc_id}", response_model=IndexingResponse)
async def index_project_documentation(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    vector_service: VectorIntegrationService = Depends(get_vector_service)
):
    """Index a specific project documentation in the vector database"""
    try:
        from sqlalchemy import select
        
        # Get project documentation
        stmt = select(ProjectDocumentation).where(ProjectDocumentation.id == doc_id)
        result = await db.execute(stmt)
        project_doc = result.scalar_one_or_none()
        
        if not project_doc:
            raise HTTPException(status_code=404, detail=f"Project documentation {doc_id} not found")
        
        # Index the document
        document_ids = await vector_service.index_project_documentation(project_doc)
        
        return IndexingResponse(
            success=True,
            indexed_documents=len(document_ids),
            document_ids=document_ids,
            message=f"Successfully indexed project documentation {doc_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")

@router.post("/reindex/all")
async def reindex_all_documents(
    background_tasks: BackgroundTasks,
    batch_size: int = Query(50, ge=1, le=200, description="Batch size for processing"),
    vector_service: VectorIntegrationService = Depends(get_vector_service)
):
    """Reindex all documents in the database (runs in background)"""
    try:
        # Add background task for bulk reindexing
        background_tasks.add_task(
            vector_service.bulk_reindex,
            batch_size=batch_size
        )
        
        return {
            "message": "Bulk reindexing started in background",
            "batch_size": batch_size,
            "status": "started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start reindexing: {str(e)}")

@router.post("/rebuild-index")
async def rebuild_vector_index(
    vector_service: VectorIntegrationService = Depends(get_vector_service)
):
    """Rebuild the entire vector index (useful after deletions)"""
    try:
        await vector_service.vector_db.rebuild_index()
        
        return {
            "message": "Vector index rebuilt successfully",
            "status": "completed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to rebuild index: {str(e)}")

@router.delete("/document/{document_id}")
async def delete_vector_document(
    document_id: str,
    vector_service: VectorIntegrationService = Depends(get_vector_service)
):
    """Delete a document from the vector database"""
    try:
        success = await vector_service.vector_db.delete_document(document_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
        
        return {
            "message": f"Document {document_id} deleted successfully",
            "status": "deleted"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

@router.get("/document/{document_id}")
async def get_vector_document(
    document_id: str,
    vector_service: VectorIntegrationService = Depends(get_vector_service)
):
    """Get a document from the vector database"""
    try:
        document = vector_service.vector_db.get_document(document_id)
        
        if not document:
            raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
        
        return {
            "id": document.id,
            "content": document.content,
            "metadata": document.metadata,
            "source": document.source,
            "created_at": document.created_at.isoformat(),
            "updated_at": document.updated_at.isoformat(),
            "chunk_index": document.chunk_index,
            "parent_document_id": document.parent_document_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get document: {str(e)}")

@router.get("/documents")
async def list_vector_documents(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of documents to return"),
    offset: int = Query(0, ge=0, description="Number of documents to skip"),
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    source: Optional[str] = Query(None, description="Filter by document source"),
    vector_service: VectorIntegrationService = Depends(get_vector_service)
):
    """List documents in the vector database with pagination and filtering"""
    try:
        # Build filters
        filters = {}
        if document_type:
            filters['type'] = document_type
        if source:
            filters['source'] = source
        
        documents = vector_service.vector_db.list_documents(
            limit=limit,
            offset=offset,
            filters=filters if filters else None
        )
        
        # Format response
        formatted_docs = []
        for doc in documents:
            formatted_docs.append({
                "id": doc.id,
                "content_preview": doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
                "metadata": doc.metadata,
                "source": doc.source,
                "created_at": doc.created_at.isoformat(),
                "updated_at": doc.updated_at.isoformat(),
                "chunk_index": doc.chunk_index,
                "parent_document_id": doc.parent_document_id
            })
        
        return {
            "documents": formatted_docs,
            "count": len(formatted_docs),
            "limit": limit,
            "offset": offset,
            "filters": filters
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")
