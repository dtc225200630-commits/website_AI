"""
Direct Agent Test - Test agents without LangChain

This bypasses LangChain to directly test the fixed agents.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.requirement_agent_fixed import requirement_agent, check_requirement


def test_requirement_agent_direct():
    """Test requirement matching logic directly."""
    
    code = '''"""
Simple calculator program
"""

def add(a, b):
    """Add two numbers."""
    return a + b

def multiply(a, b):
    """Multiply two numbers."""
    return a * b

# Get input from user
try:
    x = float(input())
    y = float(input())
    result_add = add(x, y)
    result_mult = multiply(x, y)
    print(f"Addition: {result_add}")
    print(f"Multiplication: {result_mult}")
except ValueError:
    print("Error: Invalid input")
'''
    
    print("=" * 80)
    print("DIRECT REQUIREMENT AGENT TEST")
    print("=" * 80)
    
    print("\nCode to evaluate:")
    print("-" * 40)
    print(code)
    print("-" * 40)
    
    # Test individual requirement checks
    requirements = [
        "Must use input() function",
        "Must define functions",
        "Must use print statement",
        "Must have docstrings",
    ]
    
    print("\nIndividual requirement checks:")
    code_lower = code.lower()
    lines = code.split('\n')
    
    for req in requirements:
        is_met = check_requirement(code, code_lower, lines, req)
        print(f"  '{req}': {'✓ MET' if is_met else '✗ NOT MET'}")
    
    # Test full requirement agent
    print("\nFull requirement_agent result:")
    req_dicts = [{"requirement_text": r, "weight": 1} for r in requirements]
    result = requirement_agent(code, requirements=req_dicts)
    
    print(f"  Score: {result.get('score')}/20")
    print(f"  Fulfilled: {result.get('fulfilled')}/{result.get('total')}")
    print(f"  Summary: {result.get('summary')}")
    print("\n  Details:")
    for detail in result.get('details', []):
        print(f"    {detail}")
    
    print(f"\n  Requirements Met: {result.get('requirements_met')}")
    print(f"  Requirements Missing: {result.get('requirements_missing')}")


if __name__ == "__main__":
    test_requirement_agent_direct()
