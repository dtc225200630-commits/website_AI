from config import get_db

conn = get_db().__enter__()
cur = conn.cursor()

# Check structure
cur.execute("SELECT * FROM evaluation_sessions LIMIT 1")
columns = [desc[0] for desc in cur.description]
print("=== evaluation_sessions COLUMNS ===")
for i, col in enumerate(columns):
    print(f"  {i}: {col}")

# Check data
print("\n=== evaluation_sessions DATA ===")
cur.execute("SELECT * FROM evaluation_sessions LIMIT 3")
rows = cur.fetchall()
print(f"Found {len(rows)} rows")
for row in rows:
    print(row[:5])  # First 5 values

conn.close()
