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

# OPTIMIZED CODE - better structure
code = '''def check_even_odd(n):
    """Check if number is even or odd."""
    if n % 2 == 0:
        return "Chan"
    else:
        return "Le"

# Main program
n = int(input())
result = check_even_odd(n)
print(result)
'''

# Save to temp file
with open('temp_even_odd.py', 'w') as f:
    f.write(code)

result = coordinator('temp_even_odd.py', requirements, testcases)
print('=== SCORE BREAKDOWN (OPTIMIZED) ===')
print(f"Syntax: {result['syntax']['score']}/20")
print(f"Requirement: {result['requirement']['score']}/20")
print(f"Structure: {result['structure']['score']}/20")
print(f"Test: {result['test']['score']}/20")
print(f"LLM: {result['llm']['score']}/20")
print(f"=== TOTAL: {result['total']['total_score']}/100 ===")
