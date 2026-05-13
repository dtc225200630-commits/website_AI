## DIAGNOSTIC REPORT: BUGS FOUND IN MULTI-AGENT GRADING SYSTEM

### BUG #1: Syntax Agent - Subprocess Input Handling Wrong
- **File:** agents/syntax_agent.py
- **Problem:** Uses subprocess.run() with dummy input "1\n1\n..." which fails if:
  * Code expects specific input (e.g., float input for radius)
  * Dummy input causes wrong output = syntax fails
- **Fix:** Use AST parsing first to check syntax validity, only run if AST passes
- **Impact:** Student code marked syntax=0/20 even if valid Python

### BUG #2: Syntax Agent - No AST Validation  
- **File:** agents/syntax_agent.py
- **Problem:** Doesn't use ast module to validate syntax before run
- **Fix:** Add ast.parse() check BEFORE subprocess execution
- **Impact:** Subprocess error != actual syntax error

### BUG #3: Test Agent - Exact String Matching Too Strict
- **File:** agents/test_agent.py line 62
- **Problem:** Uses `if output == expected_output` (exact match)
- **Examples that should pass but fail:**
  * expected="12.56", actual="Diện tích: 12.56" 
  * expected="78.5", actual="Area is 78.50"
- **Fix:** Implement flexible numeric comparison with regex extraction
- **Impact:** Tests fail for valid output with formatting differences

### BUG #4: Structure Agent - String Counting Instead of AST
- **File:** agents/structure_agent.py
- **Problem:** Uses code.count("def ") instead of ast.parse()
- **Issues:**
  * Counts "def " in strings/comments
  * No actual function analysis
  * Variable naming detection via regex is weak
- **Fix:** Use ast.NodeVisitor to analyze AST properly
- **Impact:** Structure scores completely unreliable

### BUG #5: Aggregation Score Capping Logic Wrong
- **File:** agents/aggregation_agent.py lines 38-40
- **Problem:** Sums all 6 agents (max 120) then caps at 100
  * If student gets 5 agents at 20 pts + 0 on llm = 100 pts (wrong)
  * Should be weighted or normalized differently
- **Fix:** Either:
  * Option A: Change to 5 agents only (original design)
  * Option B: Do proper weighted sum
  * Option C: Normalize each to percentage first
- **Impact:** Scoring is mathematically unsound

### BUG #6: Test Agent - No Flexible Output Comparison
- **File:** agents/test_agent.py
- **Problem:** No logic to extract numeric values from strings
- **Examples:**
  * Student outputs "Diện tích hình tròn là: 12.56" 
  * Expected "12.56"
  * Match fails
- **Fix:** Add regex to find numbers in output, compare numerically
- **Impact:** Tests fail even though logic is correct

### BUG #7: Syntax Agent - Input Handling for Multiple input() Calls
- **File:** agents/syntax_agent.py line 13
- **Problem:** Provides 50 lines of "1" as dummy input - what if code needs multiple different inputs?
- **Fix:** 
  * If code has input_validation, provide those inputs
  * Or just check ast.parse() only
- **Impact:** Complex code with multiple input() calls fails

### BUG #8: No Input Sanitization in Test Agent
- **File:** agents/test_agent.py line 55
- **Problem:** subprocess stdin gets from testcase exactly, no encoding handling
- **Fix:** Ensure input_data is string, handle encoding properly
- **Impact:** Binary errors from input handling

### BUG #9: Requirement Agent - Hardcoded Pattern Matching
- **File:** agents/requirement_agent.py
- **Problem:** Uses hardcoded if-elif chains for 20+ requirement patterns
- **Issues:**
  * Breaks if requirement text format changes
  * Not flexible
  * Vietnamese-only
- **Fix:** Should be data-driven from semantics,  not string patterns
- **Impact:** New requirement types won't work

---

## PRIORITY FIX ORDER:

**CRITICAL (Must fix now):**
1. ✗ BUG #1: syntax_agent fails on valid code
2. ✗ BUG #3: test_agent too strict matching
3. ✗ BUG #7: syntax_agent input handling

**HIGH (Fix ASAP):**
4. ✗ BUG #4: structure_agent analysis wrong
5. ✗ BUG #5: aggregation capping logic

**MEDIUM (Improve):**
6. ✗ BUG #2: Add AST validation
7. ✗ BUG #6: Add flexible numeric compare
8. ✗ BUG #8: Input sanitization
9. ✗ BUG #9: Requirement patterns

---

## DETAILED FIXES BELOW
