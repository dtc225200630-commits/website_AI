"""
Code Analysis Agent - Static Source Code Analysis using AST

This agent performs deep static analysis of Python code without executing it.
It inspects:
- Function and class definitions
- Naming conventions
- Code modularity and organization
- Forbidden patterns
- Required constructs
- Code complexity metrics

Evaluation criteria (max 20 points, có tùy chỉnh theo rubric từng bài):
- Modularity / hàm (4 pts): ưu tiên def khi đề yêu cầu; bài lab ngắn + stdin/stdout được cộng thay thế
- Naming (4 pts): PEP 8; biến một chữ chấp nhận hơn khi rubric ưu tiên tối giản
- Imports (2 pts), Documentation (4 pts), Complexity (3 pts): độ dài ít trừ điểm hơn khi prefer_concise

Returns:
    dict with score (0-20), issues, strengths, and summary
"""

import ast
import re
from typing import Any, Dict, List, Optional, Tuple

from agents.rubric_hints import build_rubric_hints

# Import unified scoring schema
try:
    from scoring_schema import ScoringSchema
except ImportError:
    from .scoring_schema import ScoringSchema


class CodeAnalyzer(ast.NodeVisitor):
    """AST visitor for analyzing Python code structure."""
    
    def __init__(self):
        self.functions = []
        self.classes = []
        self.variables = []
        self.imports = []
        self.issues = []
        self.strengths = []
        self.docstrings_count = 0
        self.function_count = 0
        self.class_count = 0
        
    def visit_FunctionDef(self, node):
        """Visit function definitions."""
        self.functions.append({
            "name": node.name,
            "args": len(node.args.args),
            "lineno": node.lineno,
            "has_docstring": ast.get_docstring(node) is not None
        })
        if ast.get_docstring(node):
            self.docstrings_count += 1
        self.function_count += 1
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """Visit class definitions."""
        self.classes.append({
            "name": node.name,
            "methods": len([n for n in node.body if isinstance(n, ast.FunctionDef)]),
            "lineno": node.lineno,
            "has_docstring": ast.get_docstring(node) is not None
        })
        if ast.get_docstring(node):
            self.docstrings_count += 1
        self.class_count += 1
        self.generic_visit(node)
    
    def visit_Import(self, node):
        """Visit import statements."""
        for alias in node.names:
            self.imports.append({"module": alias.name, "type": "import"})
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Visit from...import statements."""
        for alias in node.names:
            self.imports.append({"module": f"from {node.module}", "type": "from"})
        self.generic_visit(node)
    
    def visit_Assign(self, node):
        """Visit variable assignments."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.variables.append({"name": target.id})
        self.generic_visit(node)


def analyze_code_structure(code: str) -> Tuple[CodeAnalyzer, List[str]]:
    """
    Parse and analyze code structure using AST.
    
    Args:
        code: Source code string
        
    Returns:
        Tuple of (analyzer object, parse errors list)
    """
    errors = []
    analyzer = CodeAnalyzer()
    
    try:
        tree = ast.parse(code)
        analyzer.visit(tree)
    except SyntaxError as e:
        errors.append(f"Lỗi cú pháp: {e.msg} (dòng {e.lineno})")
    except Exception as e:
        errors.append(f"Lỗi phân tích mã: {str(e)}")
    
    return analyzer, errors


