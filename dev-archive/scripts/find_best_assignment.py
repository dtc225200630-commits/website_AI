import psycopg2

conn = psycopg2.connect(dbname='MAS_Programming_Assessment', user='postgres', password='123456', host='localhost')
cur = conn.cursor()

# Find all assignments with requirements or test cases
cur.execute("SELECT DISTINCT assignment_id FROM assignment_requirements ORDER BY assignment_id;")
assign_with_reqs = [row[0] for row in cur.fetchall()]

cur.execute("SELECT DISTINCT assignment_id FROM assignment_test_cases ORDER BY assignment_id;")
assign_with_tests = [row[0] for row in cur.fetchall()]

print("Assignments WITH requirements:", assign_with_reqs)
print("Assignments WITH test cases:", assign_with_tests)

# Pick one with both
target = None
for a in assign_with_reqs:
    if a in assign_with_tests:
        target = a
        break

if target:
    print(f"\n=== ASSIGNMENT {target} ===")
    
    cur.execute("SELECT title, description FROM assignments WHERE assignment_id = %s;", (target,))
    a = cur.fetchone()
    print(f"Title: {a[0]}")
    print(f"Description: {a[1]}")
    
    print("\nRequirements:")
    cur.execute("""
        SELECT requirement_name, requirement_description, check_value
        FROM assignment_requirements 
        WHERE assignment_id = %s
        ORDER BY requirement_template_id;
    """, (target,))
    for req in cur.fetchall():
        print(f"  - {req[0]}: {req[1]} (check: {req[2]})")
    
    print("\nTest Cases:")
    cur.execute("""
        SELECT input_data, expected_output
        FROM assignment_test_cases 
        WHERE assignment_id = %s
        ORDER BY test_case_id;
    """, (target,))
    for i, test in enumerate(cur.fetchall(), 1):
        print(f"  Test {i}: '{test[0]}' → '{test[1]}'")
else:
    print("No assignment has both requirements AND test cases")

conn.close()
