import requests

url = "http://127.0.0.1:8000/submit"
data = {
    "assignment_id": 2, # Tính diện tích hình tròn
    "source_code": '''
import math

def calculate_area():
    """Calculate the area of a circle with a given radius."""
    r = float(input())
    PI = 3.14
    area = PI * r * r
    print(area)

if __name__ == '__main__':
    calculate_area()
'''
}
cookies = {"user_id": "1", "role": "student"}

print("Sending request...")
response = requests.post(url, data=data, cookies=cookies)
print(f"Status Code: {response.status_code}")
if response.status_code != 200:
    print(response.text)
else:
    print("Success! Check the DB or web UI for results.")
