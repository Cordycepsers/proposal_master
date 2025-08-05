"""
RAG (Retrieval-Augmented Generation) system for proposal intelligence.

This module provides RAG functionality for retrieving relevant information
from documents and generating contextual responses using the new vector database.
"""

from typing import List, Dict, Any, Optional, Tuple
import logging
from pathlib import Path

from src.core.vector_database import VectorDatabase, VectorDocument, create_vector_database
from src.services.vector_integration import VectorIntegrationService, create_vector_integration_service

logger = logging.getLogger(__name__)


class RAGSystem:
    """Enhanced RAG system using the new vector database."""
    
    def __init__(self, index_path: Optional[Path] = None):
        # Initialize with new vector database
        index_path_str = str(index_path) if index_path else "data/embeddings/rag_index.faiss"
        self.vector_service = create_vector_integration_service(
            embedding_model="all-MiniLM-L6-v2",
            index_path=index_path_str
        )
        self.vector_db = self.vector_service.vector_db
        self.is_loaded = True
        logger.info("RAG system initialized with vector database")
    
    async def build_index(self, documents: List[Dict[str, Any]]) -> None:
        """
        Build the RAG index from a collection of documents.
        
        Args:
            documents: List of processed documents with content and metadata
        """
        logger.info(f"Building RAG index from {len(documents)} documents")
        
        vector_docs = []
        for i, doc in enumerate(documents):
            doc_id = doc.get('id', f"doc_{i}")
            content = doc.get('content', '')
            metadata = doc.get('metadata', {})
            
            vector_doc = VectorDocument(
                id=doc_id,
                content=content,
                metadata=metadata,
                source='rag_build'
            )
            vector_docs.append(vector_doc)
        
        # Add to vector database
        await self.vector_db.add_documents(vector_docs)
        logger.info("RAG index built successfully")
    
    async def add_document(self, doc_id: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a single document to the RAG index"""
        vector_doc = VectorDocument(
            id=doc_id,
            content=content,
            metadata=metadata or {},
            source='rag_add'
        )
        
        await self.vector_db.add_document(vector_doc)
        logger.info(f"Added document to RAG index: {doc_id}")
        return doc_id
    
    async def search(self, query: str, top_k: int = 5, 
                    filters: Optional[Dict[str, Any]] = None) -> List[Tuple[str, Dict[str, Any], float]]:
        """
        Search for relevant documents based on query.
        
        Args:
            query: User query string
            top_k: Number of top results to return
            filters: Optional filters to apply
            
        Returns:
            List of tuples (doc_id, document_dict, similarity_score)
        """
        results = await self.vector_db.search(
            query=query,
            top_k=top_k,
            filters=filters
        )
        
        # Convert to legacy format
        legacy_results = []
        for result in results:
            doc_dict = {
                'id': result.document.id,
                'content': result.document.content,
                'metadata': result.document.metadata,
                'source': result.document.source,
                'created_at': result.document.created_at.isoformat(),
                'updated_at': result.document.updated_at.isoformat()
            }
            legacy_results.append((result.document.id, doc_dict, result.similarity_score))
        
        logger.info(f"RAG search returned {len(legacy_results)} results for query: {query[:50]}...")
        return legacy_results
    
    async def search_tenders(self, query: str, top_k: int = 5) -> List[Tuple[Any, float]]:
        """Search for relevant tender opportunities"""
        return await self.vector_service.semantic_search_tenders(query, top_k)
    
    async def search_won_bids(self, query: str, top_k: int = 5) -> List[Tuple[Any, float]]:
        """Search for similar won bids"""
        return await self.vector_service.find_similar_won_bids(query, top_k)
    
    async def search_project_docs(self, query: str, top_k: int = 5, 
                                 doc_type: Optional[str] = None) -> List[Tuple[Any, float]]:
        """Search project documentation"""
        return await self.vector_service.search_project_documentation(
            query, top_k, doc_type=doc_type
        )
    
    def load_index(self) -> None:
        """Load existing index (compatibility method)"""
        # Index is automatically loaded in the vector database
        self.is_loaded = True
        logger.info("RAG index loaded (using vector database)")
    
    def save_index(self) -> None:
        """Save index (compatibility method)"""
        # Vector database automatically saves
        logger.info("RAG index saved (using vector database)")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        return self.vector_db.get_stats()
    
    async def remove_document(self, doc_id: str) -> bool:
        """Remove a document from the RAG index"""
        return await self.vector_db.delete_document(doc_id)
    
    async def update_document(self, doc_id: str, content: str, 
                            metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Update a document in the RAG index"""
        vector_doc = VectorDocument(
            id=doc_id,
            content=content,
            metadata=metadata or {},
            source='rag_update'
        )
        
        return await self.vector_db.update_document(vector_doc)
    
    def generate_response(self, query: str, context_docs: List[Dict[str, Any]], 
                         max_length: int = 500) -> str:
        """
        Generate a response based on query and context documents.
        
        This is a placeholder for integration with language models.
        In production, this would use OpenAI, Anthropic, or local models.
        """
        if not context_docs:
            return "I don't have enough information to answer that question."
        
        # Simple response generation (placeholder)
        context_text = "\n\n".join([doc.get('content', '')[:200] for doc in context_docs[:3]])
        
        response = f"""Based on the available documents, here's what I found:

{context_text[:max_length]}

This information comes from {len(context_docs)} relevant document(s) in our database."""
        
        return response
    
    async def query_with_response(self, query: str, top_k: int = 5, 
                                max_response_length: int = 500) -> Dict[str, Any]:
        """
        Perform search and generate response in one call.
        
        Returns:
            Dictionary with search results and generated response
        """
        # Search for relevant documents
        search_results = await self.search(query, top_k)
        
        # Extract documents for response generation
        context_docs = [doc_dict for _, doc_dict, _ in search_results]
        
        # Generate response
        response = self.generate_response(query, context_docs, max_response_length)
        
        return {
            'query': query,
            'response': response,
            'sources': len(search_results),
            'search_results': search_results,
            'context_documents': context_docs
        }
        """
        Generate embedding for text (placeholder implementation).
        
        In production, this would use a proper embedding model like
        sentence-transformers or OpenAI embeddings.
        """
        # Simple hash-based embedding for demonstration
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        # Convert to numpy array (simplified)
        return np.array([ord(c) for c in hash_obj.hexdigest()[:10]], dtype=float)
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, Dict[str, Any], float]]:
        """
        Search for relevant documents based on query.
        
        Args:
            query: User query string
            top_k: Number of top results to return
            
        Returns:
            List of tuples (doc_id, document, similarity_score)
        """
        if not self.is_loaded:
            self.load_index()
        
        query_embedding = self._generate_embedding(query)
        similarities = []
        
        for doc_id, doc_embedding in self.embeddings.items():
            similarity = self._calculate_similarity(query_embedding, doc_embedding)
            similarities.append((doc_id, similarity))
        
        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for doc_id, score in similarities[:top_k]:
            document = self.documents.get(doc_id, {})
            results.append((doc_id, document, score))
        
        return results
    
    def _calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between embeddings."""
        # Simple dot product normalized (placeholder)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return np.dot(embedding1, embedding2) / (norm1 * norm2)
    
    def generate_response(self, query: str, context_docs: List[Dict[str, Any]]) -> str:
        """
        Generate response based on query and retrieved context.
        
        Args:
            query: User query
            context_docs: Retrieved relevant documents
            
        Returns:
            Generated response string
        """
        # Placeholder response generation
        context_snippets = []
        for doc in context_docs:
            content = doc.get('content', '')[:200]  # First 200 chars
            context_snippets.append(content)
        
        combined_context = "\n\n".join(context_snippets)
        
        # In production, this would use an LLM for generation
        response = f"""Based on the available documents, here's what I found relevant to your query "{query}":

