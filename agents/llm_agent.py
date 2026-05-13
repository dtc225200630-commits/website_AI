import json
import os
import re

# Import unified scoring schema
try:
    from scoring_schema import ScoringSchema, ScoringConsistencyChecker
    from llm_alignment import (
        align_llm_output,
        compute_evaluation_truth,
        format_ground_truth_block,
        llm_support_score_when_unavailable,
    )
except ImportError:
    from .scoring_schema import ScoringSchema, ScoringConsistencyChecker
    from .llm_alignment import (
        align_llm_output,
        compute_evaluation_truth,
        format_ground_truth_block,
        llm_support_score_when_unavailable,
    )

# Try to import Google Generative AI (model is picked at request time via gemini_utils fallback)
try:
    import google.generativeai as genai

    genai_available = True

    api_key = os.getenv("GEMINI_API_KEY", "AIzaSyDCahVHEdTF3p9TF46dI_b2_POzEes3B-c")
    genai.configure(api_key=api_key)

    try:
        from gemini_utils import generate_content_with_fallback
    except ImportError:
        from .gemini_utils import generate_content_with_fallback

    print("[LLM Agent] Gemini configured; model resolved on first generateContent (see GOOGLE_MODEL_CANDIDATES).")
except Exception as e:
    print(f"[LLM Agent] WARNING: LLM unavailable ({type(e).__name__}). Using fallback.")
    genai_available = False
    generate_content_with_fallback = None  # type: ignore


def _normalize_requirement_item(item):
    """Support both tuple/list and dict requirement formats."""
    if isinstance(item, dict):
        req_text = str(item.get("requirement_text", "") or item.get("requirement", "")).strip()
        weight = item.get("weight", 1)
        return req_text, weight

    if isinstance(item, (list, tuple)):
        req_text = str(item[0]).strip() if len(item) > 0 else ""
        weight = item[1] if len(item) > 1 else 1
        return req_text, weight

    return "", 1


def _format_requirements(requirements):
    if not requirements:
        return "\n(Khong co yeu cau cu the)"

    normalized_requirements = []
    for item in requirements:
        req, weight = _normalize_requirement_item(item)
        if req:
            normalized_requirements.append((req, weight))

    if not normalized_requirements:
        return "\n(Khong co yeu cau cu the)"

    req_text = "\n=== YEU CAU BAI TAP ==="
    for i, (req, weight) in enumerate(normalized_requirements, 1):
        req_text += f"\n{i}. {req} (trong so: {weight})"
    return req_text


def _format_agent_context(agent_results):
    if not agent_results:
        return "\n(Khong co ket qua tu cac agents)"

    agent_context = "\n=== KET QUA TU CAC AGENT ==="

    try:
        syntax = agent_results.get("syntax", {}) if isinstance(agent_results.get("syntax"), dict) else {}
        if syntax:
            syntax_feedback = (
                syntax.get("feedback")
                or syntax.get("summary")
                or ("Pass" if syntax.get("success") else "Fail")
            )
            agent_context += f"\n- Syntax: {syntax_feedback}"
            if syntax.get("error"):
                agent_context += f" [LOI: {syntax['error']}]"
    except Exception:
        pass

    try:
        requirement = (
            agent_results.get("requirement", {})
            if isinstance(agent_results.get("requirement"), dict)
            else {}
        )
        if requirement:
            fulfilled_count = requirement.get("fulfilled_count", requirement.get("fulfilled", 0))
            total_count = requirement.get("total_count", requirement.get("total", 0))
            req_status = "DAT" if total_count and fulfilled_count == total_count else "CHUA DAT HET"
            agent_context += f"\n- Yeu cau: {req_status} ({fulfilled_count}/{total_count})"

            missing_requirements = (
                requirement.get("requirements_missing")
                or requirement.get("unfulfilled")
                or []
            )
            if missing_requirements:
                missing_text = ", ".join(str(x) for x in missing_requirements[:3])
                agent_context += f" - Thieu: {missing_text}"
    except Exception:
        pass

    try:
        test = agent_results.get("test", {}) if isinstance(agent_results.get("test"), dict) else {}
        if test:
            passed_count = test.get("passed_count", 0)
            total_tests = test.get("total_tests", test.get("total_count", 0))
            agent_context += f"\n- Test: {passed_count}/{total_tests} passed"
            if test.get("summary"):
                agent_context += f" - {test['summary']}"

            failed_tests = [
                tr
                for tr in (test.get("test_results", []) or [])
                if tr.get("status") in {"FAIL", "ERROR", "TIMEOUT", "COMPILE_ERROR"}
            ]
            if failed_tests:
                agent_context += (
                    "\n=== BANG TEST THAT BAI (NGUON SU THAT TU TESTAGENT — BAT BUOC KHOP expected_full KHI SUA) ==="
                )
                for tr in failed_tests[:15]:
                    tno = tr.get("test_no", "?")
                    st = tr.get("status", "")
                    inp_f = tr.get("input_full")
                    if inp_f is None:
                        inp_f = tr.get("input", "")
                    exp_f = tr.get("expected_full")
                    if exp_f is None:
                        exp_f = tr.get("expected", "")
                    act_f = tr.get("actual_full")
                    if act_f is None:
                        act_f = tr.get("actual", "")
                    agent_context += f"\n--- Test #{tno} | {st} ---"
                    agent_context += f"\n  input (stdin): {repr(inp_f)[:1200]}"
                    agent_context += f"\n  expected_output (phai khop stdout): {repr(exp_f)[:1200]}"
                    agent_context += f"\n  actual_output (stdout hoac loi): {repr(act_f)[:1200]}"
                    for key in ("stderr_full", "stderr_note"):
                        if tr.get(key):
                            agent_context += f"\n  {key}: {repr(tr.get(key))[:600]}"
                            break
    except Exception:
        pass

    try:
        structure = (
            agent_results.get("structure", {})
            if isinstance(agent_results.get("structure"), dict)
            else {}
        )
        if structure:
            agent_context += f"\n- Cau truc: {structure.get('summary', 'Khong co thong tin')}"
    except Exception:
        pass

    try:
        code_analysis = (
            agent_results.get("code_analysis", {})
            if isinstance(agent_results.get("code_analysis"), dict)
            else {}
        )
        if code_analysis and code_analysis.get("issues"):
            issues_preview = "; ".join(str(x) for x in code_analysis["issues"][:3])
            agent_context += f"\n- Van de phat hien: {issues_preview}"
    except Exception:
        pass

    return agent_context


