import sys, os, tempfile, psycopg2
import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, '.')
from agents.coordinator import coordinator

def test_assign(aid, filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
        
        conn = psycopg2.connect(host='localhost', port=5432, database='AI3', user='postgres', password='123456')
        with conn.cursor() as cur:
            cur.execute('SELECT requirement_text, weight FROM assignment_requirements WHERE assignment_id=%s', (aid,))
            requirements = [{'requirement_text': text, 'weight': float(w) if w else 1.0} for text, w in cur.fetchall()]
            cur.execute('SELECT input_data, expected_output, score_weight FROM assignment_testcases WHERE assignment_id=%s', (aid,))
            testcases = [{'input_data': inp, 'expected_output': out, 'score_weight': float(w) if w else 1.0} for inp, out, w in cur.fetchall()]
        conn.close()
        
        temp_fd, temp_filepath = tempfile.mkstemp(suffix='.py', text=True)
        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                f.write(code)
            result = coordinator(filepath=temp_filepath, requirements=requirements, testcases=testcases)
            total = result.get('total', {}).get('total_score', 0)
            print(f'\n--- ASSIGNMENT {aid} DETAILS ---')
            print(f'Syntax: {result.get("syntax", {}).get("score", 0)}/20')
            print(f'Requirement: {result.get("requirement", {}).get("score", 0)}/20')
            print(f'Structure: {result.get("structure", {}).get("score", 0)}/20')
            print(f'Test: {result.get("test", {}).get("score", 0)}/20')
            print(f'LLM: {result.get("llm", {}).get("score", 0)}/20')
            print(f'TOTAL: {total}/100')
            return total
        finally:
            os.unlink(temp_filepath)
    except Exception as e:
        print(f'\nERROR A{aid}: {str(e)[:100]}')
        return 0

print("\n=== SOLUTION QUALITY CHECK ===")
for aid in [1, 4, 6, 7, 8, 9, 10]:
    filename = f'solution_assignment{aid}.py'
    test_assign(aid, filename)

