import argparse
import json

import psycopg2


def fetch_submission_audit(submission_id: int) -> dict:
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
            SELECT
                es.session_id,
                es.submission_id,
                s.assignment_id,
                a.title,
                s.student_id,
                st.full_name AS student_name,
                es.syntax_score,
                es.code_analysis_score,
                es.requirement_score,
                es.structure_score,
                es.test_score,
                es.llm_score,
                es.total_score,
                es.final_feedback,
                es.agent_details,
                es.created_at
            FROM evaluation_sessions es
            JOIN submissions s ON s.submission_id = es.submission_id
            JOIN assignments a ON a.assignment_id = s.assignment_id
            JOIN students st ON st.student_id = s.student_id
            WHERE es.submission_id = %s
            ORDER BY es.created_at DESC
            LIMIT 1
            """,
            (submission_id,),
        )
        row = cur.fetchone()
    conn.close()

    if not row:
        raise SystemExit(f"No evaluation session found for submission_id={submission_id}")

    cols = [
        "session_id",
        "submission_id",
        "assignment_id",
        "assignment_title",
        "student_id",
        "student_name",
        "syntax_score",
        "code_analysis_score",
        "requirement_score",
        "structure_score",
        "test_score",
        "llm_score",
        "total_score",
        "final_feedback",
        "agent_details",
        "created_at",
    ]
    out = dict(zip(cols, row))

    raw = out.get("agent_details")
    if isinstance(raw, dict):
        out["agent_details"] = raw
    else:
        try:
            out["agent_details"] = json.loads(raw) if raw else {}
        except Exception:
            out["agent_details"] = {}

    return out


def print_human(audit: dict) -> None:
    print("=== SUBMISSION AUDIT ===")
    print(f"Submission: {audit['submission_id']} | Session: {audit['session_id']}")
    print(f"Assignment: {audit['assignment_id']} - {audit['assignment_title']}")
    print(f"Student: {audit['student_id']} - {audit['student_name']}")
    print("--- Scores ---")
    print(f"syntax        : {audit['syntax_score']}")
    print(f"code_analysis : {audit['code_analysis_score']}")
    print(f"requirement   : {audit['requirement_score']}")
    print(f"structure     : {audit['structure_score']}")
    print(f"test          : {audit['test_score']}")
    print(f"llm           : {audit['llm_score']}")
    print(f"total         : {audit['total_score']}")
    print("--- Final Feedback ---")
    print(audit.get("final_feedback") or "")
    print("--- Agent Details (JSON) ---")
    print(json.dumps(audit.get("agent_details", {}), ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit one submission scoring breakdown")
    parser.add_argument("submission_id", type=int, help="Submission ID to inspect")
    args = parser.parse_args()

    audit = fetch_submission_audit(args.submission_id)
    print_human(audit)


if __name__ == "__main__":
    main()
