#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verify database reads - simulate /submission-result endpoint query
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json

DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "AI3",
    "user": "postgres",
    "password": "123456"
}

def verify_database_reads():
    """Verify the /submission-result endpoint can read new columns"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print("=" * 70)
        print("TEST: Database Read Query (from /submission-result endpoint)")
        print("=" * 70)
        
        # Get sample evaluation session
        cur.execute("""
            SELECT
                session_id,
                syntax_score,
                code_analysis_score,
                structure_score,
                requirement_score,
                test_score,
                llm_score,
                total_score,
                final_feedback,
                agent_details,
                created_at
            FROM evaluation_sessions
            ORDER BY created_at DESC
            LIMIT 1
        """)
        
        row = cur.fetchone()
        
        if not row:
            print("\n[INFO] No evaluation sessions in database yet")
            print("       (This is OK - system is ready for first submission)")
        else:
            print("\n[FOUND] Sample evaluation session from database:")
            print(f"\nSession ID: {row[0]}")
            print(f"Scores:")
            print(f"  - Syntax: {row[1]}/20")
            print(f"  - Code Analysis: {row[2]}/20 <-- NEW!")
            print(f"  - Structure: {row[3]}/20")
            print(f"  - Requirement: {row[4]}/20")
            print(f"  - Test: {row[5]}/20")
            print(f"  - LLM: {row[6]}/20 <-- NEW!")
            print(f"  - TOTAL: {row[7]}/100")
            print(f"\nFinal Feedback: {row[8][:100]}...")
            
            # Parse agent_details
            if row[9]:
                try:
                    agent_details = json.loads(row[9])
                    print(f"\nAgent Details Keys: {list(agent_details.keys())}")
                    if 'code_analysis' in agent_details:
                        print(f"  - code_analysis score: {agent_details['code_analysis'].get('score', 0)}/20")
                    if 'llm' in agent_details:
                        print(f"  - llm score: {agent_details['llm'].get('score', 0)}/20")
                except:
                    print(f"  Could not parse agent_details JSON")
            
            print(f"\nCreated: {row[10]}")
        
        # List all columns in table
        print("\n" + "=" * 70)
        print("TABLE STRUCTURE: evaluation_sessions")
        print("=" * 70)
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'evaluation_sessions'
            ORDER BY ordinal_position
        """)
        
        print("\nColumn Name                  | Data Type      | Nullable")
        print("-" * 70)
        for col_name, data_type, nullable in cur.fetchall():
            print(f"{col_name:28} | {data_type:14} | {'YES' if nullable == 'YES' else 'NO'}")
        
        print("\n" + "=" * 70)
        print("SUCCESS: Database structure is ready!")
        print("=" * 70)
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_database_reads()
