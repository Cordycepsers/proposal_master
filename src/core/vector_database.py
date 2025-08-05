"""
Vector Database Implementation - FAISS-based Vector Storage and Retrieval

This module provides a comprehensive vector database solution using FAISS for
efficient similarity search and retrieval of document embeddings. It supports
multiple embedding models, batch operations, and persistent storage.

Features:
- FAISS-based vector indexing for fast similarity search
- Multiple embedding model support (SentenceTransformers, OpenAI, etc.)
- Batch operations for efficient processing
- Persistent storage with metadata management
- Async operations for scalability
- Advanced filtering and search options
- Index optimization and maintenance
"""

import asyncio
import logging
import json
import os
import pickle
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple, Union
from datetime import datetime
from pathlib import Path
import hashlib
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import threading

# Core ML libraries
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class VectorDocument:
    """Document with vector embedding"""
    id: str
    content: str
    embedding: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    source: Optional[str] = None
    chunk_index: Optional[int] = None
    parent_document_id: Optional[str] = None

@dataclass
class SearchResult:
    """Search result with similarity score"""
    document: VectorDocument
    similarity_score: float
    rank: int

@dataclass
class VectorIndexConfig:
    """Configuration for vector index"""
    dimension: int = 384  # Default for sentence-transformers models
    index_type: str = "IndexFlatIP"  # Inner Product (cosine similarity)
    nlist: int = 100  # Number of centroids for IVF indices
    nprobe: int = 10  # Number of centroids to search
    metric: str = "cosine"  # cosine, euclidean, manhattan
    store_on_disk: bool = True
    index_path: str = "data/embeddings/vector_index.faiss"
    metadata_path: str = "data/embeddings/metadata.json"
    embedding_model: str = "all-MiniLM-L6-v2"
    batch_size: int = 32
    max_retries: int = 3

