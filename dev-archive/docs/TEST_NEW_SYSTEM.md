# Hướng Dẫn Kiểm Tra Hệ Thống Chấm Điểm Mới

## So Sánh: Cũ vs Mới

### ❌ HỆ THỐNG CŨ (Mock)
```
Student 1 submission: "fff"
Result: 95/100 ❌ SAI - không có lý do

Student 2 submission: "a=int(input()); b=int(input()); print(a+b)"
Result: 95/100 ❌ SAI - giống như "fff"

All students: 95/100 (dù code đúng hay sai)
```

### ✅ HỆ THỐNG MỚI (Thực Tế)
```
Student 1 submission: "fff"
Syntax: ✗ SyntaxError - 0/25
Requirements: ✗ Missing input(), print(), + - 0/25
Structure: Plain text - 5/25
Test: Cannot run due to syntax error - 0/25
━━━━━━━━━━━━━━━━━━━━━━
TOTAL: 5/100 ✅ ĐÚNG

Student 2 submission: "a=int(input()); b=int(input()); print(a+b)"
Syntax: ✓ Valid Python - 25/25
Requirements: ✓ Has input(), print(), + - 25/25
Structure: Good indentation, no comments - 15/25
Test: Passed 3/3 test cases - 25/25
━━━━━━━━━━━━━━━━━━━━━━
TOTAL: 90/100 ✅ ĐẠO ĐỨC
```

---

## Cách Kiểm Tra

### 1. **Kiểm Tra Syntax Detection**

Submit code có lỗi cú pháp:
```python
# Nộp: "fff"
Expected:
- Syntax Score: 0/25 (SyntaxError: name 'fff' is not defined)
- Total: ~5/100
```

Submit code hợp lệ:
```python
# Nộp: "a=int(input())\nb=int(input())\nprint(a+b)"
Expected:
- Syntax Score: 25/25 (Valid)
- Total: ~85-90/100
```

### 2. **Kiểm Tra Requirement**

Database requirements:
```sql
SELECT * FROM assignment_requirements WHERE assignment_id = 1;

requirement_text          | weight
─────────────────────────┼────────
Có dùng input()          | 10
Có phép cộng             | 10
Có print()               | 10
```

Test cases:
- Nộp code thiếu `input()`: Requirement score ~15/25 (missing 1/3)
- Nộp code có tất cả: Requirement score 25/25 (all 3/3)

### 3. **Kiểm Tra Test Case Execution**

Database test cases:
```sql
SELECT * FROM assignment_testcases WHERE assignment_id = 1;

input_data | expected_output | score_weight
───────────┼─────────────────┼──────────────
2\n3       | 5               | 10
10\n20     | 30              | 10
7\n8       | 15              | 10
```

Test scenarios:
```
Input: "2\n3"
Expected: "5"

Case 1: Correct code "a=int(input()); b=int(input()); print(a+b)"
Output: "5" → PASS ✓

Case 2: Wrong addition "a=int(input()); b=int(input()); print(a*b)"
Output: "6" → FAIL ✗ (expected 5, got 6)

Case 3: Code with syntax error "fff"
Output: ERROR → FAIL ✗
```

### 4. **Kiểm Tra Structure Scoring**

```
Good code:
───────────────────────────────────────
# Cộng hai số
a = int(input())    # Biến a
b = int(input())    # Biến b
print(a + b)        # In kết quả
───────────────────────────────────────
Structure Score: 20-22/25
- Comments: ✓ (+6)
- Indentation: ✓ (+6)
- Naming: ✓ (+6)
- Formatting: ✓ (+3)
- Base: ✓ (+5)

Bad code:
───────────────────────────────────────
a=int(input())
b=int(input())
print(a+b)
───────────────────────────────────────
Structure Score: 10-12/25
- Comments: ✗ (-6)
- Indentation: ✓ (+6)
- Naming: Okay (+3)
- Formatting: Okay (+3)
- Base: ✓ (+5)
```

---

## Test Data trong seed_test_data.sql

### Students & Submissions
```sql
-- 10 students (student1 - student10)
-- 10 submissions (mỗi student 1 submission cho assignment 1)
-- Code submissions khác nhau (biến tên, cấu trúc khác nhau)
```

### Current Scores (từ seed data cũ)
```
All 95-97: Placeholder data (mock)
```

