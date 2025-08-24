import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.api.main import app
from src.config.database import Base, get_db_session
from src.models.core import Document, Proposal, TenderOpportunity, Feedback, OpportunitySource
import os
from pathlib import Path
from unittest.mock import patch

# Use a separate test database
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_api.db"

engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db_session] = override_get_db

client = TestClient(app)

@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_and_teardown_db():
    """Create and drop the test database for the module."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    os.remove("./test_api.db")

@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture(scope="function")
def sample_txt_file(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("This is a test file.")
    return file_path

@pytest_asyncio.fixture(scope="function")
async def sample_proposal(db_session):
    """Create a sample proposal for testing."""
    opportunity = TenderOpportunity(
        tender_id="SAMPLE-001",
        title="Sample Tender",
        source=OpportunitySource.MANUAL
    )
    db_session.add(opportunity)
    await db_session.commit()
    await db_session.refresh(opportunity)

    proposal = Proposal(
        opportunity_id=opportunity.id,
        proposal_number="PROP-001",
        title="Sample Proposal"
    )
    db_session.add(proposal)
    await db_session.commit()
    await db_session.refresh(proposal)
    return proposal

@pytest.mark.asyncio
async def test_upload_document(db_session, sample_txt_file):
    """Test uploading a document."""
    with open(sample_txt_file, "rb") as f:
        response = client.post("/api/v1/documents/upload", files={"file": ("test.txt", f, "text/plain")})

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Document uploaded successfully"

    doc = await db_session.get(Document, data["document_id"])
    assert doc is not None
    assert doc.original_filename == "test.txt"

@pytest.mark.asyncio
async def test_list_documents(db_session, sample_txt_file):
    """Test listing documents."""
    # Clear the table first to ensure a clean state
    await db_session.execute(Document.__table__.delete())
    await db_session.commit()

    with open(sample_txt_file, "rb") as f:
        client.post("/api/v1/documents/upload", files={"file": ("test.txt", f, "text/plain")})

    response = client.get("/api/v1/documents/")
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 1

@pytest.mark.asyncio
async def test_create_feedback(db_session, sample_proposal):
    """Test creating feedback for a proposal."""
    feedback_data = {
        "proposal_id": sample_proposal.id,
        "rating": 5,
        "comment": "Excellent proposal!"
    }
    response = client.post("/api/v1/feedback/", json=feedback_data)

    assert response.status_code == 200
    data = response.json()
    assert data["proposal_id"] == sample_proposal.id

    feedback = await db_session.get(Feedback, data["id"])
    assert feedback is not None
    assert feedback.rating == 5
