import psycopg2
import json

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='AI3',
    user='postgres',
    password='123456'
)

cursor = conn.cursor()

# Get latest evaluation
cursor.execute('''
SELECT agent_details, session_id
FROM evaluation_sessions
ORDER BY session_id DESC
LIMIT 1;
''')

row = cursor.fetchone()
if row:
    agent_details, session_id = row
    if isinstance(agent_details, str):
        agent_details = json.loads(agent_details)
    
    print(f'=== SESSION {session_id} - LLM/CODE ANALYSIS ===\n')
    
    # Check LLM agent
    llm = agent_details.get('llm', {})
    print(f"LLM (Phân Tích AI): {llm.get('score')}/20")
    if llm.get('details'):
        print(f"  Details: {llm.get('details')}")
    print()
    
    # Check code analysis
    code_analysis = agent_details.get('code_analysis', {})
    print(f"Code Analysis (Phân Tích Code): {code_analysis.get('score')}/20")
    print(f"Summary: {code_analysis.get('summary')}")
    
    if code_analysis.get('issues'):
        print(f"\nIssues (Vấn Đề):")
        for issue in code_analysis.get('issues', []):
            print(f"  ✗ {issue}")
    
    if code_analysis.get('strengths'):
        print(f"\nStrengths (Ưu Điểm):")
        for strength in code_analysis.get('strengths', []):
            print(f"  ✓ {strength}")

cursor.close()
conn.close()
