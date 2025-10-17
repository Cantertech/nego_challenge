"""
Initialize database tables for Nego Challenge
Run this once to create all necessary tables
"""
import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv
from models import Base
from database import engine

load_dotenv()

def init_database():
    """Create all database tables"""
    print("[*] Initializing database...")
    print(f"[*] Database URL: {os.getenv('DATABASE_URL', 'Not set')[:50]}...")
    
    try:
        # Create all tables defined in models
        Base.metadata.create_all(bind=engine)
        
        # Verify tables were created
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print("[SUCCESS] Database initialized successfully!")
        print(f"[INFO] Tables created: {', '.join(tables)}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error initializing database: {str(e)}")
        return False

if __name__ == "__main__":
    success = init_database()
    if success:
        print("\n[SUCCESS] Database is ready to use!")
    else:
        print("\n[WARNING] Database initialization failed. Check the error above.")

