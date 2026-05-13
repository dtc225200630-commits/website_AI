import psycopg2
import json

# Database connection
conn = psycopg2.connect(
    dbname="MAS_Programming_Assessment",
    user="postgres",
    password="123456",
    host="localhost",
    port=5432
)
cursor = conn.cursor()

print("=== QUERYING DATABASE ===\n")

# Get all assignments
print("--- ALL ASSIGNMENTS ---")
cursor.execute("SELECT id, name, description FROM assignments ORDER BY id;")
assignments = cursor.fetchall()
for a in assignments:
    print(f"ID: {a[0]}, Name: {a[1]}, Desc: {a[2]}")

print("\n--- ASSIGNMENT 2 (Even/Odd Check) ---")

# Get assignment 2
cursor.execute("SELECT id, name, description FROM assignments WHERE id = 2;")
assignment = cursor.fetchone()
if assignment:
    print(f"Assignment: {assignment[1]}")
    print(f"Description: {assignment[2]}")
    assignment_id = assignment[0]
    
    # Get requirements for assignment 2
    print("\nRequirements:")
    cursor.execute("""
        SELECT id, requirement_text, requirement_type, weight 
        FROM requirements 
        WHERE assignment_id = %s
        ORDER BY id;
    """, (assignment_id,))
    requirements = cursor.fetchall()
    for req in requirements:
        print(f"  {req[0]}. {req[1]} (Type: {req[2]}, Weight: {req[3]})")
    
    # Get test cases for assignment 2
    print("\nTest Cases:")
    cursor.execute("""
        SELECT id, input_data, expected_output, description 
        FROM test_cases 
        WHERE assignment_id = %s
        ORDER BY id;
    """, (assignment_id,))
    test_cases = cursor.fetchall()
    for tc in test_cases:
        print(f"  Test {tc[0]}: input='{tc[1]}' → output='{tc[2]}' ({tc[3]})")

conn.close()
