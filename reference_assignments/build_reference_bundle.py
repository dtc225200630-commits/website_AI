#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Xuất 2 file cạnh thư mục này:
  1) du_lieu_bai_tap_va_quy_trinh.json — bài tập + yêu cầu + test + mô tả quy trình chấm
  2) dap_an_dat_100_diem.py — mã Python mẫu theo từng assignment_id (đủ test seed 1..11)

Chạy: python reference_assignments/build_reference_bundle.py
Có thể đặt DATABASE_URL giống app.py để lấy dữ liệu thật từ DB; nếu lỗi kết nối sẽ dùng snapshot.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

DIR = Path(__file__).resolve().parent
OUT_JSON = DIR / "du_lieu_bai_tap_va_quy_trinh.json"
OUT_PY = DIR / "dap_an_dat_100_diem.py"

# Snapshot khớp dev-archive/sql/seed_test_data.sql (bài 1) + seed_10_assignments.sql (bài 2..11)
_SNAPSHOT_ASSIGNMENTS: list[dict] = [
    {
        "assignment_id": 1,
        "class_id": 1,
        "title": "Viết chương trình cộng 2 số",
        "description": "Nhập 2 số và in ra tổng",
        "due_date": "2026-12-30T23:59:00",
        "programming_language": "Python",
        "requirements": [
            {"requirement_text": "Có dùng input()", "weight": 10.0},
            {"requirement_text": "Có phép cộng", "weight": 10.0},
            {"requirement_text": "Có print()", "weight": 10.0},
        ],
        "testcases": [
            {"input_data": "2\n3\n", "expected_output": "5", "score_weight": 10.0},
            {"input_data": "10\n20\n", "expected_output": "30", "score_weight": 10.0},
            {"input_data": "7\n8\n", "expected_output": "15", "score_weight": 10.0},
        ],
    },
    {
        "assignment_id": 2,
        "class_id": 1,
        "title": "Viết chương trình kiểm tra số chẵn hay lẻ",
        "description": "Nhập một số và kiểm tra xem nó là số chẵn hay số lẻ, in ra kết quả.",
        "due_date": "2026-12-31T23:59:00",
        "programming_language": "Python",
        "requirements": [
            {"requirement_text": "Có dùng input()", "weight": 10.0},
            {"requirement_text": "Có phép chia lấy dư (%) hoặc biểu thức điều kiện", "weight": 10.0},
            {"requirement_text": 'Có print() kết quả "chẵn" hoặc "lẻ"', "weight": 10.0},
        ],
        "testcases": [
            {"input_data": "4\n", "expected_output": "chẵn", "score_weight": 10.0},
            {"input_data": "7\n", "expected_output": "lẻ", "score_weight": 10.0},
            {"input_data": "0\n", "expected_output": "chẵn", "score_weight": 10.0},
        ],
    },
    {
        "assignment_id": 3,
        "class_id": 1,
        "title": "Viết chương trình tính giai thừa",
        "description": "Nhập một số n, tính và in ra giai thừa n! (n * (n-1) * (n-2) * ... * 1).",
        "due_date": "2027-01-05T23:59:00",
        "programming_language": "Python",
        "requirements": [
            {"requirement_text": "Có dùng input() và int()", "weight": 10.0},
            {"requirement_text": "Có sử dụng vòng lặp (for hoặc while)", "weight": 10.0},
            {"requirement_text": "Có tính toán và in ra kết quả giai thừa", "weight": 10.0},
        ],
        "testcases": [
            {"input_data": "5\n", "expected_output": "120", "score_weight": 10.0},
            {"input_data": "3\n", "expected_output": "6", "score_weight": 10.0},
            {"input_data": "0\n", "expected_output": "1", "score_weight": 10.0},
        ],
    },
    {
        "assignment_id": 4,
        "class_id": 1,
        "title": "Viết chương trình tính tổng từ 1 đến n",
        "description": "Nhập một số n, tính tổng các số từ 1 đến n, in ra kết quả.",
        "due_date": "2027-01-10T23:59:00",
        "programming_language": "Python",
        "requirements": [
            {"requirement_text": "Có dùng input() để nhập số n", "weight": 10.0},
            {"requirement_text": "Có sử dụng vòng lặp hoặc công thức tính tổng", "weight": 10.0},
            {"requirement_text": "Có print() kết quả tổng", "weight": 10.0},
        ],
        "testcases": [
            {"input_data": "5\n", "expected_output": "15", "score_weight": 10.0},
            {"input_data": "10\n", "expected_output": "55", "score_weight": 10.0},
            {"input_data": "1\n", "expected_output": "1", "score_weight": 10.0},
        ],
    },
    {
        "assignment_id": 5,
        "class_id": 1,
        "title": "Viết chương trình kiểm tra số nguyên tố",
        "description": "Nhập một số, kiểm tra xem nó có phải là số nguyên tố không (chỉ chia hết cho 1 và chính nó).",
        "due_date": "2027-01-15T23:59:00",
        "programming_language": "Python",
        "requirements": [
            {"requirement_text": "Có dùng input() để nhập số", "weight": 10.0},
            {"requirement_text": "Có vòng lặp để kiểm tra chia hết", "weight": 10.0},
            {"requirement_text": 'Có print() kết quả "là số nguyên tố" hoặc "không là số nguyên tố"', "weight": 10.0},
        ],
        "testcases": [
            {"input_data": "7\n", "expected_output": "là số nguyên tố", "score_weight": 10.0},
            {"input_data": "4\n", "expected_output": "không là số nguyên tố", "score_weight": 10.0},
            {"input_data": "2\n", "expected_output": "là số nguyên tố", "score_weight": 10.0},
        ],
    },
    {
        "assignment_id": 6,
        "class_id": 1,
        "title": "Viết chương trình đảo ngược chuỗi",
        "description": "Nhập một chuỗi ký tự, in ra chuỗi đó nhưng theo thứ tự đảo ngược.",
        "due_date": "2027-01-20T23:59:00",
        "programming_language": "Python",
        "requirements": [
            {"requirement_text": "Có dùng input() để nhập chuỗi", "weight": 10.0},
            {"requirement_text": "Có cách đảo ngược chuỗi (slicing hoặc vòng lặp)", "weight": 10.0},
            {"requirement_text": "Có print() chuỗi đảo ngược", "weight": 10.0},
        ],
        "testcases": [
            {"input_data": "hello\n", "expected_output": "olleh", "score_weight": 10.0},
            {"input_data": "Python\n", "expected_output": "nohtyP", "score_weight": 10.0},
            {"input_data": "abc\n", "expected_output": "cba", "score_weight": 10.0},
        ],
    },
    {
        "assignment_id": 7,
        "class_id": 1,
        "title": "Viết chương trình tính trung bình cộng",
        "description": "Nhập 3 số, tính trung bình cộng của 3 số đó và in ra kết quả (làm tròn 2 chữ số thập phân).",
        "due_date": "2027-01-25T23:59:00",
        "programming_language": "Python",
        "requirements": [
            {"requirement_text": "Có dùng input() để nhập 3 số", "weight": 10.0},
            {"requirement_text": "Có tính tổng 3 số rồi chia cho 3", "weight": 10.0},
            {"requirement_text": "Có print() kết quả trung bình cộng (làm tròn)", "weight": 10.0},
        ],
        "testcases": [
            {"input_data": "5\n10\n15\n", "expected_output": "10.00", "score_weight": 10.0},
            {"input_data": "7\n8\n9\n", "expected_output": "8.00", "score_weight": 10.0},
            {"input_data": "3\n6\n9\n", "expected_output": "6.00", "score_weight": 10.0},
        ],
    },
    {
        "assignment_id": 8,
        "class_id": 1,
        "title": "Viết chương trình chuyển đổi nhiệt độ Celsius sang Fahrenheit",
        "description": "Nhập nhiệt độ Celsius, chuyển sang Fahrenheit theo công thức: F = (C * 9/5) + 32, in ra kết quả.",
        "due_date": "2027-02-01T23:59:00",
        "programming_language": "Python",
        "requirements": [
            {"requirement_text": "Có dùng input() để nhập độ Celsius", "weight": 10.0},
            {"requirement_text": "Có công thức chuyển đổi đúng: F = (C * 9/5) + 32", "weight": 10.0},
            {"requirement_text": "Có print() kết quả nhiệt độ Fahrenheit", "weight": 10.0},
        ],
        "testcases": [
            {"input_data": "0\n", "expected_output": "32.0", "score_weight": 10.0},
            {"input_data": "100\n", "expected_output": "212.0", "score_weight": 10.0},
            {"input_data": "25\n", "expected_output": "77.0", "score_weight": 10.0},
        ],
    },
    {
        "assignment_id": 9,
        "class_id": 1,
        "title": "Viết chương trình phân loại điểm số",
        "description": "Nhập điểm số (0-10), phân loại thành: Xuất sắc (9-10), Tốt (7-8), Khá (5-6), Yếu (<5), in ra kết quả.",
        "due_date": "2027-02-05T23:59:00",
        "programming_language": "Python",
        "requirements": [
            {"requirement_text": "Có dùng input() để nhập điểm số", "weight": 10.0},
            {"requirement_text": "Có sử dụng if-elif-else hoặc cấu trúc điều kiện", "weight": 10.0},
            {"requirement_text": "Có print() kết quả phân loại đúng theo khoảng điểm", "weight": 10.0},
        ],
        "testcases": [
            {"input_data": "9\n", "expected_output": "Xuất sắc", "score_weight": 10.0},
            {"input_data": "7\n", "expected_output": "Tốt", "score_weight": 10.0},
            {"input_data": "4\n", "expected_output": "Yếu", "score_weight": 10.0},
        ],
    },
    {
        "assignment_id": 10,
        "class_id": 1,
        "title": "Viết chương trình máy tính đơn giản",
        "description": "Nhập 2 số và một phép toán (+, -, *, /), in ra kết quả của phép toán đó.",
        "due_date": "2027-02-10T23:59:00",
        "programming_language": "Python",
        "requirements": [
            {"requirement_text": "Có dùng input() để nhập 2 số và phép toán", "weight": 10.0},
            {"requirement_text": "Có sử dụng if-elif hoặc cấu trúc xử lý phép toán", "weight": 10.0},
            {"requirement_text": "Có print() kết quả phép toán", "weight": 10.0},
        ],
        "testcases": [
            {"input_data": "10\n5\n+\n", "expected_output": "15", "score_weight": 10.0},
            {"input_data": "10\n5\n-\n", "expected_output": "5", "score_weight": 10.0},
            {"input_data": "10\n5\n*\n", "expected_output": "50", "score_weight": 10.0},
        ],
    },
    {
        "assignment_id": 11,
        "class_id": 1,
        "title": "Viết chương trình đếm số ký tự trong chuỗi",
        "description": "Nhập một chuỗi, đếm số lượng ký tự (không tính khoảng trắng) và in ra kết quả.",
        "due_date": "2027-02-15T23:59:00",
        "programming_language": "Python",
        "requirements": [
            {"requirement_text": "Có dùng input() để nhập chuỗi", "weight": 10.0},
            {"requirement_text": "Có hàm len() hoặc vòng lặp để đếm ký tự", "weight": 10.0},
            {"requirement_text": "Có print() số lượng ký tự (loại bỏ khoảng trắng)", "weight": 10.0},
        ],
        "testcases": [
            {"input_data": "hello world\n", "expected_output": "10", "score_weight": 10.0},
            {"input_data": "python\n", "expected_output": "6", "score_weight": 10.0},
            {"input_data": "a b c\n", "expected_output": "3", "score_weight": 10.0},
        ],
    },
]

