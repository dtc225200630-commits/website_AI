"""
LangChain-based Multi-Agent Orchestrator

This module implements a proper LangChain tool-based orchestration system
where each agent is registered as a tool and chained together using
LangChain's Runnable interfaces.

Tool Registration Flow:
  syntax_agent (tool 1)
       ↓
  requirement_agent (tool 2) ← uses code from tool 1
       ↓
  structure_agent (tool 3) ← uses code from tool 1
       ↓
  test_agent (tool 4) ← uses filepath from input
       ↓
  llm_agent (tool 5) ← uses code from tool 1
       ↓
  aggregation_agent (tool 6) ← aggregates all results

All tools are coordinated by LangChain chain execution.
"""

from typing import Any, Dict, Optional
from langchain_core.tools import tool
from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableLambda
from agents.syntax_agent_fixed import syntax_agent
from agents.requirement_agent_fixed import requirement_agent
from agents.structure_agent_fixed import structure_agent
from agents.code_analysis_agent import code_analysis_agent
from agents.test_agent_fixed import test_agent
from agents.llm_agent import llm_agent
from agents.rubric_hints import build_rubric_hints
from agents.aggregation_agent_fixed import aggregation_agent


# ============================================pip install uvicorn================================
# TOOL DEFINITIONS - Registered with LangChain
# ============================================================================

@tool
def syntax_check_tool(filepath: str) -> Dict[str, Any]:
    """
    Tool: Check Python file syntax validity.
    
    Args:
        filepath: Path to Python file
        
    Returns:
        Syntax validation result with score (0-20)
    """
    result = syntax_agent(filepath)
    return result


@tool
def requirement_check_tool(code: str, requirements: list) -> Dict[str, Any]:
    """
    Tool: Validate code against requirements.
    
    Args:
        code: Source code string
        requirements: List of (requirement_text, weight) tuples
        
    Returns:
        Requirement check result with score (0-20)
    """
    result = requirement_agent(code, requirements)
    return result


