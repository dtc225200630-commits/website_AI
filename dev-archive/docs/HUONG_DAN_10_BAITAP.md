# Hướng Dẫn 10 Bài Tập Mới - SQL PostgreSQL

## 📋 Danh Sách 10 Bài Tập Mới (Assignment 2-11)

### Assignment 2: Kiểm tra số chẵn/lẻ
- **Mô tả**: Nhập một số và kiểm tra xem nó là số chẵn hay số lẻ
- **Yêu cầu**:
  - Có dùng input()
  - Có phép chia lấy dư (%)
  - Có print() kết quả "chẵn" hoặc "lẻ"
- **Test case**: 4 → chẵn, 7 → lẻ, 0 → chẵn

### Assignment 3: Tính giai thừa
- **Mô tả**: Nhập một số n, tính n! (n × (n-1) × ... × 1)
- **Yêu cầu**:
  - Có dùng input() và int()
  - Có sử dụng vòng lặp (for hoặc while)
  - Có tính toán và in ra giai thừa
- **Test case**: 5 → 120, 3 → 6, 0 → 1

### Assignment 4: Tính tổng từ 1 đến n
- **Mô tả**: Nhập số n, tính tổng 1 + 2 + 3 + ... + n
- **Yêu cầu**:
  - Có dùng input() để nhập số n
  - Có vòng lặp hoặc công thức
  - Có print() kết quả tổng
- **Test case**: 5 → 15, 10 → 55, 1 → 1

### Assignment 5: Kiểm tra số nguyên tố
- **Mô tả**: Kiểm tra xem số có phải số nguyên tố không (chỉ chia hết cho 1 và chính nó)
- **Yêu cầu**:
  - Có dùng input() để nhập số
  - Có vòng lặp để kiểm tra chia hết
  - Có print() kết quả "là số nguyên tố" hoặc "không là số nguyên tố"
- **Test case**: 7 → là số nguyên tố, 4 → không là số nguyên tố, 2 → là số nguyên tố

### Assignment 6: Đảo ngược chuỗi
- **Mô tả**: Nhập chuỗi, in ra chuỗi đó theo thứ tự đảo ngược
- **Yêu cầu**:
  - Có dùng input() để nhập chuỗi
  - Có cách đảo ngược chuỗi (slicing hoặc vòng lặp)
  - Có print() chuỗi đảo ngược
- **Test case**: hello → olleh, Python → nohtyP, abc → cba

### Assignment 7: Tính trung bình cộng
- **Mô tả**: Nhập 3 số, tính trung bình cộng (làm tròn 2 chữ số thập phân)
- **Yêu cầu**:
  - Có dùng input() để nhập 3 số
  - Có tính tổng 3 số rồi chia cho 3
  - Có print() kết quả (làm tròn 2 chữ số)
- **Test case**: 5 10 15 → 10.00, 7 8 9 → 8.00, 3 6 9 → 6.00

### Assignment 8: Chuyển đổi nhiệt độ
- **Mô tả**: Nhập độ Celsius, chuyển sang Fahrenheit: F = (C × 9/5) + 32
- **Yêu cầu**:
  - Có dùng input() để nhập độ Celsius
  - Có công thức chuyển đổi đúng
  - Có print() kết quả Fahrenheit
- **Test case**: 0 → 32.0, 100 → 212.0, 25 → 77.0

### Assignment 9: Phân loại điểm
- **Mô tả**: Nhập điểm (0-10), phân loại: Xuất sắc (9-10), Tốt (7-8), Khá (5-6), Yếu (<5)
- **Yêu cầu**:
  - Có dùng input() để nhập điểm
  - Có if-elif-else
  - Có print() kết quả phân loại
- **Test case**: 9 → Xuất sắc, 7 → Tốt, 4 → Yếu

### Assignment 10: Máy tính đơn giản
- **Mô tả**: Nhập 2 số và phép toán (+, -, *, /), in kết quả
- **Yêu cầu**:
  - Có dùng input() để nhập 2 số và phép toán
  - Có if-elif để xử lý phép toán
  - Có print() kết quả
- **Test case**: 10 5 + → 15, 10 5 - → 5, 10 5 * → 50

### Assignment 11: Đếm ký tự trong chuỗi
- **Mô tả**: Nhập chuỗi, đếm số ký tự (không tính khoảng trắng)
- **Yêu cầu**:
  - Có dùng input() để nhập chuỗi
  - Có len() hoặc vòng lặp để đếm
  - Có print() số ký tự (loại bỏ khoảng trắng)
- **Test case**: hello world → 10, python → 6, a b c → 3

---

## 🚀 Cách Chạy SQL trong PostgreSQL

