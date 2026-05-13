"""
Requirement Verification Agent - Database-Driven, LLM-Enhanced, Snippet-Aware

This agent checks if code meets requirements and understands code snippets.
For snippets with correct logic but missing boilerplate, it gives partial credit.
"""

import ast
import re
import os
import json
from typing import Dict, List

# Import unified scoring schema
try:
    from scoring_schema import ScoringSchema
except ImportError:
    from .scoring_schema import ScoringSchema

# Try to import Google Generative AI for smart validation (model fallback on generateContent)
try:
    import google.generativeai as genai
    genai_available = True

    api_key = os.getenv("GEMINI_API_KEY", "AIzaSyCBbeAHpaIyuwC6abeRypiaB_1BfGWjOCg")
    genai.configure(api_key=api_key)

    try:
        from gemini_utils import generate_content_with_fallback
    except ImportError:
        from .gemini_utils import generate_content_with_fallback

    print("[RequirementAgent] Gemini configured; model resolved per LLM request (GOOGLE_MODEL_CANDIDATES).")
except Exception as e:
    print(f"[RequirementAgent] WARNING: LLM unavailable - using regex fallback ({type(e).__name__})")
    genai_available = False
    generate_content_with_fallback = None  # type: ignore


def _requirement_gemini_llm_enabled() -> bool:
    """Tat bang GEMINI_DISABLE_REQUIREMENT_LLM=1 de tiet kiem 1 lan goi API / bai (free tier)."""
    return os.getenv("GEMINI_DISABLE_REQUIREMENT_LLM", "").strip().lower() not in (
        "1",
        "true",
        "yes",
        "on",
    )


def _module_ast_is_trivial(tree: ast.AST) -> bool:
    """
    Một module rỗng hoặc một biểu thức lẻ (Name/Constant/f-string) — không phải chương trình.
    Trùng logic với code_analysis_agent để các agent nhất quán.
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


def is_cpp_snippet(code: str) -> bool:
    """Detect if code is a C++ snippet (missing main or includes)."""
    # If it has main() or #include, it's a full program
    if 'main' in code or '#include' in code:
        return False
    # But if it has C++ syntax, it's a snippet
    if any(pattern in code for pattern in ['cout', 'cin', 'vector', 'if (', 'else {', '<<', '>>']):
        return True
    return False


def requirement_agent(code: str, requirements: List[Dict] = None, requirements_dict: Dict = None) -> Dict:
    """
    Verify if code meets assignment requirements.
    
    Snippet-aware: If code is a snippet with correct logic, give partial credit.
    
    Args:
        code: Student's submitted code
        requirements: List of dicts with 'requirement_text' and 'weight' from DB
        requirements_dict: Alternative dict format from app.py
    
    Returns:
        dict containing score, details, met/missing lists.
    """
    if requirements_dict:
        reqs = []
        for _, req_list in requirements_dict.items():
            reqs.extend(req_list)
        requirements = reqs
    
    if not requirements:
        requirements = []
    
    total_requirements = len(requirements)
    is_snippet = is_cpp_snippet(code)
    
    if total_requirements == 0:
        return {
            "score": 20,
            "fulfilled": 0,
            "total": 0,
            "details": ["Không có yêu cầu cụ thể nào được cung cấp."],
            "requirements_met": [],
            "requirements_missing": [],
            "summary": "Không có yêu cầu để kiểm tra"
        }

    # Extract only the texts
    req_texts = []
    for req in requirements:
        txt = req.get("requirement_text", "").strip()
        if txt:
            req_texts.append(txt)
            
    total_requirements = len(req_texts)
    if total_requirements == 0:
        return {
            "score": 20,
            "fulfilled": 0,
            "total": 0,
            "details": ["Không có yêu cầu cụ thể nào được cung cấp."],
            "requirements_met": [],
            "requirements_missing": [],
            "summary": "Không có yêu cầu để kiểm tra"
        }

    # Mã Python hợp lệ nhưng chỉ là biểu thức rác (vd. `h`, `42`) — không đối chiếu yêu cầu / LLM
    try:
        _trivial_tree = ast.parse(code)
    except SyntaxError:
        _trivial_tree = None
    if _trivial_tree is not None and _module_ast_is_trivial(_trivial_tree):
        return {
            "score": 0,
            "fulfilled": 0,
            "total": total_requirements,
            "fulfilled_count": 0,
            "total_count": total_requirements,
            "details": [
                "Mã không đủ nội dung để kiểm tra yêu cầu (ví dụ chỉ một biểu thức / ký tự lẻ).",
                f"0/{total_requirements} yêu cầu đạt.",
            ],
            "requirements_met": [],
            "requirements_missing": list(req_texts),
            "unfulfilled": list(req_texts),
            "summary": f"Yêu cầu: 0/{total_requirements} — cần chương trình có lệnh gán, hàm hoặc luồng điều khiển",
            "is_snippet": is_snippet,
        }

    llm_results = {}
    used_llm = False
    
    # 1) Try using Gemini to accurately check requirements (optional off to save quota)
    if genai_available and generate_content_with_fallback and _requirement_gemini_llm_enabled():
        req_list_str = "\n".join([f"{i+1}. {txt}" for i, txt in enumerate(req_texts)])
        prompt = f"""
