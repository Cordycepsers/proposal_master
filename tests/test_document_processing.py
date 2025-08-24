import pytest
from pathlib import Path
from src.core.document_processor import DocumentProcessor

@pytest.fixture
def temp_test_dir(tmp_path):
    """Create a temporary directory for test files."""
    return tmp_path

@pytest.fixture
def txt_file(temp_test_dir):
    """Create a sample .txt file."""
    file_path = temp_test_dir / "test.txt"
    file_path.write_text("This is a test text file.", encoding="utf-8")
    return file_path

@pytest.fixture
def md_file(temp_test_dir):
    """Create a sample .md file."""
    file_path = temp_test_dir / "test.md"
    file_path.write_text("# Markdown Test\n\nThis is a test markdown file.", encoding="utf-8")
    return file_path

@pytest.fixture
def unsupported_file(temp_test_dir):
    """Create an unsupported file type."""
    file_path = temp_test_dir / "test.xyz"
    file_path.write_text("This is an unsupported file.", encoding="utf-8")
    return file_path

def test_process_txt_document(txt_file):
    """Test processing a .txt document."""
    processor = DocumentProcessor()
    result = processor.process_document(txt_file)

    assert isinstance(result, dict)
    assert result['file_name'] == "test.txt"
    assert result['format'] == ".txt"
    assert result['content'] == "This is a test text file."
    assert "created" in result["metadata"]
    assert "modified" in result["metadata"]

def test_process_md_document(md_file):
    """Test processing a .md document."""
    processor = DocumentProcessor()
    result = processor.process_document(md_file)

    assert isinstance(result, dict)
    assert result['file_name'] == "test.md"
    assert result['format'] == ".md"
    assert result['content'] == "# Markdown Test\n\nThis is a test markdown file."

def test_process_unsupported_document(unsupported_file):
    """Test processing an unsupported document type."""
    processor = DocumentProcessor()
    with pytest.raises(ValueError, match="Unsupported format: .xyz"):
        processor.process_document(unsupported_file)

def test_process_non_existent_document(temp_test_dir):
    """Test processing a non-existent document."""
    processor = DocumentProcessor()
    non_existent_file = temp_test_dir / "non_existent.txt"
    with pytest.raises(FileNotFoundError, match=f"Document not found: {non_existent_file}"):
        processor.process_document(non_existent_file)

def test_batch_process(txt_file, md_file):
    """Test batch processing of documents."""
    processor = DocumentProcessor()
    results = processor.batch_process([txt_file, md_file])

    assert isinstance(results, list)
    assert len(results) == 2
    assert results[0]['file_name'] == "test.txt"
    assert results[1]['file_name'] == "test.md"

def test_batch_process_with_errors(txt_file, unsupported_file, temp_test_dir):
    """Test batch processing with some files causing errors."""
    processor = DocumentProcessor()
    non_existent_file = temp_test_dir / "non_existent.txt"
    results = processor.batch_process([txt_file, unsupported_file, non_existent_file])

    assert isinstance(results, list)
    assert len(results) == 3
    assert results[0]['file_name'] == "test.txt"
    assert "error" in results[1]
    assert "Unsupported format: .xyz" in results[1]['error']
    assert "error" in results[2]
    assert f"Document not found: {non_existent_file}" in results[2]['error']

