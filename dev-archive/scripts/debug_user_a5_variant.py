import os
import sys
import tempfile

import psycopg2

sys.path.insert(0, ".")
from agents.coordinator import coordinator

CODE = '''class InputParser:
    """Parses integer input."""

    @staticmethod
    def safe_int(text: str, default: int = 0) -> int:
        """Convert text to int safely."""
        try:
            return int(text)
        except Exception:
            return default

    @staticmethod
    def read_number() -> int:
        """Read integer from stdin.

        
        """
        return InputParser.safe_int(input().strip())


class PrimeService:
    """Prime checking business logic."""

    @staticmethod
    def is_prime(n: int) -> bool:
        
       
        if n == 2:
            return False
        if n % 2 == 0:
            return False
        i = 3
        while i * i <= n:
            if n % i == 0:
                return False
            i += 2
        return True


def format_result(is_prime_number: bool) -> str:
    if is_prime_number:
        return "Yes"
    return "No"
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

        print("\nREQUIREMENT DETAILS")
        for d in result.get("requirement", {}).get("details", []):
            print(d)

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == "__main__":
    main()
