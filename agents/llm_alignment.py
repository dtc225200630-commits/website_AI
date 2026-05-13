"""
Align LLM review output with deterministic agent results.

The LLM must not contradict testcase/requirement/syntax outcomes from the
automated pipeline; this module computes a canonical ground-truth snapshot
and post-processes model output to remove obvious conflicts.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple


def _safe_int(x: Any, default: int = 0) -> int:
    try:
        if x is None:
            return default
        return int(float(x))
    except Exception:
        return default


def compute_evaluation_truth(agent_results: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Single source of truth for prompt + post-alignment (from agent dicts)."""
    agent_results = agent_results or {}
    syntax = agent_results.get("syntax") or {}
    requirement = agent_results.get("requirement") or {}
    test = agent_results.get("test") or {}
    structure = agent_results.get("structure") or {}
    code_analysis = agent_results.get("code_analysis") or {}

    syntax_ok = bool(syntax.get("success", False))

    passed = _safe_int(test.get("passed_count"))
    total_tests = _safe_int(test.get("total_tests")) or _safe_int(test.get("total_count"))
    test_results = test.get("test_results") or []
    if isinstance(test_results, list) and test_results:
        if total_tests <= 0:
            total_tests = len(test_results)
        if passed <= 0 and total_tests > 0:
            passed = sum(1 for r in test_results if (r or {}).get("status") == "PASS")

    tests_all_pass = total_tests == 0 or (total_tests > 0 and passed >= total_tests)
    any_test_fail = total_tests > 0 and passed < total_tests

    fulfilled = _safe_int(requirement.get("fulfilled_count", requirement.get("fulfilled")))
    total_req = _safe_int(requirement.get("total_count", requirement.get("total")))
    reqs_all_met = total_req == 0 or (total_req > 0 and fulfilled >= total_req)

    missing_reqs = (
        requirement.get("requirements_missing")
        or requirement.get("unfulfilled")
        or []
    )
    if not isinstance(missing_reqs, list):
        missing_reqs = []

    scores = {
        "syntax": _safe_int(syntax.get("score")),
        "requirement": _safe_int(requirement.get("score")),
        "structure": _safe_int(structure.get("score")),
        "code_analysis": _safe_int(code_analysis.get("score")),
        "test": _safe_int(test.get("score")),
    }

    return {
        "syntax_ok": syntax_ok,
        "tests_all_pass": tests_all_pass,
        "any_test_fail": any_test_fail,
        "test_passed": passed,
        "test_total": total_tests,
        "reqs_all_met": reqs_all_met,
        "req_fulfilled": fulfilled,
        "req_total": total_req,
        "missing_requirements": [str(x) for x in missing_reqs][:12],
        "scores": scores,
    }


def llm_support_score_when_unavailable(agent_results: Optional[Dict[str, Any]]) -> int:
    """
    Score 0-20 to show when Gemini did not produce a real review (quota, outage, etc.).

    Uses the average of the five scored agents so the UI never shows 20/20 for LLM
    while Test/Analysis are near zero.
    """
    if not agent_results:
        return 10
    truth = compute_evaluation_truth(agent_results)
    sc = truth["scores"]
    core_avg = (
        sc["syntax"] + sc["requirement"] + sc["structure"] + sc["code_analysis"] + sc["test"]
    ) / 5.0
    return max(0, min(20, int(round(core_avg))))


def format_ground_truth_block(truth: Dict[str, Any]) -> str:
    """Human-readable block injected into the LLM prompt."""
    sc = truth["scores"]
    lines: List[str] = [
        "=== TRANG THAI CHAM DINH (NGUON SU THAT - KHONG DUOC MAU THUAN) ===",
        f"- Syntax chay duoc: {truth['syntax_ok']}",
    ]
    if truth["test_total"] > 0:
        lines.append(
            f"- Test tu dong: {truth['test_passed']}/{truth['test_total']} PASS; "
            f"tat_ca_pass={truth['tests_all_pass']}"
        )
    else:
        lines.append("- Test tu dong: (khong co testcase trong he thong)")

    if truth["req_total"] > 0:
        lines.append(
            f"- Yeu cau: {truth['req_fulfilled']}/{truth['req_total']} dat; "
            f"dat_het={truth['reqs_all_met']}"
        )
        if truth["missing_requirements"]:
            miss = ", ".join(truth["missing_requirements"][:5])
            lines.append(f"  + Yeu cau CHUA DAT (neu co): {miss}")
    else:
        lines.append("- Yeu cau: (khong co requirement trong he thong)")

    lines.append(
        "- Diem cac agent (/20, trung khop voi tong hop diem): "
        f"syntax={sc['syntax']}, requirement={sc['requirement']}, "
        f"structure={sc['structure']}, code_analysis={sc['code_analysis']}, test={sc['test']}"
    )
    return "\n".join(lines)


