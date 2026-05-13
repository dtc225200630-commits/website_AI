"""
Syntax Agent - Check Python & C++ Code Syntax

This agent checks if code is valid Python or C++ by:
1. For Python: AST parsing + runtime execution
2. For C++: Wrap snippets, compile with g++, validate syntax
3. Auto-wrap incomplete code snippets
"""

import ast
import subprocess
import os
import sys
import tempfile


def _module_ast_is_trivial(tree: ast.AST) -> bool:
    """
    Module rỗng hoặc một Expr lẻ (Name / Constant / f-string) — hợp lệ về grammar
    nhưng không được coi là 'chương trình' cho rubric Cú pháp (tránh 20/20 với `4`).
    Đồng bộ với code_analysis_agent / structure_agent / requirement_agent.
    """
    if not isinstance(tree, ast.Module):
        return False
    body = [n for n in tree.body if not isinstance(n, ast.Pass)]
    if not body:
        return True
    if len(body) > 1:
        return False
    first = body[0]
    if not isinstance(first, ast.Expr):
        return False
    val = first.value
    if isinstance(val, (ast.Name, ast.Constant, ast.JoinedStr)):
        return True
    return False


def wrap_cpp_code(code):
    """Auto-wrap C++ snippet into a complete program if needed."""
    # Check if code already has main() 
    if 'main' in code or '#include' in code:
        return code  # Already a complete program
    
    # It's a snippet - wrap it
    wrapped = """#include <iostream>
using namespace std;

int main() {
    // Student code:
    {code}
    
    return 0;
}}""".format(code='\n    '.join(code.split('\n')))
    
    return wrapped


