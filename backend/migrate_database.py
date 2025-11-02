#!/usr/bin/env python3
"""
Migrate SQLite database from old schema (portfolio_id) to new schema (mindfolio_id)
"""
import sqlite3
import shutil
from pathlib import Path

DB_PATH = "/app/data/flowmind.db"
BACKUP_PATH = "/app/data/flowmind.db.backup"

def migrate_database():
    """Migrate database schema"""
    print("🔄 Starting database migration...")
    
    # Backup original database
    print(f"📦 Creating backup: {BACKUP_PATH}")
    shutil.copy2(DB_PATH, BACKUP_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if migration is needed
        cursor.execute("PRAGMA table_info(accounts)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if "mindfolio_id" in columns:
            print("✅ Database already migrated")
            return
        
        if "portfolio_id" not in columns:
            print("⚠️  No migration needed - creating fresh schema")
            conn.close()
            # Delete and reinitialize
            Path(DB_PATH).unlink()
            from database import DatabaseManager
            DatabaseManager()
            print("✅ Fresh database created")
            return
        
        print("🔧 Migrating schema...")
        
        # Start transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # 1. Rename portfolios to mindfolios if exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='portfolios'")
        if cursor.fetchone():
            print("  - Renaming portfolios → mindfolios")
            cursor.execute("DROP TABLE IF EXISTS mindfolios")
            cursor.execute("ALTER TABLE portfolios RENAME TO mindfolios")
        
        # 2. Create new accounts table with mindfolio_id
        print("  - Migrating accounts table")
        cursor.execute("""
            CREATE TABLE accounts_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mindfolio_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                broker TEXT,
                currency TEXT NOT NULL DEFAULT 'USD',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (mindfolio_id) REFERENCES mindfolios(id)
            )
        """)
        
        # Copy data from old table
        cursor.execute("""
            INSERT INTO accounts_new (id, mindfolio_id, name, broker, currency, created_at)
            SELECT id, portfolio_id, name, broker, currency, created_at
            FROM accounts
        """)
        
        # Drop old table and rename new one
        cursor.execute("DROP TABLE accounts")
        cursor.execute("ALTER TABLE accounts_new RENAME TO accounts")
        cursor.execute("CREATE INDEX idx_accounts_mindfolio ON accounts(mindfolio_id)")
        
        # 3. Create new buckets table if needed
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='buckets'")
        if cursor.fetchone():
            print("  - Migrating buckets table")
            cursor.execute("""
                CREATE TABLE buckets_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mindfolio_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    start_value REAL DEFAULT 0,
                    notes TEXT,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    FOREIGN KEY (mindfolio_id) REFERENCES mindfolios(id)
                )
            """)
            
            cursor.execute("""
                INSERT INTO buckets_new (id, mindfolio_id, name, start_value, notes, created_at)
                SELECT id, portfolio_id, name, start_value, notes, created_at
                FROM buckets
            """)
            
            cursor.execute("DROP TABLE buckets")
            cursor.execute("ALTER TABLE buckets_new RENAME TO buckets")
        
        # Commit transaction
        conn.commit()
        print("✅ Migration completed successfully")
        print(f"💾 Backup saved at: {BACKUP_PATH}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        print("🔄 Restoring from backup...")
        conn.close()
        shutil.copy2(BACKUP_PATH, DB_PATH)
        print("✅ Backup restored")
        raise
    
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