def llm_agent(code, requirements=None, agent_results=None):
    """
    LLM agent: AI-based code review using Google Gemini.

    Receives full context to provide targeted feedback:
    - Code: Student's submission
    - Requirements: Assignment specification
    - Agent results: Syntax, test, requirement validation results

    Returns:
        dict with score (0-20), feedback, and detailed suggestions
    """

    if not genai_available or generate_content_with_fallback is None:
        return {
            "score": 10,
            "feedback": "LLM review unavailable - google.generativeai not installed",
            "details": ["To enable LLM review, run: pip install google-generativeai"],
        }

    req_text = _format_requirements(requirements)
    agent_context = _format_agent_context(agent_results)
    truth = compute_evaluation_truth(agent_results)
    truth_block = format_ground_truth_block(truth)

    prompt = f"""{req_text}
{truth_block}
{agent_context}

Muc tieu phan hoi:
1) Ngan gon nhung trung van de chinh.
2) Dua vao ket qua agents: neu test fail thi chi ra loi logic; neu requirement khong dat thi giai thich tai sao.
3) Uu tien loi anh huong tinh dung dan truoc (logic, edge case, output sai).
4) Dua ra cach sua cu the, co the lam ngay.
5) Giong dieu trung tinh, huong dan, khong sao rong.

Nguyen tac DONG BO (bat buoc):
- Phai DONG Y voi khoi "TRANG THAI CHAM DINH". Khong duoc khang dinh nguoc lai (vi du: noi test fail khi tat_ca_pass=true).
- Khong duoc ket luan "loi he thong/CSDL/ghi nhan requirement" neu khong co bang chung ky thuat; neu test pass nhung requirement thap, hay giai thich co the do pattern requirement_agent hoac can bo sung tu khoa trong code cho fallback — khong doan boi loi database.
- Neu tat_ca_pass=true: KHONG duoc dat must_fix lien quan toi testcase that bai / output test sai; chi duoc goi y cai thien chat luong (vao improvements/suggestions).
- Neu dat_het=true (yeu cau): KHONG duoc dat must_fix noi "chua dap ung yeu cau" / thieu requirement; chi goi y them neu can (improvements).
- Neu Syntax chay duoc=false: uu tien loi cu phap/runtime, khong noi "da pass het test" neu dieu do khong dung voi TRANG THAI CHAM DINH.
- Diem LLM (0-20) phai phan anh tong the cac diem agent o tren: neu nhieu agent 18-20 thi diem LLM khong duoc qua thap (duoi ~12) neu khong co ly do ro trong code.

Nguyen tac:
- Diem LLM dua tren logic, do ro rang, cau truc, readability, best practice va do phu hop voi yeu cau.
- Luu y ket qua test/requirement de dua loi khuyen chinh xac.
- Khong thay the test/syntax validation, ma bo sung va giai thich them.

KHI TEST FAIL (bat buoc):
- Chi duoc dua ra cach sua dua tren bang "BANG TEST THAT BAI": moi test co expected_full va actual_full.
- Code sau khi sua phai cho stdout KHOP expected_full (tung dong, khoang trang, xuong dong) theo cach cham cua he thong — KHONG duoc doan them nhan tieng Viet/prompt neu expected khong co.
- suggestions / must_fix phai ghi ro "Test #N: ..." va neu co the trich expected_full can dat duoc.
- Khong khuyen "toi uu" lam thay doi format output khac expected.

Huong dan tra loi:
- summary: 1-2 cau.
- teacher_feedback: 1 doan 5-8 cau, neu test/requirement fail thi phai lien ket truc tiep voi cac ket qua do.
- must_fix: cac loi bat buoc sua de dung bai, uu tien theo test failures, toi da 5 muc.
- improvements: nang cap chat luong code, toi da 5 muc.
- suggestions: huong dan sua cu the, dang buoc lam hoac code change ro rang, toi da 6 muc.

Code can danh gia:
```python
{code}
```

Tra loi DUY NHAT bang JSON hop le, khong markdown, khong text ngoai JSON:
{{
    "score": <so nguyen 0-20>,
    "summary": "...",
    "teacher_feedback": "...",
    "must_fix": ["..."],
    "improvements": ["..."],
    "suggestions": ["..."]
}}"""

    try:
        response, _used_model = generate_content_with_fallback(prompt)
        text = (response.text or "").strip()

        parsed = None
        try:
            parsed = json.loads(text)
        except Exception:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group(0))
                except Exception:
                    parsed = None

        if isinstance(parsed, dict):
            if not isinstance(parsed.get("must_fix"), list):
                parsed["must_fix"] = []
            if not isinstance(parsed.get("improvements"), list):
                parsed["improvements"] = []
            if not isinstance(parsed.get("suggestions"), list):
                parsed["suggestions"] = []
            parsed = align_llm_output(parsed, agent_results)

            score_val = parsed.get("score", 10)
            try:
                score = min(max(int(float(score_val)), 0), 20)
            except Exception:
                score = 10

            summary = str(parsed.get("summary", "")).strip()
            teacher_feedback = str(parsed.get("teacher_feedback", "")).strip()
            must_fix = parsed.get("must_fix", [])
            improvements = parsed.get("improvements", [])
            suggestions = parsed.get("suggestions", [])

            if not isinstance(must_fix, list):
                must_fix = []
            if not isinstance(improvements, list):
                improvements = []
            if not isinstance(suggestions, list):
                suggestions = []

            feedback_parts = []
            if summary:
                feedback_parts.append(f"Summary: {summary}")
            if teacher_feedback:
                feedback_parts.append(f"Teacher Feedback: {teacher_feedback}")

            return {
                "score": score,
                "feedback": "\n".join(feedback_parts) if feedback_parts else text,
                "summary": summary,
                "teacher_feedback": teacher_feedback,
                "must_fix": [str(x) for x in must_fix][:8],
                "improvements": [str(x) for x in improvements][:8],
                "suggestions": [str(x) for x in suggestions][:8],
                "details": [f"AI Review: {score}/20", "Gemini teacher-style analysis completed"],
            }

        score = 10
        score_match = re.search(r"Score:\s*(\d+)\s*/?\s*20", text, re.IGNORECASE)
        if score_match:
            try:
                score = min(max(int(score_match.group(1)), 0), 20)
            except Exception:
                score = 10

        return {
            "score": score,
            "feedback": text,
            "summary": "LLM tra ve dang van ban tu do",
            "teacher_feedback": text,
            "must_fix": [],
            "improvements": [],
            "suggestions": [],
            "details": [f"AI Review: {score}/20", "Gemini-based code analysis completed (fallback mode)"],
        }

    except Exception as e:
        error_text = str(e)
        lower_error = error_text.lower()

        if "429" in lower_error or "quota" in lower_error or "rate limit" in lower_error:
            sync = llm_support_score_when_unavailable(agent_results)
            return {
                "score": sync,
                "feedback": f"LLM tam ngung do quota/gioi han API. Diem hien thi dong bo voi cac agent cham tu dong (~{sync}/20), khong phai danh gia AI day du. Chi tiet: {error_text}",
                "summary": "LLM khong chay duoc (quota); diem LLM chi la tham chieu theo cac muc khac",
                "teacher_feedback": (
                    "He thong khong the goi Gemini. Diem o muc LLM duoc gan gan voi trung binh "
                    "Syntax / Yeu cau / Cau truc / Phan tich / Test de giao dien khong hien thi 20/20 "
                    "trong khi bai chua dat. Vui long thu lai sau hoac kiem tra goi API."
                ),
                "must_fix": [],
                "improvements": [],
                "suggestions": ["Thu lai sau khi quota Gemini phuc hoi hoac nang cap goi API."],
                "details": [
                    f"LLM quota exceeded — display score synced to core agents ({sync}/20)",
                    "Khong con dung diem 20/20 khi LLM khong phan tich duoc",
                ],
            }

        sync = llm_support_score_when_unavailable(agent_results)
        return {
            "score": sync,
            "feedback": f"LLM evaluation error: {error_text}",
            "summary": "LLM gap loi trong qua trinh phan tich",
            "teacher_feedback": (
                "Khong tao duoc nhan xet AI. Diem LLM hien thi duoc can chinh theo ket qua cac agent khac "
                f"(~{sync}/20) de tranh chenh lech voi test/yeu cau thuc te."
            ),
            "must_fix": [],
            "improvements": [],
            "suggestions": ["Thu nop lai sau hoac kiem tra GOOGLE_MODEL_CANDIDATES / API key."],
            "details": [f"Error: {error_text}", f"Fallback LLM display score aligned to agents ({sync}/20)"],
        }
