import argparse
import psycopg2


def fetch_requirements(cur, assignment_id: int):
    cur.execute(
        """
        SELECT requirement_text, weight
        FROM assignment_requirements
        WHERE assignment_id = %s
        ORDER BY requirement_text;
        """,
        (assignment_id,),
    )
    return cur.fetchall()


def fetch_tests(cur, assignment_id: int):
    cur.execute(
        """
        SELECT testcase_id, input_data, expected_output, score_weight
        FROM assignment_testcases
        WHERE assignment_id = %s
        ORDER BY testcase_id;
        """,
        (assignment_id,),
    )
    return cur.fetchall()


def fetch_assignment(cur, assignment_id: int):
    cur.execute(
        "SELECT title, description FROM assignments WHERE assignment_id = %s;",
        (assignment_id,),
    )
    return cur.fetchone()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Show assignment requirements and test cases from DB"
    )
    parser.add_argument(
        "assignment_id",
        type=int,
        nargs="?",
        help="Assignment ID to show (omit to list all)",
    )
    parser.add_argument(
        "--db",
        default="AI3",
        help="Database name (default: AI3)",
    )
    parser.add_argument("--user", default="postgres", help="DB user (default: postgres)")
    parser.add_argument(
        "--password", default="123456", help="DB password (default: 123456)"
    )
    parser.add_argument("--host", default="localhost", help="DB host (default: localhost)")
    args = parser.parse_args()

    conn = psycopg2.connect(
        dbname=args.db,
        user=args.user,
        password=args.password,
        host=args.host,
    )
    cur = conn.cursor()

    if args.assignment_id is None:
        cur.execute("SELECT assignment_id FROM assignments ORDER BY assignment_id;")
        assignment_ids = [row[0] for row in cur.fetchall()]
    else:
        assignment_ids = [args.assignment_id]

    for assignment_id in assignment_ids:
        row = fetch_assignment(cur, assignment_id)
        if not row:
            print(f"Assignment {assignment_id} not found")
            continue

        title, desc = row
        print("=" * 70)
        print(f"Bai {assignment_id}: {title}")
        print("=" * 70)
        print(f"Description: {desc}\n")

        requirements = fetch_requirements(cur, assignment_id)
        print("Requirements:")
        if requirements:
            for idx, (text, weight) in enumerate(requirements, 1):
                print(f"  {idx}. {text} (weight: {weight})")
        else:
            print("  (No requirements)")

        tests = fetch_tests(cur, assignment_id)
        print("\nTest Cases:")
        if tests:
            for testcase_id, input_data, expected_output, weight in tests:
                input_data = (input_data or "").strip()
                expected_output = (expected_output or "").strip()
                print(
                    f"  Test {testcase_id}: Input='{input_data}' -> Output='{expected_output}' (weight: {weight})"
                )
        else:
            print("  (No test cases)")
        print("\n")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
