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

print("=== DATABASE SCHEMA ===\n")

# Get all tables
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema='public'
    ORDER BY table_name;
""")
tables = cursor.fetchall()
print("Tables:")
for table in tables:
    print(f"  - {table[0]}")

print("\n--- ASSIGNMENTS TABLE SCHEMA ---")
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name='assignments'
    ORDER BY ordinal_position;
""")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[0]}: {col[1]}")

print("\n--- REQUIREMENTS TABLE SCHEMA ---")
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name='requirements'
    ORDER BY ordinal_position;
""")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[0]}: {col[1]}")

print("\n--- TEST_CASES TABLE SCHEMA ---")
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name='test_cases'
    ORDER BY ordinal_position;
""")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[0]}: {col[1]}")

print("\n--- DATA FROM ASSIGNMENTS ---")
cursor.execute("SELECT * FROM assignments LIMIT 5;")
rows = cursor.fetchall()
for row in rows:
    print(f"  {row}")

conn.close()
