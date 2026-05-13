#!/usr/bin/env python3
"""
Test script to submit Assignment 3 code and check the score
"""

import requests
import json
import time

# The solution for Assignment 3
ASSIGNMENT3_CODE = """n = int(input())
if n % 2 == 0:
    print("Chan")
else:
    print("Le")
"""

DATABASE_URL = "postgresql://postgres:123456@localhost:5432/AI3"

def test_submission():
    """Submit Assignment 3 and display results"""
    
    # Use hardcoded student_id = 1 and assignment_id = 3
    student_id = 1
    assignment_id = 3
    
    print(f"[TEST] Submitting Assignment 3 for Student {student_id}")
    print(f"[TEST] Code:\n{ASSIGNMENT3_CODE}")
    print("-" * 70)
    
    # We need to login first to get cookies
    # For testing, let's directly check the database
    
    import psycopg2
    import sys
    import tempfile
    import os
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        with conn.cursor() as cur:
            # Create a test submission
            cur.execute("""
                INSERT INTO submissions (assignment_id, student_id, source_code, submitted_at)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                RETURNING submission_id
            """, (assignment_id, student_id, ASSIGNMENT3_CODE))
            submission_id = cur.fetchone()[0]
            conn.commit()
            
        print(f"[OK] Submission {submission_id} created in database")
        
        # Now simulate what the /submit endpoint would do
        # Call the coordinator directly
        sys.path.insert(0, '.')
        
        from agents.coordinator import coordinator
        
        # Prepare requirements and testcases
        with conn.cursor() as cur:
            # Get requirements
            cur.execute("""
                SELECT requirement_text, weight
                FROM assignment_requirements
                WHERE assignment_id=%s
            """, (assignment_id,))
            requirements = [{"requirement_text": text, "weight": float(w) if w else 1.0} 
                          for text, w in cur.fetchall()]
            
            # Get testcases
            cur.execute("""
                SELECT input_data, expected_output, score_weight
                FROM assignment_testcases
                WHERE assignment_id=%s
            """, (assignment_id,))
            testcases = [{"input_data": inp, "expected_output": out, "score_weight": float(w) if w else 1.0} 
                        for inp, out, w in cur.fetchall()]
        
        conn.close()
        
        print(f"[OK] Loaded {len(requirements)} requirements and {len(testcases)} testcases")
        
        # Create temp file
        temp_fd, temp_filepath = tempfile.mkstemp(suffix=".py", text=True)
        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                f.write(ASSIGNMENT3_CODE)
            
            print(f"\n[EVAL] Calling coordinator...")
            result = coordinator(
                filepath=temp_filepath,
                requirements=requirements,
                testcases=testcases
            )
            
            print(f"\n[RESULTS]")
            print(f"  Syntax Score:     {result.get('syntax', {}).get('score', 0)}/20")
            print(f"  Requirement Score: {result.get('requirement', {}).get('score', 0)}/20")
            print(f"  Structure Score:  {result.get('structure', {}).get('score', 0)}/20")
            print(f"  Test Score:       {result.get('test', {}).get('score', 0)}/20")
            print(f"  LLM Score:        {result.get('llm', {}).get('score', 0)}/20")
            print(f"  Code Analysis:    {result.get('code_analysis', {}).get('score', 0)}/20 (informational)")
            
            total = result.get('total', {}).get('total_score', 0)
            print(f"\n  TOTAL: {total}/100")
            
            # Calculate expected
            sx = float(result.get('syntax', {}).get('score', 0))
            rq = float(result.get('requirement', {}).get('score', 0))
            st = float(result.get('structure', {}).get('score', 0))
            ts = float(result.get('test', {}).get('score', 0))
            lm = float(result.get('llm', {}).get('score', 0))
            
            if sx + rq + st + ts + lm > 0:
                expected = (sx + rq + st + ts + lm) / 5 * 100
                print(f"  Expected: ({sx}+{rq}+{st}+{ts}+{lm})/5 * 100 = {expected:.0f}/100")
            
            return total
        finally:
            if os.path.exists(temp_filepath):
                try:
                    os.remove(temp_filepath)
                except:
                    pass
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    test_submission()
