import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='AI3',
    user='postgres',
    password='123456'
)

cursor = conn.cursor()

# Get all assignments with class info
cursor.execute('''
SELECT a.assignment_id, a.title, a.description, a.programming_language, 
       c.class_name, a.due_date
FROM assignments a
LEFT JOIN classes c ON a.class_id = c.class_id
ORDER BY a.assignment_id;
''')

print('='*80)
print('DANH SÁCH TẤT CẢ CÁC BÀI TẬP'.center(80))
print('='*80)

assignments = cursor.fetchall()
for assign_id, title, desc, lang, class_name, due_date in assignments:
    print(f'\n📝 BÀI TẬP {assign_id}: {title}')
    print(f'   Lớp: {class_name or "N/A"} | Ngôn ngữ: {lang}')
    desc_display = desc[:70] + '...' if len(desc or '') > 70 else desc
    print(f'   Mô tả: {desc_display}')
    print(f'   Hạn nộp: {due_date}')
    
    # Get requirements
    cursor.execute('''
    SELECT requirement_id, requirement_text, weight
    FROM assignment_requirements
    WHERE assignment_id = %s
    ORDER BY requirement_id;
    ''', (assign_id,))
    
    reqs = cursor.fetchall()
    if reqs:
        print(f'   📋 Yêu cầu ({len(reqs)}):')
        for req_id, req_text, weight in reqs:
            print(f'      - [{req_id}] {req_text} (weight: {weight})')
    else:
        print(f'   📋 Yêu cầu: không có')
    
    # Get test cases
    cursor.execute('''
    SELECT testcase_id, input_data, expected_output, score_weight
    FROM assignment_testcases
    WHERE assignment_id = %s
    ORDER BY testcase_id;
    ''', (assign_id,))
    
    tests = cursor.fetchall()
    if tests:
        print(f'   🧪 Test Cases ({len(tests)}):')
        for test_id, input_data, expected, weight in tests:
            input_display = repr(input_data[:30]) if input_data else 'None'
            expected_display = repr(expected[:30]) if expected else 'None'
            print(f'      - [Test {test_id}] Input: {input_display} → Expected: {expected_display} (weight: {weight})')
    else:
        print(f'   🧪 Test Cases: không có')

print('\n' + '='*80)

cursor.close()
conn.close()
