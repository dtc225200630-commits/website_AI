#!/usr/bin/env python3
"""Test Code Analysis Agent functionality."""

from agents.code_analysis_agent import code_analysis_agent
import json

# Test 1: Good code
print("=" * 60)
print("TEST 1: Good Python code with functions and classes")
print("=" * 60)

good_code = """
def calculate_sum(numbers):
    \"\"\"Calculate sum of a list of numbers.\"\"\"
    total = 0
    for num in numbers:
        total += num
    return total

class Calculator:
    \"\"\"Simple calculator class.\"\"\"
    
    def __init__(self, initial=0):
        self.value = initial
    
    def add(self, num):
        self.value += num
        return self.value

if __name__ == "__main__":
    calc = Calculator(10)
    result = calc.add(5)
    print(result)
"""

result1 = code_analysis_agent(good_code)
print(f"Score: {result1['score']}/20")
print(f"Summary: {result1['summary']}")
print(f"Strengths: {result1['strengths'][:2]}")
print()

# Test 2: Simple code
print("=" * 60)
print("TEST 2: Simple code without functions/classes")
print("=" * 60)

simple_code = """
x = int(input("Enter number: "))
y = int(input("Enter another number: "))
print(x + y)
"""

result2 = code_analysis_agent(simple_code)
print(f"Score: {result2['score']}/20")
print(f"Summary: {result2['summary']}")
print(f"Issues: {result2['issues'][:2]}")
print()

# Test 3: Code with bad naming
print("=" * 60)
print("TEST 3: Code with poor naming conventions")
print("=" * 60)

bad_naming_code = """
def CalcSum(lst):
    total = 0
    for i in lst:
        total += i
    return total

X = [1, 2, 3, 4, 5]
result = CalcSum(X)
print(result)
"""

result3 = code_analysis_agent(bad_naming_code)
print(f"Score: {result3['score']}/20")
print(f"Summary: {result3['summary']}")
print(f"Issues: {result3['issues'][:2]}")
print()

# Test 4: Integration test - verify JSON output structure
print("=" * 60)
print("TEST 4: Output structure validation")
print("=" * 60)

required_keys = {"score", "issues", "strengths", "summary", "details", "metrics"}
actual_keys = set(result1.keys())

if required_keys.issubset(actual_keys):
    print("✓ All required keys present in output")
    print(f"  - Keys: {sorted(actual_keys)}")
else:
    print("✗ Missing keys:", required_keys - actual_keys)

print()
print("=" * 60)
print("CODE ANALYSIS AGENT TEST COMPLETE")
print("=" * 60)