### Expected Scores Sau Khi Deploy (từ evaluation engine mới)
```
Student 1-10: Varied scores từ 50-97 dựa trên quality
  - "a=int(input()); b=int(input()); print(a+b)" → ~92
  - "x,y=int(input()),int(input()); print(x+y)" → ~88
  - "a=int(input())\nprint(int(input())+a)" → ~85
  - Codebasic nhưng syntax error → ~5-10
```

---

## Database Inserts Tự Động

Khi submit:
```sql
-- Submission lưu
INSERT INTO submissions (assignment_id, student_id, source_code, submitted_at)
VALUES (1, 5, 'a=int(input())\n...', NOW());

-- Evaluation session lưu
INSERT INTO evaluation_sessions 
(submission_id, syntax_score, structure_score, requirement_score, test_score, total_score, final_feedback, agent_details)
VALUES (10, 25, 18, 25, 22, 90, 'Cú pháp OK | Yêu cầu OK | ...', 
'{"syntax":{"success":true,...},"requirement":{"score":25,"details":["✓ input()","✓ +","✓ print()"]},...}');

-- Agent logs lưu (4 agents)
INSERT INTO agent_logs (submission_id, agent_name, result) VALUES
(10, 'SyntaxAgent', 'Syntax: PASS'),
(10, 'RequirementAgent', 'Requirements met: 3/3'),
(10, 'StructureAgent', 'Structure: good'),
(10, 'TestAgent', 'Tests passed: 3/3');
```

---

## Các Bước Để Kiểm Tra Toàn Bộ

### Step 1: Khởi động hệ thống
```bash
# Terminal 1: Database
# Đảm bảo PostgreSQL chạy với DB "AI3" 
# Chạy seed_test_data.sql để reset dữ liệu

# Terminal 2: Backend
python -m uvicorn app:app --reload --port 8000
```

### Step 2: Đăng nhập
```
URL: http://localhost:8000
- Email: student1@example.com
- Password: 123456
- Role: Student
```

### Step 3: Submit các loại code khác nhau
```
Assignment: "Viết chương trình cộng 2 số"

Test 1: Submit "fff"
Expected: ~5/100 (syntax error, no requirements met)

Test 2: Submit "a=int(input())\nb=int(input())\nprint(a+b)"
Expected: ~90-95/100 (all requirements met, all tests pass)

Test 3: Submit "x=int(input())\ny=int(input())\nprint(x*y)"
Expected: ~65-75/100 (syntax ok, has input/print, 0 tests pass)

Test 4: Submit "a=1\nb=2\nprint(a+b)"
Expected: ~50-60/100 (no input requirement, some tests fail)
```

### Step 4: Xem kết quả
- Điểm chi tiết: Syntax / Requirement / Structure / Test
- Agent feedback từ mỗi evaluator
- Total score out of 100

---

## Expected Behavior Changes

| Aspect | Cũ | Mới |
|--------|-----|-----|
| "fff" score | 95 ❌ | 5 ✅ |
| Code không test | 95 ❌ | ~60-80 ✅ |
| Code đúng hoàn toàn | 95 ❌ | 90-95 ✅ |
| Feedback | Generic | Chi tiết từng agent |
| Test execution | Không | Có ✅ |
| Requirement check | Không | Có ✅ |
| Structure analysis | Không | Có ✅ |

---

## Edge Cases Xử Lý

✅ **Syntax Error**: Code sai cú pháp → 0 syntax điểm, khôn gì test
✅ **Timeout**: Code chạy quá lâu (5s) → Test fail, ghi nhận trong log
✅ **Runtime Error**: Exception khi chạy → Test fail, error message lưu
✅ **Empty Code**: Chuỗi trống → Reject tại submit
✅ **No Requirements**: Assignment không có requirement → Default 20 điểm
✅ **No Test Cases**: Assignment không có test → 20 điểm default

---

## Troubleshooting

### Problem: Agent execution fails
☑ Check Python version (3.7+)
☑ Check subprocess timeout (5 seconds)
☑ Check if `ast` module available

### Problem: Scores bất thường
☑ Check requirement tuples format (text, weight)
☑ Check testcase tuples format (input, output, weight)
☑ Check if code has invisible characters

### Problem: Test cases không match
☑ Input string phải exact match (including newlines)
☑ Output được strip() whitespace, nên "5\n" == "5"
☑ Check database testcase data

---

## Performance Notes

- SyntaxAgent: Fast (~1ms)
- RequirementAgent: Fast (~5ms)
- StructureAgent: Fast (~10ms)
- TestAgent: Slow (~100-500ms per test)
- **Total per submission**: ~100-1000ms (depending on tests)

Nên implement async evaluation nếu có nhiều submissions đồng thời.

