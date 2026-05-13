"""
Coordinator Module - Routes between Simple and LangChain Orchestrators

This module provides the main entry point for the multi-agent evaluation system.
It attempts to use the LangChain orchestrator (with proper tool registration)
and falls back to the simple sequential orchestrator if LangChain is unavailable.
"""

# Import FIXED versions of agents (production-ready)
from agents.rubric_hints import build_rubric_hints
from agents.syntax_agent_fixed import syntax_agent
from agents.requirement_agent_fixed import requirement_agent
from agents.structure_agent_fixed import structure_agent
from agents.code_analysis_agent import code_analysis_agent
from agents.test_agent_fixed import test_agent
from agents.aggregation_agent_fixed import aggregation_agent
from agents.llm_agent import llm_agent
from agents.response_generator_agent import response_generator_agent

# Try to import LangChain orchestrator
langchain_available = False
try:
    from agents.langchain_orchestrator import orchestrate_agents as langchain_orchestrate
    langchain_available = True
    print("[Coordinator] LangChain orchestrator available")
except ImportError as e:
    print(f"[Coordinator] LangChain not available, using simple orchestrator: {e}")


def coordinator(filepath, requirements, testcases, assignment_context=None):
    """
    Main coordinator function - Entry point for the evaluation system.
    
    This function orchestrates all agents to evaluate Python code. It uses LangChain
    for proper tool registration and chain execution if available, otherwise falls
    back to simple sequential execution.
    
    LangChain Flow (when available) — thuc te chay TUAN TU trong langchain_orchestrator:
    ├── syntax_agent
    ├── code_analysis_agent
    ├── requirement_agent, structure_agent, test_agent
    ├── llm_agent (nhan day du ket qua cac agent tren + yeu cau)
    └── aggregation_agent
    
    Fallback Flow (simple sequential):
    └── Same as above but without LangChain tool registration
    
    Args:
        filepath (str): Path to the Python file to evaluate
        requirements (list): List of (requirement_text, weight) tuples
        testcases (list): List of (input, expected_output, weight) tuples
        assignment_context (dict|None): title, description — suy rubric ưu tiên tối giản vs bắt hàm/class
    
    Returns:
        dict: Evaluation results containing:
            - syntax: Syntax validation result
            - requirement: Requirement fulfillment check
            - structure: Code structure analysis
            - test: Test case results
            - llm: AI-based code review
            - total: Aggregated final score and grade
    
    Example:
        >>> result = coordinator(
        ...     "code.py",
        ...     [("input()", 5), ("phép cộng", 3)],
        ...     [("5", "5", 1), ("10", "10", 1)]
        ... )
        >>> print(result["total"]["total_score"])
        85
    """
    
    # Try LangChain orchestrator first
    if langchain_available:
        try:
            print("[Coordinator] Using LangChain orchestrator...")
            result = langchain_orchestrate(
                filepath, requirements, testcases, assignment_context=assignment_context
            )
            if isinstance(result, dict) and not result.get("error"):
                result["response"] = response_generator_agent(result)
            return result
        except Exception as e:
            print(f"[Coordinator] LangChain execution failed: {e}")
            print("[Coordinator] Falling back to simple orchestrator...")
    
    # Fallback: Simple sequential orchestration
    print("[Coordinator] Using simple orchestrator...")
    result = simple_coordinator(
        filepath, requirements, testcases, assignment_context=assignment_context
    )
    if isinstance(result, dict) and not result.get("error"):
        result["response"] = response_generator_agent(result)
    return result


def simple_coordinator(filepath, requirements, testcases, assignment_context=None):
    """
    Simple sequential orchestrator (fallback when LangChain is unavailable).
    
    Each agent is called in sequence with its dependencies properly managed.
    Output from one agent is passed to the next as required.
    
    Args:
        filepath: Path to Python file to evaluate
        requirements: List of requirement tuples
        testcases: List of test case tuples
        assignment_context: dict tùy chọn (title, description) để suy rubric từng bài
    
    Returns:
        dict: Evaluation results from all agents
    """    
    # Convert tuple-format requirements to dict format for agents
    req_dicts = []
    for req in requirements:
        if isinstance(req, tuple):
            req_dicts.append({"requirement_text": req[0], "weight": req[1]})
        elif isinstance(req, dict):
            req_dicts.append(req)
    requirements = req_dicts
    
    # Convert tuple-format testcases to dict format for agents
    test_dicts = []
    for test in testcases:
        if isinstance(test, tuple):
            test_dicts.append({
                "input_data": test[0],
                "expected_output": test[1],
                "score_weight": test[2] if len(test) > 2 else 10
            })
        elif isinstance(test, dict):
            test_dicts.append(test)
    testcases = test_dicts

    ctx = assignment_context or {}
    rubric = build_rubric_hints(
        ctx.get("title") or "",
        ctx.get("description") or "",
        requirements,
    )

    # Load code from file
    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    # Step 1: Syntax validation
    print("[Simple] Running syntax_agent...")
    syntax = syntax_agent(filepath)
    
    # Step 2: Code Analysis (after syntax check - requires parseable code)
    print("[Simple] Running code_analysis_agent...")
    code_analysis = code_analysis_agent(code, rubric)
    
    # Step 3: Requirement check
    print("[Simple] Running requirement_agent...")
    requirement = requirement_agent(code, requirements)
    
    # Step 4: Structure analysis
    print("[Simple] Running structure_agent...")
    structure = structure_agent(code, rubric)
    
    # Step 5: Test case validation
    print("[Simple] Running test_agent...")
    test = test_agent(filepath, testcases)
    
    # Step 6: LLM-based review (only if code runs successfully)
    if syntax["success"]:
        print("[Simple] Running llm_agent...")
        # Pass full context to LLM: requirements, test results, requirement results, etc.
        llm = llm_agent(code, requirements, {
            "syntax": syntax,
            "requirement": requirement,
            "structure": structure,
            "test": test,
            "code_analysis": code_analysis
        })
    else:
        llm = {
            "score": 0,
            "feedback": "LLM review skipped - code has syntax errors",
            "details": ["Code cannot run - skipping AI review"]
        }

    # Step 7: Aggregate all results
    print("[Simple] Running aggregation_agent...")
    result = {
        "syntax": syntax,
        "code_analysis": code_analysis,
        "requirement": requirement,
        "structure": structure,
        "test": test,
        "llm": llm
    }

    # Add aggregated total score
    total = aggregation_agent(result)
    result["total"] = total

    print("[Simple] Evaluation complete!")
    return result


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = ["coordinator", "simple_coordinator"]
