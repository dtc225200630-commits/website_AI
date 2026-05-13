import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='AI3',
    user='postgres',
    password='123456'
)

cursor = conn.cursor()

# Get latest 3 evaluations
cursor.execute('''
SELECT session_id, syntax_score, structure_score, requirement_score, 
       test_score, llm_score, code_analysis_score, total_score, created_at
FROM evaluation_sessions
ORDER BY session_id DESC
LIMIT 3;
''')

print('=== LATEST EVALUATIONS ===\n')

rows = cursor.fetchall()
for session_id, syntax, structure, req, test, llm, code_analysis, total, created in rows:
    print(f'Session {session_id}: {total}/100 🎯')
    print(f'  Syntax Agent:      {syntax}/20      {"✅" if syntax >= 15 else "❌"}')
    print(f'  Structure Agent:   {structure}/20    {"✅" if structure >= 10 else "❌"}')
    print(f'  Requirement Agent: {req}/20    {"✅" if req >= 15 else "❌"}')
    print(f'  Test Agent:        {test}/20      {"✅" if test >= 15 else "❌"}')
    print(f'  LLM Agent:         {llm}/20      {"✅" if llm >= 10 else "⚠️"}')
    print(f'  Code Analysis:     {code_analysis}/20    (informational)')
    print(f'  Created: {str(created)[:19]}')
    print()

cursor.close()
conn.close()
