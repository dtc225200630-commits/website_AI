#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tempfile
import os
import sys

# Force simple orchestrator by disabling LangChain
os.environ['DISABLE_LANGCHAIN'] = '1'

# Temporarily rename langchain_orchestrator to force fallback
import shutil
orchestrator_path = os.path.join(os.path.dirname(__file__), 'agents', 'langchain_orchestrator.py')
backup_path = orchestrator_path + '.bak'

def test_with_simple_orchestrator():
    from agents.coordinator import simple_coordinator
    
    # Create test file
    test_code = '''
r = float(input('Input radius: '))
s = 3.14 * r * r
print('Area: {}'.format(s))
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(test_code)
        temp_filepath = f.name
    
    try:
        requirements = [
            ("input", 1),
            ("operator", 1),
            ("print", 1),
        ]
        
        testcases = [
            ("5", "78.5", 1),
        ]
        
        print("=" * 60)
        print("Simple Orchestrator Test")
        print("=" * 60)
        
        result = simple_coordinator(
            filepath=temp_filepath,
            requirements=requirements,
            testcases=testcases
        )
        
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
        
        # Verify code_analysis is present
        if 'code_analysis' in result:
            print("\n✓ code_analysis key present in result")
        else:
            print("\nX code_analysis key MISSING!")
            
        return result
        
    finally:
        os.unlink(temp_filepath)

print("[Test] Running simple orchestrator test...")
result = test_with_simple_orchestrator()
print("\n[RESULT] Simple orchestrator test completed successfully!")