Context from documents:
{combined_context}

[Note: This is a placeholder response. In production, this would use an LLM to generate a proper response based on the retrieved context.]
"""
        return response
    
    def query(self, query: str, top_k: int = 5) -> str:
        """
        Complete RAG query pipeline: retrieve and generate.
        
        Args:
            query: User query string
            top_k: Number of documents to retrieve
            
        Returns:
            Generated response
        """
        # Retrieve relevant documents
        search_results = self.search(query, top_k)
        context_docs = [doc for _, doc, _ in search_results]
        
        # Generate response
        response = self.generate_response(query, context_docs)
        
        return response
    
    def _save_index(self) -> None:
        """Save the RAG index to disk."""
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        
        index_data = {
            'embeddings': self.embeddings,
            'documents': self.documents
        }
        
        with open(self.index_path, 'wb') as f:
            pickle.dump(index_data, f)
        
        logger.info(f"RAG index saved to {self.index_path}")
    
    def load_index(self) -> None:
        """Load the RAG index from disk."""
        if not self.index_path.exists():
            logger.warning(f"No RAG index found at {self.index_path}")
            return
        
        with open(self.index_path, 'rb') as f:
            index_data = pickle.load(f)
        
        self.embeddings = index_data.get('embeddings', {})
        self.documents = index_data.get('documents', {})
        self.is_loaded = True
        
        logger.info(f"RAG index loaded from {self.index_path}")