### Phương pháp 1: Sử dụng psql command line

```bash
# Kết nối đến PostgreSQL
psql -U postgres -d assignment_db

# Sau đó chạy file SQL
\i 'c:/AI1 - Copy (3) - Copy/seed_10_assignments.sql'
```

### Phương pháp 2: Chạy file SQL trực tiếp

```bash
psql -U postgres -d assignment_db -f "c:/AI1 - Copy (3) - Copy/seed_10_assignments.sql"
```

### Phương pháp 3: Sử dụng Python script

```python
import psycopg2

# Kết nối đến database
conn = psycopg2.connect(
    host="localhost",
    database="assignment_db",
    user="postgres",
    password="your_password"
)

cursor = conn.cursor()

# Đọc file SQL
with open('seed_10_assignments.sql', 'r') as f:
    sql = f.read()

# Thực thi
cursor.execute(sql)
conn.commit()

cursor.close()
conn.close()

print("✅ Dữ liệu đã được thêm thành công!")
```

---

## 📊 Thống Kê Dữ Liệu

| Thành phần | Số lượng |
|-----------|---------|
| Bài tập mới | 10 (Assignment 2-11) |
| Yêu cầu (Requirements) | 30 (3 yêu cầu mỗi bài) |
| Test case | 30 (3 test case mỗi bài) |
| Bài nộp (Submissions) | 100 (10 sinh viên × 10 bài) |
| Đánh giá (Evaluations) | 100 (mỗi bài nộp) |
| Agent logs | 50 (đại diện cho tất cả) |

---

## ✅ Xác Minh Dữ Liệu Sau Khi Chạy

Chạy các câu query để kiểm tra:

```sql
-- Kiểm tra số lượng assignments
SELECT COUNT(*) as total_assignments FROM assignments;
-- Kết quả mong đợi: 11 (1 cũ + 10 mới)

-- Kiểm tra số lượng requirements
SELECT COUNT(*) as total_requirements FROM assignment_requirements;
-- Kết quả mong đợi: 33 (3 cũ + 30 mới)

-- Kiểm tra số lượng test cases
SELECT COUNT(*) as total_testcases FROM assignment_testcases;
-- Kết quả mong đợi: 33 (3 cũ + 30 mới)

-- Kiểm tra số lượng submissions
SELECT COUNT(*) as total_submissions FROM submissions;
-- Kết quả mong đợi: 110 (10 cũ + 100 mới)

-- Kiểm tra số lượng evaluations
SELECT COUNT(*) as total_evaluations FROM evaluation_sessions;
-- Kết quả mong đợi: 110 (10 cũ + 100 mới)

-- Xem chi tiết các assignments
SELECT assignment_id, title, due_date FROM assignments ORDER BY assignment_id;

-- Xem yêu cầu của assignment 2
SELECT * FROM assignment_requirements WHERE assignment_id = 2;

-- Xem test cases của assignment 3
SELECT * FROM assignment_testcases WHERE assignment_id = 3;

-- Xem tất cả submissions của assignment 2
SELECT s.submission_id, s.student_id, s.file_name, es.total_score 
FROM submissions s
JOIN evaluation_sessions es ON s.submission_id = es.submission_id
WHERE s.assignment_id = 2;
```

---

## 📝 Ghi Chú Quan Trọng

1. **ID bắt đầu từ 2**: Assignments 2-11 (Assignment 1 đã có sẵn)
2. **Submissions bắt đầu từ ID 11**: Submissions 11-110
3. **Evaluation sessions bắt đầu từ ID 11**: Evaluations 11-110
4. **Tất cả 10 sinh viên** có submission cho mỗi bài tập
5. **Điểm số đa dạng** từ 88 đến 100 để mô phỏng thực tế
6. **Agent logs** được thêm cho các submissions đầu tiên của mỗi bài

---

## 🔧 Chỉnh Sửa Dữ Liệu Nếu Cần

### Thêm bài tập khác (Assignment 12)

```sql
INSERT INTO assignments (class_id, title, description, due_date, programming_language)
VALUES (1, 'Tên bài tập', 'Mô tả', '2027-03-01 23:59:00', 'Python');

INSERT INTO assignment_requirements (assignment_id, requirement_text, weight)
VALUES 
(12, 'Yêu cầu 1', 10),
(12, 'Yêu cầu 2', 10),
(12, 'Yêu cầu 3', 10);

INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight)
VALUES
(12, 'input1', 'output1', 10),
(12, 'input2', 'output2', 10),
(12, 'input3', 'output3', 10);
```

---

**✨ Xong! Bạn đã có 10 bài tập đầy đủ với yêu cầu, test case, submissions và đánh giá!**
