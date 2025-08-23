#!/usr/bin/env python3
"""
Database initialization and management script.
Run this script to set up the database for the Automated RFP System.
"""
import asyncio
import sys
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.migrations import initialize_database
from src.config.environments import detect_environment, get_database_settings
from src.utils.logging_config import setup_logging


def print_banner():
    """Print script banner."""
    print("\n" + "="*60)
    print("  AUTOMATED RFP SYSTEM - DATABASE INITIALIZATION")
    print("="*60)


def print_environment_info():
    """Print current environment information."""
    env = detect_environment()
    settings = get_database_settings()
    
    print(f"\nEnvironment: {env.upper()}")
    print(f"Database: {settings.db_name}")
    print(f"Host: {settings.db_host}:{settings.db_port}")
    print(f"User: {settings.db_user}")
    print(f"SSL Mode: {settings.db_ssl_mode}")
    print(f"Pool Size: {settings.pool_size}")


def parse_arguments() -> dict:
    """Parse command line arguments."""
    args = {
        "create_db": True,
        "create_tables": True,
        "seed_data": False,
        "skip_confirmation": False,
        "verbose": False
    }
    
    for arg in sys.argv[1:]:
        if arg == "--skip-db":
            args["create_db"] = False
        elif arg == "--skip-tables":
            args["create_tables"] = False
        elif arg == "--seed":
            args["seed_data"] = True
        elif arg in ["-y", "--yes"]:
            args["skip_confirmation"] = True
        elif arg in ["-v", "--verbose"]:
            args["verbose"] = True
        elif arg in ["-h", "--help"]:
            print_help()
            sys.exit(0)
    
    return args


def print_help():
    """Print help information."""
    print("""
Database Initialization Script

Usage: python init_database.py [OPTIONS]

Options:
  --skip-db          Skip database creation
  --skip-tables      Skip table creation  
  --seed             Insert sample data for testing
  -y, --yes          Skip confirmation prompts
  -v, --verbose      Enable verbose logging
  -h, --help         Show this help message

Environment Variables:
  ENVIRONMENT        Set to 'development', 'testing', 'production', or 'docker'
  DB_HOST           Database host (default: localhost)
  DB_PORT           Database port (default: 5432)
  DB_NAME           Database name (default: proposal_master)
  DB_USER           Database user (default: postgres)
  DB_PASSWORD       Database password

Examples:
  python init_database.py                    # Full initialization
  python init_database.py --seed             # Initialize with sample data
  python init_database.py --skip-db --seed   # Skip DB creation, seed data
  python init_database.py -y -v              # Auto-confirm with verbose output
""")


def confirm_action(message: str) -> bool:
    """Get user confirmation."""
    while True:
        response = input(f"{message} (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' or 'n'")


async def main():
    """Main initialization process."""
    print_banner()
    
    # Parse arguments
    args = parse_arguments()
    
    # Setup logging
    log_level_str = "DEBUG" if args["verbose"] else "INFO"
    setup_logging(log_level=log_level_str)
    
    # Print environment information
    print_environment_info()
    
    # Confirm actions unless skipped
    if not args["skip_confirmation"]:
        print("\nPlanned Actions:")
        if args["create_db"]:
            print("  ✓ Create database if it doesn't exist")
        if args["create_tables"]:
            print("  ✓ Create all tables from models")
        if args["seed_data"]:
            print("  ✓ Insert sample data for testing")
        
        if not confirm_action("\nProceed with initialization?"):
            print("Initialization cancelled.")
            return
    
    # Run initialization
    print("\nStarting database initialization...")
    
    try:
        results = await initialize_database(
            create_db=args["create_db"],
            create_tables=args["create_tables"],
            seed_data=args["seed_data"]
        )
        
        # Print detailed results
        print("\n" + "="*60)
        print("INITIALIZATION RESULTS")
        print("="*60)
        
        print(f"Database created: {'✓' if results['database_created'] else '○'}")
        print(f"Tables created: {'✓' if results['tables_created'] else '○'}")
        print(f"Sample data seeded: {'✓' if results['data_seeded'] else '○'}")
        
        # Health check results
        if results["health_check"]:
            health = results["health_check"]
            print(f"\nHealth Check:")
            print(f"  Connection: {'✓' if health['database_connection'] else '✗'}")
            print(f"  Tables: {'✓' if health['tables_created'] else '✗'}")
            print(f"  Data Access: {'✓' if health['sample_data_accessible'] else '✗'}")
            print(f"  Indexes: {'✓' if health['indexes_working'] else '✗'}")
            
            if "schema_info" in health:
                schema = health["schema_info"]
                if "total_tables" in schema:
                    print(f"  Total Tables: {schema['total_tables']}")
                if "sample_records" in schema:
                    print(f"  Sample Records: {schema['sample_records']}")
        
        # Show errors if any
        if results["errors"]:
            print(f"\nErrors encountered:")
            for error in results["errors"]:
                print(f"  ✗ {error}")
            print("\n⚠️  Initialization completed with errors")
            sys.exit(1)
        else:
            print(f"\n✅ Database initialization completed successfully!")
            
            # Show next steps
            print(f"\nNext Steps:")
            print(f"  • Start the API server: python src/api/main.py")
            print(f"  • Run tests: pytest")
            print(f"  • View API docs: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\n❌ Initialization failed: {e}")
        if args["verbose"]:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    # Run main process
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Initialization cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
