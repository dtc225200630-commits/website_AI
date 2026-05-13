import psycopg2

# Try both databases
databases = [
    'MAS_Programming_Assessment',
    'AI3'
]

for dbname in databases:
    try:
        print(f"\n=== CHECKING DATABASE: {dbname} ===\n")
        conn = psycopg2.connect(dbname=dbname, user='postgres', password='123456', host='localhost')
        cur = conn.cursor()
        
        # Check assignments 2, 3, 4
        cur.execute("""
            SELECT assignment_id, title, description 
            FROM assignments 
            WHERE assignment_id IN (2, 3, 4)
            ORDER BY assignment_id;
        """)
        
        rows = cur.fetchall()
        print(f"Assignments found: {len(rows)}")
        for row in rows:
            print(f"\n  ID {row[0]}: {row[1]}")
            print(f"  Desc: {row[2]}")
            
            # Check if table is assignment_requirements or assignment_requirements
            try:
                cur.execute("""
                    SELECT requirement_text, weight 
                    FROM assignment_requirements 
                    WHERE assignment_id = %s;
                """, (row[0],))
                reqs = cur.fetchall()
                print(f"  Requirements ({len(reqs)}):")
                for req in reqs:
                    print(f"    - {req[0]} (weight: {req[1]})")
            except:
                print("  Requirements table error")
            
            # Check test cases
            try:
                cur.execute("""
                    SELECT input_data, expected_output 
                    FROM assignment_test_cases 
                    WHERE assignment_id = %s;
                """, (row[0],))
                tests = cur.fetchall()
                print(f"  Test Cases ({len(tests)}):")
                for test in tests:
                    print(f"    Input: '{test[0]}' → Output: '{test[1]}'")
            except:
                print("  Test cases table error")
        
        conn.close()
        break  # Found data, stop checking
        
    except Exception as e:
        print(f"  Error: {e}")
        continue
