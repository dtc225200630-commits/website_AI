import subprocess, tempfile, os

code = '''"""Assignment 1: add two numbers."""
a = int(input())
b = int(input())
result = a + b
print(result)
'''

temp_fd, temp_filepath = tempfile.mkstemp(suffix='.py', text=True)
try:
    with os.fdopen(temp_fd, 'w') as f:
        f.write(code)
    
    # Same as syntax_agent does
    dummy_input = "\n".join(["1"] * 50)
    
    result = subprocess.run(
        ["python", temp_filepath],
        input=dummy_input,
        capture_output=True,
        text=True,
        timeout=3
    )
    
    print(f"Return code: {result.returncode}")
    print(f"STDOUT:\n{result.stdout}")
    print(f"STDERR:\n{result.stderr}")
    
finally:
    os.unlink(temp_filepath)
