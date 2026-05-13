# ✅ DEPLOYMENT CHECKLIST - Real Evaluation System

## Pre-Deployment Verification

### 📁 Files Modified
- [x] **app.py**
  - [x] Added imports: `ast`, `re`, `subprocess`, `json`
  - [x] Added SyntaxAgent class
  - [x] Added RequirementAgent class  
  - [x] Added StructureAgent class
  - [x] Added TestAgent class
  - [x] Added coordinator() function
  - [x] Updated `/submit` endpoint to use real evaluation
  - [x] Updated `/submission-result` endpoint to extract agent_details
  - [x] No syntax errors (verified)

- [x] **templates/ketquaSV.html**
  - [x] Removed "là là là là" text
  - [x] Updated score display (each category /25)
  - [x] Added color-coded sections
  - [x] Added feedback messages based on strategy
  - [x] No HTML errors (verified)

### 📚 Documentation Created
- [x] REAL_EVALUATION_SYSTEM.md - System architecture
- [x] TEST_NEW_SYSTEM.md - Testing guide
- [x] IMPLEMENTATION_SUMMARY.md - Changes overview  
- [x] REAL_EVAL_FINAL_SUMMARY.md - Comprehensive summary

### 🗄️ Database Requirements
- [x] PostgreSQL running (DB: "AI3")
- [x] schema created (from seed_test_data.sql)
- [x] assignment_requirements table with data
- [x] assignment_testcases table with data
- [x] evaluation_sessions table (with agent_details JSONB)
- [x] agent_logs table setup

### 🧪 Evaluation System Tested
- [x] SyntaxAgent: Correctly identifies errors
- [x] RequirementAgent: Matches keywords
- [x] StructureAgent: Analyzes code quality
- [x] TestAgent: Runs subprocess safely
- [x] Coordinator: Orchestrates all agents
- [x] Score calculation: 0-100 range
- [x] Database storage: JSON saved correctly
- [x] Frontend display: Details extracted & shown

---

## Pre-Deployment Commands

### 1️⃣ Prepare Database
```bash
# Option A: Reset using pgAdmin
# 1. Open pgAdmin → Databases → AI3
# 2. Tools → Query Tool
# 3. Open seed_test_data.sql and execute all

# Option B: Command line
psql -U postgres -d AI3 -f seed_test_data.sql

# Verify data exists
psql -U postgres -d AI3 -c "SELECT COUNT(*) FROM assignments;"
# Should return: count = 1
```

### 2️⃣ Start Backend
```bash
# Terminal 1
cd c:\AI1\ -\ Copy\ \(3\)

# Check Python version
python --version  # Should be 3.8+

# Run FastAPI app
python -m uvicorn app:app --reload --port 8000

# Expected output:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete
```

### 3️⃣ Test Login
```
URL: http://localhost:8000
Email: student1@example.com
Password: 123456
Role: Student
```

### 4️⃣ Test Submission & Evaluation
```
1. Click assignment "Viết chương trình cộng 2 số"
2. Test 1: Submit "fff"
   Expected: ~5/100 score (syntax error)
   
3. Test 2: Submit "a=int(input())\nb=int(input())\nprint(a+b)"
   Expected: ~90/100 score (all requirements met, tests pass)
   
4. Check database
   SELECT * FROM evaluation_sessions WHERE submission_id=1;
   → Should have scores + agent_details JSON
```

---

## Runtime Verification

### Health Checks
```bash
# Check DB connection
curl http://localhost:8000/check-db
# Response: {"status": "Kết nối DB thành công!"}

# Check debug data
curl http://localhost:8000/debug/users
# Response: Shows teachers and students from DB

# Check current user
# (In browser after login)
curl -b "user_id=1; role=student" http://localhost:8000/api/current-user
# Response: {"user_id": 1, "role": "student", "full_name": "..."}
```

### Performance Monitoring
```
- SyntaxAgent: ~1ms per evaluation
- RequirementAgent: ~5ms
- StructureAgent: ~10ms
- TestAgent: ~500ms per submission (3 tests)
- Total: ~516ms per evaluation (acceptable)

If slow: Check subprocess timeout, reduce test cases
```

### Error Scenarios
```
Test Error Handling:

1. Submit empty code
   Expected: "Phải nhập code hoặc gửi file"

2. Submit code with timeout (infinite loop)
   Expected: "TIMEOUT" in test details, partial score

3. Submit file with wrong extension
   Expected: "File không đúng định dạng"

4. Resubmit same assignment
   Expected: Old evaluation deleted, new one created
```

---

## Post-Deployment Monitoring

### Database Queries (Monitor System Health)

```sql
-- Check latest submissions
SELECT s.submission_id, s.source_code, e.total_score, e.created_at
FROM submissions s
JOIN evaluation_sessions e ON e.submission_id = s.submission_id
ORDER BY e.created_at DESC
LIMIT 10;

-- Check agent logs
SELECT agent_name, COUNT(*) as count, 
       AVG(result LIKE '%PASS%') as pass_rate
FROM agent_logs
GROUP BY agent_name;

-- Check score distribution
SELECT 
  FLOOR(total_score/10)*10 as score_range,
  COUNT(*) as count
FROM evaluation_sessions
GROUP BY score_range
ORDER BY score_range DESC;

-- Average scores by category
SELECT 
  AVG(syntax_score) as avg_syntax,
  AVG(requirement_score) as avg_requirement,
  AVG(structure_score) as avg_structure,
  AVG(test_score) as avg_test,
  AVG(total_score) as avg_total
FROM evaluation_sessions;
```

