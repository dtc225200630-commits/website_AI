# 🚀 FastAPI + Multi-Agent Integration Guide

## Setup & Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Database Setup
Ensure your PostgreSQL database has these tables:
```sql
-- evaluation_sessions table
CREATE TABLE IF NOT EXISTS evaluation_sessions (
    session_id SERIAL PRIMARY KEY,
    submission_id INT NOT NULL,
    syntax_score FLOAT,
    structure_score FLOAT,
    requirement_score FLOAT,
    test_score FLOAT,
    total_score FLOAT,
    final_feedback TEXT,
    agent_details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- agent_logs table
CREATE TABLE IF NOT EXISTS agent_logs (
    log_id SERIAL PRIMARY KEY,
    submission_id INT NOT NULL,
    agent_name VARCHAR(100),
    result TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## How It Works

### Web Flow
```
1. Student opens browser
   ↓
2. Student submits code via /submit endpoint
   ↓
3. Code saved to temp file
   ↓
4. Coordinator evaluates code:
   ├─ syntax_agent → score 0-20
   ├─ requirement_agent → score 0-20
   ├─ structure_agent → score 0-20
   ├─ test_agent → score 0-20
   └─ llm_agent → score 0-20
   ↓
5. Results saved to database (evaluation_sessions)
   ↓
6. Redirect to /submission-result/{submission_id}
   ↓
7. Template ketquaSV.html displays results
   ├─ Total score (0-100)
   ├─ Grade (A-F)
   ├─ Breakdown by agent
   └─ LLM feedback
```

---

## Starting the Application

### Run FastAPI Server
```bash
cd "c:\AI1 - Copy (3) - Copy"
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Output should show:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
[APP] ✓ Multi-agent coordinator imported successfully
```

### Access the Interface
Open browser: `http://localhost:8000`

---

## Testing the Integration

### Test Case 1: Submit Good Code
1. Navigate to assignment submission page
2. Paste this code:
```python
def add_numbers(a, b):
    """Add two numbers"""
    result = a + b
    print(f"Sum: {result}")
    return result

if __name__ == "__main__":
    x = int(input("Enter first number: "))
    y = int(input("Enter second number: "))
    total = add_numbers(x, y)
```

3. Click "Nộp bài"
4. Expected result: Score 80-95/100 (Grade B-A)

---

### Test Case 2: Submit Code with Errors
1. Paste this code:
```python
def broken():
    x = 1 / 0  # This will cause error
    return x

print(broken())
```

2. Click "Nộp bài"
3. Expected result: 
   - Syntax score: 0 (code doesn't run)
   - Other scores: Low
   - Total: 0-20/100 (Grade F)
   - LLM: Skipped (syntax error)

---

### Test Case 3: Submit Simple Code
1. Paste this code:
```python
x = input()
print(x)
```

2. Click "Nộp bài"
3. Expected result: Score 40-60/100 (Grade D-C)

---

## Result Display (ketquaSV.html)

The results page automatically displays:

### Sections shown:
1. **Syntax Check (🔍)**
   - Status: ✓ Thành công or ✗ Lỗi
   - Score: X/20
   - Error details if any

2. **Requirements (✅)**
   -✓ Requirement met
   - ✗ Missing requirement
   - Score: X/20

3. **Structure (🏗️)**
   - ✓ Has functions
   - • Comments found
   - • Code organization
   - Score: X/20

4. **Test Cases (🧪)**
   - ✓ Test 1 PASS
   - ✓ Test 2 PASS
   - ✗ Test 3 FAIL
   - Pass rate: X%
   - Score: X/20

5. **LLM Analysis (🤖)**
   - AI Score: X/20
   - Detailed feedback from Gemini AI
   - Code quality assessment

6. **Total Score**
   - Large display: X/100
   - Grade: A/B/C/D/F
   - Motivational message

---

## Database Results

After submission, check your database:

### evaluation_sessions table
```sql
SELECT 
    submission_id,
    syntax_score,
    requirement_score,
    structure_score,
    test_score,
    total_score,
    final_feedback,
    agent_details
FROM evaluation_sessions
WHERE submission_id = 1;
```

### agent_logs table
```sql
SELECT agent_name, result FROM agent_logs 
WHERE submission_id = 1
ORDER BY log_id;
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'google'"
**Fix**: 
```bash
pip install google-generativeai==0.3.0
```

### Issue: "Coordinator unavailable"
**Check**:
1. agents/coordinator.py exists
2. agents/ folder structure is correct
3. Check console for import error messages

### Issue: Results not showing in ketquaSV.html
**Check**:
1. Database has evaluation_sessions record
2. agent_details JSON is valid
3. Flask template variables are correct

### Issue: LLM score always 0 or missing
**Possible causes**:
1. Syntax error in code (LLM is skipped)
2. API key not valid
3. Internet connection issue

---

## Performance Notes

- **First submission**: 15-30 seconds (includes LLM API call)
- **Subsequent submissions**: 15-30 seconds each
- **Bottleneck**: LLM API response (5-15 seconds)

To speed up development:
- Mock the LLM agent by modifying llm_agent.py
- Or add caching layer for similar code patterns

---

## File Structure After Integration

```
app.py                          # Updated with coordinator import
agents/
  ├── coordinator.py            # Main orchestrator
  ├── syntax_agent.py           # Fixed
  ├── requirement_agent.py       # Fixed
  ├── structure_agent.py         # Fixed
  ├── test_agent.py              # Fixed
  ├── llm_agent.py               # Fixed
  ├── aggregation_agent.py       # Fixed
  └── langchain_orchestrator.py  # NEW
templates/
  └── ketquaSV.html              # Results display (no changes needed)
```

---

## API Endpoints

### Submit Assignment
```
POST /submit
Form data:
  - assignment_id: int
  - file: UploadFile (optional)
  - source_code: str (if no file)

Response:
  - Redirect to /submission-result/{submission_id}
```

### View Results
```
GET /submission-result/{submission_id}
Response:
  - HTML page with ketquaSV.html template
  - Contains all evaluation results
```

---

## Environment Variables (Optional)

Create `.env` file:
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# Google API
GOOGLE_API_KEY=your-gemini-api-key

# FastAPI
ENVIRONMENT=development
DEBUG=true
```

---

**You're all set! Now students can submit code and see AI evaluation results in the web interface!** 🎉

For detailed technical documentation, see:
- `FIXES_SUMMARY.md` - What was fixed
- `INTEGRATION_GUIDE.md` - Integration examples
- `BEFORE_AFTER_COMPARISON.md` - Code comparisons
