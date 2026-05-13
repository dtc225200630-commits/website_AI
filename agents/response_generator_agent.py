"""
Response Generator Agent

Converts structured multi-agent scoring output into:
- structured_response: stable JSON for API consumers
- natural_text: chatbot-style natural language feedback
"""

try:
    from llm_alignment import merge_must_fix_for_response
except ImportError:
    from .llm_alignment import merge_must_fix_for_response


def _to_num(value, default=0):
    try:
        if value is None:
            return default
        return int(float(value))
    except Exception:
        return default


def response_generator_agent(result: dict) -> dict:
    syntax = result.get("syntax", {}) if isinstance(result, dict) else {}
    requirement = result.get("requirement", {}) if isinstance(result, dict) else {}
    structure = result.get("structure", {}) if isinstance(result, dict) else {}
    code_analysis = result.get("code_analysis", {}) if isinstance(result, dict) else {}
    test = result.get("test", {}) if isinstance(result, dict) else {}
    llm = result.get("llm", {}) if isinstance(result, dict) else {}
    total = result.get("total", {}) if isinstance(result, dict) else {}
    requirement_details = requirement.get("details", []) if isinstance(requirement.get("details", []), list) else []
    test_details = test.get("details", []) if isinstance(test.get("details", []), list) else []
    analysis_issues = code_analysis.get("issues", []) if isinstance(code_analysis.get("issues", []), list) else []

    syntax_score = _to_num(syntax.get("score"))
    requirement_score = _to_num(requirement.get("score"))
    structure_score = _to_num(structure.get("score"))
    analysis_score = _to_num(code_analysis.get("score"))
    test_score = _to_num(test.get("score"))
    llm_score = _to_num(llm.get("score"))
    total_score = _to_num(total.get("total_score"))

    strengths = []
    if syntax_score >= 18:
        strengths.append("Cu phap chay on dinh")
    if test_score >= 18:
        strengths.append("Vuot test tot")
    if requirement_score >= 15:
        strengths.append("Bam sat yeu cau de bai")
    if structure_score >= 15:
        strengths.append("Cau truc code kha ro rang")

    must_fix_prog = []
    if syntax_score < 20:
        must_fix_prog.append("Sua loi cu phap/runtime truoc khi toi uu")
    if test_score < 20:
        must_fix_prog.append("Can chinh logic de pass tat ca test")

    llm_must_fix = llm.get("must_fix", []) if isinstance(llm.get("must_fix", []), list) else []
    must_fix, must_fix_overflow = merge_must_fix_for_response(must_fix_prog, llm_must_fix, result)

    improvements = []
    if analysis_score < 12:
        improvements.append("Tang chat luong code: dat ten bien ro nghia, bo sung docstring, giam code lap")
    if structure_score < 12:
        improvements.append("To chuc lai ham/lop de de bao tri hon")
    if requirement_score < 20:
        improvements.append("Doi chieu tung requirement va bo sung cac truong hop con thieu")

    suggestion_candidates = []
    suggestion_candidates.extend(llm.get("suggestions", []) if isinstance(llm.get("suggestions", []), list) else [])
    suggestion_candidates.extend([str(x) for x in must_fix_overflow if str(x).strip()])
    suggestion_candidates.extend(improvements)
    suggestions = [str(x) for x in suggestion_candidates if str(x).strip()][:5]

    requirement_checks = []
    requirements_met = requirement.get("requirements_met", []) if isinstance(requirement.get("requirements_met", []), list) else []
    requirements_missing = requirement.get("requirements_missing", []) if isinstance(requirement.get("requirements_missing", []), list) else []

    for item in requirements_met:
        requirement_checks.append({"requirement": str(item), "status": "MET"})
    for item in requirements_missing:
        requirement_checks.append({"requirement": str(item), "status": "NOT_MET"})

    if not requirement_checks:
        for item in requirement_details:
            text = str(item)
            if ": MET" in text:
                requirement_checks.append({"requirement": text.split("'")[-2] if "'" in text else text, "status": "MET"})
            elif ": NOT MET" in text:
                requirement_checks.append({"requirement": text.split("'")[-2] if "'" in text else text, "status": "NOT_MET"})

    agent_activity = [
        {"agent": "SyntaxAgent", "status": "PASS" if syntax.get("success", False) else "FAIL", "score": syntax_score},
        {"agent": "RequirementAgent", "status": "PASS" if requirement_score >= 15 else "PARTIAL", "score": requirement_score},
        {"agent": "StructureAgent", "status": "PASS" if structure_score >= 15 else "PARTIAL", "score": structure_score},
        {"agent": "CodeAnalysisAgent", "status": "PASS" if analysis_score >= 15 else "PARTIAL", "score": analysis_score},
        {"agent": "TestAgent", "status": "PASS" if test_score >= 20 else "PARTIAL", "score": test_score},
        {"agent": "LLMAgent", "status": "SUPPORT", "score": llm_score},
    ]

    detected_errors = []
    if not syntax.get("success", False):
        detected_errors.append(str(syntax.get("error", "Loi cu phap/runtime")))
    for issue in analysis_issues[:5]:
        detected_errors.append(str(issue))
    for item in test_details:
        item_text = str(item)
        if "FAIL" in item_text or "ERROR" in item_text or "TIMEOUT" in item_text:
            detected_errors.append(item_text)
    detected_errors = detected_errors[:8]

    structured_response = {
        "style": "teacher_chatbot",
        "formula": {
            "scored_agents": ["syntax", "requirement", "structure", "code_analysis", "test"],
            "not_scored": ["llm"],
            "max_per_scored_agent": 20,
            "max_total": 100,
        },
        "scores": {
            "syntax": syntax_score,
            "requirement": requirement_score,
            "structure": structure_score,
            "code_analysis": analysis_score,
            "test": test_score,
            "llm_support": llm_score,
            "total": total_score,
            "grade": total.get("grade", ""),
        },
        "agent_activity": agent_activity,
        "requirement_checks": requirement_checks,
        "detected_errors": detected_errors,
        "strengths": strengths,
        "must_fix": must_fix,
        "improvements": improvements,
        "suggestions": suggestions,
        "auto_assessment": {
            "summary": f"He thong da phan tich code, doi chieu yeu cau va test, ket qua hien tai {total_score}/100.",
            "next_step": must_fix[0] if must_fix else "Tiep tuc toi uu chat luong code de dat diem toi da.",
        },
    }

    short_strength = strengths[0] if strengths else "Ban da hoan thanh duoc mot phan yeu cau"
    primary_fix = must_fix[0] if must_fix else "Tiep tuc toi uu de dat diem toi da"
    natural_text = (
        f"He thong da chay day du cac agents va doi chieu voi yeu cau trong CSDL. "
        f"Tong diem hien tai la {total_score}/100. {short_strength}. "
        f"Loi/van de can uu tien: {primary_fix}. "
        f"Breakdown: Syntax {syntax_score}/20, Requirement {requirement_score}/20, "
        f"Structure {structure_score}/20, Analysis {analysis_score}/20, Test {test_score}/20."
    )

    return {
        "structured_response": structured_response,
        "natural_text": natural_text,
    }
