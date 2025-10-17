"""
Add referral tracking columns to existing database
"""

import sqlite3
import os

def migrate():
    db_path = "nego_challenge.db"
    
    if not os.path.exists(db_path):
        print("✅ No existing database found.")
        return
    
    print(f"🔄 Migrating database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check existing columns
        cursor.execute("PRAGMA table_info(waitlist)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Add referral_code if missing
        if "referral_code" not in columns:
            print("📝 Adding referral_code column...")
            cursor.execute("ALTER TABLE waitlist ADD COLUMN referral_code VARCHAR")
            
        # Add referred_by if missing
        if "referred_by" not in columns:
            print("📝 Adding referred_by column...")
            cursor.execute("ALTER TABLE waitlist ADD COLUMN referred_by VARCHAR")
            
        # Add referral_count if missing
        if "referral_count" not in columns:
            print("📝 Adding referral_count column...")
            cursor.execute("ALTER TABLE waitlist ADD COLUMN referral_count INTEGER DEFAULT 0")
        
        # Check chat_sessions for discount_percentage
        cursor.execute("PRAGMA table_info(chat_sessions)")
        session_columns = [row[1] for row in cursor.fetchall()]
        
        if "discount_percentage" not in session_columns:
            print("📝 Adding discount_percentage column...")
            cursor.execute("ALTER TABLE chat_sessions ADD COLUMN discount_percentage FLOAT")
        
        if "referral_code" not in session_columns:
            print("📝 Adding referral_code to chat_sessions...")
            cursor.execute("ALTER TABLE chat_sessions ADD COLUMN referral_code VARCHAR")
            
        if "referred_by" not in session_columns:
            print("📝 Adding referred_by to chat_sessions...")
            cursor.execute("ALTER TABLE chat_sessions ADD COLUMN referred_by VARCHAR")
        
        conn.commit()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()

