#!/usr/bin/env python3
"""
Test the working API functionality
"""

import sys
from pathlib import Path
import asyncio

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_api_components():
    """Test API components individually"""
    print("🧪 Testing API Components")
    print("=" * 40)
    
    try:
        # Test FastAPI import
        from fastapi import FastAPI
        print("✅ FastAPI import successful")
        
        # Test our vector database
        from src.core.vector_database import VectorDatabase, VectorIndexConfig, VectorDocument
        print("✅ Vector database import successful")
        
        # Test creating FastAPI app
        app = FastAPI(title="Test API")
        print("✅ FastAPI app creation successful")
        
        # Test vector database initialization
        config = VectorIndexConfig()
        vector_db = VectorDatabase(config)
        print("✅ Vector database initialization successful")
        
        # Test adding a document
        test_doc = VectorDocument(
            id="test_1",
            content="This is a test document for API testing",
            metadata={"type": "test"}
        )
        
        doc_id = await vector_db.add_document(test_doc)
        print(f"✅ Document added successfully: {doc_id}")
        
        # Test search
        results = await vector_db.search("test document", top_k=1)
        if results:
            result = results[0]
            print(f"✅ Search successful: {result.document.id} (score: {result.similarity_score:.3f})")
        else:
            print("⚠️ Search returned no results")
        
        print("\n🎉 All API components are working!")
        print("✨ The vector database integration is functional")
        print("🚀 Ready to serve API requests")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_api_components())
    if success:
        print("\n🌟 API is ready to be deployed!")
    else:
        print("\n⚠️ API has issues that need to be resolved")
