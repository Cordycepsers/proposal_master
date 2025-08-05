"""
Similarity engine for comparing proposals, documents, and requirements.

This module provides advanced similarity calculation capabilities
for proposal matching and analysis.
"""

from typing import List, Dict, Any, Tuple, Optional
import logging
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)


class SimilarityType(Enum):
    """Types of similarity calculations."""
    COSINE = "cosine"
    JACCARD = "jaccard"
    SEMANTIC = "semantic"
    STRUCTURAL = "structural"


class SimilarityEngine:
    """Advanced similarity calculation engine."""
    
    def __init__(self):
        self.cache = {}
    
    def calculate_similarity(
        self, 
        doc1: Dict[str, Any], 
        doc2: Dict[str, Any], 
        similarity_type: SimilarityType = SimilarityType.COSINE
    ) -> float:
        """
        Calculate similarity between two documents.
        
        Args:
            doc1: First document dictionary
            doc2: Second document dictionary
            similarity_type: Type of similarity to calculate
            
        Returns:
            Similarity score between 0 and 1
        """
        # Create cache key
        cache_key = f"{doc1.get('file_name', '')}_{doc2.get('file_name', '')}_{similarity_type.value}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        if similarity_type == SimilarityType.COSINE:
            score = self._cosine_similarity(doc1, doc2)
        elif similarity_type == SimilarityType.JACCARD:
            score = self._jaccard_similarity(doc1, doc2)
        elif similarity_type == SimilarityType.SEMANTIC:
            score = self._semantic_similarity(doc1, doc2)
        elif similarity_type == SimilarityType.STRUCTURAL:
            score = self._structural_similarity(doc1, doc2)
        else:
            raise ValueError(f"Unsupported similarity type: {similarity_type}")
        
        self.cache[cache_key] = score
        return score
    
    def _cosine_similarity(self, doc1: Dict[str, Any], doc2: Dict[str, Any]) -> float:
        """Calculate cosine similarity between documents."""
        content1 = doc1.get('content', '').lower()
        content2 = doc2.get('content', '').lower()
        
        # Simple word-based vector representation
        words1 = set(content1.split())
        words2 = set(content2.split())
        all_words = words1.union(words2)
        
        if not all_words:
            return 0.0
        
        # Create vectors
        vec1 = np.array([1 if word in words1 else 0 for word in all_words])
        vec2 = np.array([1 if word in words2 else 0 for word in all_words])
        
        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _jaccard_similarity(self, doc1: Dict[str, Any], doc2: Dict[str, Any]) -> float:
        """Calculate Jaccard similarity between documents."""
        content1 = doc1.get('content', '').lower()
        content2 = doc2.get('content', '').lower()
        
        words1 = set(content1.split())
        words2 = set(content2.split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    def _semantic_similarity(self, doc1: Dict[str, Any], doc2: Dict[str, Any]) -> float:
        """Calculate semantic similarity (placeholder for advanced NLP)."""
        # In production, this would use advanced NLP models
        # For now, using a combination of cosine and structural similarity
        cosine_score = self._cosine_similarity(doc1, doc2)
        structural_score = self._structural_similarity(doc1, doc2)
        
        return (cosine_score + structural_score) / 2
    
    def _structural_similarity(self, doc1: Dict[str, Any], doc2: Dict[str, Any]) -> float:
        """Calculate structural similarity based on document format and metadata."""
        # Compare file formats
        format_score = 1.0 if doc1.get('format') == doc2.get('format') else 0.5
        
        # Compare file sizes (normalized)
        size1 = doc1.get('file_size', 0)
        size2 = doc2.get('file_size', 0)
        
        if size1 == 0 and size2 == 0:
            size_score = 1.0
        elif size1 == 0 or size2 == 0:
            size_score = 0.0
        else:
            size_ratio = min(size1, size2) / max(size1, size2)
            size_score = size_ratio
        
        # Combine scores
        return (format_score + size_score) / 2
    
    def find_similar_documents(
        self, 
        target_doc: Dict[str, Any], 
        candidate_docs: List[Dict[str, Any]], 
        threshold: float = 0.5,
        similarity_type: SimilarityType = SimilarityType.COSINE
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Find documents similar to a target document.
        
        Args:
            target_doc: Document to find matches for
            candidate_docs: List of candidate documents
            threshold: Minimum similarity threshold
            similarity_type: Type of similarity to use
            
        Returns:
            List of (document, similarity_score) tuples above threshold
        """
        similar_docs = []
        
        for candidate in candidate_docs:
            similarity = self.calculate_similarity(target_doc, candidate, similarity_type)
            
            if similarity >= threshold:
                similar_docs.append((candidate, similarity))
        
        # Sort by similarity score (descending)
        similar_docs.sort(key=lambda x: x[1], reverse=True)
        
        return similar_docs
    
    def compare_proposals(
        self, 
        proposal1: Dict[str, Any], 
        proposal2: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Comprehensive comparison between two proposals.
        
        Args:
            proposal1: First proposal document
            proposal2: Second proposal document
            
        Returns:
            Dictionary with different similarity scores
        """
        comparison = {}
        
        for sim_type in SimilarityType:
            try:
                score = self.calculate_similarity(proposal1, proposal2, sim_type)
                comparison[sim_type.value] = score
            except Exception as e:
                logger.warning(f"Error calculating {sim_type.value} similarity: {e}")
                comparison[sim_type.value] = 0.0
        
        # Calculate overall similarity (weighted average)
        weights = {
            SimilarityType.COSINE.value: 0.3,
            SimilarityType.JACCARD.value: 0.2,
            SimilarityType.SEMANTIC.value: 0.4,
            SimilarityType.STRUCTURAL.value: 0.1
        }
        
        overall_score = sum(
            comparison[sim_type] * weight 
            for sim_type, weight in weights.items()
        )
        
        comparison['overall'] = overall_score
        
        return comparison
    
    def clear_cache(self) -> None:
        """Clear the similarity calculation cache."""
        self.cache.clear()
        logger.info("Similarity cache cleared")