_QUY_TRINH = {
    "tong_diem_hien_thi": "100 điểm = Cú pháp (20) + Phân tích (20) + Yêu cầu (20) + Cấu trúc (20) + Test (20). Điểm LLM chỉ nhận xét, không cộng vào tổng.",
    "thu_tu_agent": [
        "SyntaxAgent — ast.parse + chạy thử Python (stdin probe) hoặc biên dịch C++",
        "CodeAnalysisAgent — AST tĩnh: đặt tên, modular, import, độ phức tạp",
        "RequirementAgent — so khớp yêu cầu (LLM tùy chọn + fallback)",
        "StructureAgent — cấu trúc hàm/lớp/import (Python AST hoặc regex C++)",
        "TestAgent — chạy từng testcase, so stdout với expected_output",
        "LLMAgent — nhận xét bổ sung",
        "AggregationAgent — gộp điểm các nhánh",
    ],
    "ghi_chu": "Đáp án trong dap_an_dat_100_diem.py đảm bảo PASS toàn bộ testcase trong snapshot; điểm tối đa 100 phụ thuộc thêm agent phân tích/cấu trúc/yêu cầu.",
}


def _fetch_from_postgres() -> list[dict] | None:
    try:
        import psycopg2
    except ImportError:
        return None
    url = os.getenv("DATABASE_URL", "postgresql://postgres:123456@localhost:5432/AI3")
    try:
        conn = psycopg2.connect(url)
    except Exception:
        return None
    rows: list[dict] = []
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT assignment_id, class_id, title, description, due_date, programming_language
                FROM assignments
                ORDER BY assignment_id
                """
            )
            for r in cur.fetchall():
                aid = r[0]
                cur.execute(
                    """
                    SELECT requirement_text, weight
                    FROM assignment_requirements
                    WHERE assignment_id = %s
                    ORDER BY requirement_id
                    """,
                    (aid,),
                )
                reqs = [{"requirement_text": x[0] or "", "weight": float(x[1] or 10)} for x in cur.fetchall()]
                cur.execute(
                    """
                    SELECT input_data, expected_output, score_weight
                    FROM assignment_testcases
                    WHERE assignment_id = %s
                    ORDER BY testcase_id
                    """,
                    (aid,),
                )
                tests = [
                    {
                        "input_data": t[0] if t[0] is not None else "",
                        "expected_output": t[1] if t[1] is not None else "",
                        "score_weight": float(t[2] or 10),
                    }
                    for t in cur.fetchall()
                ]
                due = r[4]
                if due is not None and hasattr(due, "isoformat"):
                    due_s = due.isoformat()
                else:
                    due_s = str(due) if due else ""
                rows.append(
                    {
                        "assignment_id": aid,
                        "class_id": r[1],
                        "title": r[2] or "",
                        "description": r[3] or "",
                        "due_date": due_s,
                        "programming_language": r[5] or "Python",
                        "requirements": reqs,
                        "testcases": tests,
                    }
                )
    finally:
        conn.close()
    return rows if rows else None


SOLUTIONS: dict[int, str] = {
    1: """a = int(input())
