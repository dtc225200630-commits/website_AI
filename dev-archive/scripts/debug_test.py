#!/usr/bin/env python
# -*- coding: utf-8 -*-
code = '''
r = float(input('Nhập bán kính r: '))
s = 3.14 * r * r
print(f'Diện tích hình tròn là: {s}')
'''

from agents.coordinator import coordinator

print("=== Testing coordinator ===\n")
try:
    result = coordinator(code)
    print("Result keys:", result.keys())
    print("\nFull result:")
    for key, value in result.items():
        if isinstance(value, dict):
            print(f"  {key}: (dict with {len(value)} items)")
        else:
            print(f"  {key}: {value}")
    
    print(f"\nTotal score: {result.get('total_score', 'N/A')}")
    print(f"Code Analysis Score: {result.get('code_analysis', 'N/A')}")
except Exception as e:
    import traceback
    print(f"ERROR: {e}")
    traceback.print_exc()
