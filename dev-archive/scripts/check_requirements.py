import psycopg2
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = psycopg2.connect(dbname='AI3', user='postgres', password='123456', host='localhost')
cur = conn.cursor()

cur.execute("""
    SELECT requirement_text 
    FROM assignment_requirements 
    WHERE assignment_id = 3;
""")

print("=== REQUIREMENTS FROM DATABASE ===\n")
for i, row in enumerate(cur.fetchall(), 1):
    req_text = row[0]
    print(f"{i}. '{req_text}'")
    print(f"   Contains '%': {'%' in req_text}")
    print(f"   Contains 'if...else': {'if' in req_text and 'else' in req_text}")
    print()

conn.close()
