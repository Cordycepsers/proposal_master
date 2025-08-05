"""
Document Parser Sub-Agent

Specialized sub-agent for parsing and extracting content from various document formats.
Handles PDF, DOCX, TXT, and Markdown files with intelligent content structuring.
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import asyncio

from ...agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class DocumentParser(BaseAgent):
    """Sub-agent for document parsing and content extraction."""
    
    def __init__(self):
        super().__init__(
            name="Document Parser", 
            description="Extracts and structures content from various document formats"
        )
        self.supported_formats = ['.pdf', '.docx', '.txt', '.md']
        self.extraction_stats = {
            'documents_processed': 0,
            'total_pages': 0,
            'avg_processing_time': 0.0
        }
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse document and extract structured content.
        
        Args:
            input_data: Dictionary containing:
                - document_path: Path to document file
                - extraction_options: Optional parsing preferences
                
        Returns:
            Dictionary containing parsed content and metadata
        """
        try:
            self.log_operation("Starting document parsing", input_data)
            
            document_path = input_data.get('document_path')
            if not document_path:
                raise ValueError("document_path is required")
            
            file_path = Path(document_path)
            if not file_path.exists():
                raise FileNotFoundError(f"Document not found: {document_path}")
            
            # Extract based on file type
            file_extension = file_path.suffix.lower()
            if file_extension not in self.supported_formats:
                raise ValueError(f"Unsupported format: {file_extension}")
            
            # Parse document content
            content = await self._extract_content(file_path, file_extension)
            
            # Extract metadata
            metadata = await self._extract_metadata(file_path)
            
            # Structure the content
            structured_content = await self._structure_content(content)
            
            # Update statistics
            self.extraction_stats['documents_processed'] += 1
            
            result = {
                'status': 'success',
                'document_path': str(file_path),
                'file_type': file_extension,
                'metadata': metadata,
                'raw_content': content,
                'structured_content': structured_content,
                'extraction_stats': self.extraction_stats.copy()
            }
            
            self.log_operation("Document parsing completed", {'document': str(file_path)})
            return result
            
        except Exception as e:
            error_msg = f"Document parsing failed: {str(e)}"
            self.logger.error(error_msg)
            return {
                'status': 'error',
                'error': error_msg,
                'document_path': input_data.get('document_path', 'unknown')
            }
    
    async def _extract_content(self, file_path: Path, file_extension: str) -> str:
        """Extract raw content from document based on file type."""
        try:
            if file_extension == '.txt':
                return await self._extract_txt_content(file_path)
            elif file_extension == '.md':
                return await self._extract_md_content(file_path)
            elif file_extension == '.pdf':
                return await self._extract_pdf_content(file_path)
            elif file_extension == '.docx':
                return await self._extract_docx_content(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
                
        except Exception as e:
            self.logger.error(f"Content extraction failed: {e}")
            raise
    
    async def _extract_txt_content(self, file_path: Path) -> str:
        """Extract content from text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
    
    async def _extract_md_content(self, file_path: Path) -> str:
        """Extract content from Markdown file."""
        return await self._extract_txt_content(file_path)
    
    async def _extract_pdf_content(self, file_path: Path) -> str:
        """Extract content from PDF file."""
        # Placeholder for PDF extraction - would use PyPDF2 or similar
        try:
            # Simulate PDF extraction
            await asyncio.sleep(0.1)  # Simulate processing time
            return f"[PDF CONTENT] Extracted from {file_path.name}\n\nThis is simulated PDF content extraction. In production, this would use a PDF parsing library like PyPDF2 or pdfplumber."
        except Exception as e:
            self.logger.error(f"PDF extraction failed: {e}")
            raise
    
    async def _extract_docx_content(self, file_path: Path) -> str:
        """Extract content from DOCX file."""
        # Placeholder for DOCX extraction - would use python-docx
        try:
            # Simulate DOCX extraction
            await asyncio.sleep(0.1)  # Simulate processing time
            return f"[DOCX CONTENT] Extracted from {file_path.name}\n\nThis is simulated DOCX content extraction. In production, this would use the python-docx library."
        except Exception as e:
            self.logger.error(f"DOCX extraction failed: {e}")
            raise
    
    async def _extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from document."""
        try:
            stat = file_path.stat()
            return {
                'filename': file_path.name,
                'file_size': stat.st_size,
                'created_time': stat.st_ctime,
                'modified_time': stat.st_mtime,
                'file_extension': file_path.suffix.lower()
            }
        except Exception as e:
            self.logger.error(f"Metadata extraction failed: {e}")
            return {}
    
    async def _structure_content(self, content: str) -> Dict[str, Any]:
        """Structure the extracted content into logical sections."""
        try:
            # Simple content structuring
            lines = content.split('\n')
            
            # Identify sections based on patterns
            sections = []
            current_section = {'title': 'Introduction', 'content': []}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if line is a potential header
                if (line.isupper() and len(line) < 100) or \
                   (line.startswith('#') and line.count('#') <= 3):
                    # Save current section if it has content
                    if current_section['content']:
                        sections.append(current_section)
                    
                    # Start new section
                    title = line.replace('#', '').strip()
                    current_section = {'title': title, 'content': []}
                else:
                    current_section['content'].append(line)
            
            # Add the last section
            if current_section['content']:
                sections.append(current_section)
            
            return {
                'sections': sections,
                'total_sections': len(sections),
                'total_lines': len(lines),
                'word_count': len(content.split())
            }
            
        except Exception as e:
            self.logger.error(f"Content structuring failed: {e}")
            return {'sections': [], 'error': str(e)}
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported document formats."""
        return self.supported_formats.copy()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get parsing statistics."""
        return self.extraction_stats.copy()
