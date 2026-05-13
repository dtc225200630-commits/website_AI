import subprocess
import tempfile
import os

code = """n = int(input("Nhập một số: "))

if n % 2 == 0:
    print(f"{n} là số chẵn")
else:
    print(f"{n} là số lẻ")
"""

# Write to temp file
with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
    f.write(code)
    temp_file = f.name

print(f"Testing with PYTHONIOENCODING=utf-8...")

# Set environment variable for utf-8
env = os.environ.copy()
env['PYTHONIOENCODING'] = 'utf-8'

result = subprocess.run(
    ["python", temp_file],
    input="1\n",
    capture_output=True,
    text=True,
    timeout=5,
    encoding='utf-8',
    env=env  # <-- FIX: Pass environment with PYTHONIOENCODING
)

print(f"Return code: {result.returncode}")
print(f"Stdout: '{result.stdout}'")
print(f"Stderr: '{result.stderr}'")

if result.returncode == 0:
    print("\n✅ SUCCESS - Code runs correctly with UTF-8 encoding!")
else:
    print("\n❌ FAILED")

os.unlink(temp_file)
