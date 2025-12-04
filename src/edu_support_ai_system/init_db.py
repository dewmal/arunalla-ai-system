"""Database initialization script for edu_support_ai_system"""
import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from edu_support_ai_system.config import settings
from edu_support_ai_system.database_pg import init_db, Base, engine


def initialize_database():
    """Initialize the PostgreSQL database"""
    if not settings.DATABASE_URL:
        print("ERROR: DATABASE_URL environment variable is not set")
        print("Please set DATABASE_URL to initialize the database")
        sys.exit(1)
    
    print(f"Initializing database...")
    print(f"Database URL: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'localhost'}")
    
    try:
        # Initialize database connection and create tables
        init_db(settings.DATABASE_URL)
        
        print("✓ Database connection established")
        print("✓ Creating tables...")
        
        # Tables are created in init_db, but we can verify here
        Base.metadata.create_all(bind=engine)
        
        print("✓ Database tables created successfully!")
        print("\nCreated tables:")
        for table in Base.metadata.sorted_tables:
            print(f"  - {table.name}")
        
        print("\nDatabase initialization complete!")
        
    except Exception as e:
        print(f"✗ Failed to initialize database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    initialize_database()
