# DocumentParser Module

The DocumentParser module is a specialized sub-agent for parsing and extracting content from various document formats in the Proposal Master system.

## Overview

The DocumentParser handles multiple document formats with intelligent content structuring and comprehensive error handling. It's designed to be robust, efficient, and provide detailed feedback about the parsing process.

## Supported Formats

- **Text Files (.txt)**: Plain text documents with encoding detection
- **Markdown Files (.md)**: Markdown documents with structure parsing
- **PDF Files (.pdf)**: PDF documents with encryption detection and page-by-page extraction
- **Word Documents (.docx)**: Microsoft Word documents with paragraph, table, and header/footer extraction

## Features

### Content Extraction
- **Multi-format Support**: Handles TXT, MD, PDF, and DOCX files
- **Encoding Detection**: Automatic fallback from UTF-8 to Latin-1 for text files
- **Structure Preservation**: Maintains document structure including sections, headers, and formatting
- **Metadata Extraction**: Provides file size, format, and processing timestamps

### Error Handling
- **File Validation**: Comprehensive checks for file existence, permissions, and format
- **Size Limits**: Configurable file size limits (100MB default, 50MB for PDF/DOCX)
- **Corruption Detection**: Handles corrupted or invalid files gracefully
- **Encryption Handling**: Detects and reports encrypted PDF files
- **Missing Dependencies**: Graceful fallback when PyPDF2 or python-docx are unavailable

### Performance Features
- **Async Processing**: Non-blocking document processing
- **Progress Tracking**: Detailed statistics and processing metrics
- **Memory Efficient**: Streaming processing for large files
- **Error Recovery**: Continues processing even when some operations fail

## Usage

### Basic Usage

```python
from src.modules.analysis.document_parser import DocumentParser

# Initialize the parser
parser = DocumentParser()

# Parse a document
result = await parser.process({
    'document_path': '/path/to/document.pdf'
})

# Check the result
if result['status'] == 'success':
    content = result['content']
    metadata = result['metadata']
    structured_data = result['structured_data']
else:
    error_message = result['error']
```

### Response Format

#### Success Response
```python
{
    'status': 'success',
    'document_path': '/path/to/document.pdf',
    'content': 'Extracted text content...',
    'structured_data': {
        'sections': [...],
        'total_sections': 5,
        'total_lines': 120,
        'word_count': 850
    },
    'metadata': {
        'file_size': 1024768,
        'file_extension': '.pdf',
        'processing_timestamp': '2025-08-25T10:30:00'
    },
    'extraction_stats': {
        'documents_processed': 1,
        'pages_processed': 12,
        'file_size': 1024768,
        'file_extension': '.pdf'
    }
}
```

#### Error Response
```python
{
    'status': 'error',
    'error': 'Document not found: /path/to/document.pdf',
    'error_type': 'FileNotFoundError',
    'document_path': '/path/to/document.pdf'
}
```

#### Warning Response (Empty Files)
```python
{
    'status': 'warning',
    'warning': 'File is empty',
    'document_path': '/path/to/document.pdf',
    'content': '',
    'structured_data': {},
    'metadata': {...}
}
```

## Configuration

### File Size Limits
- **General Files**: 100MB maximum
- **PDF Files**: 50MB maximum  
- **DOCX Files**: 50MB maximum

### Dependencies
- **Required**: pathlib, asyncio, logging
- **Optional**: PyPDF2 (for PDF support), python-docx (for DOCX support)

## Error Types

### FileNotFoundError
- **Cause**: Document file doesn't exist
- **Solution**: Verify the file path is correct

### PermissionError
- **Cause**: No read permission for the file
- **Solution**: Check file permissions

### ValueError
- **Cause**: Invalid file format, corrupted file, or file too large
- **Solution**: Verify file integrity and size

### RuntimeError
- **Cause**: Content extraction failed
- **Solution**: Check file format and dependencies

## Advanced Features

### PDF Processing
- **Encryption Detection**: Automatically detects password-protected PDFs
- **Page-by-Page Extraction**: Processes large PDFs efficiently
- **Error Recovery**: Continues processing even if some pages fail
- **Format Validation**: Verifies PDF structure before processing

### DOCX Processing
- **Complete Content Extraction**: Paragraphs, tables, headers, and footers
- **Format Preservation**: Maintains document structure
- **Error Handling**: Graceful handling of corrupted Office documents
- **Metadata Extraction**: Document properties and formatting information

### Content Structuring
- **Section Detection**: Automatically identifies document sections
- **Header Hierarchy**: Maintains heading levels and structure
- **Statistics Generation**: Word count, line count, and section analysis

## Testing

The module includes comprehensive tests covering:
- **Valid file processing** for all supported formats
- **Error handling** for various failure scenarios
- **Edge cases** like empty files and permission issues
- **Performance** with large files and complex documents

```bash
# Run tests
python -m pytest tests/test_document_parser.py -v

# Test specific functionality
python -c "
import asyncio
from src.modules.analysis.document_parser import DocumentParser

async def test():
    parser = DocumentParser()
    result = await parser.process({'document_path': 'test.txt'})
    print(result['status'])

asyncio.run(test())
"
```

## Implementation Status

✅ **Completed Features:**
- Multi-format document parsing (TXT, MD, PDF, DOCX)
- Comprehensive error handling and validation
- Content structuring and metadata extraction
- Async processing with progress tracking
- Extensive test coverage

✅ **Production Ready:** Yes, with comprehensive error handling and testing

## Integration

The DocumentParser integrates seamlessly with other Proposal Master modules:
- **Document Analysis**: Provides structured content for analysis
- **Requirement Extraction**: Supplies parsed text for requirement identification
- **Risk Assessment**: Offers document content for risk analysis
- **Content Generation**: Provides source material for proposal writing

## Performance Considerations

- **Memory Usage**: Efficient streaming for large files
- **Processing Time**: Optimized for typical business documents
- **Error Recovery**: Robust handling of problematic files
- **Scalability**: Async design supports concurrent processing
