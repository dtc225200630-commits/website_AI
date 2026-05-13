#!/usr/bin/env python3
"""
Simulate exact web submission flow
"""
import tempfile
import psycopg2
import json
import os
from agents.coordinator import coordinator

conn = psycopg2.connect(
    host="localhost",
    database="AI3",
    user="postgres",
    password="123456"
)
cur = conn.cursor()

# Test code - exactly as user would submit
test_code = """# Nhập dữ liệu đầu vào n
n = int(input())

# Thỏa mãn requirement: Sử dụng vòng lặp for và hàm range()
# Thỏa mãn test case: In mỗi số trên một dòng (\\n)
for i in range(1, n + 1):
    print(i)
"""

assignment_id = 4
student_id = 1

print("=" * 80)
print("SIMULATING WEB APP SUBMISSION")
print("=" * 80)

# Step 1: Get requirements from DB
print(f"\n[Step 1] Fetching requirements and test cases for assignment {assignment_id}...")
cur.execute("""
    SELECT requirement_text, weight
    FROM assignment_requirements
    WHERE assignment_id=%s
""", (assignment_id,))
requirements = cur.fetchall()
print(f"  ✓ Got {len(requirements)} requirements")

cur.execute("""
    SELECT input_data, expected_output, score_weight
    FROM assignment_testcases
    WHERE assignment_id=%s
""", (assignment_id,))
testcases = cur.fetchall()
print(f"  ✓ Got {len(testcases)} test cases")

# Step 2: create temp file and run coordinator
print(f"\n[Step 2] Creating temp file and running coordinator...")
temp_fd, temp_filepath = tempfile.mkstemp(suffix=".py", text=True)
try:
    with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print(f"  Temp file: {temp_filepath}")
    print(f"  Code length: {len(test_code)} bytes")
    
    # Run coordinator
    result = coordinator(
        filepath=temp_filepath,
        requirements=requirements,
        testcases=testcases
    )
    
    print(f"  ✓ Coordinator executed")
    
    # Extract scores
    syntax_score = float(result.get("syntax", {}).get("score", 0))
    requirement_score = float(result.get("requirement", {}).get("score", 0))
    structure_score = float(result.get("structure", {}).get("score", 0))
    test_score = float(result.get("test", {}).get("score", 0))
    total_score = float(result.get("total", {}).get("total_score", 0))
    
    print(f"\n[Step 3] Scores extracted:")
    print(f"  Syntax: {syntax_score}/20")
    print(f"  Requirement: {requirement_score}/20")
    print(f"  Structure: {structure_score}/20")
    print(f"  Test: {test_score}/20")
    print(f"  Total: {total_score}/100")
    
    # Check if any score is problematic
    if total_score == 0:
        print(f"\n❌ PROBLEM: Total score is 0!")
        print(f"  Result dict keys: {result.keys()}")
        print(f"  Result['total']: {result.get('total', {})}")
    elif total_score < 50:
        print(f"\n⚠️  WARNING: Low total score ({total_score})")
    else:
        print(f"\n✓ Scores look reasonable")
    
    # Step 3: Simulate database storage
    print(f"\n[Step 4] Simulating database storage...")
    
    # Check if submission exists
    cur.execute("""
        SELECT submission_id FROM submissions
        WHERE assignment_id=%s AND student_id=%s
    """, (assignment_id, student_id))
    
    existing = cur.fetchone()
    
    if existing:
        submission_id = existing[0]
        print(f"  Found existing submission ID: {submission_id}")
        
        # Delete old evaluations
        cur.execute("""
            DELETE FROM evaluation_sessions
            WHERE submission_id=%s
        """, (submission_id,))
        print(f"    - Deleted old evaluation_sessions")
        
        cur.execute("""
            DELETE FROM agent_logs
            WHERE submission_id=%s
        """, (submission_id,))
        print(f"    - Deleted old agent_logs")
    else:
        print(f"  No existing submission, would create new one")
    
    # Build agent details
    agent_details = {
        "syntax": result.get("syntax", {}),
        "requirement": {
            "score": result.get("requirement", {}).get("score", 0),
            "details": result.get("requirement", {}).get("details", [])
        },
        "structure": {
            "score": result.get("structure", {}).get("score", 0),
            "details": result.get("structure", {}).get("details", [])
        },
        "test": {
            "score": result.get("test", {}).get("score", 0),
            "details": result.get("test", {}).get("details", [])
        },
        "llm": {
            "score": result.get("llm", {}).get("score", 0),
            "feedback": result.get("llm", {}).get("feedback", "No feedback")
        }
    }
    
    print(f"\n[Step 5] Would store to evaluation_sessions:")
    print(f"  submission_id: {submission_id if existing else 'NEW'}")
    print(f"  syntax_score: {syntax_score}")
    print(f"  structure_score: {structure_score}")
    print(f"  requirement_score: {requirement_score}")
    print(f"  test_score: {test_score}")
    print(f"  total_score: {total_score}")
    print(f"  agent_details keys: {agent_details.keys()}")
    
finally:
    if os.path.exists(temp_filepath):
        try:
            os.remove(temp_filepath)
        except:
            pass

print("\n" + "=" * 80)
print("SIMULATION COMPLETE")
print("=" * 80)

conn.close()
