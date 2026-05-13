## KIẾN TRÚC HỆ THỐNG - SAU KHI FIX

### 1. FLOW HOẠT ĐỘNG (Coordinator Agent):

```
/submit endpoint (app.py)
    ↓
coordinator(filepath, requirements, testcases)
    ↓
    ├─ Step 1: syntax_agent(filepath)
    │   └─ Returns: {success, score: 0-20, error, details}
    │
    ├─ Step 2: code_analysis_agent(code) [NEW!]
    │   └─ Returns: {score: 0-20, issues, strengths, summary, details}
    │
    ├─ Step 3: requirement_agent(code, requirements)
    │   ├─ Depends on: code (parsed, no syntax errors)
    │   └─ Returns: {score: 0-20, details, fulfilled, total}
    │
    ├─ Step 4: structure_agent(code)
    │   └─ Returns: {score: 0-20, details}
    │
    ├─ Step 5: test_agent(filepath, testcases)
    │   └─ Returns: {score: 0-20, details, passed_count, test_results, summary}
    │
    ├─ Step 6: llm_agent(code) [CONDITIONALLY]
    │   ├─ Condition: Only if syntax["success"] == True
    │   └─ Returns: {score: 0-20, feedback, details}
    │
    └─ Step 7: aggregation_agent(all_results)
        └─ Returns: {total_score, grade, breakdown, details}

Result = {
    "syntax": {...},
    "code_analysis": {...},
    "requirement": {...},
    "structure": {...},
    "test": {...},
    "llm": {...},
    "total": {...}
}
```

### 2. DATABASE SCHEMA (evaluation_sessions):

```sql
evaluation_sessions {
    session_id: INTEGER (PK),
    submission_id: INTEGER (FK),
    syntax_score: DECIMAL(5,2),
    code_analysis_score: DECIMAL(5,2),      [NEW!]
    structure_score: DECIMAL(5,2),
    requirement_score: DECIMAL(5,2),
    test_score: DECIMAL(5,2),
    llm_score: DECIMAL(5,2),                [NEW!]
    total_score: DECIMAL(5,2),
    final_feedback: TEXT,
    agent_details: JSONB {                  [Contains all agent data]
        "syntax": {...},
        "code_analysis": {...},             [NEW!]
        "requirement": {...},
        "structure": {...},
        "test": {...},
        "llm": {...}
    },
    created_at: TIMESTAMP
}
```

### 3. AGENT LOGS (agent_logs):

```
Stored agents (6 total):
├─ SyntaxAgent: "Syntax: ✓ PASS" or "✗ FAIL - error"
├─ CodeAnalysisAgent: "Code Analysis: Score: 7/20"
├─ RequirementAgent: "Requirements met: 3/3"
├─ StructureAgent: "Structure: 7/20"
├─ TestAgent: "Tests: N/A"
└─ LLMAgent: "LLM Score: 16/20"
```

### 4. SCORING CALCULATION (aggregation_agent):

```
Total Score = Syntax + CodeAnalysis + Requirement + Structure + Test + LLM
            = 20 + 7 + 13 + 7 + 0 + 17
            = 64 points (max 120, capped at 100)
```

**Weighting:** Simple sum (no weighted multipliers)
- Each agent contributes 0-20 points
- Total is capped at 100 (backward compatible)

### 5. BACKWARD COMPATIBILITY:

✓ Database columns: Added, not modified
✓ Existing queries: Still work (old columns intact)
✓ Score calculation: Simple sum (doesn't break old results)
✓ Template rendering: Uses bracket notation with .get() (safe)

### 6. KEY DIFFERENCES FROM ORIGINAL:

Old (5 agents):
- syntax+requirement+structure+test+llm = 0-100 direct

New (6 agents):
- syntax+code_analysis+requirement+structure+test+llm = 0-100 capped
- code_analysis provides AST-based static analysis
- database saves individual scores + JSON details

### 7. RESULT DISPLAY (/submission-result/{submission_id}):

Template receives:
```python
{
    "evaluation": {
        "syntax_score": 20,
        "code_analysis_score": 7,    [NEW!]
        "requirement_score": 13,
        "structure_score": 7,
        "test_score": 0,
        "llm_score": 17,             [NEW!]
        "total_score": 64,
        ...
    },
    "agent_details": {
        "syntax": {...},
        "code_analysis": {...},      [NEW!]
        "requirement": {...},
        "structure": {...},
        "test": {...},
        "llm": {...}
    }
}
```

### 8. WHEN TO USE EACH AGENT:

1. **SyntaxAgent**: Always (prerequisite for others)
2. **CodeAnalysisAgent**: Always (static analysis)
3. **RequirementAgent**: Always (policy check)
4. **StructureAgent**: Always (quality metrics)
5. **TestAgent**: Always (functional validation)
6. **LLMAgent**: Only if syntax passes (needs runnable code)

---

## FIXED ISSUES:

❌ OLD BUG #1: Database didn't support code_analysis_score
✅ FIXED: Added code_analysis_score + llm_score columns

❌ OLD BUG #2: app.py didn't save code_analysis data
✅ FIXED: app.py now saves 6 agents with their scores and details

❌ OLD BUG #3: agent_logs only saved 5 agents
✅ FIXED: agent_logs now saves 6 agents (added CodeAnalysisAgent)

❌ OLD BUG #4: Aggregation formula was weighted (dropped student scores)
✅ FIXED: Back to simple sum (syntax+ca+req+struct+test+llm)

❌ OLD BUG #5: Template couldn't access code_analysis data
✅ FIXED: agent_details now contains code_analysis in JSONB

✓ BACKWARD COMPATIBILITY: All old submissions still readable
