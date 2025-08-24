import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.api.main import app
from src.config.database import Base, get_db_session
from src.models.core import Document
import os
from pathlib import Path
from unittest.mock import patch

# Use a separate in-memory test database
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db_session] = override_get_db

client = TestClient(app)

@pytest_asyncio.fixture(scope="function")
async def test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
def sample_txt_file(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("This is a test file.")
    return file_path

@pytest.mark.asyncio
async def test_upload_document(test_db, sample_txt_file):
    """Test uploading a document."""
    with open(sample_txt_file, "rb") as f:
        response = client.post("/api/v1/documents/upload", files={"file": ("test.txt", f, "text/plain")})

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Document uploaded successfully"
    assert "document_id" in data
    assert data["metadata"]["original_filename"] == "test.txt"
    assert data["metadata"]["file_type"] == ".txt"

    async with TestingSessionLocal() as db:
        doc = await db.get(Document, data["document_id"])
        assert doc is not None
        assert doc.original_filename == "test.txt"

@pytest.mark.asyncio
async def test_list_documents(test_db, sample_txt_file):
    """Test listing documents."""
    with open(sample_txt_file, "rb") as f:
        client.post("/api/v1/documents/upload", files={"file": ("test.txt", f, "text/plain")})

    response = client.get("/api/v1/documents/")
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 1
    assert len(data["documents"]) == 1
    assert data["documents"][0]["original_filename"] == "test.txt"

@pytest.mark.asyncio
async def test_get_document_metadata(test_db, sample_txt_file):
    """Test getting a single document's metadata."""
    with open(sample_txt_file, "rb") as f:
        upload_response = client.post("/api/v1/documents/upload", files={"file": ("test.txt", f, "text/plain")})

    document_id = upload_response.json()["document_id"]
    response = client.get(f"/api/v1/documents/{document_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == document_id
    assert data["original_filename"] == "test.txt"

@pytest.mark.asyncio
async def test_download_document(test_db, sample_txt_file):
    """Test downloading a document."""
    with open(sample_txt_file, "rb") as f:
        upload_response = client.post("/api/v1/documents/upload", files={"file": ("test.txt", f, "text/plain")})

    document_id = upload_response.json()["document_id"]
    response = client.get(f"/api/v1/documents/{document_id}/download")

    assert response.status_code == 200
    assert response.headers["content-disposition"] == 'attachment; filename="test.txt"'
    assert response.text == "This is a test file."

@pytest.mark.asyncio
@patch('src.core.rag_system.RAGSystem.remove_document')
async def test_delete_document(mock_remove_doc, test_db, sample_txt_file):
    """Test deleting a document."""
    with open(sample_txt_file, "rb") as f:
        upload_response = client.post("/api/v1/documents/upload", files={"file": ("test.txt", f, "text/plain")})

    document_id = upload_response.json()["document_id"]

    delete_response = client.delete(f"/api/v1/documents/{document_id}")

    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Document deleted successfully"

    async with TestingSessionLocal() as db:
        doc = await db.get(Document, document_id)
        assert doc is None

    doc_from_response = upload_response.json()["metadata"]
    file_path = Path("data/documents/uploads") / doc_from_response["filename"]
    assert not file_path.exists()

@pytest.mark.asyncio
@patch('src.api.routes.documents.process_document_background')
async def test_process_document_endpoint(mock_process_background, test_db, sample_txt_file):
    """Test the process document endpoint."""
    with open(sample_txt_file, "rb") as f:
        upload_response = client.post("/api/v1/documents/upload", files={"file": ("test.txt", f, "text/plain")})

    document_id = upload_response.json()["document_id"]

    response = client.post(f"/api/v1/documents/{document_id}/process")

    assert response.status_code == 200
    data = response.json()
    assert data["document_id"] == document_id
    assert data["status"] == "processing"
    mock_process_background.assert_called_once()
