"""
Verify database connection and tables
"""
import os
from sqlalchemy import create_engine, inspect, text
from dotenv import load_dotenv

load_dotenv()

def verify_database():
    """Verify database connection and show table info"""
    
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("[ERROR] DATABASE_URL not set!")
        return False
    
    # Fix postgres:// to postgresql:// if needed
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    print("[*] Verifying database connection...")
    print(f"[*] Database URL: {database_url[:50]}...")
    
    try:
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"[SUCCESS] Connected to PostgreSQL!")
            print(f"[INFO] Version: {version[:80]}")
        
        # Check tables
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if tables:
            print(f"\n[INFO] Tables found: {len(tables)}")
            for table in tables:
                columns = inspector.get_columns(table)
                print(f"  - {table}: {len(columns)} columns")
        else:
            print("\n[WARNING] No tables found. Run 'python init_database.py' to create them.")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Database connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    verify_database()

