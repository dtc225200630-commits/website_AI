#!/usr/bin/env python3
import psycopg2

conn = psycopg2.connect(host='localhost', database='AI3', user='postgres', password='123456')
cur = conn.cursor()

print('ALL ASSIGNMENTS:')
cur.execute('SELECT assignment_id, title FROM assignments ORDER BY assignment_id')
for row in cur.fetchall():
    print(f'  Assignment {row[0]}: {row[1]}')

print('\nREQUIREMENTS & TESTCASES COUNT:')
cur.execute('''
    SELECT 
        a.assignment_id, 
        a.title,
        COUNT(DISTINCT ar.requirement_id) as req_count,
        COUNT(DISTINCT at.testcase_id) as test_count
    FROM assignments a
    LEFT JOIN assignment_requirements ar ON a.assignment_id = ar.assignment_id
    LEFT JOIN assignment_testcases at ON a.assignment_id = at.assignment_id
    GROUP BY a.assignment_id, a.title
    ORDER BY a.assignment_id
''')
for row in cur.fetchall():
    print(f'  ID {row[0]:2d}: "{row[1]:30s}" -> {row[2]:2d} req', f'{row[3]:2d} tests')

conn.close()
