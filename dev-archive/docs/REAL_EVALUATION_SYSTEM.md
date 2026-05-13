# Hệ Thống Chấm Điểm Thực Tế (Real Evaluation System)

## Vấn Đề Cũ
- ❌ Tất cả submission đều được 95 điểm, dù code có đúng hay không
- ❌ Không có kiểm tra cú pháp, yêu cầu, cấu trúc hay test cases thực tế
- ❌ Submission "fff" cũng được 95 điểm

## Giải Pháp Mới

### 1. **Hệ Thống 4 Agents**

#### SyntaxAgent (Kiểm tra cú pháp)
- Sử dụng `ast.parse()` để kiểm tra lỗi Python
- **Điểm**: 0/25 nếu có lỗi syntax, 25/25 nếu hợp lệ
- Chi tiết: "Cú pháp Python hợp lệ" hoặc "Lỗi cú pháp tại dòng X"

#### RequirementAgent (Kiểm tra yêu cầu)
- Kiểm tra requirement từ bảng `assignment_requirements`
- Hỗ trợ keywords: `input()`, `print()`, `+` (cộng), `def` (hàm), etc.
- **Điểm**: Tính dựa trên % yêu cầu được met (0-25)
- Chi tiết: Liệt kê các yêu cầu đã meet (✓) và chưa met (✗)

#### StructureAgent (Đánh giá cấu trúc)
- Kiểm tra: Comments, indentation, tên biến, độ dài dòng
- Scoring: 
  - Comments: +6 điểm
  - Indentation: +6 điểm  
  - Tên biến tốt: +6 điểm
  - Độ dài dòng hợp lý: +3 điểm
  - Function/Class: +4 điểm
  - Base: +5 điểm
- **Tối đa**: 25/25 điểm

#### TestAgent (Chạy test cases)
- Chạy code Python với các test cases từ `assignment_testcases`
- So sánh output thực tế vs kỳ vọng
- **Điểm**: (number_passed / total_tests) × 25
- Chi tiết: "Test case #1: PASS/FAIL", "TIMEOUT", "ERROR"

### 2. **Coordinator Function**
- Phối hợp 4 agents
- Tổng điểm = syntax + requirement + structure + test (0-100)
- Trả về object chứa:
  ```python
  {
    "syntax": {"success": bool, "error": str, "score": float},
    "requirement": {"score": float, "details": list},
    "structure": {"score": float, "details": list},
    "test": {"score": float, "details": list},
    "total": float
  }
  ```

### 3. **Cách Tính Điểm Chi Tiết**

| Component | Max | Tính toán |
|-----------|-----|----------|
| **Syntax** | 25 | 25 nếu valid, 0 nếu error |
| **Requirement** | 25 | (Met requirements / Total) × 25 |
| **Structure** | 25 | Comments + Indentation + Naming + Formatting + Functions + Base |
| **Test** | 25 | (Tests Passed / Total Tests) × 25 |
| **TOTAL** | **100** | Sum of all 4 |

### 4. **Ví Dụ Chấm Điểm**

#### Code: `a=int(input())\nb=int(input())\nprint(a+b)`
```
✓ Syntax: 25/25 (valid Python)
✓ Requirement: 25/25 (có input, print, +)
✓ Structure: 15/25 (careless format, thiếu comments)
✓ Test: 25/25 (pass tất cả test cases)
━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL: 90/100
```

#### Code: `fff`
```
✗ Syntax: 0/25 (invalid syntax - undefined name 'fff')
✗ Requirement: 0/25 (không có input, print, +)
✗ Structure: 5/25 (không có structure)
✗ Test: 0/25 (không thể chạy vì syntax error)
━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL: 5/100
```

#### Code: `x = 1\ny = 2\nprint(x+y)` (thiếu input)
```
✓ Syntax: 25/25 (valid)
✗ Requirement: 15/25 (missing input, có print và +)
✓ Structure: 18/25 (good format)
✓ Test: 20/25 (1 test fail do keine input)
━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL: 78/100
```

### 5. **Giao Diện Kết Quả (ketquaSV.html)**

Cập nhật hiển thị:
- ✅ Xóa text "là là là là là"
- ✅ Hiển thị điểm từng component (Syntax/Requirement/Structure/Test)
- ✅ Mỗi component ra /25 (không phải /100)
- ✅ Tổng điểm /100 với gradient
- ✅ Feedback tương ứng:
  - 90-100: "Xuất sắc!"
  - 80-89: "Tốt lắm!"
  - 70-79: "Được rồi nhưng cần cải thiện"
  - 60-69: "Cần cố gắng hơn"
  - <60: "Cần ôn lại"

### 6. **Database Changes**

Agent logs được tạo tự động:
```sql
INSERT INTO agent_logs (submission_id, agent_name, result)
VALUES 
  (id, 'SyntaxAgent', 'Syntax: PASS/FAIL - error_msg'),
  (id, 'RequirementAgent', 'Requirements met: 3/3'),
  (id, 'StructureAgent', 'Structure: good'),
  (id, 'TestAgent', 'Tests passed: 3/3')
```

Evaluation session lưu chi tiết:
```sql
INSERT INTO evaluation_sessions 
  (syntax_score, structure_score, requirement_score, test_score, 
   total_score, agent_details)
VALUES 
  (25, 15, 25, 20, 85, 
   '{"syntax":..., "requirement":{"score":25,"details":[...]}, ...}')
```

## Cách Sử Dụng

1. **Sinh viên submit code**:
   - Gửi file `.py` hoặc nhập code trực tiếp
   - Backend tự động chạy coordinator

2. **Coordinator chạy**:
   ```python
   result = coordinator(code, requirements, testcases)
   ```

3. **Kết quả lưu DB** với chi tiết đầy đủ

4. **Hiển thị ketquaSV.html** với điểm chi tiết từng agent

## Test Cases từ seed_test_data.sql

```sql
-- Input 1: "2\n3", Expected: "5"
-- Input 2: "10\n20", Expected: "30"  
-- Input 3: "7\n8", Expected: "15"
```

Requirements:
```sql
-- "Có dùng input()"
-- "Có phép cộng"
-- "Có print()"
```

## Tệ Tin Thay Đổi

✅ **app.py**:
- Thêm imports: `ast`, `re`, `subprocess`, `json`
- Thêm classes: `SyntaxAgent`, `RequirementAgent`, `StructureAgent`, `TestAgent`
- Thêm function: `coordinator()`
- Update `/submit` endpoint để sử dụng coordinator thực

✅ **templates/ketquaSV.html**:
- Xóa text "là là là là"
- Cập nhật score hiển thị (từng component /25)
- Thêm emojis và color coding
- Thêm feedback message dựa trên tổng điểm

## Lợi Ích

✅ Chấm điểm **thực tế** dựa trên code quality  
✅ Sinh viên **không thể** được 95 điểm cho "fff"  
✅ **Chi tiết** feedback từng phần để sinh viên học hỏi  
✅ **Tự động** chạy test cases  
✅ **Có thể mở rộng** để thêm agents mới  
✅ **Lưu trữ** chi tiết đánh giá cho tracking

---

**Lưu ý**: TestAgent dùng `subprocess` để chạy Python code, có timeout 5 giây để tránh infinite loops.
