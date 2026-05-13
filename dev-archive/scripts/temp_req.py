"""
Requirement Verification Agent - Database-Driven and LLM-Enhanced

This agent checks if submitted code meets assignment requirements that are
stored in the database. It primarily uses LLM to smartly evaluate the requirements,
falling back to hardcoded regex/patterns.
"""

import re
import os
import json
from typing import Dict, List

# Try to import Google Generative AI for smart validation
try:
    import google.generativeai as genai
    genai_available = True
    
    api_key = os.getenv("GEMINI_API_KEY", "AIzaSyCBbeAHpaIyuwC6abeRypiaB_1BfGWjOCg")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash-lite")
except ImportError:
    genai_available = False
    model = None


def requirement_agent(code: str, requirements: List[Dict] = None, requirements_dict: Dict = None) -> Dict:
    """
    Verify if code meets assignment requirements from database.
    
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

    llm_results = {}
    used_llm = False
    
    # 1) Try using Gemini to accurately check requirements
    if genai_available and model:
        req_list_str = "\n".join([f"{i+1}. {txt}" for i, txt in enumerate(req_texts)])
        prompt = f"""
Là một hệ thống chấm code tự động, hãy kiểm tra xem đoạn code Python sau có đáp ứng các yêu cầu không.

TRẢ LỜI ĐÚNG ĐỊNH DẠNG JSON (với key là số thứ tự yêu cầu như là string, value là boolean true nếu đáp ứng hoặc false nếu KHÔNG).
KHÔNG thêm bất kỳ block code hay giải thích nào khác.

Bắt buộc trả về format:
{{
  "1": true,
  "2": false
}}

Code cần kiểm tra:
```python
{code}
```

Các yêu cầu:
{req_list_str}
"""
        try:
            response = model.generate_content(prompt)
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
            is_met = bool(llm_results[idx_str])
            method = "LLM"
        else:
            is_met = check_requirement(code, code_lower, lines, req_text)
            
        debug_info.append(f"  [{method}] '{req_text}': {'MET' if is_met else 'NOT MET'}")
        
        if is_met:
            fulfilled += 1
            requirements_met.append(req_text)
        else:
            requirements_missing.append(req_text)
    
    # 3) Scoring
    fulfillment_rate = fulfilled / total_requirements
    score = min(20, int(fulfillment_rate * 20))
    
    details = [
        f"Kiểm tra yêu cầu: {fulfilled}/{total_requirements} đạt ({fulfillment_rate*100:.0f}%)",
        f"Điểm: {score}/20"
    ]
    
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
        "fulfilled": fulfilled,
        "total": total_requirements,
        "details": details,
        "requirements_met": requirements_met,
        "requirements_missing": requirements_missing,
        "summary": summary
    }

def check_requirement(code: str, code_lower: str, lines: List[str], requirement: str) -> bool:
    """Fallback basic matching for requirements if LLM is unavailable."""
    requirement_lower = requirement.lower()
    
    if contains_any(requirement_lower, ["input", "nhập", "read"]):
        if any(pattern in code_lower for pattern in ["input", "stdin", "sys.stdin"]):
            return True
            
    if contains_any(requirement_lower, ["tính toán", "calculate"]):
        if re.findall(r'[+\-*/]', code): return True
        
    if contains_any(requirement_lower, ["vòng lặp", "loop", "for", "while"]):
        if contains_any(code_lower, ["for ", "while "]): return True
        
    if contains_any(requirement_lower, ["hàm", "function", "def "]):
        if contains_any(code_lower, ["def "]): return True

    if contains_any(requirement_lower, ["hằng số pi", "pi ="]):
        if "3.14" in code or "math.pi" in code_lower: return True
        
    if contains_any(requirement_lower, ["ép kiểu", "float", "int"]):
        if "float(" in code or "int(" in code: return True

    if contains_any(requirement_lower, ["print", "in ", "xuất"]):
        if "print(" in code: return True
        
    # Default matching ratio
    keywords = list(set([w for w in re.findall(r'\b[a-zA-Z_]\w*\b', requirement_lower) if len(w) > 2]))
    if not keywords: return False
    
    matches = sum(1 for kw in keywords if kw in code_lower)
    if matches >= len(keywords) * 0.7:
        return True

    return False

def contains_any(text: str, keywords: List[str]) -> bool:
    return any(keyword.lower() in text.lower() for keyword in keywords)
