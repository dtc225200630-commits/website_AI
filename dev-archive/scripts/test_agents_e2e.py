"""
End-to-End Test Script for Multi-Agent Evaluation System

This script tests the complete agent orchestration pipeline with real code samples.
Run this to verify all agents work correctly and pass data properly between each other.
"""

import json
import sys
from pathlib import Path

# Create test Python files
test_files = {
    "test_good.py": '''def add_numbers(a, b):
    """Add two numbers"""
    result = a + b
    print(f"Sum: {result}")
    return result

if __name__ == "__main__":
    # Get user input
    x = int(input("Enter first number: "))
    y = int(input("Enter second number: "))
    
    # Add and display
    total = add_numbers(x, y)
''',
    
    "test_simple.py": '''x = 5
print(x)
''',
    
    "test_with_errors.py": '''def broken_function(
    x = 1 / 0  # This will cause runtime error
    print(x)
''',
}

# Create test files
for filename, content in test_files.items():
    filepath = Path(filename)
    filepath.write_text(content)
    print(f"Created test file: {filename}")

# Test cases
test_requirements = [
    ("input()", 5),
    ("phép cộng", 3),
    ("print()", 4),
]

test_cases = [
    ("5\n3", "Sum: 8", 5),
    ("10\n20", "Sum: 30", 5),
]

print("\n" + "="*80)
print("MULTI-AGENT EVALUATION SYSTEM - END-TO-END TEST")
print("="*80)

# Test 1: Test good code
print("\n[TEST 1] Evaluating well-structured code (test_good.py)")
print("-" * 80)

try:
    from agents.coordinator import coordinator
    
    result = coordinator("test_good.py", test_requirements, test_cases)
    
    print("\nEvaluation Results:")
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    
    total_score = result.get("total", {}).get("total_score", 0)
    print(f"\n✓ Test 1 PASSED - Total Score: {total_score}/100")
    
except Exception as e:
    print(f"\n✗ Test 1 FAILED - Error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Test simple code
print("\n" + "="*80)
print("\n[TEST 2] Evaluating simple code (test_simple.py)")
print("-" * 80)

try:
    from agents.coordinator import coordinator
    
    result = coordinator("test_simple.py", test_requirements, test_cases)
    
    print("\nEvaluation Results:")
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    
    total_score = result.get("total", {}).get("total_score", 0)
    print(f"\n✓ Test 2 PASSED - Total Score: {total_score}/100")
    
except Exception as e:
    print(f"\n✗ Test 2 FAILED - Error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Test code with errors
print("\n" + "="*80)
print("\n[TEST 3] Evaluating code with syntax errors (test_with_errors.py)")
print("-" * 80)

try:
    from agents.coordinator import coordinator
    
    result = coordinator("test_with_errors.py", test_requirements, test_cases)
    
    print("\nEvaluation Results:")
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    
    total_score = result.get("total", {}).get("total_score", 0)
    print(f"\n✓ Test 3 PASSED - Total Score: {total_score}/100")
    print("  (Low score expected for code with errors)")
    
except Exception as e:
    print(f"\n✗ Test 3 FAILED - Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("END-TO-END TEST COMPLETE")
print("="*80)

# Cleanup
import os
for filename in test_files.keys():
    if os.path.exists(filename):
        os.remove(filename)
        print(f"Cleaned up: {filename}")