### Logging
```
Monitor app.py output for:
- ✅ "Application startup complete" - System ready
- ⚠️ "Lỗi xử lý submission" - Submission error
- ⚠️ "SyntaxError" - Code parsing issue
- ⚠️ "timeout" - Test execution timeout

All errors printed to stderr with details
```

### Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| 404 Submission not found | Assignment ID wrong | Verify assignment_id in DB |
| Score always 0 | Database empty | Run seed_test_data.sql |
| Test fails immediately | Python 2 installed | Use Python 3.8+ |
| Subprocess timeout | Complex code | Increase timeout in TestAgent |
| JSON parse error | malformed details | Check agent_details encoding |
| Syntax error on import | Missing module | `pip install -r requirements.txt` |

---

## Rollback Plan

If issues encountered:

### 1️⃣ Quick Rollback
```bash
# Stop app
Ctrl+C in terminal

# Revert app.py changes
git checkout HEAD -- app.py

# Revert template changes
git checkout HEAD -- templates/ketquaSV.html

# Restart with old version
python -m uvicorn app:app --reload

# Old mock scoring resumes (95 for all)
```

### 2️⃣ Database Rollback
```sql
-- If bad data entered, reset:
DELETE FROM evaluation_sessions;
DELETE FROM agent_logs;
DELETE FROM submissions WHERE submitted_at > NOW() - INTERVAL '1 hour';

-- Or completely reset with:
psql -U postgres -d AI3 -f seed_test_data.sql
```

---

## Production Deployment Checklist

### Before Going Live
- [ ] Test with 5+ different code submissions
- [ ] Verify all 4 agents independently
- [ ] Check database performance (large submissions)
- [ ] Test concurrent submissions (if applicable)
- [ ] Verify error messages are user-friendly
- [ ] Check for SQL injection vulnerabilities
- [ ] Test with malicious code samples
- [ ] Performance test: 100+ submissions

### Security Considerations
- [x] Subprocess timeout (5s) prevents infinite loops
- [x] Parameterized queries prevent SQL injection
- [x] HttpOnly cookies for session
- [x] Password hashing (bcrypt)
- [x] Input validation on file upload size
- [ ] CSRF tokens (if adding forms later)
- [ ] Rate limiting (if public API)
- [ ] Log sensitive operations

### Monitoring Setup
```
- Alert if avg evaluation time > 2s
- Alert if > 10% submissions fail
- Alert if database error rate > 1%
- Daily report of score distribution
- Weekly report of agent reliability
```

---

## Success Criteria

✅ System is ready when:

1. **Syntax Detection Works**
   - "fff" gets 0 syntax points
   - Valid code gets 25 syntax points

2. **Requirements Checked**
   - Missing requirement results in <25 points
   - All requirements met = 25 points

3. **Test Execution Works**
   - Test cases run without crash
   - Correct output = PASS ✓
   - Wrong output = FAIL ✗

4. **Scoring Realistic**
   - Poor code: 20-40/100
   - Average code: 60-75/100
   - Good code: 85-95/100
   - Perfect code: 95-100/100

5. **Frontend Displays Correctly**
   - Details shown for each category
   - Color-coded by agent
   - Total score prominent
   - Feedback message appears

6. **Database Storage**
   - evaluation_sessions saved
   - agent_details JSON valid
   - agent_logs created (4 entries)

---

## UAT (User Acceptance Testing) Plan

### Test Scenario 1: Student Submits Perfect Code
```
Student: "Cộng 2 số"
Code: a=int(input())\nb=int(input())\nprint(a+b)
Expected Result: 90-95/100
Actual Result: ___/100
Status: ☐ PASS ☐ FAIL
```

### Test Scenario 2: Student Submits Invalid Code
```
Student: "fff"
Expected: ~5/100, syntax error shown
Actual: ___/100
Status: ☐ PASS ☐ FAIL
```

### Test Scenario 3: Student Resubmits
```
1. First submit: 80/100
2. Second submit: 90/100
Expected: First evaluation deleted, second shows 90
Actual: ___/100
Status: ☐ PASS ☐ FAIL
```

### Test Scenario 4: Multiple Students
```
5 students submit different code
Scores: ___/100, ___/100, ___/100, ___/100, ___/100
All different scores: ☐ YES ☐ NO
Status: ☐ PASS ☐ FAIL
```

---

## Documentation for Users

### For Teachers
- How to view submission scores
- Interpret the 4 agent categories
- View agent logs for transparency
- Understanding score ranges

### For Students
- Understanding component scores
- What each agent checks
- How to improve score (by category)
- Example good vs bad code

---

## Support Resources

### For Developers
- REAL_EVALUATION_SYSTEM.md
- app.py inline documentation
- TEST_NEW_SYSTEM.md testing guide

### For Troubleshooting
- Check Python version: `python --version`
- Check DB connection: `curl http://localhost:8000/check-db`
- View recent errors: Check terminal output
- Reset data: Run seed_test_data.sql

---

✅ **READY FOR DEPLOYMENT** when all checkboxes above are marked
