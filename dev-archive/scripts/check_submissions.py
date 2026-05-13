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

print("=== STUDENT SUBMISSIONS ===\n")

# Get all submissions
cursor.execute("""
    SELECT s.submission_id, s.assignment_id, a.title, s.submission_date 
    FROM submissions s
    JOIN assignments a ON s.assignment_id = a.assignment_id
    ORDER BY s.submission_date DESC
    LIMIT 10;
""")
rows = cursor.fetchall()

for row in rows:
    sub_id, assign_id, title, date = row
    print(f"Submission {sub_id}: Assignment {assign_id} '{title}' ({date})")
    
    # Show requirements and test cases for this assignment
    print(f"  Requirements:")
    cursor.execute("""
        SELECT requirement_text 
        FROM assignment_requirements 
        WHERE assignment_id = %s;
    """, (assign_id,))
    reqs = cursor.fetchall()
    if reqs:
        for req in reqs:
            print(f"    - {req[0]}")
    else:
        print("    (None)")
    
    print(f"  Test Cases:")
    cursor.execute("""
        SELECT input_data, expected_output 
        FROM assignment_test_cases 
        WHERE assignment_id = %s;
    """, (assign_id,))
    tests = cursor.fetchall()
    if tests:
        for test in tests:
            print(f"    Input: '{test[0]}' → Output: '{test[1]}'")
    else:
        print("    (None)")
    print()

conn.close()
