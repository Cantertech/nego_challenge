"""
Database Migration Script
Adds minimum_price column to existing chat_sessions
"""

import sqlite3
import os

def migrate():
    db_path = "nego_challenge.db"
    
    if not os.path.exists(db_path):
        print("✅ No existing database found. New schema will be created automatically.")
        return
    
    print(f"🔄 Migrating database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if minimum_price column exists
        cursor.execute("PRAGMA table_info(chat_sessions)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "minimum_price" in columns:
            print("✅ Database already up to date!")
            return
        
        # Add minimum_price column with default value
        print("📝 Adding minimum_price column...")
        cursor.execute("""
            ALTER TABLE chat_sessions 
            ADD COLUMN minimum_price FLOAT NOT NULL DEFAULT 380
        """)
        
        conn.commit()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()



