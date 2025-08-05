"""
Vector Database Configuration

This module provides configuration management for the vector database,
including environment-specific settings and model configurations.
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path
from dataclasses import dataclass
from src.config.settings import settings

@dataclass
class VectorConfig:
    """Vector database configuration"""
    # Embedding model settings
    embedding_model: str = "all-MiniLM-L6-v2"
    dimension: int = 384
    
    # Index settings
    index_type: str = "IndexFlatIP"  # IndexFlatIP, IndexFlatL2, IndexIVFFlat, IndexHNSW
    metric: str = "cosine"  # cosine, euclidean, manhattan
    
    # FAISS-specific settings
    nlist: int = 100  # Number of centroids for IVF indices
    nprobe: int = 10  # Number of centroids to search
    
    # Storage settings
    index_path: str = "data/embeddings/vector_index.faiss"
    metadata_path: str = "data/embeddings/metadata.json"
    store_on_disk: bool = True
    
    # Processing settings
    batch_size: int = 32
    max_retries: int = 3
    chunk_size: int = 1000
    chunk_overlap: int = 100
    
    # Performance settings
    max_concurrent_operations: int = 5
    enable_gpu: bool = False  # Set to True if FAISS-GPU is available
    
    # API settings (for external embedding providers)
    openai_api_key: Optional[str] = None
    openai_model: str = "text-embedding-ada-002"
    anthropic_api_key: Optional[str] = None
    
    def __post_init__(self):
        """Initialize configuration after creation"""
        # Load API keys from environment
        self.openai_api_key = self.openai_api_key or os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = self.anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.metadata_path), exist_ok=True)
        
        # Set embedding dimension based on model
        if self.embedding_model.startswith("text-embedding"):
            # OpenAI models
            openai_dimensions = {
                "text-embedding-ada-002": 1536,
                "text-embedding-3-small": 1536,
                "text-embedding-3-large": 3072
            }
            self.dimension = openai_dimensions.get(self.embedding_model, 1536)
        elif "MiniLM" in self.embedding_model:
            self.dimension = 384
        elif "large" in self.embedding_model.lower():
            self.dimension = 1024
        # Keep existing dimension if not recognized

def get_vector_config() -> VectorConfig:
    """Get vector database configuration from environment and settings"""
    config = VectorConfig()
    
    # Override with environment variables if present
    config.embedding_model = os.getenv("VECTOR_EMBEDDING_MODEL", config.embedding_model)
    config.index_type = os.getenv("VECTOR_INDEX_TYPE", config.index_type)
    config.metric = os.getenv("VECTOR_METRIC", config.metric)
    
    # Parse integer settings
    try:
        config.batch_size = int(os.getenv("VECTOR_BATCH_SIZE", config.batch_size))
        config.chunk_size = int(os.getenv("VECTOR_CHUNK_SIZE", config.chunk_size))
        config.chunk_overlap = int(os.getenv("VECTOR_CHUNK_OVERLAP", config.chunk_overlap))
        config.nlist = int(os.getenv("VECTOR_NLIST", config.nlist))
        config.nprobe = int(os.getenv("VECTOR_NPROBE", config.nprobe))
        config.max_concurrent_operations = int(os.getenv("VECTOR_MAX_CONCURRENT", config.max_concurrent_operations))
    except ValueError as e:
        # Use defaults if environment variables are invalid
        pass
    
    # Parse boolean settings
    config.store_on_disk = os.getenv("VECTOR_STORE_ON_DISK", "true").lower() in ("true", "1", "yes")
    config.enable_gpu = os.getenv("VECTOR_ENABLE_GPU", "false").lower() in ("true", "1", "yes")
    
    # Custom paths if specified
    if os.getenv("VECTOR_INDEX_PATH"):
        config.index_path = os.getenv("VECTOR_INDEX_PATH")
        config.metadata_path = config.index_path.replace('.faiss', '_metadata.json')
    
    return config

def get_embedding_model_info(model_name: str) -> Dict[str, Any]:
    """Get information about an embedding model"""
    model_info = {
        # SentenceTransformers models
        "all-MiniLM-L6-v2": {
            "provider": "sentence-transformers",
            "dimension": 384,
            "max_seq_length": 256,
            "description": "Lightweight, fast model good for general purpose",
            "performance": "high_speed",
            "quality": "good"
        },
        "all-mpnet-base-v2": {
            "provider": "sentence-transformers",
            "dimension": 768,
            "max_seq_length": 384,
            "description": "Higher quality model with better semantic understanding",
            "performance": "medium_speed",
            "quality": "excellent"
        },
        "multi-qa-MiniLM-L6-cos-v1": {
            "provider": "sentence-transformers",
            "dimension": 384,
            "max_seq_length": 512,
            "description": "Optimized for question-answering and retrieval",
            "performance": "high_speed",
            "quality": "very_good"
        },
        "paraphrase-multilingual-MiniLM-L12-v2": {
            "provider": "sentence-transformers",
            "dimension": 384,
            "max_seq_length": 128,
            "description": "Multilingual model supporting 50+ languages",
            "performance": "medium_speed",
            "quality": "good"
        },
        
        # OpenAI models
        "text-embedding-ada-002": {
            "provider": "openai",
            "dimension": 1536,
            "max_seq_length": 8191,
            "description": "OpenAI's general-purpose embedding model",
            "performance": "medium_speed",
            "quality": "excellent",
            "cost_per_1k_tokens": 0.0001
        },
        "text-embedding-3-small": {
            "provider": "openai",
            "dimension": 1536,
            "max_seq_length": 8191,
            "description": "OpenAI's newer, improved small model",
            "performance": "high_speed",
            "quality": "excellent",
            "cost_per_1k_tokens": 0.00002
        },
        "text-embedding-3-large": {
            "provider": "openai",
            "dimension": 3072,
            "max_seq_length": 8191,
            "description": "OpenAI's most capable embedding model",
            "performance": "medium_speed",
            "quality": "outstanding",
            "cost_per_1k_tokens": 0.00013
        }
    }
    
    return model_info.get(model_name, {
        "provider": "unknown",
        "dimension": 384,
        "max_seq_length": 512,
        "description": "Unknown model",
        "performance": "unknown",
        "quality": "unknown"
    })

def validate_vector_config(config: VectorConfig) -> Dict[str, Any]:
    """Validate vector configuration and return status"""
    issues = []
    warnings = []
    
    # Check if required dependencies are available
    try:
        import faiss
    except ImportError:
        issues.append("FAISS library not installed. Run: pip install faiss-cpu")
    
    try:
        import sentence_transformers
    except ImportError:
        if config.embedding_model and not config.embedding_model.startswith("text-embedding"):
            issues.append("sentence-transformers library not installed. Run: pip install sentence-transformers")
    
    # Check API keys for external providers
    if config.embedding_model.startswith("text-embedding"):
        if not config.openai_api_key:
            issues.append("OpenAI API key required for text-embedding models")
    
    # Check index type compatibility
    valid_index_types = ["IndexFlatIP", "IndexFlatL2", "IndexIVFFlat", "IndexHNSW"]
    if config.index_type not in valid_index_types:
        issues.append(f"Invalid index type: {config.index_type}. Valid types: {valid_index_types}")
    
    # Check dimension limits
    if config.embedding_dimension < 1 or config.embedding_dimension > 10000:
        issues.append(f"Invalid embedding dimension: {config.embedding_dimension}")
    
    # Check batch size
    if config.batch_size < 1 or config.batch_size > 1000:
        warnings.append(f"Unusual batch size: {config.batch_size}. Recommended: 16-128")
    
    # Check chunk settings
    if config.chunk_overlap >= config.chunk_size:
        issues.append("Chunk overlap must be less than chunk size")
    
    # Check paths
    try:
        os.makedirs(os.path.dirname(config.index_path), exist_ok=True)
        os.makedirs(os.path.dirname(config.metadata_path), exist_ok=True)
    except Exception as e:
        issues.append(f"Cannot create directories for vector storage: {e}")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "config": config
    }

def get_recommended_config(use_case: str = "general") -> VectorConfig:
    """Get recommended configuration for specific use cases"""
    configs = {
        "general": VectorConfig(
            embedding_model="all-MiniLM-L6-v2",
            index_type="IndexFlatIP",
            batch_size=32,
            chunk_size=1000,
            chunk_overlap=100
        ),
        
        "high_quality": VectorConfig(
            embedding_model="all-mpnet-base-v2",
            index_type="IndexFlatIP",
            batch_size=16,
            chunk_size=1200,
            chunk_overlap=120
        ),
        
        "large_scale": VectorConfig(
            embedding_model="all-MiniLM-L6-v2",
            index_type="IndexIVFFlat",
            nlist=500,
            nprobe=20,
            batch_size=64,
            chunk_size=800,
            chunk_overlap=80
        ),
        
        "openai": VectorConfig(
            embedding_model="text-embedding-3-small",
            index_type="IndexFlatIP",
            batch_size=100,  # OpenAI allows larger batches
            chunk_size=1500,
            chunk_overlap=150
        ),
        
        "multilingual": VectorConfig(
            embedding_model="paraphrase-multilingual-MiniLM-L12-v2",
            index_type="IndexFlatIP",
            batch_size=24,
            chunk_size=1000,
            chunk_overlap=100
        ),
        
        "qa_optimized": VectorConfig(
            embedding_model="multi-qa-MiniLM-L6-cos-v1",
            index_type="IndexFlatIP",
            batch_size=32,
            chunk_size=600,  # Smaller chunks for Q&A
            chunk_overlap=60
        )
    }
    
    return configs.get(use_case, configs["general"])

# Global configuration instance
_vector_config = None

def get_global_vector_config() -> VectorConfig:
    """Get global vector configuration (singleton pattern)"""
    global _vector_config
    if _vector_config is None:
        _vector_config = get_vector_config()
    return _vector_config

def update_global_vector_config(config: VectorConfig) -> None:
    """Update global vector configuration"""
    global _vector_config
    _vector_config = config
