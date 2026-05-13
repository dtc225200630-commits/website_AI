#!/usr/bin/env python3
"""
Manual diagnostic test - Mimics exact web flow
"""
import tempfile
import psycopg2
import os
from agents.coordinator import coordinator

# Connect to database
conn = psycopg2.connect(
    host="localhost",
    database="AI3",
    user="postgres",
    password="123456"
)
cur = conn.cursor()

# User's actual code
test_code = """# Nhập dữ liệu đầu vào n
n = int(input())

# Thỏa mãn requirement: Sử dụng vòng lặp for và hàm range()
# Thỏa mãn test case: In mỗi số trên một dòng (\\n)
for i in range(1, n + 1):
    print(i)
"""

assignment_id = 4

print("=" * 80)
print("DIAGNOSTIC TEST - EXACT WEB FLOW SIMULATION")
print("=" * 80)

# Step 1: Load from DB (exact code from app.py)
print(f"\n[Step 1] Loading assignment {assignment_id} requirements and testcases...")

cur.execute("""
    SELECT requirement_text, weight
    FROM assignment_requirements
    WHERE assignment_id=%s
""", (assignment_id,))
requirements = cur.fetchall()
print(f"✓ Loaded {len(requirements)} requirements")
for i, (text, weight) in enumerate(requirements):
    print(f"  [{i}] {text[:50]}... (weight={weight})")

cur.execute("""
    SELECT input_data, expected_output, score_weight
    FROM assignment_testcases
    WHERE assignment_id=%s
""", (assignment_id,))
testcases = cur.fetchall()
print(f"✓ Loaded {len(testcases)} testcases")
for i, (inp, out, weight) in enumerate(testcases):
    print(f"  [{i}] Input={repr(inp[:30])}... Expect={repr(out[:30])}... (weight={weight})")

# Step 2: Create temp file and call coordinator
print(f"\n[Step 2] Creating temp file and coordinator call...")
temp_fd, temp_filepath = tempfile.mkstemp(suffix=".py", text=True)

try:
    with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print(f"✓ Temp file created: {temp_filepath}")
    print(f"✓ Code size: {len(test_code)} bytes")
    print(f"✓ Calling coordinator...")
    
    try:
        result = coordinator(
            filepath=temp_filepath,
            requirements=requirements,
            testcases=testcases
        )
        print(f"✓ Coordinator returned successfully")
    except Exception as e:
        print(f"❌ Coordinator raised exception: {e}")
        import traceback
        traceback.print_exc()
        conn.close()
        exit(1)
    
    # Step 3: Extract scores (exact code from app.py)
    print(f"\n[Step 3] Extracting scores from result...")
    
    print(f"  Result keys: {result.keys()}")
    
    syntax_score = float(result.get("syntax", {}).get("score", 0))
    requirement_score = float(result.get("requirement", {}).get("score", 0))
    structure_score = float(result.get("structure", {}).get("score", 0))
    test_score = float(result.get("test", {}).get("score", 0))
    total_score = float(result.get("total", {}).get("total_score", 0))
    
    print(f"  - syntax_score: {syntax_score}/20")
    print(f"  - requirement_score: {requirement_score}/20")
    print(f"  - structure_score: {structure_score}/20")
    print(f"  - test_score: {test_score}/20")
    print(f"  - total_score: {total_score}/100")
    
    # Step 4: Check if scores are valid
    print(f"\n[Step 4] Validation...")
    if total_score == 0:
        print(f"❌ ERROR: total_score is 0!")
        print(f"  Full result['total']: {result.get('total')}")
    elif total_score < 50:
        print(f"⚠️  WARNING: Low score ({total_score})")
    else:
        print(f"✓ Score is reasonable: {total_score}/100")
    
    # Step 5: Would be stored to DB
    print(f"\n[Step 5] Would write to database:")
    print(f"  submission_id: (NEW)")
    print(f"  syntax_score: {syntax_score}")
    print(f"  structure_score: {structure_score}")
    print(f"  requirement_score: {requirement_score}")
    print(f"  test_score: {test_score}")
    print(f"  total_score: {total_score}")
    
finally:
    if os.path.exists(temp_filepath):
        os.remove(temp_filepath)

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)

conn.close()
