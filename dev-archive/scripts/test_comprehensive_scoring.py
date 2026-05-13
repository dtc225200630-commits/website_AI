#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tempfile
import os
from agents.coordinator import coordinator

test_cases = [
    {
        "name": "Simple code (low quality)",
        "code": '''
r = float(input('Input radius: '))
s = 3.14 * r * r
print('Area:', s)
''',
        "requirements": [("input", 1), ("operator", 1), ("print", 1)],
        "testcases": [("5", "78.5", 1)],
    },
    {
        "name": "Code with function (medium quality)",
        "code": '''
def calculate_area(r):
    """Calculate circle area"""
    return 3.14 * r * r

r = float(input('Input radius: '))
s = calculate_area(r)
print('Area:', s)
''',
        "requirements": [("input", 1), ("operator", 1), ("print", 1), ("def", 1)],
        "testcases": [("5", "78.5", 1)],
    },
]

print("=" * 70)
print("COMPREHENSIVE SCORE VERIFICATION (After Fix)")
print("=" * 70)

for test_case in test_cases:
    print(f"\n[TEST] {test_case['name']}")
    print("-" * 70)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(test_case['code'])
        temp_filepath = f.name
    
    try:
        result = coordinator(
            filepath=temp_filepath,
            requirements=test_case['requirements'],
            testcases=test_case['testcases']
        )
        
        total_info = result.get('total', {})
        print("  Syntax:", result.get('syntax', {}).get('score', 'N/A'), "/20 ->", int(result.get('syntax', {}).get('score', 0)), "pts")
        print("  Code Analysis:", result.get('code_analysis', {}).get('score', 'N/A'), "/20 ->", int(result.get('code_analysis', {}).get('score', 0)), "pts")
        print("  Requirement:", result.get('requirement', {}).get('score', 'N/A'), "/20 ->", int(result.get('requirement', {}).get('score', 0)), "pts")
        print("  Structure:", result.get('structure', {}).get('score', 'N/A'), "/20 ->", int(result.get('structure', {}).get('score', 0)), "pts")
        print("  Test:", result.get('test', {}).get('score', 'N/A'), "/20 ->", int(result.get('test', {}).get('score', 0)), "pts")
        print("  LLM:", result.get('llm', {}).get('score', 'N/A'), "/20 ->", int(result.get('llm', {}).get('score', 0)), "pts")
        
        total_score = total_info.get('total_score', 0)
        print(f"\n  >>> TOTAL SCORE: {total_score}/100 - ", end="")
        
        if total_score >= 90:
            print("GRADE A")
        elif total_score >= 80:
            print("GRADE B")
        elif total_score >= 70:
            print("GRADE C")
        elif total_score >= 60:
            print("GRADE D")
        else:
            print("GRADE F")
            
    finally:
        os.unlink(temp_filepath)

print("\n" + "=" * 70)
print("TEST COMPLETE - All scores are now using corrected formula!")
print("=" * 70)