def syntax_agent(filepath):
    """
    Syntax agent: Checks if code has valid Python or C++ syntax.
    
    Returns:
        {{
            "success": bool,
            "score": 20 (valid) or 0-15 (wrapper/snippet issues),
            "error": error message if any,
            "details": list of diagnostic messages,
            "is_snippet": bool (True if code was auto-wrapped)
        }}
    """
    details = []
    
    # Try to read file
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        # UTF-8 BOM ở đầu file có thể làm lệch dòng 1 / import trên một số môi trường
        if code.startswith("\ufeff"):
            code = code.lstrip("\ufeff")
            try:
                with open(filepath, "w", encoding="utf-8", newline="\n") as wf:
                    wf.write(code)
            except OSError:
                pass
    except Exception as e:
        return {
            "success": False,
            "score": 0,
            "error": f"Cannot read file: {str(e)}",
            "details": [f"File read error: {str(e)}"],
            "is_snippet": False
        }
    
    # Detect language from file extension
    is_cpp = filepath.endswith(('.cpp', '.cc', '.cxx'))
    is_python = filepath.endswith('.py')
    
    # ============== PYTHON VALIDATION ==============
    if is_python:
        # Check syntax using AST parsing
        try:
            tree = ast.parse(code)
            details.append("✓ Valid Python grammar (AST parse passed)")
        except SyntaxError as e:
            error_msg = f"Line {e.lineno}: {e.msg}"
            return {
                "success": False,
                "score": 0,
                "error": error_msg,
                "details": [f"Syntax Error: {error_msg}"],
                "is_snippet": False
            }
        except Exception as e:
            return {
                "success": False,
                "score": 0,
                "error": f"Parse error: {str(e)}",
                "details": [f"Parse error: {str(e)}"],
                "is_snippet": False
            }

        if _module_ast_is_trivial(tree):
            msg = (
                "Mã chỉ là literal/biểu thức lẻ hoặc module rỗng — không đủ để chấm đủ điểm Cú pháp "
                "(cần lệnh gán, hàm, if/for/while, import, hoặc nhiều dòng có ý nghĩa)."
            )
            return {
                "success": False,
                "score": 0,
                "error": "Nội dung không phải chương trình hoàn chỉnh",
                "details": details + [msg],
                "is_snippet": False,
            }

        # Run code with stdin probe (nhiều bài đọc n rồi n số — dummy cũ dài dễ gây IndexError / lỗi logic)
        try:
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"

            # Thử lần lượt stdin ngắn, an toàn cho pattern phổ biến; chỉ cần một lần exit 0 là đủ để coi "chạy được".
            probe_inputs = [
                "0\n",  # n=0 sau split: nhiều bài contest
                "1\n0\n",  # n=1 + một số
                "1\n2\n3\n4\n5\n",  # n=1, một dòng số
                "\n".join(["1", "2", "3", "4"] * 10),  # legacy probe (40 token)
            ]

            last_result = None
            for probe in probe_inputs:
                last_result = subprocess.run(
                    [sys.executable, filepath],
                    input=probe,
                    capture_output=True,
                    text=True,
                    timeout=5,
                    encoding="utf-8",
                    env=env,
                )
                if last_result.returncode == 0:
                    details.append(f"✓ Code executes without runtime errors (stdin probe OK)")
                    details.append("✓ Syntax validation: PASS")
                    return {
                        "success": True,
                        "score": 20,
                        "error": None,
                        "details": details,
                        "is_snippet": False,
                    }

            result = last_result
            error_output = (result.stderr or "").strip()
            error_line = error_output.split("\n")[0] if error_output else "Unknown runtime error"
            out_preview = ((result.stdout or "").strip()[:200]) if result.stdout else ""
            detail_lines = [f"Runtime Error (sau {len(probe_inputs)} stdin probe): {error_line}"]
            if out_preview:
                detail_lines.append(f"stdout (rút gọn): {out_preview}")
            return {
                "success": False,
                "score": 0,
                "error": error_line,
                "details": detail_lines,
                "is_snippet": False,
            }
        
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "score": 0,
                "error": "Timeout - Code execution exceeded 5 seconds",
                "details": ["Execution timeout"],
                "is_snippet": False
            }
        except Exception as e:
            return {
                "success": False,
                "score": 0,
                "error": f"Execution error: {str(e)}",
                "details": [f"Execution error: {str(e)}"],
                "is_snippet": False
            }
    
    # ============== C++ VALIDATION ==============
    elif is_cpp:
        is_snippet = False
        compiled_code = code
        
        # Check if it's a snippet (no main function)
        if 'main' not in code or '#include' not in code:
            is_snippet = True
            details.append("⚠ Code snippet detected - auto-wrapping with main()")
            compiled_code = wrap_cpp_code(code)
        
        # Try to compile with g++
        try:
            # Create temp C++ file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False, encoding='utf-8') as f:
                f.write(compiled_code)
                temp_cpp = f.name
            
            # Compile
            temp_exe = temp_cpp.replace('.cpp', '.exe')
            result = subprocess.run(
                ['g++', '-o', temp_exe, temp_cpp],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Clean up temp files
            try:
                os.remove(temp_cpp)
                if os.path.exists(temp_exe):
                    os.remove(temp_exe)
            except:
                pass
            
            if result.returncode == 0:
                if is_snippet:
                    score = 15  # Snippet logic is correct but needs wrapper
                    details.append("✓ Code logic is valid but needed wrapper")
                else:
                    score = 20
                    details.append("✓ Valid C++ syntax and compiles")
                
                return {
                    "success": True,
                    "score": score,
                    "error": None,
                    "details": details,
                    "is_snippet": is_snippet
                }
            else:
                err_msg = result.stderr.strip().split('\n')[0] if result.stderr else "Compilation failed"
                return {
                    "success": False,
                    "score": 0,
                    "error": err_msg,
                    "details": [f"Compilation Error: {err_msg}"],
                    "is_snippet": is_snippet
                }
        
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "score": 0,
                "error": "Compilation timeout",
                "details": ["Compilation exceeded timeout"],
                "is_snippet": is_snippet
            }
        except Exception as e:
            return {
                "success": False,
                "score": 0,
                "error": f"Compilation error: {str(e)}",
                "details": [f"Compilation error: {str(e)}"],
                "is_snippet": is_snippet
            }
    
    else:
        return {
            "success": False,
            "score": 0,
            "error": "Unsupported file type",
            "details": [f"File type not supported: {filepath}"],
            "is_snippet": False
        }
