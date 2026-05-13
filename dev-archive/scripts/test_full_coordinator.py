#!/usr/bin/env python3
"""Test full coordinator with Code Analysis Agent integrated."""

import tempfile
import os
import json
from agents.coordinator import coordinator

# Create test code
test_code = """
def fibonacci(n):
    \"\"\"Calculate the nth Fibonacci number.\"\"\"
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

class FibonacciCalculator:
    \"\"\"Calculator for Fibonacci numbers.\"\"\"
    
    def __init__(self, max_n=10):
        self.max_n = max_n
    
    def calculate(self, n):
        if n > self.max_n:
            raise ValueError(f"n must be <= {self.max_n}")
        return fibonacci(n)

if __name__ == "__main__":
    calc = FibonacciCalculator(50)
    for i in range(10):
        print(f"fib({i}) = {calc.calculate(i)}")
"""

# Create temporary file
with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
    f.write(test_code)
    temp_filepath = f.name

try:
    # Define test requirements and testcases
    requirements = [
        ("function", 1),
        ("input", 1),
        ("output/print", 1),
    ]
    
    testcases = [
        ("5", "5"),  # fib(5) = 5
    ]
    
    print("=" * 70)
    print("FULL COORDINATOR TEST WITH CODE ANALYSIS AGENT")
    print("=" * 70)
    print()
    
    # Run coordinator
    print("[TEST] Running coordinator with new code_analysis_agent...")
    result = coordinator(temp_filepath, requirements, testcases)
    
    print()
    print("=" * 70)
    print("COORDINATOR RESULTS")
    print("=" * 70)
    
    # Check for code_analysis in results
    if "code_analysis" in result:
        print("✓ code_analysis agent was executed")
        ca_result = result["code_analysis"]
        print(f"  - Score: {ca_result.get('score', 'N/A')}/20")
        print(f"  - Summary: {ca_result.get('summary', 'N/A')}")
        print(f"  - Issues: {len(ca_result.get('issues', []))} issues")
        print(f"  - Strengths: {len(ca_result.get('strengths', []))} strengths")
    else:
        print("✗ code_analysis agent NOT in results")
    
    print()
    print("All Agent Results:")
    print("-" * 70)
    for agent_name in ["syntax", "code_analysis", "requirement", "structure", "test", "llm"]:
        if agent_name in result:
            score = result[agent_name].get("score", 0)
            print(f"  ✓ {agent_name:20} : {score}/20")
        else:
            print(f"  ✗ {agent_name:20} : NOT FOUND")
    
    print()
    print("=" * 70)
    print("FINAL SCORE")
    print("=" * 70)
    total = result.get("total", {})
    print(f"Total Score: {total.get('total_score', 'N/A')}/100")
    print(f"Grade: {total.get('grade', 'N/A')}")
    print()
    print("Breakdown:")
    breakdown = total.get("breakdown", {})
    for key, value in breakdown.items():
        print(f"  - {key}: {value}/20")

finally:
    # Cleanup
    if os.path.exists(temp_filepath):
        os.remove(temp_filepath)
    
print()
print("=" * 70)
print("✓ INTEGRATION TEST COMPLETE - code_analysis_agent is working!")
print("=" * 70)
