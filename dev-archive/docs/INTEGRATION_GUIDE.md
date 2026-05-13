# 📋 FastAPI Integration Guide

## Quick Integration

To use the fixed multi-agent evaluation system in your FastAPI app:

### Option 1: Use Coordinator (Recommended)
```python
from agents.coordinator import coordinator

# In your endpoint
result = coordinator(
    filepath="/path/to/submitted_code.py",
    requirements=[
        ("input()", 5),      # requirement, weight
        ("phép cộng", 3),
        ("print()", 4),
    ],
    testcases=[
        ("5", "5", 1),           # input, expected_output, weight
        ("10", "10", 1),
        ("hello\nworld", "hello\nworld", 2),
    ]
)

# Access results
total_score = result["total"]["total_score"]    # 0-100
grade = result["total"]["grade"]                # "A", "B", etc.
all_details = result["total"]["details"]        # Summary breakdown

# Individual agent results
print(result["syntax"]["score"])                # 0-20
print(result["requirement"]["details"])         # List of details
print(result["structure"]["metrics"])           # Metrics dict
print(result["test"]["pass_rate"])              # Percentage string
print(result["llm"]["feedback"])                # LLM feedback text
```

### Option 2: Direct LangChain Orchestrator
```python
from agents.langchain_orchestrator import orchestrate_agents

result = orchestrate_agents(
    filepath="/path/to/code.py",
    requirements=[...],
    testcases=[...]
)
```

### Option 3: Individual Agents
```python
from agents.syntax_agent_fixed import syntax_agent
from agents.requirement_agent_fixed import requirement_agent
from agents.structure_agent_fixed import structure_agent
from agents.test_agent_fixed import test_agent
from agents.llm_agent import llm_agent
from agents.aggregation_agent_fixed import aggregation_agent

# Read code
with open("code.py", "r") as f:
    code = f.read()

# Run individual agents
syntax = syntax_agent("code.py")           # Pass filepath
requirement = requirement_agent(code, req_list)      # Pass code
structure = structure_agent(code)
test = test_agent("code.py", test_list)
llm = llm_agent(code)

# Aggregate (if syntax passed)
result = {
    "syntax": syntax,
    "requirement": requirement,
    "structure": structure,
    "test": test,
    "llm": llm
}
total = aggregation_agent(result)
result["total"] = total
```

## Example FastAPI Endpoint

```python
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from agents.coordinator import coordinator

app = FastAPI()

@app.post("/evaluate-assignment/{assignment_id}")
async def evaluate_assignment(
    assignment_id: int,
    file: UploadFile = File(...),
):
    """
    Evaluate submitted Python code using multi-agent system
    """
    try:
        # Save uploaded file temporarily
        filename = f"/tmp/submit_{assignment_id}_{file.filename}"
        contents = await file.read()
        with open(filename, "wb") as f:
            f.write(contents)
        
        # Get requirements and test cases from database
        # (This is pseudo-code - adapt to your DB)
        requirements = get_requirements_from_db(assignment_id)
        testcases = get_testcases_from_db(assignment_id)
        
        # Run evaluation
        result = coordinator(
            filepath=filename,
            requirements=requirements,  # [(req_text, weight), ...]
            testcases=testcases        # [(input, expected, weight), ...]
        )
        
        return {
            "assignment_id": assignment_id,
            "total_score": result["total"]["total_score"],
            "grade": result["total"]["grade"],
            "breakdown": result["total"]["breakdown"],
            "details": result["total"]["details"],
            "full_report": result  # Include all agent details
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup
        import os
        if os.path.exists(filename):
            os.remove(filename)
```

## Result Structure