def _mentions_test_failure(text: str) -> bool:
    t = (text or "").lower()
    needles = (
        "test fail",
        "failed test",
        "failing test",
        "khong pass",
        "không pass",
        "khong qua test",
        "không qua test",
        "test that bai",
        "test thất bại",
        "sai test",
        "test sai",
        "loi test",
        "lỗi test",
        "expected '",
        "expected:",
        "expected output",
        "actual output",
        "ket qua test sai",
        "kết quả test sai",
        "testcase",
        "test case",
    )
    return any(n in t for n in needles)


def _implies_requirement_gap(text: str) -> bool:
    t = (text or "").lower()
    needles = (
        "chua dap ung yeu cau",
        "chưa đáp ứng yêu cầu",
        "khong dap ung yeu cau",
        "không đáp ứng yêu cầu",
        "thieu yeu cau",
        "thiếu yêu cầu",
        "khong du yeu cau",
        "không đủ yêu cầu",
        "requirement not met",
        "unmet requirement",
    )
    return any(n in t for n in needles)


def _append_improvement(improvements: List[str], note: str, cap: int = 8) -> List[str]:
    out = list(improvements or [])
    if note and note not in out:
        out.insert(0, note)
    return out[:cap]


def align_llm_output(llm_out: Dict[str, Any], agent_results: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Post-process parsed LLM JSON so must_fix / narrative do not contradict agents.

    Returns a new dict (does not mutate the input).
    """
    truth = compute_evaluation_truth(agent_results)
    out = {k: v for k, v in (llm_out or {}).items()}
    must_fix: List[str] = [str(x).strip() for x in (out.get("must_fix") or []) if str(x).strip()]
    improvements: List[str] = [str(x).strip() for x in (out.get("improvements") or []) if str(x).strip()]
    moved: List[str] = []

    # All automated tests passed: do not keep must_fix that claim test failures.
    if truth["tests_all_pass"] and truth["test_total"] > 0:
        kept: List[str] = []
        for m in must_fix:
            if _mentions_test_failure(m):
                moved.append(m)
            else:
                kept.append(m)
        must_fix = kept

    # All DB requirements met: do not keep must_fix that claim unmet requirements.
    if truth["reqs_all_met"] and truth["req_total"] > 0:
        kept = []
        for m in must_fix:
            if _implies_requirement_gap(m):
                moved.append(m)
            else:
                kept.append(m)
        must_fix = kept

    for m in moved:
        improvements = _append_improvement(
            improvements,
            f"(Goi y chat luong / mo rong; he thong cham tu dong khong ghi nhan loi buoc nay) {m}",
        )

    # Syntax broken: must_fix should not claim "code chay on" / all tests pass in a contradictory way — prompt handles; optional note
    if not truth["syntax_ok"]:
        summary = str(out.get("summary", "") or "")
        low = summary.lower()
        if "pass" in low and "test" in low and "tat ca" in low.replace("tất cả", "tat ca"):
            out["summary"] = (
                "Code chua chay duoc theo SyntaxAgent; uu tien sua loi cu phap/runtime truoc. "
                + summary
            )

    out["must_fix"] = must_fix[:8]
    out["improvements"] = improvements[:8]

    # Align LLM score with deterministic agents (never max score while tests fail badly)
    score = _safe_int(out.get("score"), 10)
    sc = truth["scores"]
    core_avg = (
        sc["syntax"] + sc["requirement"] + sc["structure"] + sc["code_analysis"] + sc["test"]
    ) / 5.0
    if truth["tests_all_pass"] and truth["reqs_all_met"] and truth["syntax_ok"]:
        if score < max(12, int(round(core_avg * 0.85))):
            out["score"] = max(score, min(20, max(12, int(round(core_avg * 0.85)))))
    else:
        ceiling = int(round(core_avg))
        if truth["test_total"] > 0:
            frac = truth["test_passed"] / float(truth["test_total"])
            ceiling = min(ceiling, 6 + int(round(14 * frac)))
        if not truth["syntax_ok"]:
            ceiling = min(ceiling, max(4, sc["syntax"] + 2))
        if truth["req_total"] > 0 and not truth["reqs_all_met"]:
            ceiling = min(ceiling, max(4, sc["requirement"] + 3))
        out["score"] = min(score, max(0, min(20, ceiling)))

    return out


def merge_must_fix_for_response(
    programmatic: List[str],
    llm_must_fix: List[str],
    agent_results: Optional[Dict[str, Any]],
) -> Tuple[List[str], List[str]]:
    """
    Combine deterministic must_fix with LLM items that still align with ground truth.

    Returns (merged_must_fix, overflow_for_suggestions).
    """
    truth = compute_evaluation_truth(agent_results)
    prog = [str(x).strip() for x in (programmatic or []) if str(x).strip()]
    extra: List[str] = []
    overflow: List[str] = []

    for m in [str(x).strip() for x in (llm_must_fix or []) if str(x).strip()]:
        if truth["tests_all_pass"] and truth["test_total"] > 0 and _mentions_test_failure(m):
            overflow.append(m)
            continue
        if truth["reqs_all_met"] and truth["req_total"] > 0 and _implies_requirement_gap(m):
            overflow.append(m)
            continue
        extra.append(m)

    seen = set()
    merged: List[str] = []
    for item in prog + extra:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        merged.append(item)
    return merged[:10], overflow
