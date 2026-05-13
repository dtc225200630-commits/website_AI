"""
Test Scoring Consistency - Validates unified scoring schema across all agents

This test ensures:
1. All agents use the same 0-20 point scale
2. Proportional scoring is consistent
3. No agent breaks when one is fixed
4. LLM receives consistent score information
"""

import sys
import os

# Add agents directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agents'))

from scoring_schema import ScoringSchema, ScoringConsistencyChecker
from requirement_agent_fixed import requirement_agent
from test_agent_fixed import test_agent
from structure_agent_fixed import structure_agent
from code_analysis_agent import code_analysis_agent
from syntax_agent_fixed import syntax_agent


def test_proportional_scoring():
    """Test that proportional scoring is consistent."""
    print("\n" + "="*70)
    print("TEST 1: Proportional Scoring Consistency")
    print("="*70)
    
    test_cases = [
        (3, 3, 20),  # 3/3 = 100% = 20 pts
        (2, 3, 13),  # 2/3 = 66.7% = 13.33 → 13 pts
        (1, 3, 6),   # 1/3 = 33.3% = 6.67 → 6 pts
        (0, 3, 0),   # 0/3 = 0% = 0 pts
        (1, 2, 10),  # 1/2 = 50% = 10 pts
    ]
    
    all_pass = True
    for achieved, total, expected_score in test_cases:
        actual_score = ScoringSchema.proportional_score(achieved, total)
        status = "✓ PASS" if actual_score == expected_score else "✗ FAIL"
        print(f"{status}: {achieved}/{total} → {actual_score} pts (expected {expected_score})")
        if actual_score != expected_score:
            all_pass = False
    
    return all_pass


def test_requirements_agent_consistency():
    """Test that requirement_agent uses unified scoring."""
    print("\n" + "="*70)
    print("TEST 2: Requirement Agent Consistency")
    print("="*70)
    
    test_code = """
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b
"""
    
    requirements = [
        {"requirement_text": "Code should have functions", "weight": 1},
        {"requirement_text": "Code should use meaningful names", "weight": 1},
        {"requirement_text": "Code should handle edge cases", "weight": 1},
    ]
    
    result = requirement_agent(test_code, requirements)
    
    print(f"Result:")
    print(f"  Score: {result.get('score')}/20")
    print(f"  Fulfilled: {result.get('fulfilled_count')}/{result.get('total_count')}")
    
    # Verify consistency
    expected_score = ScoringSchema.proportional_score(
        result.get('fulfilled_count', 0),
        result.get('total_count', 1)
    )
    
    is_consistent = result.get('score') == expected_score
    status = "✓ CONSISTENT" if is_consistent else "✗ INCONSISTENT"
    print(f"{status}: Score {result.get('score')} matches expected {expected_score}")
    
    # Validate using consistency checker
    validation_errors = ScoringConsistencyChecker.validate_agent_result('requirement', result)
    if validation_errors:
        print("✗ VALIDATION ERRORS:")
        for error in validation_errors:
            print(f"  - {error}")
        return False
    else:
        print("✓ VALIDATION PASSED")
        return is_consistent


def test_test_agent_consistency():
    """Test that test_agent uses count-based proportional scoring."""
    print("\n" + "="*70)
    print("TEST 3: Test Agent Consistency")
    print("="*70)
    
    # Create a simple test file
    test_code_file = "test_temp_script.py"
    test_code = """
n = int(input())
print(n * 2)
"""
    
    with open(test_code_file, 'w') as f:
        f.write(test_code)
    
    try:
        testcases = [
            {"input_data": "5", "expected_output": "10", "score_weight": 10},
            {"input_data": "3", "expected_output": "6", "score_weight": 10},
            {"input_data": "0", "expected_output": "0", "score_weight": 10},
        ]
        
        result = test_agent(test_code_file, testcases)
        
        print(f"Result:")
        print(f"  Score: {result.get('score')}/20")
        print(f"  Passed: {result.get('passed_count')}/{result.get('total_tests')}")
        
        # Verify consistency
        expected_score = ScoringSchema.proportional_score(
            result.get('passed_count', 0),
            result.get('total_tests', 1)
        )
        
        is_consistent = result.get('score') == expected_score
        status = "✓ CONSISTENT" if is_consistent else "✗ INCONSISTENT"
        print(f"{status}: Score {result.get('score')} matches expected {expected_score}")
        
        # Validate using consistency checker
        validation_errors = ScoringConsistencyChecker.validate_agent_result('test', result)
        if validation_errors:
            print("✗ VALIDATION ERRORS:")
            for error in validation_errors:
                print(f"  - {error}")
            return False
        else:
            print("✓ VALIDATION PASSED")
            return is_consistent
    
    finally:
        # Clean up
        if os.path.exists(test_code_file):
            os.remove(test_code_file)


