import psycopg2

# Try database AI3
try:
    print("=== CHECKING DATABASE: AI3 ===\n")
    conn = psycopg2.connect(dbname='AI3', user='postgres', password='123456', host='localhost')
    cur = conn.cursor()
    
    # Get all tables
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema='public'
        ORDER BY table_name;
    """)
    
    tables = [row[0] for row in cur.fetchall()]
    print("Tables in AI3:", tables)
    
    # Check for requirements/test cases tables
    for table in ['assignment_requirements', 'assignment_test_cases', 'requirements', 'test_cases', 'assignment_testcases']:
        if table in tables:
            print(f"\n✓ Found table: {table}")
            cur.execute(f"SELECT COUNT(*) FROM {table};")
            count = cur.fetchone()[0]
            print(f"  Row count: {count}")
            
            # Show first few rows
            cur.execute(f"SELECT * FROM {table} LIMIT 3;")
            for row in cur.fetchall():
                print(f"  {row}")
    
    # Check assignments 2, 3, 4
    print("\n--- ASSIGNMENTS 2, 3, 4 ---")
    cur.execute("SELECT assignment_id, title FROM assignments WHERE assignment_id IN (2, 3, 4) ORDER BY assignment_id;")
    for row in cur.fetchall():
        print(f"  {row}")
    
    conn.close()
    
except Exception as e:
    print(f"Error with AI3: {e}")

# Try MAS database too
try:
    print("\n\n=== CHECKING DATABASE: MAS_Programming_Assessment ===\n")
    conn = psycopg2.connect(dbname='MAS_Programming_Assessment', user='postgres', password='123456', host='localhost')
    cur = conn.cursor()
    
    # Get all tables
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema='public'
        ORDER BY table_name;
    """)
    
    tables = [row[0] for row in cur.fetchall()]
    print("Tables in MAS_Programming_Assessment:", tables)
    
except Exception as e:
    print(f"Error with MAS: {e}")
