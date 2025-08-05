"""
Document management and upload routes.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import shutil
from pathlib import Path
import uuid
from datetime import datetime
import logging
import sys

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ...core.document_processor import DocumentProcessor

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
    upload_timestamp: str
    processing_status: str
    content_preview: Optional[str] = None
    page_count: Optional[int] = None
    word_count: Optional[int] = None

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
    process_immediately: bool = False
):
    """
    Upload a document for processing.
    
    Args:
        file: The document file to upload
        process_immediately: Whether to process the document immediately
        
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
        safe_filename = f"{document_id}_{file.filename}"
        file_path = UPLOAD_DIR / safe_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        # Create metadata
        metadata = DocumentMetadata(
            id=document_id,
            filename=safe_filename,
            original_filename=file.filename,
            file_size=len(content),
            file_type=file_ext,
            upload_timestamp=datetime.now().isoformat(),
            processing_status="uploaded"
        )
        
        # Schedule background processing if requested
        if process_immediately:
            background_tasks.add_task(process_document_background, document_id, str(file_path))
            metadata.processing_status = "processing"
        
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
    file_type: Optional[str] = None
):
    """
    List uploaded documents.
    
    Args:
        limit: Maximum number of documents to return
        offset: Number of documents to skip
        file_type: Filter by file type (e.g., '.pdf', '.docx')
        
    Returns:
        DocumentListResponse: List of documents with metadata
    """
    try:
        documents = []
        
        # Get all files in upload directory
        for file_path in UPLOAD_DIR.iterdir():
            if file_path.is_file():
                # Extract document ID from filename
                try:
                    document_id = file_path.name.split('_')[0]
                    file_ext = file_path.suffix.lower()
                    
                    # Apply file type filter
                    if file_type and file_ext != file_type.lower():
                        continue
                    
                    # Get file stats
                    stat = file_path.stat()
                    
                    metadata = DocumentMetadata(
                        id=document_id,
                        filename=file_path.name,
                        original_filename=file_path.name.replace(f"{document_id}_", ""),
                        file_size=stat.st_size,
                        file_type=file_ext,
                        upload_timestamp=datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        processing_status="stored"
                    )
                    
                    documents.append(metadata)
                    
                except (IndexError, ValueError):
                    continue
        
        # Sort by upload timestamp (newest first)
        documents.sort(key=lambda x: x.upload_timestamp, reverse=True)
        
        # Apply pagination
        total_count = len(documents)
        documents = documents[offset:offset + limit]
        
        return DocumentListResponse(
            documents=documents,
            total_count=total_count
        )
        
    except Exception as e:
        logger.error(f"Failed to list documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@router.get("/{document_id}", response_model=DocumentMetadata)
async def get_document_metadata(document_id: str):
    """
    Get metadata for a specific document.
    
    Args:
        document_id: The document identifier
        
    Returns:
        DocumentMetadata: Document metadata
    """
    try:
        # Find document file
        file_path = None
        for path in UPLOAD_DIR.iterdir():
            if path.name.startswith(f"{document_id}_"):
                file_path = path
                break
        
        if not file_path or not file_path.exists():
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get file stats
        stat = file_path.stat()
        
        metadata = DocumentMetadata(
            id=document_id,
            filename=file_path.name,
            original_filename=file_path.name.replace(f"{document_id}_", ""),
            file_size=stat.st_size,
            file_type=file_path.suffix.lower(),
            upload_timestamp=datetime.fromtimestamp(stat.st_ctime).isoformat(),
            processing_status="stored"
        )
        
        return metadata
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get metadata: {str(e)}")

@router.get("/{document_id}/download")
async def download_document(document_id: str):
    """
    Download a document file.
    
    Args:
        document_id: The document identifier
        
    Returns:
        FileResponse: The document file
    """
    try:
        # Find document file
        file_path = None
        for path in UPLOAD_DIR.iterdir():
            if path.name.startswith(f"{document_id}_"):
                file_path = path
                break
        
        if not file_path or not file_path.exists():
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get original filename
        original_filename = file_path.name.replace(f"{document_id}_", "")
        
        return FileResponse(
            path=str(file_path),
            filename=original_filename,
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
    force: bool = False
):
    """
    Process a document to extract content and metadata.
    
    Args:
        document_id: The document identifier
        force: Force reprocessing even if already processed
        
    Returns:
        ProcessingResult: Processing result
    """
    try:
        # Find document file
        file_path = None
        for path in UPLOAD_DIR.iterdir():
            if path.name.startswith(f"{document_id}_"):
                file_path = path
                break
        
        if not file_path or not file_path.exists():
            raise HTTPException(status_code=404, detail="Document not found")
        
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
async def delete_document(document_id: str):
    """
    Delete a document and its associated data.
    
    Args:
        document_id: The document identifier
        
    Returns:
        dict: Deletion confirmation
    """
    try:
        # Find and delete document file
        file_path = None
        for path in UPLOAD_DIR.iterdir():
            if path.name.startswith(f"{document_id}_"):
                file_path = path
                break
        
        if not file_path or not file_path.exists():
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete file
        file_path.unlink()
        
        # TODO: Delete associated processing results, embeddings, etc.
        
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
    try:
        logger.info(f"Starting background processing for document: {document_id}")
        
        # Initialize document processor
        processor = DocumentProcessor()
        
        # Process document
        result = processor.process_document(file_path)
        
        # TODO: Store processing results (database, cache, etc.)
        
        logger.info(f"Document processing completed: {document_id}")
        
    except Exception as e:
        logger.error(f"Background processing failed for {document_id}: {str(e)}")
        # TODO: Update processing status to "failed"
