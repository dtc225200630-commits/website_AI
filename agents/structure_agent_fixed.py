"""
Structure Agent - Analyze Code Quality (Python & C++)

This agent analyzes code structure using:
- Python: AST parsing for accurate analysis
- C++: Regex patterns for snippet detection
- Snippet-aware: Doesn't penalize missing boilerplate
"""

import ast
import re
from typing import Dict, List, Optional, Tuple

from agents.rubric_hints import build_rubric_hints
try:
    from scoring_schema import ScoringSchema
except ImportError:
    from .scoring_schema import ScoringSchema


def is_python_code(code: str) -> bool:
    """Check if code looks like Python."""
    # Python keywords that are distinctive
    py_keywords = ['def ', 'class ', 'import ', 'from ', 'if __name__', 'self.']
    return any(kw in code for kw in py_keywords) or code.strip().startswith('#')


def is_cpp_code(code: str) -> bool:
    """Check if code looks like C++."""
    cpp_patterns = ['cout', 'cin', 'vector', '#include', '<<', '>>', 'std::', 'if (', 'else {']
    return sum(1 for p in cpp_patterns if p in code) >= 2


def analyze_cpp_structure(code: str) -> Dict:
    """Analyze C++ code structure using regex patterns."""
    metrics = {
        'has_if': bool(re.search(r'\bif\s*\(', code)),
        'has_else': bool(re.search(r'\}\s*else\s*\{', code)),
        'has_for': bool(re.search(r'\bfor\s*\(', code)),
        'has_while': bool(re.search(r'\bwhile\s*\(', code)),
        'has_function': bool(re.search(r'\w+\s+\w+\s*\([^)]*\)\s*\{', code)),
        'has_class': bool(re.search(r'\bclass\s+\w+', code)),
        'has_comments': bool(re.search(r'//|/\*', code)),
        'lines': len(code.split('\n')),
        'has_operators': bool(re.search(r'[+\-*/%]', code))
    }
    return metrics


class CodeStructureAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze code structure."""
    
    def __init__(self):
        self.functions = []
        self.classes = []
        self.variables = []
        self.imports = []
        self.docstrings_count = 0
        self.has_main = False
        self.function_docstrings = {}
        self.duplicates = []
    
    def visit_FunctionDef(self, node):
        """Visit function definitions."""
        self.functions.append(node.name)
        docstring = ast.get_docstring(node)
        if docstring:
            self.docstrings_count += 1
            self.function_docstrings[node.name] = True
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """Visit class definitions."""
        self.classes.append(node.name)
        docstring = ast.get_docstring(node)
        if docstring:
            self.docstrings_count += 1
        self.generic_visit(node)
    
    def visit_Assign(self, node):
        """Visit variable assignments."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.variables.append(target.id)
        self.generic_visit(node)
    
    def visit_Import(self, node):
        """Visit imports."""
        for name in node.names:
            self.imports.append(name.name)
    
    def visit_ImportFrom(self, node):
        """Visit from imports."""
        for name in node.names:
            self.imports.append(f"{node.module}.{name.name}")


def analyze_structure(code: str) -> Tuple[CodeStructureAnalyzer, List[str]]:
    """Parse code and analyze structure using AST."""
    try:
        tree = ast.parse(code)
        analyzer = CodeStructureAnalyzer()
        analyzer.visit(tree)
        return analyzer, []
    except SyntaxError as e:
        return None, [f"Syntax error in code: {e.msg}"]


def _module_ast_is_trivial(tree: ast.AST) -> bool:
    """Giống code_analysis: một biểu thức lẻ / rỗng — không coi là chương trình có cấu trúc."""
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


