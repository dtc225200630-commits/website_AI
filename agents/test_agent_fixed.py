"""
Test Agent - Run Test Cases with Flexible Output Matching & Snippet Support

This agent:
1. Runs Python code with test inputs
2. For C++ snippets: auto-wrap, compile, and run with injected inputs
3. Handles numeric comparisons with tolerance
4. Strips whitespace and normalizes output
"""

import subprocess
import re
import os
import sys
import tempfile
from typing import Tuple

# Import unified scoring schema
try:
    from scoring_schema import ScoringSchema
except ImportError:
    from .scoring_schema import ScoringSchema


def extract_numbers(text: str) -> list:
    """Extract all floating point numbers from text."""
    pattern = r'-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?'
    matches = re.findall(pattern, text)
    return [float(m) for m in matches]


def normalize_output(output: str) -> str:
    """Normalize output for comparison."""
    return output.strip().lower()


def _short_preview(text: str, limit: int = 120) -> str:
    if text is None:
        return ""
    t = str(text)
    if len(t) <= limit:
        return t
    return t[: max(0, limit - 3)] + "..."


def _test_row(
    idx: int,
    status: str,
    input_data: str,
    expected_output: str,
    actual: str,
    weight: float,
    **extra,
) -> dict:
    """Moi dong ket qua: preview ngan + full cho LLM / API."""
    row = {
        "test_no": idx,
        "status": status,
        "input": _short_preview(input_data, 120),
        "expected": _short_preview(expected_output, 120),
        "actual": _short_preview(str(actual), 120),
        "input_full": str(input_data) if input_data is not None else "",
        "expected_full": str(expected_output) if expected_output is not None else "",
        "actual_full": str(actual) if actual is not None else "",
        "weight": weight,
    }
    row.update(extra)
    return row


def compare_outputs(expected: str, actual: str) -> bool:
    """
    Compare expected vs actual output FLEXIBLY with Vietnamese text support.
    
    Returns True if outputs match after:
    - Normalizing whitespace and case
    - Removing input prompts
    - Keyword/substring matching
    - Vietnamese abbreviation matching (cha chẵn/chẵn,  lẻ)
    """
    # First attempt: exact match after normalization
    if normalize_output(expected) == normalize_output(actual):
        return True
    
    # Smart prompt removal - strip Vietnamese input prompts
    actual_cleaned = actual
    import re
    actual_cleaned = re.sub(r"Nhập[^:]*:\s*", "", actual_cleaned)
    actual_cleaned = re.sub(r"input\s*:\s*", "", actual_cleaned, flags=re.IGNORECASE)
    actual_cleaned = actual_cleaned.strip()
    
    # Try normalized comparison again with cleaned output
    if normalize_output(expected) == normalize_output(actual_cleaned):
        return True
    
    # Vietnamese keyword matching
    # Map common abbreviations
    actual_for_kw = actual_cleaned.lower()
    expected_for_kw = expected.lower()
    
    # Handle "chan" = "chẵn", "le" = "lẻ"
    actual_for_kw = actual_for_kw.replace("chẵn", "chan").replace("chẵ", "chan")
    expected_for_kw = expected_for_kw.replace("chẵn", "chan").replace("chẵ", "chan")
    
    if normalize_output(expected_for_kw) == normalize_output(actual_for_kw):
        return True
    
    def _is_numeric_text(text: str) -> bool:
        return re.fullmatch(r'\s*-?\d+(?:\.\d+)?\s*', text or "") is not None

    # Try substring match only for non-numeric expected values.
    # Numeric expected outputs must match numerically, not by substring (e.g. "5" in "12.56").
    if not _is_numeric_text(expected):
        if normalize_output(expected) in normalize_output(actual_cleaned):
            return True
    
    # Try keyword presence only for non-numeric expected outputs.
    if not _is_numeric_text(expected):
        if expected_for_kw.strip() in actual_for_kw:
            return True
    
    # Numeric comparison as fallback
    expected_nums = extract_numbers(expected)
    actual_nums = extract_numbers(actual_cleaned)
    
    if expected_nums and actual_nums:
        for exp_num in expected_nums:
            found = False
            for act_num in actual_nums:
                if abs(exp_num - act_num) / (abs(exp_num) + 0.0001) < 0.01:
                    found = True
                    break
            if not found:
                return False
        return True
    
    if expected_nums and actual_nums:
        for exp_num in expected_nums:
            if any(exp_num == act_num for act_num in actual_nums):
                return True
    
    return False


