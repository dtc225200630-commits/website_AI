import os
import sys
import tempfile

import psycopg2

sys.path.insert(0, ".")
from agents.coordinator import coordinator

# Intentionally wrong for assignment 1: for input 2 and 3 it prints 12.56
WRONG_CODE = """r = float(input())\n_ = float(input())\nprint(3.14 * r * r)\n"""


def main() -> None:
    conn = psycopg2.connect(
        host="localhost", port=5432, database="AI3", user="postgres", password="123456"
    )
    with conn.cursor() as cur:
        cur.execute(
            "SELECT requirement_text, weight FROM assignment_requirements WHERE assignment_id=%s ORDER BY requirement_id",
            (1,),
        )
        requirements = [
            {"requirement_text": t, "weight": float(w) if w else 1.0} for t, w in cur.fetchall()
        ]
        cur.execute(
            "SELECT input_data, expected_output, score_weight FROM assignment_testcases WHERE assignment_id=%s ORDER BY testcase_id",
            (1,),
        )
        testcases = [
            {"input_data": i, "expected_output": e, "score_weight": float(w) if w else 1.0}
            for i, e, w in cur.fetchall()
        ]
    conn.close()

    fd, path = tempfile.mkstemp(suffix=".py", text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(WRONG_CODE)

        result = coordinator(path, requirements, testcases)
        print("test score:", result.get("test", {}).get("score"))
        print("test results:")
        for tr in result.get("test", {}).get("test_results", []):
            print(tr)
        print("total:", result.get("total", {}).get("total_score"))
    finally:
        if os.path.exists(path):
            os.remove(path)


if __name__ == "__main__":
    main()