b = int(input())
print(a + b)
""",
    2: """n = int(input())
print("chẵn" if n % 2 == 0 else "lẻ")
""",
    3: """n = int(input())
r = 1
for i in range(1, n + 1):
    r *= i
print(r)
""",
    4: """n = int(input())
print(n * (n + 1) // 2)
""",
    5: """n = int(input())
if n < 2:
    print("không là số nguyên tố")
else:
    ok = True
    for i in range(2, n):
        if n % i == 0:
            ok = False
            break
    print("là số nguyên tố" if ok else "không là số nguyên tố")
""",
    6: """s = input()
print(s[::-1])
""",
    7: """a = int(input())
b = int(input())
c = int(input())
print(f"{(a + b + c) / 3:.2f}")
""",
    8: """c = int(input())
print((c * 9 / 5) + 32)
""",
    9: """d = int(input())
if d >= 9:
    print("Xuất sắc")
elif d >= 7:
    print("Tốt")
elif d >= 5:
    print("Khá")
else:
    print("Yếu")
""",
    10: """a = int(input())
b = int(input())
op = input().strip()
if op == "+":
    print(a + b)
elif op == "-":
    print(a - b)
elif op == "*":
    print(a * b)
else:
    print(a // b)
""",
    11: """s = input()
print(len(s.replace(" ", "")))
""",
}


def _render_dap_an_py() -> str:
    lines = [
        "# -*- coding: utf-8 -*-",
        '"""Đáp án mẫu Python: khớp testcase snapshot (assignment_id 1..11).',
        "",
        "Chạy kiểm tra: python dap_an_dat_100_diem.py",
        "Xuất từng file để nộp: python dap_an_dat_100_diem.py export",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "import os",
        "import subprocess",
        "import sys",
        "import tempfile",
        "from pathlib import Path",
        "",
        "ROOT = Path(__file__).resolve().parent",
        "",
        "",
        "def _run_solution(path: str, inp: str) -> tuple[int, str, str]:",
        "    env = os.environ.copy()",
        '    env["PYTHONIOENCODING"] = "utf-8"',
        '    env["PYTHONUTF8"] = "1"',
        '    cmd = [sys.executable, "-X", "utf8", path]',
        "    r = subprocess.run(",
        "        cmd,",
        '        input=inp.encode("utf-8"),',
        "        capture_output=True,",
        "        timeout=10,",
        "        env=env,",
        "    )",
        '    out = (r.stdout or b"").decode("utf-8", errors="replace").strip()',
        '    err = (r.stderr or b"").decode("utf-8", errors="replace").strip()',
        "    return r.returncode, out, err",
        "",
        "SOLUTIONS: dict[int, str] = {",
    ]
    for aid in sorted(SOLUTIONS):
        code = SOLUTIONS[aid]
        lit = json.dumps(code, ensure_ascii=False)
        lines.append(f"    {aid}: {lit},")
    lines.append("}")
    lines.extend(
        [
            "",
            "TESTCASES: dict[int, list[dict]] = {}",
            "",
            "",
            "def _load_testcases() -> None:",
            "    import json",
            "    p = ROOT / 'du_lieu_bai_tap_va_quy_trinh.json'",
            "    if not p.exists():",
            "        return",
            "    data = json.loads(p.read_text(encoding='utf-8'))",
            "    for a in data.get('assignments', []):",
            "        aid = int(a['assignment_id'])",
            "        TESTCASES[aid] = a.get('testcases', [])",
            "",
            "",
            "def verify_all() -> bool:",
            "    _load_testcases()",
            "    ok = True",
            "    for aid, code in sorted(SOLUTIONS.items()):",
            "        tests = TESTCASES.get(aid)",
            "        if not tests:",
            "            print(f'[skip] {aid}: không có testcase trong JSON')",
            "            continue",
            "        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False, encoding='utf-8') as f:",
            "            f.write(code)",
            "            path = f.name",
            "        try:",
            "            for i, tc in enumerate(tests, 1):",
            "                inp = tc.get('input_data', '') or ''",
            "                exp = tc.get('expected_output', '') or ''",
            "                rc, out, err = _run_solution(path, inp)",
            "                if rc != 0 and not out and err:",
            "                    print(f'[FAIL] assignment {aid} test {i}: exit {rc}, stderr={err[:200]!r}')",
            "                    ok = False",
            "                    continue",
            "                if out != exp.strip():",
            "                    print(f'[FAIL] assignment {aid} test {i}: expected {exp!r} got {out!r}')",
            "                    ok = False",
            "        finally:",
            "            Path(path).unlink(missing_ok=True)",
            "    return ok",
            "",
            "",
            "def write_solution_files(out_dir: str | Path = 'exported_solutions') -> None:",
            "    d = Path(out_dir)",
            "    d.mkdir(parents=True, exist_ok=True)",
            "    for aid, code in SOLUTIONS.items():",
            "        (d / f'bai_{aid}.py').write_text(code, encoding='utf-8')",
            "",
            "",
            'if __name__ == "__main__":',
            '    if len(sys.argv) > 1 and sys.argv[1].lower() == "export":',
            '        out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("loi_giai_nop_bai")',
            "        write_solution_files(out)",
            '        print(f"Đã ghi {len(SOLUTIONS)} file vào: {out.resolve()}")',
            "    elif verify_all():",
            "        print('Tất cả testcase trong JSON đều khớp đáp án.')",
            "    else:",
            "        sys.exit(1)",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    from_db = _fetch_from_postgres()
    # File chính luôn từ snapshot seed để đáp án khớp testcase; DB có thể khác assignment_id.
    bundle_chinh = {
        "meta": {
            "nguon_du_lieu": "snapshot_seed_sql (seed_test_data + seed_10_assignments)",
            "tao_luc": datetime.now(timezone.utc).isoformat(),
            "ghi_chu": "Nếu cần dump DB thật, xem file du_lieu_bai_tap_tu_postgres.json (khi kết nối được).",
        },
        "quy_trinh_cham_bai": _QUY_TRINH,
        "assignments": _SNAPSHOT_ASSIGNMENTS,
    }
    OUT_JSON.write_text(json.dumps(bundle_chinh, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_PY.write_text(_render_dap_an_py(), encoding="utf-8")
    print(f"Đã ghi: {OUT_JSON}")
    print(f"Đã ghi: {OUT_PY}")
    if from_db:
        extra = DIR / "du_lieu_bai_tap_tu_postgres.json"
        extra.write_text(
            json.dumps(
                {
                    "meta": {
                        "nguon_du_lieu": "postgresql",
                        "tao_luc": datetime.now(timezone.utc).isoformat(),
                    },
                    "quy_trinh_cham_bai": _QUY_TRINH,
                    "assignments": from_db,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"Đã ghi thêm (DB): {extra}")


if __name__ == "__main__":
    main()
