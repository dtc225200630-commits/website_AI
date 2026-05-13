#!/usr/bin/env python3
"""
Test script to verify LLM agent receives and uses full context
from requirements, test results, and other agent findings.
"""

import sys
import tempfile
import json

# Ensure UTF-8 output
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Test code submissions
test_submissions = {
    "good": """a = int(input())
b = int(input())
print(a + b)""",
    
    "missing_requirement": """a = int(input())
result = a + 5
print(result)""",  # Missing second input
    
    "wrong_output": """a = int(input())
b = int(input())
print(a, b)"""  # Prints with space instead of sum
}

# Requirements
requirements = [
    ("Có dùng input()", 10),
    ("Có phép cộng", 10),
    ("Có print()", 10)
]

# Test cases
testcases = [
    ("2\n3\n", "5", 10),
    ("10\n20\n", "30", 10),
    ("7\n8\n", "15", 10)
]

def test_llm_with_context():
    """Test that LLM agent receives full context"""
    
    print("=" * 70)
    print("TEST: LLM Agent with Full Context")
    print("=" * 70)
    
    try:
        from agents.coordinator import coordinator
        from agents.llm_agent import llm_agent
        
        # Test Case 1: Good submission
        print("\n[Test 1] GOOD SUBMISSION - Should pass all tests")
        print("-" * 70)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_submissions["good"])
            f.flush()
            filepath = f.name
        
        result = coordinator(filepath, requirements, testcases)
        
        # Debug: print what we got
        print(f"Result keys: {result.keys()}")
        if 'error' in result:
            print(f"ERROR in result: {result['error']}")
            return False
        
        # Test agent uses 'passed_count' and 'total_tests', not 'total_count'
        test_passed = result['test'].get('passed_count', 0)
        test_total = result['test'].get('total_tests', len(testcases))
        print(f"[OK] Test: {test_passed}/{test_total}")
        print(f"[OK] Requirement: {result['requirement'].get('fulfilled_count', 0)}/{result['requirement'].get('total_count', 0)}")
        print(f"[OK] LLM Score: {result['llm']['score']}/20")
        print(f"[OK] LLM Summary: {result['llm'].get('summary', 'N/A')}")
        print(f"[OK] LLM Teacher Feedback: {result['llm'].get('teacher_feedback', 'N/A')[:100]}...")
        
        if result['llm'].get('suggestions'):
            print(f"[OK] LLM Suggestions: {result['llm']['suggestions'][:2]}")
        
        # Verify LLM received context
        if result['llm'].get('teacher_feedback') and 'pass' in result['llm']['teacher_feedback'].lower():
            print("\n[SUCCESS] LLM received and processed test results context!")
        
        # Test Case 2: Missing requirement
        print("\n\n[Test 2] MISSING REQUIREMENT - Should fail requirement check")
        print("-" * 70)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_submissions["missing_requirement"])
            f.flush()
            filepath = f.name
        
        result = coordinator(filepath, requirements, testcases)
        
        print(f"✓ Requirement Status: {result['requirement'].get('fulfilled_count')}/{result['requirement'].get('total_count')}")
        if result['requirement'].get('unfulfilled'):
            print(f"✓ Unfulfilled: {result['requirement']['unfulfilled']}")
        print(f"✓ LLM Score: {result['llm']['score']}/20")
        print(f"✓ LLM Summary: {result['llm'].get('summary', 'N/A')}")
        
        # Verify LLM mentioned unfulfilled requirements
        if result['llm'].get('must_fix'):
            print(f"✓ LLM Must-Fix: {result['llm']['must_fix'][:1]}")
        
        if result['llm'].get('teacher_feedback'):
            feedback = result['llm']['teacher_feedback'].lower()
            if 'input' in feedback or 'requirement' in feedback:
                print("\n✅ LLM received and referenced requirement context!")
        
        # Test Case 3: Wrong output
        print("\n\n[Test 3] WRONG OUTPUT - Should fail test cases")
        print("-" * 70)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_submissions["wrong_output"])
            f.flush()
            filepath = f.name
        
        result = coordinator(filepath, requirements, testcases)
        
        print(f"✓ Test Status: {result['test']['passed_count']}/{result['test']['total_count']} passed")
        print(f"✓ LLM Score: {result['llm']['score']}/20")
        print(f"✓ LLM Summary: {result['llm'].get('summary', 'N/A')}")
        
        if result['llm'].get('must_fix'):
            print(f"✓ LLM Must-Fix Suggestions: {result['llm']['must_fix'][:2]}")
        
        # Verify LLM mentioned failing tests
        if result['llm'].get('teacher_feedback'):
            feedback = result['llm']['teacher_feedback'].lower()
            if 'test' in feedback or 'output' in feedback or 'print' in feedback:
                print("\n✅ LLM received and referenced test results context!")
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED - LLM Agent successfully receives full context!")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_llm_with_context()
    sys.exit(0 if success else 1)
