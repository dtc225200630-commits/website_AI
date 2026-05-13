import os
import sys
import tempfile

import psycopg2

sys.path.insert(0, ".")
from agents.coordinator import coordinator


def evaluate_assignment(assignment_id: int) -> dict:
    solution_file = f"solution_assignment{assignment_id}.py"

    with open(solution_file, "r", encoding="utf-8") as f:
        code = f.read()

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
            (assignment_id,),
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
            (assignment_id,),
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
            f.write(code)

        result = coordinator(temp_path, requirements, testcases)
        return {
            "assignment_id": assignment_id,
            "syntax": result.get("syntax", {}).get("score", 0),
            "requirement": result.get("requirement", {}).get("score", 0),
            "structure": result.get("structure", {}).get("score", 0),
            "test": result.get("test", {}).get("score", 0),
            "llm": result.get("llm", {}).get("score", 0),
            "total": result.get("total", {}).get("total_score", 0),
            "syntax_success": result.get("syntax", {}).get("success", False),
            "syntax_error": result.get("syntax", {}).get("error"),
            "summary": result.get("total", {}).get("details", []),
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def main() -> None:
    print("=== EVALUATE 10 SOLUTIONS ===")
    print("Scoring scale check: each core agent is 0-20, final total is 0-100.")
    print()

    totals = []
    for assignment_id in range(1, 11):
        out = evaluate_assignment(assignment_id)
        totals.append(out["total"])
        print(
            f"A{assignment_id}: total={out['total']}/100 | "
            f"syntax={out['syntax']} req={out['requirement']} struct={out['structure']} "
            f"test={out['test']} llm={out['llm']}"
        )
        if not out["syntax_success"]:
            print(f"  syntax_error: {out['syntax_error']}")

    print()
    print(f"Average total: {sum(totals) / len(totals):.2f}/100")


if __name__ == "__main__":
    main()
