"""
Aggregation Agent - Combine All Scores into Final Grade

Scoring formula (REVISED):
- Each scored core agent: 0-20 points
- Final score scale: 0-100

Core scored agents:
- syntax (build/run readiness)
- requirement (functional requirements)
- structure (code structure)
- code_analysis (code quality)
- test (test case validation)

LLM is support-only (feedback assistant), not a direct scored component.
"""


def aggregation_agent(result):
    """
    Aggregation agent: Combines scores from all agents into final evaluation.
    
    REVISED FORMULA:
    - Extract scores from agents (each 0-20)
    - Average CORE 5 scored agents: syntax, requirement, structure, code_analysis, test
    - LLM score is not included in total (support feedback only)
    - Final Score = (Core_5_Sum / 5) * 100 = 0-100 scale
    
    This ensures student can get 100 only by doing well in ALL core areas.
    
    Returns:
        dict with total_score (0-100), grade, breakdown, details
    """
    
    # Extract scores from each agent
    syntax_score = result.get("syntax", {}).get("score", 0)
    code_analysis_score = result.get("code_analysis", {}).get("score", 0)
    requirement_score = result.get("requirement", {}).get("score", 0)
    structure_score = result.get("structure", {}).get("score", 0)
    test_score = result.get("test", {}).get("score", 0)
    llm_score = result.get("llm", {}).get("score", 0)
    
    # Average of core scored agents, multiply by 5 to get 0-100 scale.
    core_agents_sum = (
        syntax_score
        + requirement_score
        + structure_score
        + code_analysis_score
        + test_score
    )
    core_agents_count = 5
    
    # Average of core 5 on 0-20 scale
    core_average = core_agents_sum / core_agents_count if core_agents_count > 0 else 0
    
    # Convert to 0-100 scale
    total_score = int(core_average * 5)  # multiply by 5 to get 0-100
    
    # Ensure within bounds
    total_score = min(100, max(0, total_score))

    # Hard gates to prevent unrealistic high scores on broken submissions.
    syntax_success = bool(result.get("syntax", {}).get("success", False))
    test_results = result.get("test", {}).get("test_results", []) or []
    has_runtime_or_exec_errors = any(
        (tr.get("status") in {"ERROR", "TIMEOUT", "COMPILE_ERROR"}) for tr in test_results
    )

    # If syntax/runtime is broken, cap score aggressively.
    if (not syntax_success) or syntax_score <= 0:
        total_score = min(total_score, 40)

    # Any execution/test errors means code is not fully reliable.
    if has_runtime_or_exec_errors:
        total_score = min(total_score, 60)

    # If core requirements are not met, cap the score to avoid high scores on wrong answers.
    if requirement_score <= 0:
        total_score = min(total_score, 40)
    elif requirement_score < 10:
        total_score = min(total_score, 60)

    # A perfect 100 is allowed only when both syntax and tests are perfect.
    if syntax_score < 20 or test_score < 20:
        total_score = min(total_score, 99)
    
    # Determine grade based on total score
    if total_score >= 90:
        grade = "A (Xuat sac)"
    elif total_score >= 80:
        grade = "B (Tot)"
    elif total_score >= 70:
        grade = "C (Kha)"
    elif total_score >= 60:
        grade = "D (Trung binh)"
    else:
        grade = "F (Yeu)"
    
    # Build breakdown
    breakdown = {
        "syntax_score": syntax_score,
        "code_analysis_score": code_analysis_score,
        "requirement_score": requirement_score,
        "structure_score": structure_score,
        "test_score": test_score,
        "llm_score": llm_score,
        "core_agents_sum": core_agents_sum,
        "core_agents_average": round(core_average, 2),
        "final_score": total_score,
        "syntax_success": syntax_success,
        "has_runtime_or_exec_errors": has_runtime_or_exec_errors,
    }
    
    # Detailed breakdown
    details = [
        f"Syntax Check: {syntax_score}/20",
        f"Code Analysis: {code_analysis_score}/20",
        f"Requirements: {requirement_score}/20",
        f"Structure Quality: {structure_score}/20",
        f"Test Cases: {test_score}/20",
        f"AI Review (LLM Support): {llm_score}/20 (not included in total)",
        f"",
        f"Core Agents Sum: {core_agents_sum}/100",
        f"Core Agents Average: {core_average:.1f}/20",
        f"Final Score: {total_score}/100",
        f"Grade: {grade}"
    ]

    if not syntax_success:
        details.append("Gate applied: Syntax failed, score capped at 40")
    if has_runtime_or_exec_errors:
        details.append("Gate applied: Runtime/test execution errors detected, score capped at 60")
    if requirement_score <= 0:
        details.append("Gate applied: Requirements not met, score capped at 40")
    elif requirement_score < 10:
        details.append("Gate applied: Low requirement score, capped at 60")
    if syntax_score < 20 or test_score < 20:
        details.append("Gate applied: 100 requires Syntax=20 and Test=20")
    
    return {
        "total_score": total_score,
        "grade": grade,
        "breakdown": breakdown,
        "details": details
    }
