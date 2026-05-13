import argparse
import json
import os
from decimal import Decimal

import psycopg2


def _to_float(value) -> float:
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


def _has_runtime_or_exec_errors(agent_details) -> bool:
    try:
        test_results = (agent_details or {}).get("test", {}).get("test_results", []) or []
        for tr in test_results:
            status = str((tr or {}).get("status", "")).upper()
            if status in {"ERROR", "TIMEOUT", "COMPILE_ERROR"}:
                return True
    except Exception:
        return False
    return False


def _syntax_success(agent_details, syntax_score: float) -> bool:
    try:
        syntax = (agent_details or {}).get("syntax", {})
        if "success" in syntax:
            return bool(syntax.get("success"))
    except Exception:
        pass
    return syntax_score > 0


def compute_new_total(row) -> tuple[int, dict]:
    (
        session_id,
        submission_id,
        syntax_score,
        structure_score,
        requirement_score,
        test_score,
        total_score,
        agent_details,
        code_analysis_score,
        llm_score,
    ) = row

    syntax_score = _to_float(syntax_score)
    structure_score = _to_float(structure_score)
    requirement_score = _to_float(requirement_score)
    test_score = _to_float(test_score)
    code_analysis_score = _to_float(code_analysis_score)
    old_total = _to_float(total_score)
    llm_score = _to_float(llm_score)

    # New scored core: syntax + requirement + structure + code_analysis + test
    core_sum = syntax_score + requirement_score + structure_score + code_analysis_score + test_score
    new_total = int(core_sum)
    new_total = min(100, max(0, new_total))

    details_obj = agent_details
    if isinstance(agent_details, str):
        try:
            details_obj = json.loads(agent_details)
        except Exception:
            details_obj = {}
    if details_obj is None:
        details_obj = {}

    syntax_ok = _syntax_success(details_obj, syntax_score)
    has_runtime_errors = _has_runtime_or_exec_errors(details_obj)

    # Keep legacy hard gates for consistency.
    if (not syntax_ok) or syntax_score <= 0:
        new_total = min(new_total, 40)
    if has_runtime_errors:
        new_total = min(new_total, 60)
    if syntax_score < 20 or test_score < 20:
        new_total = min(new_total, 99)

    meta = {
        "session_id": session_id,
        "submission_id": submission_id,
        "old_total": old_total,
        "new_total": new_total,
        "syntax": syntax_score,
        "requirement": requirement_score,
        "structure": structure_score,
        "code_analysis": code_analysis_score,
        "test": test_score,
        "llm": llm_score,
        "syntax_ok": syntax_ok,
        "has_runtime_errors": has_runtime_errors,
    }
    return new_total, meta


def main():
    parser = argparse.ArgumentParser(description="Recalculate total_score with new core-agent formula.")
    parser.add_argument("--apply", action="store_true", help="Apply updates to DB. Default is dry-run.")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of rows to process (0 = all).")
    args = parser.parse_args()

    dsn = os.getenv("DATABASE_URL", "postgresql://postgres:123456@localhost:5432/AI3")
    conn = psycopg2.connect(dsn)

    try:
        with conn.cursor() as cur:
            query = """
                SELECT
                    session_id,
                    submission_id,
                    syntax_score,
                    structure_score,
                    requirement_score,
                    test_score,
                    total_score,
                    agent_details,
                    code_analysis_score,
                    llm_score
                FROM evaluation_sessions
                ORDER BY created_at DESC
            """
            if args.limit and args.limit > 0:
                query += " LIMIT %s"
                cur.execute(query, (args.limit,))
            else:
                cur.execute(query)

            rows = cur.fetchall()

            changed = 0
            unchanged = 0
            previews = []

            for row in rows:
                new_total, meta = compute_new_total(row)
                if int(meta["old_total"]) != int(new_total):
                    changed += 1
                    previews.append(meta)
                    if args.apply:
                        cur.execute(
                            "UPDATE evaluation_sessions SET total_score = %s WHERE session_id = %s",
                            (new_total, meta["session_id"]),
                        )
                else:
                    unchanged += 1

            if args.apply:
                conn.commit()
            else:
                conn.rollback()

            mode = "APPLY" if args.apply else "DRY-RUN"
            print(f"[{mode}] processed={len(rows)} changed={changed} unchanged={unchanged}")
            print("Sample changed rows (up to 10):")
            for item in previews[:10]:
                print(
                    f"session={item['session_id']} submission={item['submission_id']} "
                    f"old={int(item['old_total'])} new={item['new_total']} "
                    f"(syn={item['syntax']}, req={item['requirement']}, str={item['structure']}, "
                    f"ana={item['code_analysis']}, test={item['test']}, llm={item['llm']})"
                )
    finally:
        conn.close()


if __name__ == "__main__":
    main()
