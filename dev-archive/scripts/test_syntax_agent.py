import subprocess
import tempfile
import os

# The code that was submitted
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

print(f"Temp file: {temp_file}")
print(f"File exists: {os.path.exists(temp_file)}")

# Read it back
with open(temp_file, 'r', encoding='utf-8') as f:
    print(f"File content:\n{f.read()}")

# Try to run it
print("\n" + "="*60)
print("Running code with subprocess...")
print("="*60 + "\n")

dummy_input = "1\n"  # Just one input

result = subprocess.run(
    ["python", temp_file],
    input=dummy_input,
    capture_output=True,
    text=True,
    timeout=5,
    encoding='utf-8'
)

print(f"Return code: {result.returncode}")
print(f"Stdout:\n{result.stdout}")
print(f"Stderr:\n{result.stderr}")

# Cleanup
os.unlink(temp_file)
print(f"\nCleaned up: {temp_file}")
