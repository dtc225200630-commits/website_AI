import psycopg2

# Database connection
conn = psycopg2.connect(
    dbname="MAS_Programming_Assessment",
    user="postgres",
    password="123456",
    host="localhost",
    port=5432
)
cursor = conn.cursor()

print("=== ALL ASSIGNMENTS ===\n")

cursor.execute("SELECT assignment_id, title, description FROM assignments ORDER BY assignment_id;")
rows = cursor.fetchall()
for row in rows:
    print(f"ID {row[0]}: {row[1]}")
    print(f"   Desc: {row[2]}\n")

# Try to find even/odd check assignment
print("\n=== SEARCHING FOR 'CHẴN' OR 'LẺ' ===")
cursor.execute("SELECT assignment_id, title, description FROM assignments WHERE description ILIKE '%chẵn%' OR description ILIKE '%lẻ%' OR title ILIKE '%chẵn%';")
rows = cursor.fetchall()
if rows:
    for row in rows:
        print(f"ID {row[0]}: {row[1]}")
        print(f"   Desc: {row[2]}")
        
        # Get requirements and test cases
        assignment_id = row[0]
        
        print("\n   Requirements:")
        cursor.execute("""
            SELECT requirement_id, requirement_text 
            FROM assignment_requirements 
            WHERE assignment_id = %s
            ORDER BY requirement_id;
        """, (assignment_id,))
        reqs = cursor.fetchall()
        for req in reqs:
            print(f"     - {req[1]}")
        
        print("\n   Test Cases:")
        cursor.execute("""
            SELECT test_case_id, input_data, expected_output 
            FROM assignment_test_cases 
            WHERE assignment_id = %s
            ORDER BY test_case_id;
        """, (assignment_id,))
        tests = cursor.fetchall()
        for test in tests:
            print(f"     Input: '{test[1]}' → Output: '{test[2]}'")
else:
    print("No assignment found with 'chẵn' or 'lẻ' in title/description")

conn.close()
