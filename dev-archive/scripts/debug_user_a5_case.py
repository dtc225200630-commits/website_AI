import os
import sys
import tempfile

import psycopg2

sys.path.insert(0, ".")
from agents.coordinator import coordinator

CODE = '''import math

def is_prime(n):
    # So nguyen to phai lon hon 1
    if n > 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

n = int(input("Nhap so n: "))

if is_prime(n):
    print("Yes")
else:
    print("No")
'''


def main() -> None:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="AI3",
        user="postgres",
        password="123456",
    )
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT requirement_text, weight
            FROM assignment_requirements
            WHERE assignment_id=%s
            ORDER BY requirement_id
            """,
            (5,),
        )
        requirements = [
            {"requirement_text": text, "weight": float(weight) if weight else 1.0}
            for text, weight in cur.fetchall()
        ]

        cur.execute(
            """
            SELECT input_data, expected_output, score_weight
            FROM assignment_testcases
            WHERE assignment_id=%s
            ORDER BY testcase_id
            """,
            (5,),
        )
        testcases = [
            {
                "input_data": input_data,
                "expected_output": expected_output,
                "score_weight": float(score_weight) if score_weight else 1.0,
            }
            for input_data, expected_output, score_weight in cur.fetchall()
        ]
    conn.close()

    fd, temp_path = tempfile.mkstemp(suffix=".py", text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(CODE)

        result = coordinator(temp_path, requirements, testcases)

        print("syntax=", result.get("syntax", {}).get("score"))
        print("requirement=", result.get("requirement", {}).get("score"))
        print("structure=", result.get("structure", {}).get("score"))
        print("test=", result.get("test", {}).get("score"))
        print("llm=", result.get("llm", {}).get("score"))
        print("total=", result.get("total", {}).get("total_score"))

        print("\nTEST RESULTS")
        for item in result.get("test", {}).get("test_results", []):
            print(item)

        print("\nAGG DETAILS")
        for d in result.get("total", {}).get("details", []):
            print(d)

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == "__main__":
    main()