```python
{
    # Individual agent results
    "syntax": {
        "score": 20,                    # 0-20
        "details": ["Syntax OK - Code runs without errors"],
        "success": True,
        "error": ""
    },
    
    "requirement": {
        "score": 15,                    # 0-20 (normalized)
        "details": ["✓ Requirement: 'input()' - FOUND", "✗ Missing: 'phép cộng'"],
        "fulfilled_count": 1,
        "total_requirements": 2,
        "summary": "Fulfilled 1/2 requirements"
    },
    
    "structure": {
        "score": 18,                    # 0-20
        "details": [`✓ Found 2 function(s)...`, ...],
        "metrics": {
            "functions": 2,
            "comments": 5,
            "lines": 25,
            "single_letter_vars": 0,
            "has_class": False,
            "has_main": True
        }
    },
    
    "test": {
        "score": 20,                    # 0-20 (normalized)
        "details": [`✓ Test 1 PASS...`, `✓ Test 2 PASS...`],
        "passed_count": 5,
        "total_weight": 5,
        "pass_rate": "100.0%",
        "test_results": [
            {
                "test_no": 1,
                "status": "PASS",
                "input": "5",
                "expected": "5",
                "actual": "5",
                "weight": 1
            }
        ]
    },
    
    "llm": {
        "score": 16,                    # 0-20
        "feedback": "Score: 16/20\n<detailed feedback from Gemini>",
        "details": ["AI Review: 16/20", "Gemini-based code analysis completed"]
    },
    
    # Aggregated final result
    "total": {
        "total_score": 89,              # 0-100 (sum of all agents)
        "grade": "B (Tốt)",             # Grade assignment
        "breakdown": {
            "syntax_score": 20,
            "requirement_score": 15,
            "structure_score": 18,
            "test_score": 20,
            "llm_score": 16
        },
        "details": [
            "Syntax: 20/20",
            "Requirement: 15/20",
            "Structure: 18/20",
            "Test: 20/20",
            "LLM Review: 16/20",
            "Total: 89/100 - B (Tốt)"
        ]
    }
}
```

## Error Handling

The coordinator has built-in error handling:

```python
try:
    result = coordinator("code.py", reqs, testcases)
    
    # Check if evaluation succeeded
    if result.get("error"):
        print(f"Evaluation failed: {result['error']}")
    
    score = result["total"]["total_score"]
    
except Exception as e:
    # Handle unexpected errors
    print(f"Error: {e}")
    return {"error": str(e), "score": 0, "grade": "F"}
```

## Database Schema (Example)

```sql
-- Store assignment requirements
CREATE TABLE assignment_requirements (
    requirement_id SERIAL PRIMARY KEY,
    assignment_id INT REFERENCES assignments(assignment_id),
    requirement_text VARCHAR(500),
    weight INT DEFAULT 1
);

-- Store test cases
CREATE TABLE test_cases (
    testcase_id SERIAL PRIMARY KEY,
    assignment_id INT REFERENCES assignments(assignment_id),
    input_data TEXT,
    expected_output TEXT,
    weight INT DEFAULT 1
);

-- Store evaluation results
CREATE TABLE evaluation_results (
    result_id SERIAL PRIMARY KEY,
    submission_id INT REFERENCES submissions(submission_id),
    syntax_score INT,
    requirement_score INT,
    structure_score INT,
    test_score INT,
    llm_score INT,
    total_score INT,
    grade VARCHAR(10),
    full_result JSONB,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Performance Notes

- **Time**: Full evaluation typically takes 10-30 seconds depending on code complexity and LLM response time
- **Memory**: Each evaluation loads the code in memory - safe for files up to ~10MB
- **LLM Cost**: Using Gemini API - costs depend on API calls. Consider rate limiting.

## Environment Variables

Set these in `.env`:

```env
# For LLM Agent
GOOGLE_API_KEY=AIzaSyC9A_o_sE-o44peD2dHR_ZJJxiTso_2yqw

# For Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Optional: Set LangChain debug mode
LANGCHAIN_DEBUG=false
```

## Troubleshooting

### Problem: "LLM agent returns 0/20"
- Check if Gemini API key is valid
- Check internet connection
- Look at llm_agent error in result["llm"]["feedback"]

### Problem: "Test cases always fail"
- Make sure expected output is exact match (whitespace matters)
- Check if test inputs include newlines: `"5\n"` not `"5"`
- Verify code actually produces expected output when run manually

### Problem: "Requirement score is 0"
- Requirements must match exact keywords or patterns
- Check if code contains required functions/keywords
- Try simpler requirement patterns for debugging

### Problem: "Coordinator runs forever"
- Code might be in infinite loop - check syntax_agent timeout (3 seconds)
- Increase timeout if needed (edit agents/syntax_agent.py: `timeout=5`)

---

**Ready to integrate!** Just import `coordinator` and use it in your endpoints.
