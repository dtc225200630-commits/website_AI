import sys, os, tempfile, psycopg2
sys.path.insert(0, '.')
from agents.coordinator import coordinator

aid = 1
with open(f'solution_assignment{aid}.py', 'r') as f:
    code = f.read()

conn = psycopg2.connect(host='localhost', port=5432, database='AI3', user='postgres', password='123456')
with conn.cursor() as cur:
    cur.execute('SELECT requirement_text FROM assignment_requirements WHERE assignment_id=%s', (aid,))
    reqs = [text for (text,) in cur.fetchall()]
    cur.execute('SELECT input_data, expected_output FROM assignment_testcases WHERE assignment_id=%s', (aid,))
    tests = cur.fetchall()
conn.close()

print(f"Code:\n{code}\n")
print(f"Requirements:")
for i, r in enumerate(reqs, 1):
    print(f"  {i}. {r}")

print(f"\nTest Cases:")
for inp, out in tests:
    print(f"  Input: {inp} → Expected: {out}")

temp_fd, temp_filepath = tempfile.mkstemp(suffix='.py', text=True)
try:
    with os.fdopen(temp_fd, 'w') as f:
        f.write(code)
    
    requirements = [{'requirement_text': text, 'weight': 1.0} for text in reqs]
    testcases = [{'input_data': inp, 'expected_output': out, 'score_weight': 1.0} for inp, out in tests]
    
    result = coordinator(filepath=temp_filepath, requirements=requirements, testcases=testcases)
    
    print(f"\nDETAILS:")
    print(f"  Syntax: {result.get('syntax', {}).get('score', 0)}/20 - {result.get('syntax', {}).get('passed', False)}")
    if result.get('syntax', {}).get('error'):
        print(f"    Error: {result.get('syntax', {}).get('error')[:150]}")
    
    print(f"  Requirement: {result.get('requirement', {}).get('score', 0)}/20")
    print(f"  Structure: {result.get('structure', {}).get('score', 0)}/20")
    print(f"  Test: {result.get('test', {}).get('score', 0)}/20")
    print(f"  LLM: {result.get('llm', {}).get('score', 0)}/20")
    
    print(f"\nFINAL: {result.get('total', {}).get('total_score', 0)}/100")
finally:
    os.unlink(temp_filepath)
