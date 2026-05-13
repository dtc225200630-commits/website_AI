#!/usr/bin/env python3
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="AI3",
    user="postgres",
    password="123456"
)
cur = conn.cursor()

print("=" * 80)
print("ASSIGNMENTS TABLE")
print("=" * 80)
cur.execute("SELECT * FROM assignments LIMIT 1")
col_names = [desc[0] for desc in cur.description]
print(f"Columns: {col_names}\n")

print("All assignments:")
cur.execute("SELECT * FROM assignments")
for row in cur.fetchall():
    print(row)

print("\n" + "=" * 80)
print("ASSIGNMENT_REQUIREMENTS TABLE")
print("=" * 80)
cur.execute("SELECT * FROM assignment_requirements LIMIT 1")
col_names = [desc[0] for desc in cur.description]
print(f"Columns: {col_names}\n")

print("Requirements:")
cur.execute("SELECT * FROM assignment_requirements LIMIT 10")
for row in cur.fetchall():
    print(row)

print("\n" + "=" * 80)
print("ASSIGNMENT_TESTCASES TABLE")
print("=" * 80)
cur.execute("SELECT * FROM assignment_testcases LIMIT 1")
col_names = [desc[0] for desc in cur.description]
print(f"Columns: {col_names}\n")

print("Test cases:")
cur.execute("SELECT * FROM assignment_testcases LIMIT 10")
for row in cur.fetchall():
    print(row)

conn.close()
