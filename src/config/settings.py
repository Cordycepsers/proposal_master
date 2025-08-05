# src/config/settings.py
import os

class Settings:
    # System settings
    SYSTEM_NAME = "Smart Proposal System"
    VERSION = "1.0.0"
    
    # Database settings (if needed)
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///proposals.db")
    
    # API settings
    MAX_RETRIES = 3
    TIMEOUT_SECONDS = 30
    
    # Logging settings
    LOG_LEVEL = "INFO"
    LOG_FILE = "logs/proposal_system.log"
    
    # Agent settings
    AGENT_TIMEOUT = 60  # seconds

import os
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "5432"))
    name: str = os.getenv("DB_NAME", "proposal_master")
    user: str = os.getenv("DB_USER", "postgres")
    password: str = os.getenv("DB_PASSWORD", "")
    pool_size: int = int(os.getenv("DB_POOL_SIZE", "10"))
    max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))

@dataclass
class AIConfig:
    """AI and ML model configuration"""
    # OpenAI settings
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4")
    openai_temperature: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    openai_max_tokens: int = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
    
    # Azure OpenAI settings (alternative)
    azure_openai_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    azure_openai_key: str = os.getenv("AZURE_OPENAI_KEY", "")
    azure_openai_version: str = os.getenv("AZURE_OPENAI_VERSION", "2023-12-01-preview")
    
    # Embedding model settings
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
    embedding_dimensions: int = int(os.getenv("EMBEDDING_DIMENSIONS", "1536"))
    
    # Local model settings
    use_local_models: bool = os.getenv("USE_LOCAL_MODELS", "false").lower() == "true"
    local_model_path: str = os.getenv("LOCAL_MODEL_PATH", "models/")
    
    # Content generation settings
    max_proposal_length: int = int(os.getenv("MAX_PROPOSAL_LENGTH", "10000"))
    min_section_length: int = int(os.getenv("MIN_SECTION_LENGTH", "100"))

@dataclass
class FileStorageConfig:
    """File storage and processing configuration"""
    # File paths
    upload_dir: Path = DATA_DIR / "uploads"
    documents_dir: Path = DATA_DIR / "documents"
    templates_dir: Path = DATA_DIR / "templates"
    cache_dir: Path = DATA_DIR / "cache"
    embeddings_dir: Path = DATA_DIR / "embeddings"
    
    # File size limits (in bytes)
    max_file_size: int = int(os.getenv("MAX_FILE_SIZE", "50000000"))  # 50MB
    max_batch_size: int = int(os.getenv("MAX_BATCH_SIZE", "100"))
    
    # Supported file formats
    supported_formats: List[str] = field(default_factory=lambda: [
        ".pdf", ".docx", ".doc", ".txt", ".md", ".rtf"
    ])
    
    # Document processing settings
    ocr_enabled: bool = os.getenv("OCR_ENABLED", "true").lower() == "true"
    ocr_language: str = os.getenv("OCR_LANGUAGE", "eng")
    
settings = Settings()
