"""
Gợi ý rubric theo từng bài (tiêu đề, mô tả, danh sách yêu cầu).

Mặc định: ưu tiên code tối giản / tối ưu (bài lab stdin/stdout).
Chỉ tăng trọng số hàm/class/số dòng khi đề bài nêu rõ.
"""

from __future__ import annotations

from typing import Any, Optional


def build_rubric_hints(
    title: str = "",
    description: str = "",
    requirements: Optional[list[Any]] = None,
) -> dict[str, bool]:
    req_parts: list[str] = []
    if requirements:
        for r in requirements:
            if isinstance(r, dict):
                req_parts.append(str(r.get("requirement_text") or ""))
            elif isinstance(r, (list, tuple)) and r:
                req_parts.append(str(r[0]))
    blob = " ".join([title or "", description or "", " ".join(req_parts)]).lower()

    # Mặc định khóa học: chấm thân thiện code ngắn, đúng là đủ.
    prefer_concise = True
    expect_functions = False
    expect_classes = False

    class_kw = (
        "class ",
        "class\n",
        "oop",
        "đối tượng",
        "hướng đối tượng",
        "định nghĩa lớp",
        "kế thừa",
    )
    func_kw = (
        "hàm ",
        " hàm",
        " ham ",  # không dấu
        " co ham",
        "có hàm",
        "function",
        "phải có def",
        "phai co def",
        "def ",
        "tách hàm",
        "tach ham",
        "thủ tục",
        "định nghĩa hàm",
        "dinh nghia ham",
        "gom logic vào hàm",
    )
    concise_kw = (
        "tối ưu",
        "ngắn gọn",
        "hiệu quả",
        "ít dòng",
        "tối thiểu",
        "pythonic",
        "idiomatic",
        "một lệnh",
        "gọn nhất",
    )

    if any(k in blob for k in class_kw):
        expect_classes = True
        prefer_concise = False
    if any(k in blob for k in func_kw):
        expect_functions = True
        prefer_concise = False
    if any(k in blob for k in concise_kw):
        prefer_concise = True

    # Đề vừa bắt hàm vừa nói tối ưu → ưu tiên đúng yêu cầu cấu trúc hơn "càng ít dòng càng tốt".
    if expect_functions and any(k in blob for k in concise_kw):
        prefer_concise = False

    return {
        "prefer_concise": prefer_concise,
        "expect_functions": expect_functions,
        "expect_classes": expect_classes,
    }
