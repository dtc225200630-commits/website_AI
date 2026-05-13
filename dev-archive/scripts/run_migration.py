#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Database migration script to add code_analysis_score and llm_score columns
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import sys

DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "AI3",
    "user": "postgres",
    "password": "123456"
}

def run_migration():
    """Run database migration"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print("[Migration] Starting...")
        
        # Check if columns exist before adding
        cur.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name='evaluation_sessions'
            AND column_name IN ('code_analysis_score', 'llm_score')
        """)
        existing_cols = [row[0] for row in cur.fetchall()]
        
        # Add code_analysis_score if not exists
        if 'code_analysis_score' not in existing_cols:
            print("[Migration] Adding code_analysis_score column...")
            cur.execute("""
                ALTER TABLE evaluation_sessions
                ADD COLUMN code_analysis_score DECIMAL(5,2)
            """)
            print("  ✓ code_analysis_score column added")
        else:
            print("  ✓ code_analysis_score column already exists")
        
        # Add llm_score if not exists
        if 'llm_score' not in existing_cols:
            print("[Migration] Adding llm_score column...")
            cur.execute("""
                ALTER TABLE evaluation_sessions
                ADD COLUMN llm_score DECIMAL(5,2)
            """)
            print("  ✓ llm_score column added")
        else:
            print("  ✓ llm_score column already exists")
        
        # Create index
        print("[Migration] Creating index...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_evaluation_sessions_submission_id
            ON evaluation_sessions(submission_id)
        """)
        print("  ✓ Index created/exists")
        
        conn.commit()
        print("[Migration] SUCCESS - All changes applied!")
        
        # Verify columns
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns
            WHERE table_name='evaluation_sessions'
            ORDER BY ordinal_position
        """)
        print("\n[Verification] Current table columns:")
        for col_name, data_type in cur.fetchall():
            print(f"  - {col_name}: {data_type}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_migration()
