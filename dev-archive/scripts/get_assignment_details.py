import psycopg2

conn = psycopg2.connect(dbname='AI3', user='postgres', password='123456', host='localhost')
cur = conn.cursor()

print("=== DATABASE AI3 - 3 BÀI TẬP MỚI ===\n")

for assign_id in [2, 3, 4]:
    # Get assignment info
    cur.execute("SELECT title, description FROM assignments WHERE assignment_id = %s;", (assign_id,))
    title, desc = cur.fetchone()
    
    print(f"\n{'='*60}")
    print(f"BÀI {assign_id}: {title}")
    print(f"{'='*60}")
    print(f"Description: {desc}\n")
    
    # Get requirements
    print("Requirements:")
    cur.execute("""
        SELECT requirement_text, weight 
        FROM assignment_requirements 
        WHERE assignment_id = %s
        ORDER BY requirement_text;
    """, (assign_id,))
    
    reqs = cur.fetchall()
    if reqs:
        for i, (req_text, weight) in enumerate(reqs, 1):
            print(f"  {i}. {req_text} (weight: {weight})")
    else:
        print("  (No requirements)")
    
    # Get test cases
    print("\nTest Cases:")
    cur.execute("""
        SELECT testcase_id, input_data, expected_output, score_weight 
        FROM assignment_testcases 
        WHERE assignment_id = %s
        ORDER BY testcase_id;
    """, (assign_id,))
    
    tests = cur.fetchall()
    if tests:
        for testcase_id, input_data, output, weight in tests:
            print(f"  Test {testcase_id}: Input='{input_data.strip()}' → Output='{output}' (weight: {weight})")
    else:
        print("  (No test cases)")

conn.close()

print("\n\n" + "="*60)
print("BẢNG TÓM TẮT - CHO VÀO uploads/bai1.py")
print("="*60)
print("""
BÀI 3: Kiểm tra số chẵn lẻ
- Yêu cầu: Dùng % operator, dùng if...else
- Input: '4\\n' → Output: 'Chan'
- Input: '7\\n' → Output: 'Le'
- Input: '100\\n' → Output: 'Chan'
""")
