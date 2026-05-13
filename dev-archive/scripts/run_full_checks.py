import argparse
import subprocess
import sys


def run_cmd(cmd: list[str]) -> int:
    print("\n$", " ".join(cmd))
    proc = subprocess.run(cmd)
    return proc.returncode


def main() -> None:
    parser = argparse.ArgumentParser(description="Run full scoring checks")
    parser.add_argument("--submission-id", type=int, default=None, help="Optional submission id for deep audit")
    args = parser.parse_args()

    # 1) Evaluate local 10 solution files
    code1 = run_cmd([sys.executable, "evaluate_10_solutions.py"])

    # 2) Optional deep audit for one submission
    code2 = 0
    if args.submission_id is not None:
        code2 = run_cmd([sys.executable, "audit_submission.py", str(args.submission_id)])

    if code1 != 0 or code2 != 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
