"""
Document processing module for handling various document formats.

This module provides functionality for processing RFPs, proposals,
and other business documents.
"""

from typing import List, Dict, Any, Optional
import logging
from pathlib import Path
import PyPDF2
import docx

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Handles document processing operations."""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.txt', '.md']
    
    def process_document(self, file_path: Path) -> Dict[str, Any]:
        """
        Process a document and extract relevant information.
        
        Args:
            file_path: Path to the document to process
            
        Returns:
            Dictionary containing extracted document information
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")
        
        if file_path.suffix.lower() not in self.supported_formats:
            raise ValueError(f"Unsupported format: {file_path.suffix}")
        
        logger.info(f"Processing document: {file_path}")
        
        # Basic document information
        doc_info = {
            'file_path': str(file_path),
            'file_name': file_path.name,
            'file_size': file_path.stat().st_size,
            'format': file_path.suffix.lower(),
            'content': self._extract_content(file_path),
            'metadata': self._extract_metadata(file_path)
        }
        
        return doc_info
    
    def _extract_content(self, file_path: Path) -> str:
        """Extract text content from document."""
        extension = file_path.suffix.lower()
        if extension == '.txt':
            return file_path.read_text(encoding='utf-8')
        elif extension == '.md':
            return file_path.read_text(encoding='utf-8')
        elif extension == '.pdf':
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                return "".join(page.extract_text() for page in reader.pages)
        elif extension == '.docx':
            doc = docx.Document(file_path)
            return "\n".join(para.text for para in doc.paragraphs)
        else:
            raise ValueError(f"Unsupported format: {extension}")
    
    def _extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from document."""
        return {
            'created': file_path.stat().st_ctime,
            'modified': file_path.stat().st_mtime,
            'encoding': 'utf-8'  # Default assumption
        }
    
    def batch_process(self, file_paths: List[Path]) -> List[Dict[str, Any]]:
        """Process multiple documents in batch."""
        results = []
        for file_path in file_paths:
            try:
                result = self.process_document(file_path)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                results.append({'error': str(e), 'file_path': str(file_path)})
        
        return results
