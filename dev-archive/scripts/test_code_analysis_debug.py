#!/usr/bin/env python
# -*- coding: utf-8 -*-

from agents.code_analysis_agent import code_analysis_agent

code1 = '''
r = float(input('Nhập bán kính r: '))
s = 3.14 * r * r
print(f'Diện tích hình tròn là: {s}')
'''

code2 = '''
def calculate_area(r):
    """Calculate circle area."""
    return 3.14 * r * r

r = float(input('Nhập bán kính r: '))
s = calculate_area(r)
print(f'Diện tích hình tròn là: {s}')
'''

print("=" * 60)
print("Testing code_analysis_agent")
print("=" * 60)

print("\n[TEST 1] Simple code (no functions)")
print("-" * 40)
try:
    result1 = code_analysis_agent(code1)
    print(f"Result type: {type(result1)}")
    print(f"Result keys: {result1.keys()}")
    print(f"Score: {result1.get('score', 'N/A')}/20")
    print(f"Details: {result1.get('details', 'N/A')}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n[TEST 2] Code with function")
print("-" * 40) 
try:
    result2 = code_analysis_agent(code2)
    print(f"Result type: {type(result2)}")
    print(f"Result keys: {result2.keys()}")
    print(f"Score: {result2.get('score', 'N/A')}/20")
    print(f"Details: {result2.get('details', 'N/A')}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
