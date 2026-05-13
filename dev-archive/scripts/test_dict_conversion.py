#!/usr/bin/env python3
"""Quick test for dict conversion"""

# Test that dict conversion works
testcases_raw = [('5', '8', 1), ('4', '20', 1)]
testcases = [
    {
        'input_data': inp,
        'expected_output': out,
        'score_weight': float(weight) if weight else 1.0
    }
    for inp, out, weight in testcases_raw
]

print("✓ Dict conversion SUCCESS")
print(f"Example testcase: {testcases[0]}")
print(f"Has .get() method: {hasattr(testcases[0], 'get')}")
print(f"Accessing with .get(): {testcases[0].get('input_data')}")
