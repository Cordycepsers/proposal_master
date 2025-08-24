"""
Database migration scripts and schema initialization.
"""
import asyncio
import logging
from pathlib import Path
from typing import Optional

from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError

from ..config.database import AsyncSessionLocal, async_engine as engine, Base
from ..models.core import (
    TenderOpportunity, Requirement, Proposal, WonBid, ProjectDocumentation, Document
)

logger = logging.getLogger(__name__)


class DatabaseMigrator:
    """Handles database schema creation and migrations."""
    
    def __init__(self):
        self.engine = engine
        self.migrations_dir = Path(__file__).parent / "migrations"
        self.migrations_dir.mkdir(exist_ok=True)
    
    async def create_database_if_not_exists(self, database_name: str = "proposal_master") -> bool:
        """Create database if it doesn't exist."""
        # For SQLite, the database is created automatically on connection if it doesn't exist.
        if self.engine.url.drivername.startswith('sqlite'):
            logger.info(f"Using SQLite, database '{database_name}' will be created automatically.")
            return True

        try:
            # Connect to postgres default database to create our database
            temp_engine_url = str(self.engine.url).replace(f"/{database_name}", "/postgres")
            
            from sqlalchemy.ext.asyncio import create_async_engine
            temp_engine = create_async_engine(temp_engine_url)
            
            async with temp_engine.connect() as conn:
                # Check if database exists
                result = await conn.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                    {"db_name": database_name}
                )
                
                if result.fetchone() is None:
                    # Database doesn't exist, create it
                    await conn.execute(text("COMMIT"))  # End any existing transaction
                    await conn.execute(text(f"CREATE DATABASE {database_name}"))
                    logger.info(f"Created database: {database_name}")
                    await temp_engine.dispose()
                    return True
                else:
                    logger.info(f"Database {database_name} already exists")
                    await temp_engine.dispose()
                    return False
                    
        except SQLAlchemyError as e:
            logger.error(f"Error creating database: {e}")
            if 'temp_engine' in locals():
                await temp_engine.dispose()
            raise
    
    async def create_all_tables(self) -> bool:
        """Create all tables from models."""
        try:
            async with self.engine.begin() as conn:
                # Create all tables
                await conn.run_sync(Base.metadata.create_all)
                logger.info("Successfully created all tables")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    async def drop_all_tables(self) -> bool:
        """Drop all tables (use with caution!)."""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                logger.info("Successfully dropped all tables")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Error dropping tables: {e}")
            raise
    
    async def check_table_exists(self, table_name: str) -> bool:
        """Check if a specific table exists."""
        try:
            async with self.engine.connect() as conn:
                inspector = await conn.run_sync(
                    lambda sync_conn: inspect(sync_conn)
                )
                tables = await conn.run_sync(
                    lambda sync_conn: inspector.get_table_names()
                )
                return table_name in tables
                
        except SQLAlchemyError as e:
            logger.error(f"Error checking table existence: {e}")
            return False
    
    async def get_database_schema_info(self) -> dict:
        """Get information about current database schema."""
        try:
            async with self.engine.connect() as conn:
                inspector = await conn.run_sync(
                    lambda sync_conn: inspect(sync_conn)
                )
                
                tables = await conn.run_sync(
                    lambda sync_conn: inspector.get_table_names()
                )
                
                schema_info = {
                    "tables": {},
                    "total_tables": len(tables)
                }
                
                for table_name in tables:
                    columns = await conn.run_sync(
                        lambda sync_conn: inspector.get_columns(table_name)
                    )
                    indexes = await conn.run_sync(
                        lambda sync_conn: inspector.get_indexes(table_name)
                    )
                    
                    schema_info["tables"][table_name] = {
                        "columns": len(columns),
                        "indexes": len(indexes),
                        "column_details": [
                            {
                                "name": col["name"], 
                                "type": str(col["type"]),
                                "nullable": col["nullable"]
                            } 
                            for col in columns
                        ]
                    }
                
                return schema_info
                
        except SQLAlchemyError as e:
            logger.error(f"Error getting schema info: {e}")
            return {"error": str(e)}
    
    async def seed_sample_data(self) -> bool:
        """Insert sample data for testing."""
        try:
            async with AsyncSessionLocal() as session:
                # Check if data already exists
                result = await session.execute(
                    text("SELECT COUNT(*) FROM tender_opportunities")
                )
                count = result.scalar()
                
                if count > 0:
                    logger.info("Sample data already exists, skipping seed")
                    return True
                
                # Create sample tender opportunity
                from ..models.core import TenderStatus, OpportunitySource
                
                sample_opportunity = TenderOpportunity(
                    tender_id="SAMPLE_001",
                    title="Sample RFP - Digital Transformation Consulting",
                    description="A sample RFP for testing the automated proposal system",
                    source=OpportunitySource.MANUAL,
                    status=TenderStatus.DISCOVERED,
                    procuring_organization="Sample UN Agency",
                    organization_type="UN",
                    country="Global",
                    estimated_budget=100000.0,
                    currency="USD",
                    relevance_score=85.0,
                    tags=["digital-transformation", "consulting", "sample"]
                )
                
                session.add(sample_opportunity)
                await session.commit()
                
                logger.info("Successfully seeded sample data")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Error seeding sample data: {e}")
            raise
    
    async def run_health_check(self) -> dict:
        """Run comprehensive database health check."""
        health_status = {
            "database_connection": False,
            "tables_created": False,
            "sample_data_accessible": False,
            "indexes_working": False,
            "schema_info": {},
            "errors": []
        }
        
        try:
            # Test connection
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                health_status["database_connection"] = True
            
            # Check tables
            schema_info = await self.get_database_schema_info()
            if "error" not in schema_info:
                health_status["tables_created"] = schema_info["total_tables"] > 0
                health_status["schema_info"] = schema_info
            
            # Test data access
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    text("SELECT COUNT(*) FROM tender_opportunities")
                )
                count = result.scalar()
                health_status["sample_data_accessible"] = True
                health_status["schema_info"]["sample_records"] = count
                
                # Test index usage
                result = await session.execute(
                    text("SELECT COUNT(*) FROM pg_indexes WHERE tablename LIKE 'tender%'")
                )
                index_count = result.scalar()
                health_status["indexes_working"] = index_count > 0
                
        except Exception as e:
            health_status["errors"].append(str(e))
            logger.error(f"Health check error: {e}")
        
        return health_status


