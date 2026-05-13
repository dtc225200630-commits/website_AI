"""
Integration Test - Verify All Fixed Agents Work Correctly

This test creates a sample Python submission and runs it through the
complete evaluation pipeline to verify scoring works correctly.
"""

import os
import sys
import json
from pathlib import Path

# Add agents to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.coordinator import coordinator


def create_test_submission():
    """Create a sample Python file for testing."""
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
    
    test_file = "test_submission.py"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(code)
    
    return test_file, code


def run_integration_test():
    """Run complete evaluation pipeline."""
    
    print("=" * 80)
    print("INTEGRATION TEST - Fixed Agents Evaluation Pipeline")
    print("=" * 80)
    
    # Create test submission
    print("\n1. Creating test submission...")
    filepath, code = create_test_submission()
    print(f"   ✓ Created: {filepath}")
    print(f"   ✓ Code size: {len(code)} bytes")
    
    # Define test requirements (from database)
    requirements = [
        {"requirement_text": "Must use input() function", "weight": 1},
        {"requirement_text": "Must define functions", "weight": 1},
        {"requirement_text": "Must use print statement", "weight": 1},
        {"requirement_text": "Must have docstrings", "weight": 1},
    ]
    
    # Define test cases
    testcases = [
        {"input_data": "5\n3", "expected_output": "8"},  # 5+3 = 8
        {"input_data": "4\n5", "expected_output": "20"},  # 4*5 = 20
    ]
    
    print("\n2. Running coordinator with:")
    print(f"   - Requirements: {len(requirements)}")
    print(f"   - Test cases: {len(testcases)}")
    
    try:
        print("\n3. Executing evaluation pipeline...")
        result = coordinator(filepath, requirements, testcases)
        print("   ✓ Evaluation complete!")
        
    except Exception as e:
        print(f"   ✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Display results
    print("\n" + "=" * 80)
    print("EVALUATION RESULTS")
    print("=" * 80)
    
    # Syntax check
    if "syntax" in result:
        syntax = result["syntax"]
        print(f"\n✓ SYNTAX CHECK")
        print(f"  Score: {syntax.get('score', '?')}/20")
        print(f"  Success: {syntax.get('success', '?')}")
        if syntax.get('error'):
            print(f"  Error: {syntax['error']}")
        for detail in syntax.get('details', []):
            print(f"    • {detail}")
    
    # Code Analysis
    if "code_analysis" in result:
        analysis = result["code_analysis"]
        print(f"\n✓ CODE ANALYSIS")
        print(f"  Score: {analysis.get('score', '?')}/20")
        for detail in analysis.get('details', []):
            print(f"    • {detail}")
    
    # Requirements
    if "requirement" in result:
        req = result["requirement"]
        print(f"\n✓ REQUIREMENTS CHECK")
        print(f"  Score: {req.get('score', '?')}/20")
        print(f"  Fulfilled: {req.get('fulfilled', '?')}/{req.get('total', '?')}")
        print(f"  Summary: {req.get('summary', '')}")
        for detail in req.get('details', []):
            print(f"    • {detail}")
    
    # Structure
    if "structure" in result:
        struct = result["structure"]
        print(f"\n✓ STRUCTURE ANALYSIS")
        print(f"  Score: {struct.get('score', '?')}/20")
        for detail in struct.get('details', []):
            print(f"    • {detail}")
    
    # Test Results
    if "test" in result:
        test = result["test"]
        print(f"\n✓ TEST CASES")
        print(f"  Score: {test.get('score', '?')}/20")
        if test.get('pass_rate') is not None:
            print(f"  Pass Rate: {test['pass_rate']}%")
        print(f"  Summary: {test.get('summary', '')}")
    
    # LLM Review (if available)
    if "llm" in result:
        llm = result["llm"]
        print(f"\n✓ AI CODE REVIEW (LLM)")
        print(f"  Score: {llm.get('score', '?')}/20")
        if llm.get('feedback'):
            print(f"  Feedback: {llm['feedback'][:100]}...")
    
    # Total Score
    if "total" in result:
        total = result["total"]
        print(f"\n" + "=" * 80)
        print(f"FINAL SCORE: {total.get('total_score', '?')}/100")
        print(f"GRADE: {total.get('grade', '?')}")
        print("=" * 80)
        
        print(f"\nScore Breakdown:")
        for key, value in total.get('breakdown', {}).items():
            print(f"  {key}: {value}")
        
        print(f"\nDetails:")
        for detail in total.get('details', []):
            print(f"  • {detail}")
    
    # Save results to file (for inspection)
    results_file = "test_results.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        # Convert non-serializable objects to strings
        result_copy = {}
        for key, value in result.items():
            if isinstance(value, dict):
                result_copy[key] = value
            else:
                result_copy[key] = str(value)
        json.dump(result_copy, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Results saved to: {results_file}")
    
    # Cleanup
    os.remove(filepath)
    print(f"✓ Cleaned up test file: {filepath}")
    
    return True


if __name__ == "__main__":
    success = run_integration_test()
    sys.exit(0 if success else 1)
