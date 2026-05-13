#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tempfile
import os
from agents.coordinator import coordinator

# Create a test Python file 
test_code = '''
r = float(input('Input radius: '))
s = 3.14 * r * r
print('Area: {}'.format(s))
'''

# Create temp file
with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
    f.write(test_code)
    temp_filepath = f.name

try:
    # Setup requirements and test cases like the app does
    requirements = [
        ("input", 1),
        ("operator", 1),
        ("print", 1),
    ]
    
    testcases = [
        ("5", "78.5", 1),
    ]
    
    print("=" * 60)
    print("Full Coordinator Test (End-to-End)")
    print("=" * 60)
    print("Test file:", temp_filepath)
    print("Requirements:", len(requirements))
    print("Test cases:", len(testcases))
    print("=" * 60)
    
    result = coordinator(
        filepath=temp_filepath,
        requirements=requirements,
        testcases=testcases
    )
    
    print("\n[RESULT STRUCTURE]")
    print("Result keys:", list(result.keys()))
    
    print("\n[INDIVIDUAL SCORES]")
    print("  Syntax:", result.get('syntax', {}).get('score', 'N/A'), "/20")
    print("  Code Analysis:", result.get('code_analysis', {}).get('score', 'N/A'), "/20")
    print("  Requirement:", result.get('requirement', {}).get('score', 'N/A'), "/20")
    print("  Structure:", result.get('structure', {}).get('score', 'N/A'), "/20")
    print("  Test:", result.get('test', {}).get('score', 'N/A'), "/20")
    print("  LLM:", result.get('llm', {}).get('score', 'N/A'), "/20")
    
    print("\n[TOTAL SCORE]")
    total_info = result.get('total', {})
    print("  Total Score:", total_info.get('total_score', 'N/A'), "/100")
    print("  Grade:", total_info.get('grade', 'N/A'))
    
    print("\n[BREAKDOWN]")
    breakdown = total_info.get('breakdown', {})
    for key, value in breakdown.items():
        print("  ", key, ":", value)
    
    # Check for errors
    if 'error' in result:
        print("\n[ERROR in result]")
        print("  ERROR:", result['error'])
        
finally:
    os.unlink(temp_filepath)
