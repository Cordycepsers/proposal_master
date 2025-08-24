"""
Document management and upload routes.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from pathlib import Path
import uuid
from datetime import datetime
import logging
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ...core.document_processor import DocumentProcessor
from ...models.core import Document, DocumentStatus
from ...config.database import get_db_session

logger = logging.getLogger(__name__)

router = APIRouter()

# Configuration
UPLOAD_DIR = Path("data/documents/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

class DocumentMetadata(BaseModel):
    """Document metadata model."""
    id: str
    filename: str
    original_filename: str
    file_size: int
    file_type: str
    upload_timestamp: datetime
    processing_status: DocumentStatus
    content_preview: Optional[str] = None
    page_count: Optional[int] = None
    word_count: Optional[int] = None

    class Config:
        from_attributes = True

class DocumentUploadResponse(BaseModel):
    """Document upload response model."""
    document_id: str
    message: str
    metadata: DocumentMetadata

class DocumentListResponse(BaseModel):
    """Document list response model."""
    documents: List[DocumentMetadata]
    total_count: int

class ProcessingResult(BaseModel):
    """Document processing result model."""
    document_id: str
    status: str
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    process_immediately: bool = False,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Upload a document for processing.
    
    Args:
        file: The document file to upload
        process_immediately: Whether to process the document immediately
        db: Database session
        
    Returns:
        DocumentUploadResponse: Upload result with document metadata
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file_ext} not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Check file size
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024):.1f}MB"
            )
        
        # Generate unique document ID and filename
        document_id = str(uuid.uuid4())
        safe_filename = f"{document_id}{file_ext}"
        file_path = UPLOAD_DIR / safe_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        # Create database record
        new_document = Document(
            id=document_id,
            filename=safe_filename,
            original_filename=file.filename,
            file_size=len(content),
            file_type=file_ext,
            processing_status=DocumentStatus.PROCESSING if process_immediately else DocumentStatus.UPLOADED
        )
        db.add(new_document)
        await db.commit()
        await db.refresh(new_document)

        # Create metadata for response
        metadata = DocumentMetadata.from_orm(new_document)
        
        # Schedule background processing if requested
        if process_immediately:
            background_tasks.add_task(process_document_background, document_id, str(file_path))
        
        logger.info(f"Document uploaded: {document_id} ({file.filename})")
        
        return DocumentUploadResponse(
            document_id=document_id,
            message="Document uploaded successfully",
            metadata=metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    limit: int = 100,
    offset: int = 0,
    file_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db_session)
):
    """
    List uploaded documents.
    
    Args:
        limit: Maximum number of documents to return
        offset: Number of documents to skip
        file_type: Filter by file type (e.g., '.pdf', '.docx')
        db: Database session
        
    Returns:
        DocumentListResponse: List of documents with metadata
    """
    try:
        query = select(Document)
        if file_type:
            query = query.where(Document.file_type == file_type)
        
        total_count_query = select(func.count()).select_from(query.subquery())
        total_count = (await db.execute(total_count_query)).scalar_one()

        query = query.offset(offset).limit(limit).order_by(Document.upload_timestamp.desc())
        
        result = await db.execute(query)
        documents = result.scalars().all()
        
        return DocumentListResponse(
            documents=[DocumentMetadata.from_orm(doc) for doc in documents],
            total_count=total_count
        )
        
    except Exception as e:
        logger.error(f"Failed to list documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@router.get("/{document_id}", response_model=DocumentMetadata)
async def get_document_metadata(document_id: str, db: AsyncSession = Depends(get_db_session)):
    """
    Get metadata for a specific document.
    
    Args:
        document_id: The document identifier
        db: Database session
        
    Returns:
        DocumentMetadata: Document metadata
    """
    try:
        document = await db.get(Document, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return DocumentMetadata.from_orm(document)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get metadata: {str(e)}")

@router.get("/{document_id}/download")
async def download_document(document_id: str, db: AsyncSession = Depends(get_db_session)):
    """
    Download a document file.
    
    Args:
        document_id: The document identifier
        db: Database session
        
    Returns:
        FileResponse: The document file
    """
    try:
        document = await db.get(Document, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        file_path = UPLOAD_DIR / document.filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Document file not found")
        
        return FileResponse(
            path=str(file_path),
            filename=document.original_filename,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@router.post("/{document_id}/process", response_model=ProcessingResult)
async def process_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    force: bool = False,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Process a document to extract content and metadata.
    
    Args:
        document_id: The document identifier
        force: Force reprocessing even if already processed
        db: Database session
        
    Returns:
        ProcessingResult: Processing result
    """
    try:
        document = await db.get(Document, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        if document.processing_status == DocumentStatus.COMPLETED and not force:
            return ProcessingResult(
                document_id=document_id,
                status="already_processed",
                content=document.processing_result.get('content'),
                metadata=document.processing_result.get('metadata')
            )

        file_path = UPLOAD_DIR / document.filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Document file not found")
        
        # Process in background
        background_tasks.add_task(process_document_background, document_id, str(file_path))
        
        return ProcessingResult(
            document_id=document_id,
            status="processing",
            content=None,
            metadata=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@router.delete("/{document_id}")
async def delete_document(document_id: str, db: AsyncSession = Depends(get_db_session)):
    """
    Delete a document and its associated data.
    
    Args:
        document_id: The document identifier
        db: Database session
        
    Returns:
        dict: Deletion confirmation
    """
    try:
        document = await db.get(Document, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Delete file from filesystem
        file_path = UPLOAD_DIR / document.filename
        if file_path.exists():
            file_path.unlink()

        # Delete from vector database
        from ...core.rag_system import RAGSystem
        rag_system = RAGSystem()
        await rag_system.remove_document(document_id)
        
        # Delete from database
        await db.delete(document)
        await db.commit()
        
        logger.info(f"Document deleted: {document_id}")
        
        return {
            "message": "Document deleted successfully",
            "document_id": document_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")

# Background task functions
async def process_document_background(document_id: str, file_path: str):
    """Background task to process a document."""
    async with get_db_session() as db:
        try:
            logger.info(f"Starting background processing for document: {document_id}")

            # Initialize document processor
            processor = DocumentProcessor()

            # Process document
            result = processor.process_document(Path(file_path))

            # Store processing results in the database
            document = await db.get(Document, document_id)
            if document:
                document.processing_status = DocumentStatus.COMPLETED
                document.processing_result = result
                document.content_preview = result.get('content', '')[:500]
                document.word_count = len(result.get('content', '').split())
                await db.commit()

            # Add document to RAG system
            from ...core.rag_system import RAGSystem
            rag_system = RAGSystem()
            await rag_system.add_document(document_id, result.get('content', ''), result.get('metadata', {}))

            logger.info(f"Document processing completed: {document_id}")

        except Exception as e:
            logger.error(f"Background processing failed for {document_id}: {str(e)}")
            # Update processing status to "failed"
            document = await db.get(Document, document_id)
            if document:
                document.processing_status = DocumentStatus.FAILED
                document.processing_result = {"error": str(e)}
                await db.commit()