def _module_ast_is_trivial(tree: ast.AST) -> bool:
    """
    True for almost-empty modules or a single meaningless top-level expression
    (e.g. bare `h`, a lone literal) — valid AST but not a real program.
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
    if isinstance(val, ast.Name):
        return True
    if isinstance(val, ast.Constant):
        return True
    if isinstance(val, ast.JoinedStr):
        return True
    return False


def _is_stdin_stdout_script(code: str) -> bool:
    """Bài lab thường là script: có input() và print() — coi là chương trình hoàn chỉnh dù ngắn."""
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
    analyzer: CodeAnalyzer, code: str, rubric: Dict[str, bool]
) -> Tuple[int, List[str], List[str]]:
    """
    Check PEP 8 naming conventions.
    
    Returns:
        Tuple of (score, issues, strengths)
    """
    score = 0
    issues = []
    strengths = []
    
    # Check function naming (snake_case)
    for func in analyzer.functions:
        if not re.match(r'^[a-z_][a-z0-9_]*$', func["name"]):
            issues.append(
                f"✗ Tên hàm «{func['name']}» chưa theo snake_case (chữ thường, gạch dưới giữa các từ)"
            )
        else:
            score += 0.5
    
    # Check class naming (PascalCase)
    for cls in analyzer.classes:
        if not re.match(r'^[A-Z][a-zA-Z0-9]*$', cls["name"]):
            issues.append(
                f"✗ Tên lớp «{cls['name']}» chưa theo PascalCase (chữ cái đầu mỗi từ viết hoa)"
            )
        else:
            score += 0.5
    
    # Check variable naming (do NOT award "good naming" when there are zero variables)
    prefer_concise = bool(rubric.get("prefer_concise", True))
    expect_functions = bool(rubric.get("expect_functions", False))
    single_letter_vars = [v for v in analyzer.variables if len(v["name"]) == 1]
    if single_letter_vars:
        ne = len(
            [
                ln
                for ln in code.splitlines()
                if ln.strip() and not ln.strip().startswith("#")
            ]
        )
        allow_short = (
            (not expect_functions)
            and analyzer.function_count == 0
            and analyzer.class_count == 0
            and len(single_letter_vars) <= 2
            and (_is_stdin_stdout_script(code) or (prefer_concise and ne <= 12))
        )
        if allow_short:
            score += 3
            strengths.append(
                "◐ Biến tên ngắn — chấp nhận được khi rubric ưu tiên code gọn / script nhỏ"
            )
        else:
            issues.append(f"✗ Có {len(single_letter_vars)} biến chỉ một ký tự — nên đặt tên gợi nghĩa")
    elif len(analyzer.variables) > 0:
        strengths.append("✓ Đặt tên biến theo quy ước tốt")
        score += 2
    elif analyzer.function_count or analyzer.class_count:
        strengths.append("◐ Chưa có biến module-level để đánh giá đặt tên; đã xem qua hàm/lớp")
        score += 1
    else:
        issues.append("✗ Chưa có hàm/lớp/biến rõ ràng để đánh giá đặt tên")

    return min(int(score), 4), issues, strengths


def check_modularity(
    analyzer: CodeAnalyzer, code: str, rubric: Dict[str, bool]
) -> Tuple[int, List[str], List[str]]:
    """
    Check code modularity and organization.
    
    Returns:
        Tuple of (score, issues, strengths)
    """
    score = 0
    issues = []
    strengths = []
    expect_functions = bool(rubric.get("expect_functions", False))
    prefer_concise = bool(rubric.get("prefer_concise", True))

    # Check for functions
    if analyzer.function_count > 0:
        score += 2
        strengths.append(
            f"✓ Mã được tách thành {analyzer.function_count} hàm (def) — cấu trúc rõ ràng"
        )
    elif expect_functions:
        issues.append(
            "✗ Đề bài gợi ý cần hàm (def) nhưng chưa thấy — nên tách logic thành hàm rõ ràng"
        )
    elif re.search(r"\b(if|for|while|with)\b", code) and len([l for l in code.splitlines() if l.strip()]) >= 4:
        score += 1
        strengths.append("◐ Logic ở cấp module — có thể tách hàm nếu bài dài hơn")
    elif _is_stdin_stdout_script(code):
        score += 2
        strengths.append(
            "✓ Script hoàn chỉnh (input + print) — không bắt buộc def với bài lab ngắn"
        )
    elif prefer_concise:
        score += 1
        strengths.append(
            "◐ Rubric bài ưu tiên tối giản — script không def vẫn chấp nhận được nếu đúng yêu cầu"
        )
    else:
        issues.append("✗ Chưa thấy hàm (def) — nên gom logic vào hàm rõ ràng")

    # Classes: bonus only; bài tập script thường không cần class
    if analyzer.class_count > 0:
        score += 2
        strengths.append(f"✓ Có {analyzer.class_count} class — OOP")
    elif len(code.splitlines()) > 60:
        issues.append("◐ Code dài nhưng chưa dùng class — cân nhắc OOP nếu phức tạp")

    return min(score, 4), issues, strengths


def check_documentation(analyzer: CodeAnalyzer) -> Tuple[int, List[str], List[str]]:
    """
    Docstring/chú thích không còn làm tiêu chí trừ điểm hay sinh cảnh báo —
    luôn cộng trần điểm nhánh này (bài tập thường không bắt buộc docstring).
    """
    return 4, [], []


def check_imports(analyzer: CodeAnalyzer) -> Tuple[int, List[str], List[str]]:
    """
    Check import organization.
    
    Returns:
        Tuple of (score, issues, strengths)
    """
    score = 0
    issues = []
    strengths = []
    
    if len(analyzer.imports) == 0:
        strengths.append("◐ Không dùng import — bình thường nếu chỉ cần thư viện chuẩn")
        return 1, issues, strengths
    
    # Check for standard library imports
    std_libs = {"os", "sys", "math", "re", "json", "time", "datetime", "csv", "random"}
    has_std_imports = any(any(lib in imp["module"] for lib in std_libs) for imp in analyzer.imports)
    
    if has_std_imports:
        score += 1
        strengths.append("✓ Có import từ thư viện chuẩn (stdlib)")
    
    # Check for organized imports
    import_types = set(imp["type"] for imp in analyzer.imports)
    if len(import_types) <= 2:
        score += 1
        strengths.append("✓ Cách sắp xếp import gọn, dễ đọc")
    
    return min(score, 2), issues, strengths


def check_complexity(
    analyzer: CodeAnalyzer, code: str, rubric: Dict[str, bool]
) -> Tuple[int, List[str], List[str]]:
    """
    Check code complexity metrics.
    
    Returns:
        Tuple of (score, issues, strengths)
    """
    score = 0
    issues = []
    strengths = []
    
    lines = code.split('\n')
    non_empty_lines = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
    prefer_concise = bool(rubric.get("prefer_concise", True))

    # Check line count
    if non_empty_lines >= 20:
        score += 2
        strengths.append(f"✓ Adequate code length ({non_empty_lines} lines)")
    elif non_empty_lines >= 10:
        score += 1
        issues.append(f"◐ Code is somewhat short ({non_empty_lines} lines)")
    elif _is_stdin_stdout_script(code):
        score += 2
        strengths.append("✓ Chương trình tối giản nhưng đủ luồng I/O (stdin/stdout)")
    elif prefer_concise and non_empty_lines <= 8:
        score += 2
        strengths.append(
            "✓ Rubric bài ưu tiên tối giản — ít dòng không bị trừ nếu logic rõ ràng"
        )
    elif non_empty_lines >= 5:
        score += 1
        issues.append(f"◐ Code is somewhat short ({non_empty_lines} lines)")
    else:
        if prefer_concise:
            score += 1
            strengths.append("◐ Rất ít dòng — phù hợp khi đề ưu tiên code gọn")
        else:
            issues.append(f"✗ Code is too short ({non_empty_lines} lines)")
    
    # Check for control flow complexity
    has_loops = "for " in code or "while " in code
    has_conditionals = "if " in code or "else:" in code
    
    complexity_points = sum([1 for cond in [has_loops, has_conditionals] if cond])
    score += min(complexity_points, 1)
    
    if has_loops or has_conditionals:
        strengths.append("✓ Có luồng điều khiển rõ (if / for / while)")
    
    return min(score, 3), issues, strengths


def code_analysis_agent(
    code: str, rubric: Optional[Dict[str, bool]] = None
) -> Dict[str, Any]:
    """
    Main code analysis agent: Perform static source code analysis.
    
    This agent analyzes code structure without executing it, providing
    feedback on code quality, organization, and best practices.
    
    Args:
        code: Source code string to analyze
        rubric: Gợi ý từ build_rubric_hints (title/description/requirements); None = mặc định lab
        
    Returns:
        dict with:
            - score: 0-20 points
            - issues: List of issues found
            - strengths: List of strengths identified
            - summary: Overall assessment
            - details: Detailed analysis breakdown
            - metrics: Code metrics
    """
    r = rubric if rubric is not None else build_rubric_hints()
    
    # Parse the code
    analyzer, parse_errors = analyze_code_structure(code)

    # If code cannot be parsed, return low score
    if parse_errors:
        return {
            "score": 0,
            "issues": parse_errors,
            "strengths": [],
            "summary": "Phân tích thất bại — cần sửa lỗi cú pháp trước",
            "details": parse_errors,
            "metrics": {},
        }

    try:
        trivial_tree = ast.parse(code)
    except SyntaxError:
        trivial_tree = None
    if trivial_tree is not None and _module_ast_is_trivial(trivial_tree):
        return {
            "score": 0,
            "issues": [
                "Mã quá ngắn hoặc không phải chương trình hoàn chỉnh (ví dụ chỉ một biểu thức lẻ)."
            ],
            "strengths": [],
            "summary": "Phân tích: không áp dụng — cần chương trình có cấu trúc (hàm, gán, điều khiển luồng...)",
            "details": [
                "AST hợp lệ nhưng chỉ là biểu thức/module rỗng — không chấm rubric chi tiết."
            ],
            "metrics": {},
        }

    # Perform analysis checks
    all_scores = []
    all_issues = []
    all_strengths = []
    
    # 1. Naming conventions (4 pts max)
    naming_score, naming_issues, naming_strengths = check_naming_conventions(analyzer, code, r)
    all_scores.append(naming_score)
    all_issues.extend(naming_issues)
    all_strengths.extend(naming_strengths)
    
    # 2. Modularity (4 pts max)
    modularity_score, modularity_issues, modularity_strengths = check_modularity(analyzer, code, r)
    all_scores.append(modularity_score)
    all_issues.extend(modularity_issues)
    all_strengths.extend(modularity_strengths)
    
    # 3. Documentation (4 pts max)
    doc_score, doc_issues, doc_strengths = check_documentation(analyzer)
    all_scores.append(doc_score)
    all_issues.extend(doc_issues)
    all_strengths.extend(doc_strengths)
    
    # 4. Imports (2 pts max)
    import_score, import_issues, import_strengths = check_imports(analyzer)
    all_scores.append(import_score)
    all_issues.extend(import_issues)
    all_strengths.extend(import_strengths)
    
    # 5. Complexity (3 pts max)
    complexity_score, complexity_issues, complexity_strengths = check_complexity(analyzer, code, r)
    all_scores.append(complexity_score)
    all_issues.extend(complexity_issues)
    all_strengths.extend(complexity_strengths)
    
    # Calculate final score (max 20)
    # 4 + 4 + 4 + 2 + 3 = 17, so normalize to 20
    total_analysis_score = sum(all_scores)
    normalized_score = min(int(total_analysis_score * 20 / 17), 20)
    
    # Build result
    return {
        "score": normalized_score,
        "issues": all_issues if all_issues else ["Không phát hiện vấn đề nghiêm trọng"],
        "strengths": all_strengths if all_strengths else ["Cấu trúc mã ổn định"],
        "summary": f"Điểm phân tích: {normalized_score}/20 — "
        + (
            "chất lượng mã rất tốt"
            if normalized_score >= 18
            else "chất lượng mã tốt"
            if normalized_score >= 16
            else "chất lượng mã chấp nhận được"
            if normalized_score >= 14
            else "mã cần cải thiện thêm"
        ),
        "details": {
            "naming_conventions": naming_score,
            "modularity": modularity_score,
            "documentation": doc_score,
            "imports": import_score,
            "complexity": complexity_score
        },
        "metrics": {
            "function_count": analyzer.function_count,
            "class_count": analyzer.class_count,
            "import_count": len(analyzer.imports),
            "docstring_count": analyzer.docstrings_count,
            "variable_count": len(analyzer.variables),
            "rubric_hints": r,
        }
    }


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = ["code_analysis_agent", "CodeAnalyzer"]
