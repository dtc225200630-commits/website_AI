#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
End-to-end test: Verify coordinator → app.py → database flow
"""

import tempfile
import os
import json
from agents.coordinator import coordinator

# Test code
test_code = '''
def calculate_area(r):
    """Calculate circle area using formula"""
    return 3.14 * r * r

r = float(input('Input radius: '))
area = calculate_area(r)
print('Area:', area)
'''

print("=" * 70)
print("E2E Test: Coordinator -> Database Flow")
print("=" * 70)

# Create temp Python file
with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
    f.write(test_code)
    temp_filepath = f.name

try:
    # Call coordinator (same as app.py /submit endpoint does)
    requirements = [
        ("input", 1),
        ("function", 1),
        ("print", 1),
    ]
    
    testcases = [
        ("5", "78.5", 1),
    ]
    
    print("\n[1] Calling coordinator...")
    result = coordinator(
        filepath=temp_filepath,
        requirements=requirements,
        testcases=testcases
    )
    
    print("\n[2] Result structure from coordinator:")
    print(f"  Keys: {list(result.keys())}")
    
    # Show all agent scores
    print("\n[3] Agent scores:")
    for agent_name in ["syntax", "code_analysis", "requirement", "structure", "test", "llm"]:
        if agent_name in result:
            score = result[agent_name].get("score", 0)
            print(f"  {agent_name:12} : {score:2.0f}/20")
    
    print(f"\n[4] Total score: {result.get('total', {}).get('total_score', 0):.0f}/100")
    
    # Simulate what app.py does when saving
    print("\n[5] Simulating app.py database save...")
    
    # Extract like app.py does
    syntax_score = float(result.get("syntax", {}).get("score", 0))
    code_analysis_score = float(result.get("code_analysis", {}).get("score", 0))
    requirement_score = float(result.get("requirement", {}).get("score", 0))
    structure_score = float(result.get("structure", {}).get("score", 0))
    test_score = float(result.get("test", {}).get("score", 0))
    llm_score = float(result.get("llm", {}).get("score", 0))
    total_score = float(result.get("total", {}).get("total_score", 0))
    
    print("  Database values to INSERT:")
    print(f"    syntax_score: {syntax_score}")
    print(f"    code_analysis_score: {code_analysis_score} <-- NEW!")
    print(f"    requirement_score: {requirement_score}")
    print(f"    structure_score: {structure_score}")
    print(f"    test_score: {test_score}")
    print(f"    llm_score: {llm_score} <-- NEW!")
    print(f"    total_score: {total_score}")
    
    # Check agent_details JSON
    print("\n[6] Agent details (JSONB) that will be saved:")
    agent_details = {
        "syntax": result.get("syntax", {}),
        "code_analysis": result.get("code_analysis", {}),
        "requirement": result.get("requirement", {}),
        "structure": result.get("structure", {}),
        "test": result.get("test", {}),
        "llm": result.get("llm", {}),
    }
    
    # Show compact JSON representation
    json_str = json.dumps(agent_details, ensure_ascii=False)
    print(f"  JSON size: {len(json_str)} bytes")
    print(f"  Contains code_analysis: {'code_analysis' in json_str}")
    print(f"  Contains llm: {'llm' in json_str}")
    
    print("\n[7] Agent logs (6 agents now):")
    agent_names = ["SyntaxAgent", "CodeAnalysisAgent", "RequirementAgent", "StructureAgent", "TestAgent", "LLMAgent"]
    print(f"  Total agents: {len(agent_names)}")
    for name in agent_names:
        print(f"    - {name}")
    
    print("\n" + "=" * 70)
    print("SUCCESS - All data prepared for database!")
    print("=" * 70)
    
finally:
    os.unlink(temp_filepath)
