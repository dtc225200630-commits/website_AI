import psycopg2

conn = psycopg2.connect(dbname='MAS_Programming_Assessment', user='postgres', password='123456', host='localhost')
cur = conn.cursor()

cur.execute("""SELECT column_name FROM information_schema.columns 
              WHERE table_name='submissions' ORDER BY ordinal_position;""")
cols = [row[0] for row in cur.fetchall()]
print("Submissions columns:", cols)

cur.execute("SELECT * FROM submissions LIMIT 3;")
rows = cur.fetchall()
for row in rows:
    print("Submission:", row)

cur.execute("""SELECT column_name FROM information_schema.columns 
              WHERE table_name='assignment_requirements' ORDER BY ordinal_position;""")
cols = [row[0] for row in cur.fetchall()]
print("\nAssignment_requirements columns:", cols)

cur.execute("SELECT * FROM assignment_requirements LIMIT 3;")
rows = cur.fetchall()
for row in rows:
    print("Requirement:", row)

conn.close()