def test_syntax_agent_consistency():
    """Test that syntax_agent uses binary scoring."""
    print("\n" + "="*70)
    print("TEST 4: Syntax Agent Consistency")
    print("="*70)
    
    # Create test files
    valid_file = "test_valid.py"
    with open(valid_file, 'w') as f:
        f.write("print('hello')")
    
    try:
        result = syntax_agent(valid_file)
        
        print(f"Result:")
        print(f"  Score: {result.get('score')}/20")
        print(f"  Success: {result.get('success')}")
        
        # Syntax score must be 0, 15, or 20
        valid_scores = [0, 15, 20]
        is_valid = result.get('score') in valid_scores
        status = "✓ VALID" if is_valid else "✗ INVALID"
        print(f"{status}: Syntax score {result.get('score')} in {valid_scores}")
        
        # Validate using consistency checker
        validation_errors = ScoringConsistencyChecker.validate_agent_result('syntax', result)
        if validation_errors:
            print("✗ VALIDATION ERRORS:")
            for error in validation_errors:
                print(f"  - {error}")
            return False
        else:
            print("✓ VALIDATION PASSED")
            return is_valid
    
    finally:
        if os.path.exists(valid_file):
            os.remove(valid_file)


def test_all_agents_consistency():
    """Test consistency across all agents with same code."""
    print("\n" + "="*70)
    print("TEST 5: All Agents - Consistency Check")
    print("="*70)
    
    test_code = """
def add(a, b):
    '''Add two numbers'''
    return a + b

def multiply(a, b):
    '''Multiply two numbers'''
    return a * b

if __name__ == "__main__":
    print(add(2, 3))
    print(multiply(4, 5))
"""
    
    # Save test file
    test_file = "test_all_agents.py"
    with open(test_file, 'w') as f:
        f.write(test_code)
    
    try:
        all_results = {}
        
        # Run all agents
        print("Running agents...")
        all_results['syntax'] = syntax_agent(test_file)
        print(f"  Syntax: {all_results['syntax']['score']}/20")
        
        if all_results['syntax']['success']:
            all_results['code_analysis'] = code_analysis_agent(test_code)
            print(f"  Code Analysis: {all_results['code_analysis']['score']}/20")
            
            all_results['structure'] = structure_agent(test_code)
            print(f"  Structure: {all_results['structure']['score']}/20")
            
            requirements = [
                {"requirement_text": "Code should have functions", "weight": 1},
                {"requirement_text": "Code should have docstrings", "weight": 1},
            ]
            
            all_results['requirement'] = requirement_agent(test_code, requirements)
            print(f"  Requirement: {all_results['requirement']['score']}/20")
            
            testcases = [
                {"input_data": "", "expected_output": "5\n20", "score_weight": 10},
            ]
            
            all_results['test'] = test_agent(test_file, testcases)
            print(f"  Test: {all_results['test']['score']}/20")
        
        # Validate consistency
        print("\nValidating consistency...")
        consistency_report = ScoringConsistencyChecker.check_all_agents(all_results)
        
        if consistency_report:
            print("✗ CONSISTENCY ERRORS FOUND:")
            for agent_name, errors in consistency_report.items():
                print(f"  {agent_name}:")
                for error in errors:
                    print(f"    - {error}")
            return False
        else:
            print("✓ ALL AGENTS CONSISTENT!")
            print("\nScore Summary:")
            for agent_name, result in all_results.items():
                score = result.get('score', 'N/A')
                print(f"  {agent_name}: {score}/20")
            return True
    
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("UNIFIED SCORING SCHEMA - CONSISTENCY TESTS")
    print("="*70)
    
    results = []
    
    # Run all tests
    results.append(("Proportional Scoring", test_proportional_scoring()))
    results.append(("Requirement Agent", test_requirements_agent_consistency()))
    results.append(("Test Agent", test_test_agent_consistency()))
    results.append(("Syntax Agent", test_syntax_agent_consistency()))
    results.append(("All Agents", test_all_agents_consistency()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n✓ ALL TESTS PASSED - Scoring is consistent across all agents!")
        sys.exit(0)
    else:
        print(f"\n✗ {total_tests - total_passed} tests failed")
        sys.exit(1)
