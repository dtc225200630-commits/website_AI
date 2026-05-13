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

# Get latest evaluation with agent details
cursor.execute('''
SELECT session_id, agent_details
FROM evaluation_sessions
ORDER BY session_id DESC
LIMIT 1;
''')

row = cursor.fetchone()
if row:
    session_id, agent_details = row
    print(f'Session {session_id} - Agent Details:\n')
    
    if isinstance(agent_details, str):
        agent_details = json.loads(agent_details)
    
    # Pretty print syntax agent error
    print('=== SYNTAX AGENT ===')
    syntax = agent_details.get('syntax', {})
    print(f"Success: {syntax.get('success')}")
    print(f"Score: {syntax.get('score')}")
    print(f"Error: {syntax.get('error')}")
    print(f"Details: {syntax.get('details')}")
    
    print('\n=== REQUIREMENT AGENT ===')
    req = agent_details.get('requirement', {})
    print(f"Score: {req.get('score')}")
    print(f"Details: {req.get('details')}")
    
    print('\n=== TEST AGENT ===')
    test = agent_details.get('test', {})
    print(f"Score: {test.get('score')}")
    print(f"Summary: {test.get('summary')}")
    if test.get('details'):
        print(f"First error: {str(test.get('details', [])[0])[:300]}")

cursor.close()
conn.close()