@tool
def structure_analysis_tool(code: str, rubric: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Tool: Analyze code structure and quality.
    
    Args:
        code: Source code string
        rubric: build_rubric_hints dict (optional)
        
    Returns:
        Structure analysis result with score (0-20)
    """
    result = structure_agent(code, rubric)
    return result


@tool
def code_analysis_tool(code: str, rubric: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Tool: Static source code analysis using AST.
    
    Analyzes code structure, naming conventions, modularity, and best practices
    without executing the code.
    
    Args:
        code: Source code string
        rubric: build_rubric_hints dict (optional)
        
    Returns:
        Code analysis result with score (0-20), issues, and strengths
    """
    result = code_analysis_agent(code, rubric)
    return result


@tool
def test_validation_tool(filepath: str, testcases: list) -> Dict[str, Any]:
    """
    Tool: Run test cases against code.
    
    Args:
        filepath: Path to Python file
        testcases: List of (input, expected_output, weight) tuples
        
    Returns:
        Test validation result with score (0-20)
    """
    result = test_agent(filepath, testcases)
    return result


@tool
def llm_review_tool(code: str, requirements: list = None, agent_results: dict = None) -> Dict[str, Any]:
    """
    Tool: AI-based code review using LLM with full context.
    
    Args:
        code: Source code string
        requirements: Assignment requirements list
        agent_results: Results from other agents for context
        
    Returns:
        LLM review result with score (0-20) and detailed feedback
    """
    result = llm_agent(code, requirements, agent_results)
    return result


# ============================================================================
# CHAIN BUILDING FUNCTIONS
# ============================================================================

def build_agentchain() -> Dict[str, Any]:
    """
    Build the complete agent chain using LangChain Runnable interfaces.
    
    This creates a chain where:
    1. Syntax agent runs first (required)
    2. Code analysis agent runs (requires valid code structure)
    3. Other agents run independently with their respective tools
    4. Outputs are collected and passed to aggregation_agent
    5. Final result includes all intermediate and aggregated results
    
    Returns:
        dict: Functions for running the full chain
    """
    
    # Define individual tool runnables
    syntax_runnable = RunnableLambda(
        lambda inputs: syntax_check_tool.invoke({"filepath": inputs["filepath"]})
    )
    
    code_analysis_runnable = RunnableLambda(
        lambda inputs: code_analysis_tool.invoke(
            {"code": inputs["code"], "rubric": inputs.get("rubric")}
        )
    )
    
    requirement_runnable = RunnableLambda(
        lambda inputs: requirement_check_tool.invoke({
            "code": inputs["code"],
            "requirements": inputs["requirements"]
        })
    )
    
    structure_runnable = RunnableLambda(
        lambda inputs: structure_analysis_tool.invoke(
            {"code": inputs["code"], "rubric": inputs.get("rubric")}
        )
    )
    
    test_runnable = RunnableLambda(
        lambda inputs: test_validation_tool.invoke({
            "filepath": inputs["filepath"],
            "testcases": inputs["testcases"]
        })
    )
    
    llm_runnable = RunnableLambda(
        lambda inputs: llm_review_tool.invoke({
            "code": inputs["code"],
            "requirements": inputs.get("requirements"),
            "agent_results": {
                "syntax": inputs.get("syntax", {}),
                "requirement": inputs.get("requirement", {}),
                "structure": inputs.get("structure", {}),
                "test": inputs.get("test", {}),
                "code_analysis": inputs.get("code_analysis", {})
            }
        })
        if inputs.get("syntax", {}).get("success") else 
        {
            "score": 0,
            "feedback": "LLM review skipped - code has syntax errors",
            "details": ["Code cannot run - skipping AI review"]
        }
    )
    
    return {
        "syntax": syntax_runnable,
        "code_analysis": code_analysis_runnable,
        "requirement": requirement_runnable,
        "structure": structure_runnable,
        "test": test_runnable,
        "llm": llm_runnable,
    }


# ============================================================================
# MAIN ORCHESTRATOR FUNCTION
# ============================================================================

def orchestrate_agents(
    filepath: str,
    requirements: list,
    testcases: list,
    assignment_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Main orchestrator function using LangChain chains.
    
    Flow:
    1. Load code from file
    2. Run all agent tools in sequence/parallel as appropriate
    3. Pass outputs between agents correctly
    4. Aggregate all results
    5. Return comprehensive evaluation
    
    Args:
        filepath: Path to Python file to evaluate
        requirements: List of (requirement_text, weight) tuples or dicts
        testcases: List of (input, expected_output, weight) tuples or dicts
    
    Returns:
        dict: Complete evaluation with all agent results and total score
    """
    
    # Load code from file
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()
    except Exception as e:
        return {
            "error": f"Failed to read file: {str(e)}",
            "filepath": filepath,
            "total": {"total_score": 0, "grade": "F (Yếu)"}
        }
    
    # Convert tuple-format requirements to dict format
    req_dicts = []
    for req in requirements:
        if isinstance(req, tuple):
            req_dicts.append({"requirement_text": req[0], "weight": req[1]})
        elif isinstance(req, dict):
            req_dicts.append(req)
    requirements = req_dicts
    
    # Convert tuple-format testcases to dict format
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

    # Prepare input for all agents
    agent_inputs = {
        "filepath": filepath,
        "code": code,
        "requirements": requirements,
        "testcases": testcases,
        "rubric": rubric,
    }
    
    # Build the agent chain
    chain_fns = build_agentchain()
    
    # Execute agents in proper order with data passing
    # Each agent depends on previous results
    results = {}
    
    try:
        # Step 1: Syntax check (no dependencies)
        print("[LangChain] Executing syntax_agent...")
        results["syntax"] = chain_fns["syntax"].invoke(agent_inputs)
        
        # Step 2: Code analysis (requires parseable code)
        print("[LangChain] Executing code_analysis_agent...")
        results["code_analysis"] = chain_fns["code_analysis"].invoke(agent_inputs)
        
        # Step 3: Run independent agents in parallel (they all use the code)
        print("[LangChain] Executing requirement_agent...")
        results["requirement"] = chain_fns["requirement"].invoke(agent_inputs)
        
        print("[LangChain] Executing structure_agent...")
        results["structure"] = chain_fns["structure"].invoke(agent_inputs)
        
        print("[LangChain] Executing test_agent...")
        results["test"] = chain_fns["test"].invoke(agent_inputs)
        
        # Step 4: LLM agent (depends on syntax success and has access to all other results)
        print("[LangChain] Executing llm_agent...")
        agent_inputs_with_all_results = {
            **agent_inputs,
            "syntax": results["syntax"],
            "requirement": results["requirement"],
            "structure": results["structure"],
            "test": results["test"],
            "code_analysis": results["code_analysis"]
        }
        results["llm"] = chain_fns["llm"].invoke(agent_inputs_with_all_results)
        
    except Exception as e:
        return {
            "error": f"Agent execution failed: {str(e)}",
            "filepath": filepath,
            "total": {"total_score": 0, "grade": "F (Yếu)"}
        }
    
    # Step 4: Aggregation (depends on all previous results)
    print("[LangChain] Executing aggregation_agent...")
    total = aggregation_agent(results)
    results["total"] = total
    
    print("[LangChain] Chain execution completed successfully!")
    
    return results


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

__all__ = [
    "orchestrate_agents",
    "syntax_check_tool",
    "requirement_check_tool",
    "structure_analysis_tool",
    "code_analysis_tool",
    "test_validation_tool",
    "llm_review_tool",
]
