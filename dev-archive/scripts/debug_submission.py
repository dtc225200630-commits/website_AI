#!/usr/bin/env python3
"""
Debug Script - Test Submission Step by Step
"""

import tempfile
import psycopg2
from agents.coordinator import coordinator

# Database connection
conn = psycopg2.connect(
    host="localhost",
    database="AI3",
    user="postgres",
    password="123456"
)
cur = conn.cursor()

# Code to test
test_code = """# Nhập dữ liệu đầu vào n
n = int(input())

# Thỏa mãn requirement: Sử dụng vòng lặp for và hàm range()
# Thỏa mãn test case: In mỗi số trên một dòng (\\n)
for i in range(1, n + 1):
    print(i)
"""

print("=" * 80)
print("DEBUG: Vòng lặp in dãy số - Mã kiểm tra")
print("=" * 80)

# STEP 1: Find assignment
print("\n[STEP 1] Tìm assignment 'Vòng lặp in dãy số' từ database...")
cur.execute("SELECT assignment_id, title FROM assignments WHERE title ILIKE %s", ("%Vòng lặp in dãy số%",))
assignments = cur.fetchall()

if not assignments:
    print("❌ Assignment không tìm thấy!")
    print("\nDanh sách tất cả assignments:")
    cur.execute("SELECT assignment_id, title FROM assignments LIMIT 10")
    for row in cur.fetchall():
        print(f"  - ID {row[0]}: {row[1]}")
    conn.close()
    exit(1)

assignment_id = assignments[0][0]
print(f"✓ Tìm thấy assignment ID: {assignment_id}")

# STEP 2: Load requirements
print(f"\n[STEP 2] Load requirements từ database...")
cur.execute(
    "SELECT requirement_text, weight FROM assignment_requirements WHERE assignment_id=%s",
    (assignment_id,)
)
requirements = cur.fetchall()
print(f"✓ Tìm thấy {len(requirements)} requirements:")
for i, (req_text, weight) in enumerate(requirements, 1):
    print(f"  {i}. [{weight}] {req_text}")

# STEP 3: Load test cases
print(f"\n[STEP 3] Load test cases từ database...")
cur.execute(
    "SELECT input_data, expected_output, score_weight FROM assignment_testcases WHERE assignment_id=%s",
    (assignment_id,)
)
testcases = cur.fetchall()
print(f"✓ Tìm thấy {len(testcases)} test cases:")
for i, (inp, out, weight) in enumerate(testcases, 1):
    print(f"  {i}. [weight={weight}] Input: {repr(inp)} → Expected: {repr(out)}")

# STEP 4: Test code syntax
print(f"\n[STEP 4] Kiểm tra syntax code...")
with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
    f.write(test_code)
    temp_filepath = f.name

print(f"Temp file: {temp_filepath}")

# Import agents directly to test
from agents.syntax_agent_fixed import syntax_agent
from agents.requirement_agent_fixed import requirement_agent
from agents.structure_agent_fixed import structure_agent
from agents.test_agent_fixed import test_agent
from agents.llm_agent import llm_agent
from agents.aggregation_agent_fixed import aggregation_agent

# Test syntax
print("\n------- TESTING INDIVIDUAL AGENTS -------")
print("\n[AGENT 1] Syntax Agent:")
syntax_result = syntax_agent(temp_filepath)
print(f"  Score: {syntax_result.get('score', 'N/A')}/20")
print(f"  Success: {syntax_result.get('success', 'N/A')}")
print(f"  Error: {syntax_result.get('error', 'N/A')}")
if syntax_result.get('details'):
    print(f"  Details: {syntax_result.get('details')}")

if not syntax_result.get('success'):
    print("\n❌ Syntax error! Stopping tests.")
    conn.close()
    exit(1)

# Test requirements
print("\n[AGENT 2] Requirement Agent:")
req_result = requirement_agent(test_code, requirements)
print(f"  Score: {req_result.get('score', 'N/A')}/20")
print(f"  Fulfilled: {req_result.get('fulfilled_count', 0)}/{len(requirements)}")
if req_result.get('details'):
    for detail in req_result.get('details', []):
        print(f"    - {detail}")

# Test structure
print("\n[AGENT 3] Structure Agent:")
struct_result = structure_agent(test_code)
print(f"  Score: {struct_result.get('score', 'N/A')}/20")
if struct_result.get('details'):
    for detail in struct_result.get('details', []):
        print(f"    - {detail}")

# Test test cases
print("\n[AGENT 4] Test Agent:")
test_result = test_agent(temp_filepath, testcases)
print(f"  Score: {test_result.get('score', 'N/A')}/20")
print(f"  Passed: {test_result.get('passed_count', 0)}/{len(testcases)}")
if test_result.get('summary'):
    print(f"  Summary: {test_result.get('summary')}")
if test_result.get('test_results'):
    for i, tr in enumerate(test_result.get('test_results', []), 1):
        print(f"    Test {i}: {tr}")

# Test LLM
print("\n[AGENT 5] LLM Agent:")
try:
    llm_result = llm_agent(test_code)
    print(f"  Score: {llm_result.get('score', 'N/A')}/20")
    print(f"  Feedback: {llm_result.get('feedback', 'N/A')}")
except Exception as e:
    print(f"  ❌ Error: {e}")
    llm_result = {"score": 0, "feedback": str(e), "details": []}

# Test aggregation
print("\n[AGENT 6] Aggregation Agent:")
agg_result = aggregation_agent({
    "syntax": syntax_result,
    "requirement": req_result,
    "structure": struct_result,
    "test": test_result,
    "llm": llm_result
})
print(f"  Total Score: {agg_result.get('total_score', 'N/A')}/100")
print(f"  Grade: {agg_result.get('grade', 'N/A')}")

# STEP 5: Test full coordinator
print(f"\n[STEP 5] Test toàn bộ coordinator...")
result = coordinator(temp_filepath, requirements, testcases)
print(f"✓ Coordinator result:")
print(f"  Total Score: {result.get('total_score', 'N/A')}/100")
print(f"  Syntax: {result['syntax']['score']}/20")
print(f"  Requirement: {result['requirement']['score']}/20")
print(f"  Structure: {result['structure']['score']}/20")
print(f"  Test: {result['test']['score']}/20")
print(f"  LLM: {result['llm']['score']}/20")

print("\n" + "=" * 80)
print("DEBUG: HOÀN THÀNH")
print("=" * 80)

conn.close()
