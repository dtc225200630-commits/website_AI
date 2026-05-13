# -*- coding: utf-8 -*-
"""Đáp án mẫu Python: khớp testcase snapshot (assignment_id 1..11).

Chạy kiểm tra: python dap_an_dat_100_diem.py
Xuất từng file để nộp: python dap_an_dat_100_diem.py export
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path


def _run_solution(path: str, inp: str) -> tuple[int, str, str]:
    """Chạy file .py với stdin UTF-8; tránh UnicodeDecodeError trên Windows khi đọc pipe."""
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    cmd = [sys.executable, "-X", "utf8", path]
    r = subprocess.run(
        cmd,
        input=inp.encode("utf-8"),
        capture_output=True,
        timeout=10,
        env=env,
    )
    out = (r.stdout or b"").decode("utf-8", errors="replace").strip()
    err = (r.stderr or b"").decode("utf-8", errors="replace").strip()
    return r.returncode, out, err

ROOT = Path(__file__).resolve().parent

SOLUTIONS: dict[int, str] = {
    1: "a = int(input())\nb = int(input())\nprint(a + b)\n",
    2: "n = int(input())\nprint(\"chẵn\" if n % 2 == 0 else \"lẻ\")\n",
    3: "n = int(input())\nr = 1\nfor i in range(1, n + 1):\n    r *= i\nprint(r)\n",
    4: "n = int(input())\nprint(n * (n + 1) // 2)\n",
    5: "n = int(input())\nif n < 2:\n    print(\"không là số nguyên tố\")\nelse:\n    ok = True\n    for i in range(2, n):\n        if n % i == 0:\n            ok = False\n            break\n    print(\"là số nguyên tố\" if ok else \"không là số nguyên tố\")\n",
    6: "s = input()\nprint(s[::-1])\n",
    7: "a = int(input())\nb = int(input())\nc = int(input())\nprint(f\"{(a + b + c) / 3:.2f}\")\n",
    8: "c = int(input())\nprint((c * 9 / 5) + 32)\n",
    9: "d = int(input())\nif d >= 9:\n    print(\"Xuất sắc\")\nelif d >= 7:\n    print(\"Tốt\")\nelif d >= 5:\n    print(\"Khá\")\nelse:\n    print(\"Yếu\")\n",
    10: "a = int(input())\nb = int(input())\nop = input().strip()\nif op == \"+\":\n    print(a + b)\nelif op == \"-\":\n    print(a - b)\nelif op == \"*\":\n    print(a * b)\nelse:\n    print(a // b)\n",
    11: "s = input()\nprint(len(s.replace(\" \", \"\")))\n",
}

TESTCASES: dict[int, list[dict]] = {}


def _load_testcases() -> None:
    import json
    p = ROOT / 'du_lieu_bai_tap_va_quy_trinh.json'
    if not p.exists():
        return
    data = json.loads(p.read_text(encoding='utf-8'))
    for a in data.get('assignments', []):
        aid = int(a['assignment_id'])
        TESTCASES[aid] = a.get('testcases', [])


def verify_all() -> bool:
    _load_testcases()
    ok = True
    for aid, code in sorted(SOLUTIONS.items()):
        tests = TESTCASES.get(aid)
        if not tests:
            print(f'[skip] {aid}: không có testcase trong JSON')
            continue
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(code)
            path = f.name
        try:
            for i, tc in enumerate(tests, 1):
                inp = tc.get("input_data", "") or ""
                exp = tc.get("expected_output", "") or ""
                rc, out, err = _run_solution(path, inp)
                if rc != 0 and not out and err:
                    print(f"[FAIL] assignment {aid} test {i}: exit {rc}, stderr={err[:200]!r}")
                    ok = False
                    continue
                if out != exp.strip():
                    print(f"[FAIL] assignment {aid} test {i}: expected {exp!r} got {out!r}")
                    ok = False
        finally:
            Path(path).unlink(missing_ok=True)
    return ok


def write_solution_files(out_dir: str | Path = 'exported_solutions') -> None:
    d = Path(out_dir)
    d.mkdir(parents=True, exist_ok=True)
    for aid, code in SOLUTIONS.items():
        (d / f'bai_{aid}.py').write_text(code, encoding='utf-8')


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == "export":
        out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("loi_giai_nop_bai")
        write_solution_files(out)
        print(f"Đã ghi {len(SOLUTIONS)} file vào: {out.resolve()}")
    elif verify_all():
        print("Tất cả testcase trong JSON đều khớp đáp án.")
    else:
        sys.exit(1)
