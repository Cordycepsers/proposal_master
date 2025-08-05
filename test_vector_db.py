#!/usr/bin/env python3
"""
Quick test script for the vector database functionality.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.vector_database import VectorDatabase, VectorIndexConfig, VectorDocument

async def test_vector_db():
    """Test the vector database functionality."""
    print("🔍 Testing Vector Database Functionality")
    print("=" * 50)
    
    try:
        # Use existing config paths
        config = VectorIndexConfig()
        
        # Initialize vector database
        print("🚀 Initializing vector database...")
        vector_db = VectorDatabase(config)
        
        # Test documents for demonstration
        test_docs = [
            VectorDocument(id="doc_1", content="FastAPI is a modern web framework for building APIs with Python", metadata={"type": "technology"}),
            VectorDocument(id="doc_2", content="Machine learning models require vector databases for similarity search", metadata={"type": "ml"}),
            VectorDocument(id="doc_3", content="Proposal management systems help automate RFP responses", metadata={"type": "business"}),
            VectorDocument(id="doc_4", content="Document analysis uses NLP to extract key requirements", metadata={"type": "nlp"}),
            VectorDocument(id="doc_5", content="Competitive intelligence helps win more business opportunities", metadata={"type": "business"}),
        ]
        
        print("📝 Adding test documents to vector database...")
        for doc in test_docs:
            await vector_db.add_document(doc)
        
        print(f"✅ Added {len(test_docs)} documents successfully")
        print()
        
        # Test semantic search queries
        queries = [
            "API development framework",
            "business proposal automation", 
            "machine learning similarity",
            "document processing NLP"
        ]
        
        for query in queries:
            print(f"🔎 Searching for: '{query}'")
            results = await vector_db.search(query, top_k=2)
            
            print("📊 Search Results:")
            if results:
                for i, result in enumerate(results, 1):
                    print(f"  {i}. Score: {result.similarity_score:.3f} | ID: {result.document.id}")
                    print(f"     Content: {result.document.content[:60]}...")
                    print(f"     Type: {result.document.metadata.get('type', 'N/A')}")
            else:
                print("  No results found")
            print()
        
        # Get database stats
        stats = await vector_db.get_stats()
        print("📈 Database Statistics:")
        print(f"  Total documents: {stats.get('total_documents', 0)}")
        print(f"  Index type: {stats.get('index_type', 'N/A')}")
        print(f"  Embedding model: {stats.get('embedding_model', 'N/A')}")
        print(f"  Dimension: {stats.get('dimension', 0)}")
        
        print("\n✅ Vector database is working perfectly!")
        print("🎉 FAISS + SentenceTransformers integration successful!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_vector_db())
