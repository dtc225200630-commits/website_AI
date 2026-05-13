import requests
import json

# Code to submit
code = """n = int(input("Nhập một số: "))

if n % 2 == 0:
    print(f"{n} là số chẵn")
else:
    print(f"{n} là số lẻ")
"""

# The /submit endpoint expects Form data, not JSON
payload = {
    'assignment_id': 3,
    'source_code': code
}

# Set cookies with user_id
cookies = {'user_id': '4'}

response = requests.post('http://localhost:8000/submit', data=payload, cookies=cookies)

print('Response Status:', response.status_code)
print('Response Text:')
print(response.text)
print('Response Headers:')
print(response.headers)

try:
    result = response.json()
    print('\nParsed JSON:')
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Extract scores
    if 'evaluation' in result:
        eval_data = result['evaluation']
        print('\n=== SCORES ===')
        print(f"Syntax: {eval_data.get('syntax_score', 'N/A')}/20")
        print(f"Structure: {eval_data.get('structure_score', 'N/A')}/20")
        print(f"Requirement: {eval_data.get('requirement_score', 'N/A')}/20")
        print(f"Test: {eval_data.get('test_score', 'N/A')}/20")
        print(f"LLM: {eval_data.get('llm_score', 'N/A')}/20")
        print(f"TOTAL: {eval_data.get('total_score', 'N/A')}/100")
except:
    print('Could not parse JSON response')
