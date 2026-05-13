import subprocess
import os

code = """# Nhập số thứ nhất
a = int(input("Nhập số thứ nhất: "))

# Nhập số thứ hai
b = int(input("Nhập số thứ hai: "))

# Tính và in tổng hai số
print("Tổng hai số là:", a + b)"""

input_data = "2\n3"
expected = "5"

env = os.environ.copy()
env['PYTHONIOENCODING'] = 'utf-8'

result = subprocess.run(
    ['python', '-c', code],
    input=input_data.encode('utf-8'),
    capture_output=True,
    timeout=5,
    text=False,
    env=env
)

actual_output = result.stdout.decode('utf-8', errors='ignore').strip()
stderr_output = result.stderr.decode('utf-8', errors='ignore').strip()

print("Actual stdout:", repr(actual_output))
print("Stderr:", repr(stderr_output))
print("Expected:", repr(expected))
print("Match stdout:", actual_output == expected)
print()
print("Stdout Lines:")
for i, line in enumerate(actual_output.split('\n')):
    print(f"  Line {i}: {repr(line)}")

