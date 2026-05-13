import psycopg2
from agents.coordinator import coordinator
import sys

# Set encoding
sys.stdout.reconfigure(encoding='utf-8')

# Connect to AI3 database
conn = psycopg2.connect(dbname='AI3', user='postgres', password='123456', host='localhost')
cur = conn.cursor()

# Get assignment 3 requirements
cur.execute("""
    SELECT requirement_text 
    FROM assignment_requirements 
    WHERE assignment_id = 3;
""")
requirements_raw = [{'requirement': row[0]} for row in cur.fetchall()]

# Get assignment 3 test cases
cur.execute("""
    SELECT input_data, expected_output 
    FROM assignment_testcases 
    WHERE assignment_id = 3
    ORDER BY testcase_id;
""")
testcases = [{'input': row[0].strip(), 'output': row[1].strip()} for row in cur.fetchall()]

conn.close()

print("=== ASSIGNMENT 3: CHECK EVEN ODD ===\n")
print(f"Requirements: {len(requirements_raw)}")
print(f"Test Cases: {len(testcases)}")

for i, tc in enumerate(testcases, 1):
    print(f"  Test {i}: '{tc['input']}' => '{tc['output']}'")

# Test with coordinator
print("\n" + "="*60)
print("TESTING CODE")
print("="*60)

result = coordinator('uploads/bai1.py', requirements_raw, testcases)

print(f"\nFINAL SCORES:")
print(f"Syntax:      {result['syntax']['score']}/20")
print(f"Requirement: {result['requirement']['score']}/20")
print(f"Structure:   {result['structure']['score']}/20")
print(f"Test:        {result['test']['score']}/20")
print(f"LLM:         {result['llm']['score']}/20")
print(f"{'='*30}")
print(f"TOTAL:       {result['total']['total_score']}/100")
print(f"{'='*30}")
