import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='AI3',
    user='postgres',
    password='123456'
)

cursor = conn.cursor()

print('\n' + '='*100)
print('DANH SÁCH SUBMISSION VÀ KẾT QUẢ CHẤM ĐIỂM GẦN ĐÂY'.center(100))
print('='*100 + '\n')

cursor.execute('''
SELECT es.session_id, s.student_id, a.assignment_id, a.title,
       COALESCE(es.syntax_score, 0) as syntax_score,
       COALESCE(es.structure_score, 0) as structure_score,
       COALESCE(es.requirement_score, 0) as requirement_score,
       COALESCE(es.test_score, 0) as test_score,
       COALESCE(es.llm_score, 0) as llm_score,
       COALESCE(es.total_score, 0) as total_score,
       es.created_at
FROM evaluation_sessions es
JOIN submissions s ON es.submission_id = s.submission_id
JOIN assignments a ON s.assignment_id = a.assignment_id
ORDER BY es.created_at DESC
LIMIT 15;
''')

rows = cursor.fetchall()
for session_id, student_id, assign_id, title, syntax, structure, req, test, llm, total, created in rows:
    status_emoji = '✅' if total >= 75 else '⚠️' if total >= 50 else '❌'
    print(f'{status_emoji} Session {session_id} | Student {student_id} | Assignment {assign_id}: {title}')
    print(f'   Scores: Syntax={syntax:.0f}/20 | Struct={structure:.0f}/20 | Req={req:.0f}/20 | Test={test:.0f}/20 | LLM={llm:.0f}/20')
    print(f'   TOTAL: {total:.0f}/100 | Time: {str(created)[:19]}')
    print()

print('='*100)

cursor.close()
conn.close()