def wrap_cpp_with_input(code: str, input_data: str) -> str:
    """Wrap C++ snippet with input injection."""
    lines = input_data.strip().split('\n')
    input_code = '\n    '.join([f'string var{i} = "{line}"; // Test input' for i, line in enumerate(lines)])
    
    wrapped = f"""#include <iostream>
#include <string>
using namespace std;

int main() {{
    // Injected test input
    {input_code}
    
    // Student code:
    {chr(10).join(code.split(chr(10))[:100])}  // Limit to first 100 lines
    
    return 0;
}}"""
    
    return wrapped


def test_agent(filepath, testcases):
    """
    Test agent: Runs code with test cases.
    Supports Python and C++ (with snippet auto-wrapping).
    
    Args:
        filepath: Path to Python or C++ file
        testcases: List of dicts with 'input_data', 'expected_output', 'score_weight'
    
    Returns:
        dict with score (0-20), test results
    """
    
    if not testcases:
        return {
            "score": 0,
            "details": ["Không có test case"],
            "passed_count": 0,
            "total_tests": 0,
            "total_count": 0,
            "test_results": [],
            "summary": "No tests to run"
        }
    
    # Determine if Python or C++
    is_cpp = filepath.endswith(('.cpp', '.cc', '.cxx'))
    is_python = filepath.endswith('.py')
    
    details = []
    test_results = []
    passed_weight = 0.0
    total_tests = 0
    total_weight = 0.0
    
    # Read the code
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
    except:
        return {
            "score": 0,
            "details": ["Cannot read file"],
            "passed_count": 0,
            "total_tests": len(testcases),
            "total_count": len(testcases),
            "test_results": [],
            "summary": "File read error"
        }
    
    # ============= PYTHON TESTING =============
    if is_python:
        for idx, tc in enumerate(testcases, 1):
            # Parse test case
            try:
                if isinstance(tc, dict):
                    input_data = tc.get('input_data', '') or tc.get('input', '')
                    expected_output = tc.get('expected_output', '') or tc.get('output', '')
                    weight = float(tc.get('score_weight', 1) or 1)
                else:
                    input_data = str(tc[0] or '')
                    expected_output = str(tc[1] or '')
                    weight = float(tc[2] or 1)
            except (IndexError, TypeError, ValueError):
                details.append(f"✗ Test {idx}: Invalid test case format")
                continue
            
            total_tests += 1
            total_weight += weight
            
            try:
                # Set UTF-8 encoding for subprocess to handle Vietnamese characters
                env = os.environ.copy()
                env['PYTHONIOENCODING'] = 'utf-8'
                
                result = subprocess.run(
                    [sys.executable, filepath],
                    input=input_data,
                    capture_output=True,
                    text=True,
                    timeout=5,
                    encoding='utf-8',
                    env=env
                )
                
                actual_output = (result.stdout or "").strip()
                error_output = (result.stderr or "").strip()
                rc = result.returncode

                # Chuan: neu stdout KHOP expected thi PASS — stderr (canh bao, debug) khong lam sai test.
                if compare_outputs(expected_output, actual_output):
                    passed_weight += weight
                    msg = f"✓ Test {idx} PASS: Input='{_short_preview(input_data, 50)}' → '{_short_preview(actual_output, 50)}'"
                    if error_output:
                        msg += f" (co stderr, bo qua vi stdout da khop: {_short_preview(error_output, 80)})"
                    details.append(msg)
                    test_results.append(
                        _test_row(
                            idx,
                            "PASS",
                            input_data,
                            expected_output,
                            actual_output,
                            weight,
                            stderr_note=_short_preview(error_output, 500) if error_output else "",
                        )
                    )
                elif rc != 0:
                    combined = actual_output
                    if error_output:
                        combined = (combined + "\n" + error_output).strip() if combined else error_output
                    details.append(
                        f"✗ Test {idx} ERROR (exit {rc}): {_short_preview(error_output or combined, 100)}"
                    )
                    test_results.append(
                        _test_row(
                            idx,
                            "ERROR",
                            input_data,
                            expected_output,
                            combined or f"(exit {rc})",
                            weight,
                            stderr_full=_short_preview(error_output, 2000),
                        )
                    )
                else:
                    msg = (
                        f"✗ Test {idx} FAIL: Expected '{_short_preview(expected_output, 50)}', "
                        f"got '{_short_preview(actual_output, 50)}'"
                    )
                    if error_output:
                        msg += f" [stderr: {_short_preview(error_output, 80)}]"
                    details.append(msg)
                    test_results.append(
                        _test_row(
                            idx,
                            "FAIL",
                            input_data,
                            expected_output,
                            actual_output,
                            weight,
                            stderr_note=_short_preview(error_output, 500) if error_output else "",
                        )
                    )
            
            except subprocess.TimeoutExpired:
                details.append(f"✗ Test {idx} TIMEOUT: Exceeded 5 seconds")
                test_results.append(
                    _test_row(idx, "TIMEOUT", input_data, expected_output, "TIMEOUT", weight)
                )
            
            except Exception as e:
                details.append(f"✗ Test {idx} ERROR: {str(e)[:100]}")
                test_results.append(
                    _test_row(idx, "ERROR", input_data, expected_output, str(e), weight)
                )
    
    # ============= C++ TESTING =============
    elif is_cpp:
        for idx, tc in enumerate(testcases, 1):
            try:
                if isinstance(tc, dict):
                    input_data = tc.get('input_data', '') or tc.get('input', '')
                    expected_output = tc.get('expected_output', '') or tc.get('output', '')
                    weight = float(tc.get('score_weight', 1) or 1)
                else:
                    input_data = str(tc[0] or '')
                    expected_output = str(tc[1] or '')
                    weight = float(tc[2] or 1)
            except (IndexError, TypeError, ValueError):
                details.append(f"✗ Test {idx}: Invalid format")
                continue
            
            total_tests += 1
            total_weight += weight
            
            try:
                # Wrap C++ code with includes and main
                is_snippet = 'main' not in code
                if is_snippet:
                    # Simple wrap for snippet with input
                    wrapped = f"""#include <iostream>
using namespace std;
int main() {{
    {chr(10).join(code.split(chr(10)))}
    return 0;
}}"""
                else:
                    wrapped = code
                
                # Write temp C++ file and compile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False, encoding='utf-8') as f:
                    f.write(wrapped)
                    temp_cpp = f.name
                
                temp_exe = temp_cpp.replace('.cpp', '.exe')
                
                # Compile
                compile_result = subprocess.run(
                    ['g++', '-o', temp_exe, temp_cpp],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if compile_result.returncode != 0:
                    details.append(f"✗ Test {idx} COMPILE_ERROR")
                    cerr = (compile_result.stderr or compile_result.stdout or "").strip() or "Compilation failed"
                    test_results.append(
                        _test_row(idx, "COMPILE_ERROR", input_data, expected_output, cerr, weight)
                    )
                    # Cleanup
                    try:
                        os.remove(temp_cpp)
                    except:
                        pass
                    continue
                
                # Run
                run_result = subprocess.run(
                    [temp_exe],
                    input=input_data,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                actual_output = (run_result.stdout or "").strip()
                cerr_run = (run_result.stderr or "").strip()

                if compare_outputs(expected_output, actual_output):
                    passed_weight += weight
                    details.append(f"✓ Test {idx} PASS")
                    test_results.append(
                        _test_row(
                            idx,
                            "PASS",
                            input_data,
                            expected_output,
                            actual_output,
                            weight,
                            stderr_note=_short_preview(cerr_run, 500) if cerr_run else "",
                        )
                    )
                else:
                    details.append(f"✗ Test {idx} FAIL")
                    test_results.append(
                        _test_row(
                            idx,
                            "FAIL",
                            input_data,
                            expected_output,
                            actual_output,
                            weight,
                            stderr_note=_short_preview(cerr_run, 500) if cerr_run else "",
                        )
                    )
                
                # Cleanup
                try:
                    os.remove(temp_cpp)
                    os.remove(temp_exe)
                except:
                    pass
            
            except subprocess.TimeoutExpired:
                details.append(f"✗ Test {idx} TIMEOUT")
                test_results.append(
                    _test_row(idx, "TIMEOUT", input_data, expected_output, "TIMEOUT", weight)
                )
            except Exception as e:
                details.append(f"✗ Test {idx} ERROR")
                test_results.append(
                    _test_row(idx, "ERROR", input_data, expected_output, str(e), weight)
                )
    
    # Calculate score using unified schema
    # Count-based proportional scoring: (passed_count / total_tests) * 20
    # Count passed tests regardless of weight for consistency with requirement agent
    passed_count = sum(1 for result in test_results if result.get('status') == 'PASS')
    score = ScoringSchema.proportional_score(passed_count, total_tests)
    
    pass_rate = (passed_weight / total_weight * 100) if total_weight > 0 else 0
    
    return {
        "score": score,
        "details": details,
        "passed_count": passed_count,
        "total_tests": total_tests,
        "total_count": total_tests,
        "test_results": test_results,
        "total_weight": total_weight,
        "pass_rate": f"{pass_rate:.1f}%",
        "summary": f"Passed {passed_count}/{total_tests} tests ({pass_rate:.1f}%)"
    }