Là một hệ thống chấm code tự động, hãy kiểm tra xem đoạn code sau (có thể là Python hoặc C++) có đáp ứng các yêu cầu không.
CHẤP NHẬN code snippet: nếu code thiếu main() hay include nhưng logic đúng, vẫn là PASS.

TRẢ LỜI ĐÚNG ĐỊNH DẠNG JSON (với key là số thứ tự yêu cầu như là string, value là boolean true nếu đáp ứng hoặc false).
KHÔNG thêm bất kỳ block code hay giải thích nào khác.

Format:
{{
  "1": true,
  "2": false
}}

Code:
```
{code}
```

Yêu cầu:
{req_list_str}
"""
        try:
            response, _used_model = generate_content_with_fallback(prompt)
            # Find JSON block
            text = response.text
            match = re.search(r'\{(?:[^{}]|(?(?=\{).*?\}))*\}', text, re.DOTALL)
            if match:
                llm_results = json.loads(match.group(0))
                used_llm = True
        except Exception:
            llm_results = {}
            used_llm = False

    code_lower = code.lower()
    lines = code.split('\n')
    
    fulfilled = 0
    requirements_met = []
    requirements_missing = []
    debug_info = []
    
    # 2) Process each requirement
    for i, req_text in enumerate(req_texts):
        idx_str = str(i + 1)
        
        is_met = False
        method = "Fallback"
        
        if used_llm and idx_str in llm_results:
            llm_met = bool(llm_results[idx_str])
            fallback_met = check_requirement(code, code_lower, lines, req_text)
            # Hybrid decision: trust deterministic checks when LLM misses obvious patterns.
            is_met = llm_met or fallback_met
            method = "LLM+Fallback"
        else:
            is_met = check_requirement(code, code_lower, lines, req_text)
            
        debug_info.append(f"  [{method}] '{req_text}': {'MET' if is_met else 'NOT MET'}")
        
        if is_met:
            fulfilled += 1
            requirements_met.append(req_text)
        else:
            requirements_missing.append(req_text)
    
    # 3) Scoring using unified schema
    fulfillment_rate = fulfilled / total_requirements if total_requirements > 0 else 0
    
    # Use proportional scoring: (fulfilled/total) * 20
    score = ScoringSchema.proportional_score(fulfilled, total_requirements)
    
    details = [
        f"Kiểm tra yêu cầu: {fulfilled}/{total_requirements} đạt ({fulfillment_rate*100:.0f}%)",
        f"Điểm: {score}/20"
    ]
    
    if is_snippet:
        details.insert(0, "⚠ Code snippet phát hiện - không cần wrapper đầy đủ")
    
    if used_llm:
        details.append("✓ Sử dụng mô hình LLM chuyên sâu để phân tích mã và yêu cầu.")
    
    details.extend(debug_info)
    
    if requirements_met:
        details.append(f"Đạt ({len(requirements_met)}): {', '.join(requirements_met[:3])}")
    
    if requirements_missing:
        details.append(f"Chưa đạt ({len(requirements_missing)}): {', '.join(requirements_missing[:3])}")
    
    summary = f"Đạt {fulfilled}/{total_requirements} yêu cầu. Điểm: {score}/20"
    
    return {
        "score": score,
        "fulfilled_count": fulfilled,
        "total_count": total_requirements,
        "details": details,
        "requirements_met": requirements_met,
        "requirements_missing": requirements_missing,
        "unfulfilled": requirements_missing,
        "summary": summary,
        "is_snippet": is_snippet
    }

def _code_has_string_reversal(code: str, code_lower: str) -> bool:
    """
    Nhan dien logic dao chuoi: [::-1], reversed()+join, vong lap range(len(s)-1,-1,-1), v.v.
    """
    compact = re.sub(r"\s+", "", code)
    cl = re.sub(r"\s+", " ", code_lower)
    if "[::-1]" in compact:
        return True
    if "reversed(" in cl:
        return True
    # for i in range(len(s) - 1, -1, -1): ... (nhieu bien the khoang trang)
    if re.search(
        r"range\s*\(\s*len\s*\([^)]+\)\s*-\s*1\s*,\s*-?\s*1\s*,\s*-?\s*1\s*\)",
        cl,
    ):
        return True
    if re.search(r"range\s*\(\s*len\s*\([^)]+\)\s*-\s*1\s*,\s*-1\s*,\s*-1\s*\)", cl):
        return True
    # while i >= 0 / -= 1 ket hop truy cap chuoi (dao thu cong)
    if "while" in cl and "len(" in cl and ("-1" in code or "- 1" in code):
        if any(x in cl for x in ("[i]", "[j]", "[k]", "s[", "str[", "ch[", "line[")):
            if "+=" in cl or "= s[" in cl or "=s[" in compact or "+= s[" in cl:
                return True
    return False


def _code_avoids_builtin_reverse_helpers(code: str, code_lower: str) -> bool:
    """
    Yeu cau kieu 'khong dung reverse co san': chan .reverse() list va reversed().
    Cho phep [::-1] (cu phap slicing, khong phai goi ham reverse).
    """
    if re.search(r"\.\s*reverse\s*\(", code_lower):
        return False
    if re.search(r"\breversed\s*\(", code_lower):
        return False
    return True


def contains_any(text: str, keywords: List[str]) -> bool:
    return any(keyword.lower() in text.lower() for keyword in keywords)


def _code_handles_factorial_zero_base_case(code: str, code_lower: str) -> bool:
    """
    Giai thừa(0)=1: chấp nhận mọi tên biến (n, number, x...).
    - if <id> == 0: ... print(1) / return 1
    - if <id> <= 1: return 1 (0! và 1!)
    """
    if re.search(r"\bif\s+\w+\s*==\s*0\s*:", code):
        if re.search(r"print\s*\(\s*1\s*\)", code_lower) or re.search(r"\breturn\s+1\b", code_lower):
            return True
    if re.search(r"\bif\s+\w+\s*<=\s*1\s*:", code):
        if re.search(r"\breturn\s+1\b", code_lower):
            return True
    return False


def _requirement_is_factorial_zero_edge(requirement_lower: str) -> bool:
    """Yêu cầu dạng 'n=0 kết quả 1', xử lý 0!, v.v. (tiếng Việt / Anh)."""
    if re.search(r"\bn\s*=\s*0\b", requirement_lower):
        return True
    if "n=0" in requirement_lower.replace(" ", ""):
        return True
    if contains_any(requirement_lower, ["0!", "0 !", "giai thừa của 0", "giai thua cua 0"]):
        return True
    if contains_any(requirement_lower, ["bằng 0", "bang 0", "bang0"]) and contains_any(
        requirement_lower,
        ["giai thừa", "giai thua", "factorial", "kết quả", "ket qua", "ketqua", "một", "mot ", " 1)"],
    ):
        return True
    if contains_any(requirement_lower, ["trường hợp", "truong hop", "xử lý", "xu ly"]) and (
        "0" in requirement_lower and ("1" in requirement_lower or "một" in requirement_lower or "mot" in requirement_lower)
    ):
        return True
    return False


def _requirement_is_prime_check_function(requirement_lower: str) -> bool:
    return contains_any(requirement_lower, ["nguyên tố", "nguyen to", "prime"]) and contains_any(
        requirement_lower, ["hàm", "ham", "function", "def"]
    )


def _code_has_prime_predicate_function(code: str, code_lower: str) -> bool:
    if "def " not in code_lower:
        return False
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            src = ast.get_source_segment(code, node)
            if not src:
                continue
            tl = src.lower()
            if "%" in src or "range(" in tl or "while " in tl:
                if "return" in tl:
                    return True
    return False


def _requirement_is_prime_yes_no_output(requirement_lower: str) -> bool:
    return contains_any(requirement_lower, ["yes", "no"]) and contains_any(
        requirement_lower, ["output", "xuất", "xuat", "in ra", "in \"", "logic", "nguyên tố", "nguyen to"]
    )


def _code_prints_yes_no_prime(code_lower: str) -> bool:
    if "print(" not in code_lower:
        return False
    return ('"yes"' in code_lower or "'yes'" in code_lower) and ('"no"' in code_lower or "'no'" in code_lower)


def _requirement_is_prime_edge_n_leq_1(requirement_lower: str) -> bool:
    if "edge" in requirement_lower and ("n" in requirement_lower and ("<=" in requirement_lower or "<" in requirement_lower)):
        return True
    if re.search(r"n\s*<=\s*1", requirement_lower):
        return True
    if re.search(r"n\s*<\s*2", requirement_lower):
        return True
    return False


def _code_handles_prime_small_n(code: str, code_lower: str) -> bool:
    if re.search(r"\bn\s*<=\s*1\b", code_lower):
        return True
    if re.search(r"\bn\s*<\s*2\b", code_lower):
        return True
    if re.search(r"\bif\s+n\s*<=\s*1\s*:", code_lower):
        return True
    if re.search(r"\bif\s+n\s*<\s*2\s*:", code_lower):
        return True
    return False


def check_requirement(code: str, code_lower: str, lines: List[str], requirement: str) -> bool:
    """Fallback basic matching for requirements if LLM is unavailable."""
    requirement_lower = requirement.lower()

    if _requirement_is_prime_check_function(requirement_lower):
        return _code_has_prime_predicate_function(code, code_lower)

    if _requirement_is_prime_yes_no_output(requirement_lower):
        return _code_prints_yes_no_prime(code_lower)

    if _requirement_is_prime_edge_n_leq_1(requirement_lower):
        return _code_handles_prime_small_n(code, code_lower)

    # Giai thừa: xử lý 0 → 1 (yêu cầu SQL thường nói "n = 0" nhưng sinh viên đặt tên number, v.v.)
    if _requirement_is_factorial_zero_edge(requirement_lower):
        return _code_handles_factorial_zero_base_case(code, code_lower)

    # --- Bai dao nguoc chuoi (reverse string) ---
    if contains_any(requirement_lower, ["không", "khong", "ko"]) and contains_any(
        requirement_lower, ["reverse", "đảo", "dao"]
    ):
        if contains_any(
            requirement_lower,
            ["thư viện", "thu vien", "library", "có sẵn", "co san", "built-in", "builtin", "sẵn"],
        ):
            return _code_avoids_builtin_reverse_helpers(code, code_lower)

    if contains_any(requirement_lower, ["đảo ngược", "dao nguoc"]) or (
        "reverse" in requirement_lower
        and contains_any(requirement_lower, ["chuỗi", "chuoi", "string", "str"])
    ):
        if contains_any(requirement_lower, ["đầu vào", "dau vao", "input", "stdin", "nhập", "nhap"]):
            if _code_has_string_reversal(code, code_lower):
                return True
        if contains_any(requirement_lower, ["output", "xuất", "xuat", "in ra", "print"]):
            if "print(" in code_lower and _code_has_string_reversal(code, code_lower):
                return True
        if contains_any(requirement_lower, ["code", "chương trình", "chuong trinh", "phải", "phai"]):
            if _code_has_string_reversal(code, code_lower):
                return True

    if contains_any(requirement_lower, ["input", "nhập", "read"]):
        if any(pattern in code_lower for pattern in ["input", "stdin", "sys.stdin"]):
            return True
            
    if contains_any(requirement_lower, ["tính toán", "calculate", "phép cộng", "cong", "addition"]):
        if re.findall(r'[+\-*/]', code): return True
        
    if contains_any(requirement_lower, ["vòng lặp", "vong lap", "loop", "for", "while"]):
        if contains_any(code_lower, ["for ", "while "]): return True

    # Explicit detection for range() requirements (accented and non-accented text).
    if contains_any(requirement_lower, ["range", "hàm range", "ham range", "range()"]):
        if "range(" in code_lower:
            return True
        
    if contains_any(requirement_lower, ["hàm", "ham", "function", "def "]):
        if contains_any(code_lower, ["def "]): return True

    if contains_any(requirement_lower, ["hằng số pi", "pi ="]):
        if "3.14" in code or "math.pi" in code_lower: return True
        
    if contains_any(requirement_lower, ["ép kiểu", "float", "int"]):
        if "float(" in code or "int(" in code: return True

    # Tiếng Việt: "số âm và số thực" / negative + floating-point — logic dùng float() + so sánh là đủ.
    if contains_any(requirement_lower, ["số âm", "so am", "so âm", "âm và", "so am va"]):
        if contains_any(
            requirement_lower,
            ["số thực", "so thuc", "thực", "thuc", "thập phân", "thap phan", "float"],
        ):
            if "float(" in code_lower:
                return True

    if contains_any(requirement_lower, ["print", "in ", "xuất"]):
        if "print(" in code: return True

    # Diện tích hình tròn: yêu cầu dạng "S = 3.14 * r * r" — từ khóa mặc định (ASCII >2 ký tự)
    # không trích được từ câu tiếng Việt → tránh báo NOT MET sai.
    if "3.14" in requirement_lower and "*" in requirement_lower and (
        "r" in requirement_lower
        or "bán kính" in requirement_lower
        or "ban kinh" in requirement_lower
    ) and contains_any(
        requirement_lower,
        ["công thức", "cong thuc", "diện tích", "dien tich", "hình tròn", "hinh tron", "tròn", "tron", "tính", "tinh"],
    ):
        compact = re.sub(r"\s+", "", code_lower)
        if "3.14*r*r" in compact or re.search(r"3\.14\*r\*r", compact):
            return True
        if "math.pi" in compact and "*r*r" in compact:
            return True

    if contains_any(requirement_lower, ["toán tử %", "modulo", "operator %", "%"]):
        if "%" in code and any(op in requirement_lower for op in ["modulo", "toán tử", "operator"]):
            return True
        if re.search(r'\w+\s*%\s*\w+', code):  # Pattern: something % something
            return True
    
    if contains_any(requirement_lower, ["if...else", "if...else", "if else", "cấu trúc if"]):
        if re.search(r'\bif\b.*:\s*\n.*\belse\b.*:', code, re.DOTALL | re.MULTILINE):
            return True
        if "else:" in code and "if " in code:
            return True
        
    # Default matching ratio — tránh khớp nhầm trên mã cực ngắn / không liên quan
    keywords = list(set([w for w in re.findall(r'\b[a-zA-Z_]\w*\b', requirement_lower) if len(w) > 2]))
    if not keywords:
        return False
    if len(keywords) < 3 or len(code.strip()) < 12:
        return False

    matches = sum(1 for kw in keywords if kw in code_lower)
    if matches >= len(keywords) * 0.7:
        return True

    return False
