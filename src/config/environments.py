"""
Environment-specific database configuration.
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional

from pydantic import BaseSettings, validator


class DatabaseSettings(BaseSettings):
    """Database configuration with environment-specific overrides."""
    
    # PostgreSQL connection settings (default for development)
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "proposal_master"
    db_user: str = "postgres"
    db_password: str = ""
    
    # Connection pool settings
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    # SSL and security
    db_ssl_mode: str = "prefer"
    db_ssl_cert: Optional[str] = None
    db_ssl_key: Optional[str] = None
    db_ssl_root_cert: Optional[str] = None
    
    # Migration settings
    migrations_location: str = "src/config/migrations"
    auto_migrate: bool = False
    create_db_if_missing: bool = True
    
    # Backup settings
    backup_enabled: bool = False
    backup_schedule: str = "0 2 * * *"  # Daily at 2 AM
    backup_retention_days: int = 30
    backup_location: str = "backups/database"
    
    class Config:
        env_file = ".env"
        env_prefix = "DB_"
        case_sensitive = False
    
    @validator("db_password", pre=True)
    def validate_password(cls, v):
        """Ensure password is provided for production."""
        env = os.getenv("ENVIRONMENT", "development")
        if env == "production" and not v:
            raise ValueError("Database password is required for production")
        return v
    
    @property
    def database_url(self) -> str:
        """Construct database URL from components."""
        if self.db_password:
            auth = f"{self.db_user}:{self.db_password}"
        else:
            auth = self.db_user
        
        return f"postgresql+asyncpg://{auth}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    @property
    def sync_database_url(self) -> str:
        """Synchronous database URL for migrations."""
        if self.db_password:
            auth = f"{self.db_user}:{self.db_password}"
        else:
            auth = self.db_user
            
        return f"postgresql://{auth}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    @property
    def connection_args(self) -> Dict[str, Any]:
        """Additional connection arguments."""
        args = {}
        
        if self.db_ssl_mode != "disable":
            args["ssl"] = self.db_ssl_mode
            
        if self.db_ssl_cert:
            args["sslcert"] = self.db_ssl_cert
            
        if self.db_ssl_key:
            args["sslkey"] = self.db_ssl_key
            
        if self.db_ssl_root_cert:
            args["sslrootcert"] = self.db_ssl_root_cert
        
        return args


class EnvironmentConfig:
    """Environment-specific configurations."""
    
    @staticmethod
    def get_development_settings() -> DatabaseSettings:
        """Development environment settings."""
        return DatabaseSettings(
            db_host="localhost",
            db_port=5432,
            db_name="proposal_master_dev",
            db_user="postgres",
            db_password="",
            pool_size=5,
            max_overflow=10,
            auto_migrate=True,
            create_db_if_missing=True
        )
    
    @staticmethod
    def get_testing_settings() -> DatabaseSettings:
        """Testing environment settings."""
        return DatabaseSettings(
            db_host="localhost",
            db_port=5432,
            db_name="proposal_master_test",
            db_user="postgres", 
            db_password="",
            pool_size=2,
            max_overflow=5,
            auto_migrate=True,
            create_db_if_missing=True
        )
    
    @staticmethod
    def get_production_settings() -> DatabaseSettings:
        """Production environment settings."""
        return DatabaseSettings(
            # These should be overridden by environment variables
            pool_size=20,
            max_overflow=30,
            pool_timeout=60,
            pool_recycle=7200,
            db_ssl_mode="require",
            auto_migrate=False,
            create_db_if_missing=False,
            backup_enabled=True
        )
    
    @staticmethod
    def get_docker_settings() -> DatabaseSettings:
        """Docker environment settings."""
        return DatabaseSettings(
            db_host="db",  # Docker service name
            db_port=5432,
            db_name="proposal_master",
            db_user="postgres",
            db_password="postgres",
            pool_size=10,
            max_overflow=20,
            auto_migrate=True,
            create_db_if_missing=True
        )


def get_database_settings() -> DatabaseSettings:
    """Get database settings based on current environment."""
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "development":
        return EnvironmentConfig.get_development_settings()
    elif environment == "testing":
        return EnvironmentConfig.get_testing_settings()
    elif environment == "production":
        return EnvironmentConfig.get_production_settings()
    elif environment == "docker":
        return EnvironmentConfig.get_docker_settings()
    else:
        # Default to development
        return EnvironmentConfig.get_development_settings()


# Environment detection helper
def detect_environment() -> str:
    """Detect current environment based on various indicators."""
    # Check explicit environment variable
    if env := os.getenv("ENVIRONMENT"):
        return env.lower()
    
    # Check for container environment
    if Path("/.dockerenv").exists():
        return "docker"
    
    # Check for testing indicators
    if "pytest" in os.getenv("_", "") or "test" in os.getenv("PWD", ""):
        return "testing"
    
    # Check for production indicators
    if any(os.getenv(var) for var in ["HEROKU_APP_NAME", "AWS_LAMBDA_FUNCTION_NAME", "KUBERNETES_SERVICE_HOST"]):
        return "production"
    
    # Default to development
    return "development"


# Initialize settings based on detected environment
db_settings = get_database_settings()

# Export commonly used values
DATABASE_URL = db_settings.database_url
SYNC_DATABASE_URL = db_settings.sync_database_url
CONNECTION_ARGS = db_settings.connection_args
