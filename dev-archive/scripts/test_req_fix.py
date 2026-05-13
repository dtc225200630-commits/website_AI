#!/usr/bin/env python3
"""Quick test of requirement agent fix"""
import psycopg2
from agents.requirement_agent_fixed import requirement_agent

# Database connection
conn = psycopg2.connect(
    host="localhost",
    database="AI3",
    user="postgres",
    password="123456"
)
cur = conn.cursor()

# Test code
test_code = """n = int(input())
for i in range(1, n + 1):
    print(i)
"""

# Get requirements for assignment 4
cur.execute("""
    SELECT requirement_text, weight
    FROM assignment_requirements
    WHERE assignment_id=4
""")
requirements = cur.fetchall()

print("Testing Requirement Agent Fix")
print("=" * 60)
print(f"Test code:\n{test_code}")
print("\nRequirements:")
for i, (text, weight) in enumerate(requirements, 1):
    print(f"  {i}. [{weight}] {text}")

# Test requirement agent
result = requirement_agent(test_code, requirements)

print(f"\nResult:")
print(f"  Score: {result['score']}/20")
print(f"  Fulfilled: {result['fulfilled_count']}/{len(requirements)}")
print(f"  Details:")
for detail in result['details']:
    print(f"    {detail}")

print(f"\nExpected: 4/4 or 20/20 (after fix)")

conn.close()
