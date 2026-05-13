from agents.coordinator import coordinator

# Requirements for even/odd check
requirements = [
    {'requirement': 'Nhập số nguyên n'},
    {'requirement': 'Kiểm tra n % 2'},
    {'requirement': 'In Chan hoặc Le'}
]

# Test cases
testcases = [
    {'input': '4', 'output': 'Chan'},
    {'input': '3', 'output': 'Le'},
    {'input': '0', 'output': 'Chan'}
]

code = '''n = int(input())
if n % 2 == 0:
    print("Chan")
else:
    print(" Le")
'''

# Save to temp file
with open('temp_even_odd.py', 'w') as f:
    f.write(code)

result = coordinator('temp_even_odd.py', requirements, testcases)
print('=== SCORE BREAKDOWN ===')
print(f"Syntax: {result['syntax']['score']}/20")
print(f"Requirement: {result['requirement']['score']}/20")
print(f"Structure: {result['structure']['score']}/20")
print(f"Test: {result['test']['score']}/20")
print(f"LLM: {result['llm']['score']}/20")
print(f"=== TOTAL: {result['total']['total_score']}/100 ===")
print()
print('TEST DETAILS:')
for detail in result['test']['details']:
    print(f"  {detail}")
print()
print('TEST RESULTS:')
print(result['test']['test_results'])
