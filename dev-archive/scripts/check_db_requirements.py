"""
Check Database for Assignments with Missing Requirements/TestCases
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

# Use same DATABASE_URL as app.py
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:123456@localhost:5432/AI3",
)

conn = None
try:
    conn = psycopg2.connect(DATABASE_URL)
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Check all assignments
        print("=" * 80)
        print("CHECKING DATABASE FOR ASSIGNMENTS WITH MISSING DATA")
        print("=" * 80)
        
        cur.execute("""
            SELECT 
                a.assignment_id,
                a.title,
                COUNT(DISTINCT ar.requirement_id) as req_count,
                COUNT(DISTINCT at.testcase_id) as test_count
            FROM assignments a
            LEFT JOIN assignment_requirements ar ON ar.assignment_id = a.assignment_id
            LEFT JOIN assignment_testcases at ON at.assignment_id = a.assignment_id
            GROUP BY a.assignment_id, a.title
            ORDER BY a.assignment_id DESC
            LIMIT 20
        """)
        
        rows = cur.fetchall()
        
        for row in rows:
            assignment_id = row['assignment_id']
            title = row['title']
            req_count = row['req_count'] or 0
            test_count = row['test_count'] or 0
            
            status = ""
            if req_count == 0:
                status += "❌ NO REQUIREMENTS"
            else:
                status += f"✓ {req_count} requirements"
            
            status += " | "
            
            if test_count == 0:
                status += "❌ NO TEST CASES"
            else:
                status += f"✓ {test_count} test cases"
            
            print(f"\n[{assignment_id}] {title}")
            print(f"    {status}")
            
            if req_count > 0:
                print(f"    Requirements:")
                cur.execute("""
                    SELECT requirement_text, weight 
                    FROM assignment_requirements 
                    WHERE assignment_id = %s 
                    LIMIT 3
                """, (assignment_id,))
                for req in cur.fetchall():
                    print(f"      • {req['requirement_text'][:60]} ({req['weight']})")
            
            if test_count > 0:
                print(f"    Test Cases:")
                cur.execute("""
                    SELECT input_data, expected_output, score_weight 
                    FROM assignment_testcases 
                    WHERE assignment_id = %s 
                    LIMIT 2
                """, (assignment_id,))
                for tc in cur.fetchall():
                    inp = tc['input_data'][:20] if tc['input_data'] else "(empty)"
                    out = tc['expected_output'][:20] if tc['expected_output'] else "(empty)"
                    print(f"      • Input: {inp}... → Output: {out}...")
        
        print("\n" + "=" * 80)
        
finally:
    if conn:
        conn.close()
