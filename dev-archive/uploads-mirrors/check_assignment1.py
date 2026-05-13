import psycopg2

conn = psycopg2.connect(dbname='MAS_Programming_Assessment', user='postgres', password='123456', host='localhost')
cur = conn.cursor()

print("=== ASSIGNMENT 1: BỘI TẬP PYTHON 1 (TÍNH TỔNG 2 SỐ) ===\n")

# Get requirements for assignment 1
cur.execute("""
    SELECT requirement_name, requirement_description, check_type, check_value, points
    FROM assignment_requirements 
    WHERE assignment_id = 1
    ORDER BY requirement_template_id;
""")
print("Requirements:")
reqs = cur.fetchall()
for req in reqs:
    print(f"  - {req[0]}: {req[1]}")
    print(f"    (Type: {req[2]}, Check: {req[3]}, Points: {req[4]})")

# Get test cases for assignment 1
cur.execute("""
    SELECT input_data, expected_output
    FROM assignment_test_cases 
    WHERE assignment_id = 1
    ORDER BY test_case_id;
""")
print("\nTest Cases:")
tests = cur.fetchall()
for i, test in enumerate(tests, 1):
    print(f"  Test {i}: Input: '{test[0]}' → Expected Output: '{test[1]}'")

print("\n=== SUBMITTING TO ASSIGNMENT 1 ===")
print("Edit uploads/bai1.py with the correct code that:")
print("- Takes 2 inputs (a, b)")
print("- Adds them")
print("- Prints result")

conn.close()