class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers"""
    
    @abstractmethod
    async def embed_texts(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for a list of texts"""
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get model name"""
        pass

class SentenceTransformersProvider(EmbeddingProvider):
    """SentenceTransformers embedding provider"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("sentence-transformers is required for SentenceTransformersProvider")
        
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Initialized SentenceTransformers model: {model_name} (dim: {self.dimension})")
    
    async def embed_texts(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings using SentenceTransformers"""
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                embeddings = await loop.run_in_executor(
                    executor, 
                    lambda: self.model.encode(
                        texts,
                        convert_to_numpy=True,
                        normalize_embeddings=True
                    )
                )
            return [emb for emb in embeddings]
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    def get_dimension(self) -> int:
        return self.dimension
    
    def get_model_name(self) -> str:
        return self.model_name

class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI embedding provider"""
    
    def __init__(self, model_name: str = "text-embedding-ada-002", api_key: Optional[str] = None):
        if not OPENAI_AVAILABLE:
            raise ImportError("openai is required for OpenAIEmbeddingProvider")
        
        self.model_name = model_name
        if api_key:
            openai.api_key = api_key
        elif not openai.api_key:
            openai.api_key = os.getenv("OPENAI_API_KEY")
        
        if not openai.api_key:
            raise ValueError("OpenAI API key is required")
        
        # Set dimension based on model
        self.dimensions = {
            "text-embedding-ada-002": 1536,
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072
        }
        self.dimension = self.dimensions.get(model_name, 1536)
        logger.info(f"Initialized OpenAI embedding model: {model_name} (dim: {self.dimension})")
    
    async def embed_texts(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings using OpenAI API"""
        try:
            # Process in batches to avoid rate limits
            batch_size = 100  # OpenAI batch limit
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                response = await openai.Embedding.acreate(
                    input=batch,
                    model=self.model_name
                )
                
                batch_embeddings = [
                    np.array(item["embedding"], dtype=np.float32)
                    for item in response["data"]
                ]
                all_embeddings.extend(batch_embeddings)
            
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate OpenAI embeddings: {e}")
            raise
    
    def get_dimension(self) -> int:
        return self.dimension
    
    def get_model_name(self) -> str:
        return self.model_name

class VectorDatabase:
    """Main Vector Database class using FAISS"""
    
    def __init__(self, config: VectorIndexConfig):
        if not FAISS_AVAILABLE:
            raise ImportError("faiss-cpu or faiss-gpu is required for VectorDatabase")
        
        self.config = config
        self.index = None
        self.documents = {}  # id -> VectorDocument
        self.id_mapping = {}  # faiss_id -> document_id
        self.embedding_provider = None
        self.is_initialized = False
        self.lock = threading.Lock()
        
        # Initialize directories
        os.makedirs(os.path.dirname(config.index_path), exist_ok=True)
        os.makedirs(os.path.dirname(config.metadata_path), exist_ok=True)
        
        # Initialize embedding provider
        self._initialize_embedding_provider()
        
        # Initialize or load index
        self._initialize_index()
    
    def _initialize_embedding_provider(self):
        """Initialize the embedding provider"""
        try:
            if self.config.embedding_model.startswith("text-embedding"):
                # OpenAI model - check if API key is available
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    logger.warning("OpenAI API key not found, falling back to SentenceTransformers")
                    self.config.embedding_model = "all-MiniLM-L6-v2" 
                    self.embedding_provider = SentenceTransformersProvider(self.config.embedding_model)
                else:
                    self.embedding_provider = OpenAIEmbeddingProvider(self.config.embedding_model, api_key)
            else:
                # SentenceTransformers model
                self.embedding_provider = SentenceTransformersProvider(self.config.embedding_model)
            
            # Update config dimension if needed
            if self.config.dimension != self.embedding_provider.get_dimension():
                logger.warning(f"Updating dimension from {self.config.dimension} to {self.embedding_provider.get_dimension()}")
                self.config.dimension = self.embedding_provider.get_dimension()
                
        except Exception as e:
            logger.error(f"Failed to initialize embedding provider: {e}")
            # Fall back to default SentenceTransformers model
            logger.info("Falling back to default SentenceTransformers model")
            try:
                self.config.embedding_model = "all-MiniLM-L6-v2"
                self.embedding_provider = SentenceTransformersProvider(self.config.embedding_model)
                self.config.dimension = self.embedding_provider.get_dimension()
            except Exception as fallback_error:
                logger.error(f"Even fallback embedding provider failed: {fallback_error}")
                raise
    
    def _initialize_index(self):
        """Initialize or load FAISS index"""
        try:
            if os.path.exists(self.config.index_path) and os.path.exists(self.config.metadata_path):
                self._load_index()
            else:
                self._create_new_index()
            
            self.is_initialized = True
            logger.info(f"Vector database initialized with {self.index.ntotal} vectors")
            
        except Exception as e:
            logger.error(f"Failed to initialize index: {e}")
            raise
    
    def _create_new_index(self):
        """Create a new FAISS index"""
        if self.config.index_type == "IndexFlatIP":
            # Flat index with inner product (cosine similarity)
            self.index = faiss.IndexFlatIP(self.config.dimension)
        elif self.config.index_type == "IndexFlatL2":
            # Flat index with L2 distance (Euclidean)
            self.index = faiss.IndexFlatL2(self.config.dimension)
        elif self.config.index_type == "IndexIVFFlat":
            # IVF (Inverted File) with flat quantizer
            quantizer = faiss.IndexFlatIP(self.config.dimension)
            self.index = faiss.IndexIVFFlat(quantizer, self.config.dimension, self.config.nlist)
        elif self.config.index_type == "IndexHNSW":
            # HNSW (Hierarchical Navigable Small World) for approximate search
            self.index = faiss.IndexHNSWFlat(self.config.dimension, 32)
        else:
            # Default to flat IP
            self.index = faiss.IndexFlatIP(self.config.dimension)
        
        logger.info(f"Created new FAISS index: {self.config.index_type}")
    
    def _load_index(self):
        """Load existing FAISS index and metadata"""
        try:
            # Load FAISS index
            self.index = faiss.read_index(self.config.index_path)
            
            # Load metadata
            with open(self.config.metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Reconstruct documents and mappings
            self.documents = {}
            self.id_mapping = {}
            
            for doc_data in metadata.get('documents', []):
                doc = VectorDocument(
                    id=doc_data['id'],
                    content=doc_data['content'],
                    metadata=doc_data.get('metadata', {}),
                    created_at=datetime.fromisoformat(doc_data.get('created_at', datetime.now().isoformat())),
                    updated_at=datetime.fromisoformat(doc_data.get('updated_at', datetime.now().isoformat())),
                    source=doc_data.get('source'),
                    chunk_index=doc_data.get('chunk_index'),
                    parent_document_id=doc_data.get('parent_document_id')
                )
                self.documents[doc.id] = doc
            
            # Reconstruct ID mapping
            for faiss_id, doc_id in enumerate(metadata.get('id_mapping', [])):
                if doc_id:  # Skip empty slots
                    self.id_mapping[faiss_id] = doc_id
            
            logger.info(f"Loaded index with {len(self.documents)} documents")
            
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            # Create new index on failure
            self._create_new_index()
    
    def _save_index(self):
        """Save FAISS index and metadata"""
        try:
            # Save FAISS index
            faiss.write_index(self.index, self.config.index_path)
            
            # Prepare metadata
            metadata = {
                'config': {
                    'dimension': self.config.dimension,
                    'index_type': self.config.index_type,
                    'embedding_model': self.config.embedding_model,
                    'metric': self.config.metric
                },
                'documents': [
                    {
                        'id': doc.id,
                        'content': doc.content,
                        'metadata': doc.metadata,
                        'created_at': doc.created_at.isoformat(),
                        'updated_at': doc.updated_at.isoformat(),
                        'source': doc.source,
                        'chunk_index': doc.chunk_index,
                        'parent_document_id': doc.parent_document_id
                    }
                    for doc in self.documents.values()
                ],
                'id_mapping': [
                    self.id_mapping.get(i) for i in range(max(self.id_mapping.keys()) + 1)
                ] if self.id_mapping else []
            }
            
            # Save metadata
            with open(self.config.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved index with {len(self.documents)} documents")
            
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
            raise
    
    async def add_documents(self, documents: List[VectorDocument]) -> List[str]:
        """Add documents to the vector database"""
        try:
            # Generate embeddings for documents without them
            texts_to_embed = []
            docs_to_embed = []
            
            for doc in documents:
                if doc.embedding is None:
                    texts_to_embed.append(doc.content)
                    docs_to_embed.append(doc)
            
            if texts_to_embed:
                embeddings = await self.embedding_provider.embed_texts(texts_to_embed)
                for doc, embedding in zip(docs_to_embed, embeddings):
                    doc.embedding = embedding
            
            # Add to FAISS index
            with self.lock:
                embeddings_matrix = np.vstack([doc.embedding for doc in documents]).astype(np.float32)
                
                # Normalize for cosine similarity if using IndexFlatIP
                if self.config.index_type == "IndexFlatIP":
                    faiss.normalize_L2(embeddings_matrix)
                
                # Add to index
                start_id = self.index.ntotal
                self.index.add(embeddings_matrix)
                
                # Update mappings and document store
                for i, doc in enumerate(documents):
                    faiss_id = start_id + i
                    self.id_mapping[faiss_id] = doc.id
                    self.documents[doc.id] = doc
                
                # Save index
                if self.config.store_on_disk:
                    self._save_index()
            
            added_ids = [doc.id for doc in documents]
            logger.info(f"Added {len(added_ids)} documents to vector database")
            return added_ids
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    async def add_document(self, document: VectorDocument) -> str:
        """Add a single document to the vector database"""
        return (await self.add_documents([document]))[0]
    
    async def search(self, query: str, top_k: int = 10, 
                    filters: Optional[Dict[str, Any]] = None,
                    min_similarity: float = 0.0) -> List[SearchResult]:
        """Search for similar documents"""
        try:
            # Generate query embedding
            query_embeddings = await self.embedding_provider.embed_texts([query])
            query_embedding = query_embeddings[0].astype(np.float32).reshape(1, -1)
            
            # Normalize for cosine similarity
            if self.config.index_type == "IndexFlatIP":
                faiss.normalize_L2(query_embedding)
            
            # Search
            with self.lock:
                # Adjust k for potential filtering
                search_k = min(top_k * 2, self.index.ntotal) if filters else top_k
                
                if hasattr(self.index, 'nprobe'):
                    self.index.nprobe = self.config.nprobe
                
                similarities, faiss_ids = self.index.search(query_embedding, search_k)
            
            # Process results
            results = []
            for i, (faiss_id, similarity) in enumerate(zip(faiss_ids[0], similarities[0])):
                if faiss_id == -1:  # No more results
                    break
                
                if similarity < min_similarity:
                    continue
                
                doc_id = self.id_mapping.get(faiss_id)
                if not doc_id:
                    continue
                
                document = self.documents.get(doc_id)
                if not document:
                    continue
                
                # Apply filters
                if filters and not self._apply_filters(document, filters):
                    continue
                
                results.append(SearchResult(
                    document=document,
                    similarity_score=float(similarity),
                    rank=len(results) + 1
                ))
                
                if len(results) >= top_k:
                    break
            
            logger.info(f"Search returned {len(results)} results for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def _apply_filters(self, document: VectorDocument, filters: Dict[str, Any]) -> bool:
        """Apply filters to document"""
        for key, value in filters.items():
            if key == 'source' and document.source != value:
                return False
            elif key == 'parent_document_id' and document.parent_document_id != value:
                return False
            elif key in document.metadata and document.metadata[key] != value:
                return False
        return True
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document from the vector database"""
        try:
            with self.lock:
                if document_id not in self.documents:
                    logger.warning(f"Document not found: {document_id}")
                    return False
                
                # Find FAISS ID
                faiss_id_to_remove = None
                for faiss_id, doc_id in self.id_mapping.items():
                    if doc_id == document_id:
                        faiss_id_to_remove = faiss_id
                        break
                
                if faiss_id_to_remove is not None:
                    # Remove from mapping and documents
                    del self.id_mapping[faiss_id_to_remove]
                    del self.documents[document_id]
                    
                    # Note: FAISS doesn't support removing individual vectors
                    # For now, we mark as deleted in our metadata
                    # For full deletion, index needs to be rebuilt
                    
                    if self.config.store_on_disk:
                        self._save_index()
                    
                    logger.info(f"Marked document as deleted: {document_id}")
                    return True
                
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False
    
    async def update_document(self, document: VectorDocument) -> bool:
        """Update a document in the vector database"""
        try:
            # Delete old version and add new one
            await self.delete_document(document.id)
            document.updated_at = datetime.now()
            await self.add_document(document)
            return True
            
        except Exception as e:
            logger.error(f"Failed to update document: {e}")
            return False
    
    def get_document(self, document_id: str) -> Optional[VectorDocument]:
        """Get a document by ID"""
        return self.documents.get(document_id)
    
    def list_documents(self, limit: Optional[int] = None, 
                      offset: int = 0,
                      filters: Optional[Dict[str, Any]] = None) -> List[VectorDocument]:
        """List documents with optional filtering"""
        docs = list(self.documents.values())
        
        # Apply filters
        if filters:
            docs = [doc for doc in docs if self._apply_filters(doc, filters)]
        
        # Apply pagination
        if offset:
            docs = docs[offset:]
        if limit:
            docs = docs[:limit]
        
        return docs
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        return {
            'total_documents': len(self.documents),
            'total_vectors': self.index.ntotal if self.index else 0,
            'dimension': self.config.dimension,
            'index_type': self.config.index_type,
            'embedding_model': self.config.embedding_model,
            'is_initialized': self.is_initialized
        }
    
    async def rebuild_index(self):
        """Rebuild the entire index (useful after deletions)"""
        try:
            logger.info("Rebuilding vector index...")
            
            # Get all active documents
            active_docs = list(self.documents.values())
            
            # Create new index
            self._create_new_index()
            self.id_mapping.clear()
            
            # Re-add all documents
            if active_docs:
                await self.add_documents(active_docs)
            
            logger.info(f"Index rebuilt with {len(active_docs)} documents")
            
        except Exception as e:
            logger.error(f"Failed to rebuild index: {e}")
            raise
    
    def close(self):
        """Close the database and save state"""
        try:
            if self.config.store_on_disk:
                self._save_index()
            logger.info("Vector database closed")
        except Exception as e:
            logger.error(f"Error closing database: {e}")

# Utility functions for document chunking and preprocessing

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks"""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Try to break at sentence boundary
        if end < len(text):
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            break_point = max(last_period, last_newline)
            
            if break_point > start + chunk_size // 2:
                end = start + break_point + 1
                chunk = text[start:end]
        
        chunks.append(chunk.strip())
        start = end - overlap
        
        if start >= len(text):
            break
    
    return chunks

def create_document_chunks(document_id: str, content: str, 
                         metadata: Optional[Dict[str, Any]] = None,
                         chunk_size: int = 1000, 
                         overlap: int = 100) -> List[VectorDocument]:
    """Create chunked documents from a large document"""
    chunks = chunk_text(content, chunk_size, overlap)
    documents = []
    
    for i, chunk in enumerate(chunks):
        chunk_id = f"{document_id}_chunk_{i}"
        doc = VectorDocument(
            id=chunk_id,
            content=chunk,
            metadata=metadata or {},
            source=metadata.get('source') if metadata else None,
            chunk_index=i,
            parent_document_id=document_id
        )
        documents.append(doc)
    
    return documents

# Factory function for easy initialization
def create_vector_database(
    embedding_model: str = "all-MiniLM-L6-v2",
    index_path: str = "data/embeddings/vector_index.faiss",
    index_type: str = "IndexFlatIP"
) -> VectorDatabase:
    """Create a vector database with default configuration"""
    
    config = VectorIndexConfig(
        embedding_model=embedding_model,
        index_path=index_path,
        index_type=index_type,
        metadata_path=index_path.replace('.faiss', '_metadata.json')
    )
    
    return VectorDatabase(config)
