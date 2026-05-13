import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='AI3',
    user='postgres',
    password='123456'
)

cursor = conn.cursor()

# List all tables
cursor.execute("""
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;
""")

print("=== TABLES IN DATABASE ===")
for (table_name,) in cursor.fetchall():
    print(f"  {table_name}")

# Get test cases from assignments table if they're stored there
cursor.execute("""
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'assignments'
ORDER BY ordinal_position;
""")

print("\n=== COLUMNS IN 'assignments' TABLE ===")
for (col,) in cursor.fetchall():
    print(f"  {col}")

# Get test cases
cursor.execute("""
SELECT * FROM assignment_testcases 
WHERE assignment_id = 3
ORDER BY testcase_id;
""")

print("\n=== TEST CASES FOR ASSIGNMENT 3 ===")
cols = [description[0] for description in cursor.description]
print(f"Columns: {cols}")
for row in cursor.fetchall():
    print(row)

# Get requirements
cursor.execute("""
SELECT * FROM assignment_requirements 
WHERE assignment_id = 3
ORDER BY requirement_id;
""")

print("\n=== REQUIREMENTS FOR ASSIGNMENT 3 ===")
cols = [description[0] for description in cursor.description]
print(f"Columns: {cols}")
for row in cursor.fetchall():
    print(row)