def _is_stdin_stdout_script(code: str) -> bool:
    """Đồng bộ với code_analysis_agent: script có input() và print()."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False
    has_input = False
    has_print = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "input":
                has_input = True
            elif node.func.id == "print":
                has_print = True
    return has_input and has_print


def check_naming_conventions(
    code: str, rubric: Optional[Dict[str, bool]] = None
) -> Tuple[int, List[str]]:
    """
    Check PEP 8 naming conventions.
    Returns: (points, issues)
    """
    rb = rubric if rubric is not None else build_rubric_hints()
    points = 0
    issues = []
    
    # Find all identifiers (function names, variable names)
    identifiers = set(re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', code))
    
    bad_names = []
    good_names = []
    
    for name in identifiers:
        # Skip Python keywords and builtins
        if name in ['if', 'else', 'for', 'while', 'def', 'class', 'return', 'import', 'from']:
            continue
        
        # Check naming convention
        if name.isupper() and '_' in name:
            good_names.append(name)  # CONSTANT_NAME
        elif '_' in name and name.islower():
            good_names.append(name)  # function_name
        elif name[0].isupper() and not '_' in name:
            good_names.append(name)  # ClassName
        elif name.islower() and len(name) > 1:
            good_names.append(name)  # variable_name
        elif len(name) == 1 and name != 'i':
            bad_names.append(name)  # Single letter (except loop counter)
        elif name.isdigit():
            bad_names.append(name)  # All digits
    
    if len(good_names) > len(bad_names):
        points = 4
        issues.append(f"✓ Good naming conventions ({len(good_names)} well-named identifiers)")
    elif len(bad_names) > 0:
        if (
            rb.get("prefer_concise", True)
            and not rb.get("expect_functions", False)
            and len(code.splitlines()) <= 12
            and len(bad_names) <= 2
        ):
            points = 3
            issues.append(
                f"◐ {len(bad_names)} tên rất ngắn — chấp nhận khi rubric ưu tiên code gọn"
            )
        else:
            points = 1
            issues.append(f"✗ Poor naming: {len(bad_names)} single-letter or unclear names")
    else:
        points = 2
        issues.append("◐ Naming could be improved")
    
    return points, issues


def structure_agent(code: str, rubric: Optional[Dict[str, bool]] = None) -> Dict:
    """
    Analyze code structure for Python and C++ (including snippets).
    
    Scoring (total max 20):
    - For Python: AST-based analysis
    - For C++: Regex-based pattern analysis
    - Snippet-aware: Doesn't penalize missing boilerplate
    """
    
    score = 0
    details = []
    issues = []
    strengths = []
    metrics = {}
    
    # Detect code type
    is_cpp = is_cpp_code(code)
    is_python = is_python_code(code)
    
    # ============= C++ ANALYSIS =============
    if is_cpp:
        cpp_metrics = analyze_cpp_structure(code)
        
        # Check control flow (0-5 pts)
        flow_points = 0
        if cpp_metrics['has_if'] and cpp_metrics['has_else']:
            flow_points = 5
            strengths.append("✓ Good control flow with if/else")
        elif cpp_metrics['has_if']:
            flow_points = 3
            details.append("✓ Has if statement")
        elif cpp_metrics['has_for'] or cpp_metrics['has_while']:
            flow_points = 3
            details.append("✓ Has loop structure")
        else:
            flow_points = 1
            issues.append("Limited control flow")
        
        score += flow_points
        
        # Check operations (0-5 pts)
        op_points = 0
        if cpp_metrics['has_operators']:
            op_points = 3
            strengths.append("✓ Uses arithmetic operations")
        
        if cpp_metrics['has_function']:
            op_points = 5
            strengths.append("✓ Defines functions")
        
        score += op_points
        
        # Check comments (0-3 pts)
        comment_points = 0
        if cpp_metrics['has_comments']:
            comment_points = 2
            details.append("✓ Contains comments")
        
        score += comment_points
        
        # Check complexity (0-3 pts)
        lines = cpp_metrics['lines']
        if lines >= 20:
            complex_points = 3
            strengths.append(f"Good complexity ({lines} lines)")
        elif lines >= 10:
            complex_points = 2
            details.append(f"Moderate complexity ({lines} lines)")
        elif lines >= 5:
            complex_points = 1
        else:
            complex_points = 0
        
        score += complex_points
        
        # Check OOP (0-4 pts)
        oop_points = 0
        if cpp_metrics['has_class']:
            oop_points = 4
            strengths.append("✓ Uses OOP with class")
        
        score += oop_points
        
        metrics = {
            "language": "C++",
            "has_control_flow": cpp_metrics['has_if'] or cpp_metrics['has_else'],
            "has_loops": cpp_metrics['has_for'] or cpp_metrics['has_while'],
            "lines": lines,
            "has_functions": cpp_metrics['has_function'],
            "has_classes": cpp_metrics['has_class']
        }
        
        # Cap score at 20
        score = min(20, score)
        
        return {
            "score": score,
            "details": details,
            "issues": issues,
            "strengths": strengths if strengths else ["Code is functional"],
            "metrics": metrics,
            "summary": f"C++ Structure: {score}/20"
        }
    
    # ============= PYTHON ANALYSIS (AST-based) =============
    else:
        r = rubric if rubric is not None else build_rubric_hints()
        # Parse code with AST
        analyzer, parse_errors = analyze_structure(code)

        if parse_errors or analyzer is None:
            return {
                "score": 0,
                "details": parse_errors or ["Không phân tích được cấu trúc"],
                "issues": ["Cannot analyze structure - code has syntax errors"],
                "strengths": [],
                "metrics": {},
                "summary": "Cấu trúc: 0/20 — sửa lỗi cú pháp trước",
            }

        try:
            _trivial_tree = ast.parse(code)
        except SyntaxError:
            _trivial_tree = None
        if _trivial_tree is not None and _module_ast_is_trivial(_trivial_tree):
            return {
                "score": 0,
                "details": ["Mã không đủ cấu trúc (ví dụ chỉ một biểu thức lẻ)."],
                "issues": ["Nội dung quá ngắn hoặc không phải chương trình hoàn chỉnh"],
                "strengths": [],
                "metrics": {},
                "summary": "Cấu trúc: 0/20 — cần hàm, gán biến, hoặc luồng điều khiển",
            }

        # 1. Check functions (0-4 pts)
        func_count = len(analyzer.functions)
        if func_count >= 3:
            func_points = 4
            strengths.append(f"Well-structured with {func_count} functions")
        elif func_count == 2:
            func_points = 3
            details.append(f"◐ {func_count} functions - Decent modularization")
        elif func_count == 1:
            func_points = 2
            issues.append("Only 1 function - Could be more modular")
        else:
            lines_nonempty = len([ln for ln in code.splitlines() if ln.strip()])
            expect_functions = bool(r.get("expect_functions", False))
            prefer_concise = bool(r.get("prefer_concise", True))
            if expect_functions:
                func_points = 0
                issues.append(
                    "Đề bài gợi ý cần hàm (def) — chưa thấy hàm phù hợp"
                )
            elif re.search(r"\b(if|for|while|print)\b", code) and lines_nonempty >= 4:
                func_points = 2
                details.append("◐ Script có luồng điều khiển ở cấp module (+2)")
            elif _is_stdin_stdout_script(code):
                func_points = 2
                details.append("◐ Script stdin/stdout hoàn chỉnh — không bắt buộc def với bài ngắn (+2)")
            elif prefer_concise:
                func_points = 1
                details.append("◐ Rubric ưu tiên tối giản — script không def (+1)")
            else:
                func_points = 0
                issues.append("Chưa thấy hàm (def) — nên gom logic vào hàm rõ ràng")

        score += func_points
        metrics["functions"] = func_count
        details.append(f"Functions: {func_count} (+{func_points} pts)")

        # 2. Check classes (0-3 pts)
        class_count = len(analyzer.classes)
        if class_count >= 2:
            class_points = 3
            strengths.append(f"Good OOP design with {class_count} classes")
        elif class_count == 1:
            class_points = 2
            details.append(f"◐ {class_count} class - Some OOP used")
        else:
            class_points = 0
            if r.get("expect_classes", False):
                issues.append("◐ Đề gợi ý thiết kế OOP/class — chưa thấy class")
            else:
                details.append("◐ Không dùng class (bình thường với bài script nhỏ)")

        score += class_points
        metrics["classes"] = class_count
        details.append(f"Classes: {class_count} (+{class_points} pts)")
        
        # 3. Docstring — không trừ điểm thiếu chú thích (luôn trần điểm nhánh)
        doc_count = analyzer.docstrings_count
        doc_points = 4
        if doc_count > 0:
            details.append(f"◐ Có {doc_count} docstring (không ảnh hưởng điểm)")
        else:
            details.append("◐ Docstring: không bắt buộc (+4)")
        score += doc_points
        metrics["docstrings"] = doc_count
        details.append(f"Docstrings: {doc_count} (+{doc_points} pts)")
        
        # 4. Check naming conventions (0-4 pts)
        naming_points, naming_feedback = check_naming_conventions(code, r)
        score += naming_points
        metrics["naming"] = "good" if naming_points >= 3 else "poor"
        details.extend(naming_feedback)
        details.append(f"Naming: +{naming_points} pts")
        
        # 5. Check imports (0-2 pts)
        import_count = len(analyzer.imports)
        if import_count > 0:
            import_points = 2
            details.append(f"✓ Uses {import_count} import(s) (+2 pts)")
            metrics["imports"] = import_count
        else:
            import_points = 1
            details.append("◐ Không dùng import — bình thường với script chỉ thư viện chuẩn (+1)")
            metrics["imports"] = 0
        
        score += import_points
        
        # 6. Check code complexity (0-3 pts)
        lines = len(code.splitlines())
        prefer_c = bool(r.get("prefer_concise", True))
        if lines >= 20:
            complexity_points = 3
            strengths.append(f"Sufficient complexity ({lines} lines)")
        elif lines >= 10:
            complexity_points = 2
            details.append(f"◐ Moderate complexity ({lines} lines)")
        elif _is_stdin_stdout_script(code):
            complexity_points = 2
            details.append(f"◐ Script tối giản nhưng đủ I/O ({lines} dòng) (+2)")
        elif prefer_c and lines <= 8:
            complexity_points = 2
            details.append(f"◐ Rubric ưu tiên tối giản — ít dòng (+2)")
        elif lines >= 5:
            complexity_points = 1
            issues.append(f"Simple code ({lines} lines)")
        else:
            if prefer_c:
                complexity_points = 1
                details.append(f"◐ Rất ít dòng — phù hợp rubric tối giản (+1)")
            else:
                complexity_points = 0
                issues.append(f"Very simple ({lines} lines)")
        
        score += complexity_points
        metrics["lines"] = lines
        details.append(f"Complexity: +{complexity_points} pts")
        
        # Cap score at 20
        score = min(score, 20)
        score = max(score, 0)
        metrics["rubric_hints"] = r

        return {
            "score": score,
            "details": details,
            "issues": issues,
            "strengths": strengths if strengths else ["Code is functional"],
            "metrics": metrics,
            "summary": f"Structure score: {score}/20 - {len(strengths)} strengths, {len(issues)} issues"
        }
