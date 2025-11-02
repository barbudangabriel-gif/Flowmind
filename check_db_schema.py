#!/usr/bin/env python3
"""Check SQLite database schema"""
import sqlite3
import sys

db_path = sys.argv[1] if len(sys.argv) > 1 else "/app/data/flowmind.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("=== Database Tables ===")
    for table in tables:
        table_name = table[0]
        print(f"\n📊 {table_name}")
        
        # Get schema
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        for col in columns:
            cid, name, type, notnull, default, pk = col
            print(f"  - {name} ({type}) {'PRIMARY KEY' if pk else ''}")
    
    conn.close()
    print("\n✅ Database check complete")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
