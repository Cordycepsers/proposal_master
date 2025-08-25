"""
Test suite for DocumentParser module.
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from src.modules.analysis.document_parser import DocumentParser


class TestDocumentParser:
    """Test cases for DocumentParser class."""
    
    @pytest.fixture
    def parser(self):
        """Create a DocumentParser instance for testing."""
        return DocumentParser()
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    def test_initialization(self, parser):
        """Test DocumentParser initialization."""
        assert parser.name == "DocumentParser"
        assert "document parsing" in parser.description.lower()
        assert parser.supported_formats == ['.txt', '.md', '.pdf', '.docx']
        assert isinstance(parser.extraction_stats, dict)
    
    def test_get_supported_formats(self, parser):
        """Test getting supported formats."""
        formats = parser.get_supported_formats()
        assert formats == ['.txt', '.md', '.pdf', '.docx']
        assert isinstance(formats, list)
    
    def test_get_statistics(self, parser):
        """Test getting parsing statistics."""
        stats = parser.get_statistics()
        assert isinstance(stats, dict)
        assert 'pages_processed' in stats
        assert 'file_size' in stats
    
    @pytest.mark.asyncio
    async def test_parse_document_invalid_input(self, parser):
        """Test parse_document with invalid input."""
        # Test with None input
        result = await parser.parse_document(None)
        assert result['status'] == 'error'
        assert 'Invalid input data' in result['error']
        
        # Test with empty dict
        result = await parser.parse_document({})
        assert result['status'] == 'error'
        assert 'Document path is required' in result['error']
        
        # Test with missing document_path
        result = await parser.parse_document({'other_field': 'value'})
        assert result['status'] == 'error'
        assert 'Document path is required' in result['error']
    
    @pytest.mark.asyncio
    async def test_parse_document_file_not_found(self, parser):
        """Test parse_document with non-existent file."""
        result = await parser.parse_document({
            'document_path': '/non/existent/file.txt'
        })
        assert result['status'] == 'error'
        assert 'Document not found' in result['error']
        assert result['error_type'] == 'FileNotFoundError'
    
    @pytest.mark.asyncio
    async def test_parse_txt_file(self, parser, temp_dir):
        """Test parsing a text file."""
        # Create a test text file
        txt_file = temp_dir / "test.txt"
        test_content = "This is a test document.\nWith multiple lines.\nAnd some content."
        txt_file.write_text(test_content)
        
        result = await parser.parse_document({
            'document_path': str(txt_file)
        })
        
        assert result['status'] == 'success'
        assert result['content'] == test_content
        assert result['metadata']['file_extension'] == '.txt'
        assert result['metadata']['file_size'] > 0
        assert 'processing_timestamp' in result['metadata']
        assert 'structured_data' in result
    
    @pytest.mark.asyncio
    async def test_parse_md_file(self, parser, temp_dir):
        """Test parsing a Markdown file."""
        # Create a test markdown file
        md_file = temp_dir / "test.md"
        test_content = "# Test Document\n\nThis is a **test** document.\n\n## Section 1\n\nSome content here."
        md_file.write_text(test_content)
        
        result = await parser.parse_document({
            'document_path': str(md_file)
        })
        
        assert result['status'] == 'success'
        assert result['content'] == test_content
        assert result['metadata']['file_extension'] == '.md'
        assert 'structured_data' in result
    
    @pytest.mark.asyncio
    async def test_parse_empty_file(self, parser, temp_dir):
        """Test parsing an empty file."""
        # Create an empty file
        empty_file = temp_dir / "empty.txt"
        empty_file.write_text("")
        
        result = await parser.parse_document({
            'document_path': str(empty_file)
        })
        
        assert result['status'] == 'warning'
        assert result['warning'] == 'File is empty'
        assert result['content'] == ''
        assert result['metadata']['file_size'] == 0
    
    @pytest.mark.asyncio
    async def test_parse_large_file(self, parser, temp_dir):
        """Test parsing a file that exceeds size limit."""
        # Create a large file (simulate by mocking file size check)
        large_file = temp_dir / "large.txt"
        large_file.write_text("test content")
        
        # Mock the file size to exceed limit
        original_stat = Path.stat
        def mock_stat(self):
            stat_result = original_stat(self)
            if self.name == "large.txt":
                # Mock size to exceed 100MB limit
                class MockStat:
                    st_size = 101 * 1024 * 1024  # 101MB
                return MockStat()
            return stat_result
        
        Path.stat = mock_stat
        
        try:
            result = await parser.parse_document({
                'document_path': str(large_file)
            })
            
            assert result['status'] == 'error'
            assert 'File too large' in result['error']
        finally:
            # Restore original stat method
            Path.stat = original_stat
    
    @pytest.mark.asyncio
    async def test_extract_txt_content(self, parser, temp_dir):
        """Test TXT content extraction."""
        txt_file = temp_dir / "test.txt"
        test_content = "Line 1\nLine 2\nLine 3"
        txt_file.write_text(test_content)
        
        content = await parser._extract_txt_content(txt_file)
        assert content == test_content
    
    @pytest.mark.asyncio
    async def test_extract_txt_content_encoding(self, parser, temp_dir):
        """Test TXT content extraction with different encodings."""
        txt_file = temp_dir / "test_encoding.txt"
        
        # Write with latin-1 encoding
        with open(txt_file, 'w', encoding='latin-1') as f:
            f.write("Test with special chars: àáâã")
        
        content = await parser._extract_txt_content(txt_file)
        assert "special chars" in content
    
    @pytest.mark.asyncio
    async def test_structure_content(self, parser):
        """Test content structuring."""
        content = """# Main Title
        
        This is the introduction.
        
        ## Section 1
        
        Content of section 1.
        Multiple lines here.
        
        ## Section 2
        
        Content of section 2.
        """
        
        structured = await parser._structure_content(content)
        
        assert 'sections' in structured
        assert structured['total_sections'] > 0
        assert 'word_count' in structured
        assert structured['word_count'] > 0
    
    @pytest.mark.asyncio
    async def test_parse_content(self, parser):
        """Test content parsing."""
        content = "This is test content with some words."
        
        parsed = await parser._parse_content(content)
        
        assert 'word_count' in parsed or 'sections' in parsed
        
        # Test with empty content
        empty_parsed = await parser._parse_content("")
        assert empty_parsed['total_sections'] == 0
        assert empty_parsed['word_count'] == 0
    
    def test_file_permission_error(self, parser, temp_dir):
        """Test handling of permission errors."""
        # Create a file and remove read permissions
        restricted_file = temp_dir / "restricted.txt"
        restricted_file.write_text("test content")
        
        # Remove read permissions (this might not work on all systems)
        try:
            os.chmod(restricted_file, 0o000)
            
            # Test the permission check
            result = asyncio.run(parser.parse_document({
                'document_path': str(restricted_file)
            }))
            
            # Should handle permission error gracefully
            assert result['status'] == 'error'
            assert result['error_type'] in ['PermissionError', 'OSError']
            
        except (OSError, PermissionError):
            # Skip test if we can't change permissions
            pytest.skip("Cannot test permission errors on this system")
        finally:
            # Restore permissions for cleanup
            try:
                os.chmod(restricted_file, 0o644)
            except (OSError, PermissionError):
                pass


class TestDocumentParserIntegration:
    """Integration tests for DocumentParser with actual file types."""
    
    @pytest.fixture
    def parser(self):
        """Create a DocumentParser instance for testing."""
        return DocumentParser()
    
    @pytest.mark.asyncio
    async def test_pdf_extraction_missing_library(self, parser, temp_dir):
        """Test PDF extraction when PyPDF2 is not available."""
        # Create a dummy PDF file (just for path testing)
        pdf_file = temp_dir / "test.pdf"
        pdf_file.write_bytes(b"dummy pdf content")
        
        # This will test the error handling when PyPDF2 is not available
        # or when the file is not a valid PDF
        result = await parser.parse_document({
            'document_path': str(pdf_file)
        })
        
        # Should handle the error gracefully
        assert result['status'] in ['error', 'success']
        if result['status'] == 'error':
            assert 'error' in result
    
    @pytest.mark.asyncio
    async def test_docx_extraction_missing_library(self, parser, temp_dir):
        """Test DOCX extraction when python-docx is not available."""
        # Create a dummy DOCX file (just for path testing)
        docx_file = temp_dir / "test.docx"
        docx_file.write_bytes(b"dummy docx content")
        
        # This will test the error handling when python-docx is not available
        # or when the file is not a valid DOCX
        result = await parser.parse_document({
            'document_path': str(docx_file)
        })
        
        # Should handle the error gracefully
        assert result['status'] in ['error', 'success']
        if result['status'] == 'error':
            assert 'error' in result
    
    @pytest.mark.asyncio
    async def test_unsupported_file_format(self, parser, temp_dir):
        """Test handling of unsupported file formats."""
        # Create a file with unsupported extension
        unsupported_file = temp_dir / "test.xyz"
        unsupported_file.write_text("test content")
        
        result = await parser.parse_document({
            'document_path': str(unsupported_file)
        })
        
        assert result['status'] == 'error'
        assert 'Unsupported file type' in result['error']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