async def initialize_database(
    create_db: bool = True,
    create_tables: bool = True,
    seed_data: bool = False,
    database_name: str = "proposal_master"
) -> dict:
    """
    Complete database initialization process.
    
    Args:
        create_db: Whether to create the database if it doesn't exist
        create_tables: Whether to create tables from models
        seed_data: Whether to insert sample data
        database_name: Name of the database to create
    
    Returns:
        Dict with initialization results and status
    """
    migrator = DatabaseMigrator()
    results = {
        "database_created": False,
        "tables_created": False,
        "data_seeded": False,
        "health_check": {},
        "errors": []
    }
    
    try:
        # Step 1: Create database if needed
        if create_db:
            results["database_created"] = await migrator.create_database_if_not_exists(database_name)
        
        # Step 2: Create tables
        if create_tables:
            results["tables_created"] = await migrator.create_all_tables()
        
        # Step 3: Seed sample data
        if seed_data:
            results["data_seeded"] = await migrator.seed_sample_data()
        
        # Step 4: Run health check
        results["health_check"] = await migrator.run_health_check()
        
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        results["errors"].append(str(e))
        logger.error(f"Database initialization failed: {e}")
    
    finally:
        # Ensure engine cleanup
        await engine.dispose()
    
    return results


if __name__ == "__main__":
    """Run database initialization from command line."""
    import sys
    
    async def main():
        logger.info("Starting database initialization...")
        
        # Parse command line arguments
        create_db = "--skip-db" not in sys.argv
        create_tables = "--skip-tables" not in sys.argv
        seed_data = "--seed" in sys.argv
        
        results = await initialize_database(
            create_db=create_db,
            create_tables=create_tables,
            seed_data=seed_data
        )
        
        # Print results
        print("\n" + "="*50)
        print("DATABASE INITIALIZATION RESULTS")
        print("="*50)
        print(f"Database created: {results['database_created']}")
        print(f"Tables created: {results['tables_created']}")
        print(f"Data seeded: {results['data_seeded']}")
        
        if results["health_check"]:
            health = results["health_check"]
            print(f"Connection working: {health['database_connection']}")
            print(f"Tables accessible: {health['tables_created']}")
            print(f"Data accessible: {health['sample_data_accessible']}")
            print(f"Indexes working: {health['indexes_working']}")
            
            if "schema_info" in health and "total_tables" in health["schema_info"]:
                print(f"Total tables: {health['schema_info']['total_tables']}")
        
        if results["errors"]:
            print("\nERRORS:")
            for error in results["errors"]:
                print(f"  - {error}")
        
        print("="*50)
    
    asyncio.run(main())
