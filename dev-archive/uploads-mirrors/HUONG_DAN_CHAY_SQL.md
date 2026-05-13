# 🔧 HƯỚNG DẪN CHẠY SQL TRONG POSTGRESQL

## 📌 Giải Thích Câu Lệnh psql

### `psql -U postgres -d assignment_db -f "c:/AI1 - Copy (3) - Copy/seed_10_assignments.sql"`

- **psql** = Công cụ dòng lệnh (command line) của PostgreSQL
- **-U postgres** = Đăng nhập bằng user "postgres"
- **-d assignment_db** = Kết nối đến database "assignment_db"
- **-f** = Chạy file SQL (f = file)
- **"c:/AI1 - Copy (3) - Copy/seed_10_assignments.sql"** = Đường dẫn file SQL

**💡 Tóm tắt**: Câu lệnh này chạy file SQL tự động trong terminal/cmd/PowerShell

---

## ✅ CÁCH CHẠY TRONG POSTGRESQL (KHÔNG DÙNG TERMINAL)

### **Cách 1: Dùng pgAdmin 4 (Giao diện Web)**

1. Mở **pgAdmin 4** (http://localhost:5050)
2. Kết nối đến **assignment_db**
3. Click menu **Tools** → **Query Tool**
4. **Copy toàn bộ nội dung** file `add_assignments_multiple_teachers.sql`
5. **Paste vào** query editor
6. Click **Execute** (Ctrl + Enter hoặc nút ▶)
7. ✅ Hoàn tất!

### **Cách 2: Dùng psql Interactive (Command Line)**

```powershell
# Mở PowerShell
psql -U postgres

# Lệnh để kết nối đến database
\c assignment_db

# Chạy file SQL
\i 'c:/AI1 - Copy (3) - Copy/add_assignments_multiple_teachers.sql'

# Kiểm tra dữ liệu
SELECT * FROM assignments;
```

### **Cách 3: Dùng DBeaver (IDE Database)**

1. Mở **DBeaver**
2. Kế nối đến **assignment_db**
3. Click chuột phải → **SQL Editor** → **New SQL Script**
4. Copy nội dung file SQL
5. Click **Execute All** (Ctrl + Shift + E)
6. ✅ Xong!

---

## 🎯 BÀI TẬP CHO 4 GIÁO VIÊN

### **Teacher 1 (Người dạy lớp KTPM)**
- Class: "Lap trinh Python KTPM" (class_id = 1)
- Assignment 1: Cộng 2 số (từ file cũ)

### **Teacher 2 (Tran Thi B)**
- Class: "Lap trinh Python K64" (class_id = 2) - TẠO MỚI
- Assignment 2: Kiểm tra chẵn/lẻ
- Assignment 3: Tính giai thừa
- Assignment 4: Tính tổng từ 1-n
- Assignment 5: Kiểm tra số nguyên tố

### **Teacher 3 (Le Van C)**
- Class: "Lap trinh Python K65" (class_id = 3) - TẠO MỚI
- Assignment 6: Đảo ngược chuỗi
- Assignment 7: Tính trung bình cộng
- Assignment 8: Chuyển đổi nhiệt độ

### **Teacher 4 (Pham Thi D)**
- Class: "Lap trinh Python K66" (class_id = 4) - TẠO MỚI
- Assignment 9: Phân loại điểm
- Assignment 10: Máy tính đơn giản
- Assignment 11: Đếm ký tự

---

## 🚀 CÁCH CHẠY - BƯỚC THỨ NHẤT (Chắc chắn làm điều này trước)

**1. Tạo classes cho các giáo viên khác:**

Chạy SQL này trong PostgreSQL:

```sql
-- Tạo lớp cho teacher2
INSERT INTO classes (class_name, teacher_id, semester, academic_year)
VALUES ('Lap trinh Python K64', 2, 'HK1', '2025-2026');

-- Tạo lớp cho teacher3
INSERT INTO classes (class_name, teacher_id, semester, academic_year)
VALUES ('Lap trinh Python K65', 3, 'HK1', '2025-2026');

-- Tạo lớp cho teacher4
INSERT INTO classes (class_name, teacher_id, semester, academic_year)
VALUES ('Lap trinh Python K66', 4, 'HK1', '2025-2026');

-- Kiểm tra
SELECT * FROM classes;
```

---

## 🚀 CÁCH CHẠY - BƯỚC THỨ HAI

**2. Thêm assignments cho các giáo viên:**

Copy toàn bộ nội dung file `add_assignments_multiple_teachers.sql` và chạy trong PostgreSQL.

---

## 🚀 CÁCH CHẠY - BƯỚC THỨ BA (Nếu muốn thêm bài nộp + đánh giá)

**3. Thêm submissions và evaluations:**

```sql
-- SUBMISSIONS CHO TEACHER 2 - ASSIGNMENT 2
INSERT INTO submissions (assignment_id, student_id, file_name, source_code)
VALUES
(12, 1, 'bai2.py', 'n = int(input())\nif n % 2 == 0:\n    print("chẵn")\nelse:\n    print("lẻ")'),
(12, 2, 'bai2.py', 'num = int(input())\nif num % 2 == 0:\n    print("chẵn")\nelse:\n    print("lẻ")'),
(12, 3, 'bai2.py', 'x = int(input())\nif x % 2:\n    print("lẻ")\nelse:\n    print("chẵn")'),
(12, 4, 'bai2.py', 'n = int(input())\nprint("chẵn" if n % 2 == 0 else "lẻ")'),
(12, 5, 'bai2.py', 'a = int(input())\nif a % 2 == 0:\n    print("chẵn")\nelse:\n    print("lẻ")'),
(12, 6, 'bai2.py', 'num = int(input())\nif num % 2:\n    print("lẻ")\nelse:\n    print("chẵn")'),
(12, 7, 'bai2.py', 'n = int(input())\nif n % 2 == 0:\n    print("chẵn")\nelse:\n    print("lẻ")'),
(12, 8, 'bai2.py', 'x = int(input())\nprint("chẵn" if x % 2 == 0 else "lẻ")'),
(12, 9, 'bai2.py', 'n = int(input())\nif n % 2 == 0:\n    print("chẵn")\nelse:\n    print("lẻ")'),
(12, 10, 'bai2.py', 'num = int(input())\nif num % 2 == 0:\n    print("chẵn")\nelse:\n    print("lẻ")');

-- EVALUATIONS CHO TEACHER 2 - ASSIGNMENT 2
INSERT INTO evaluation_sessions (submission_id, syntax_score, code_analysis_score, structure_score, requirement_score, test_score, llm_score, total_score, final_feedback, agent_details)
VALUES
(111, 20, 18, 20, 20, 20, 19, 97, 'Xuất sắc! Code sạch và hoạt động chính xác.', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}'),
(112, 20, 18, 20, 20, 20, 19, 97, 'Code tốt, logic rõ ràng.', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}'),
(113, 20, 17, 18, 18, 18, 18, 91, 'Tốt nhưng có thể cải thiện logic.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(114, 20, 19, 20, 20, 20, 20, 99, 'Giải pháp tối ưu với ternary operator.', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}'),
(115, 20, 18, 20, 20, 20, 19, 97, 'Code chính xác và rõ ràng.', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}'),
(116, 20, 16, 17, 18, 18, 17, 90, 'Hoạt động nhưng cần cải thiện.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(117, 20, 18, 20, 20, 20, 19, 97, 'Rất tốt, code sạch.', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}'),
(118, 20, 19, 20, 20, 20, 20, 99, 'Xuất sắc! Giải pháp tối ưu.', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}'),
(119, 20, 18, 20, 20, 20, 19, 97, 'Code hoạt động chính xác.', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}'),
(120, 20, 18, 20, 20, 20, 19, 97, 'Tốt, logic đúng.', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}');
```

---

## ✅ KIỂM TRA DỮ LIỆU

Chạy những câu query này để xác minh:

```sql
-- Xem tất cả classes
SELECT * FROM classes;
-- Kết quả: 4 rows (classes 1-4)

-- Xem tất cả teachers
SELECT teacher_id, full_name FROM teachers;
-- Kết quả: 4 rows

-- Xem assignments của mỗi teacher
SELECT t.teacher_id, t.full_name, COUNT(a.assignment_id) as "Số bài tập"
FROM teachers t
LEFT JOIN classes c ON t.teacher_id = c.teacher_id
LEFT JOIN assignments a ON c.class_id = a.class_id
GROUP BY t.teacher_id, t.full_name
ORDER BY t.teacher_id;

-- Kết quả:
-- teacher_id | full_name | Số bài tập
-- 1          | Nguyen Van A | 1
-- 2          | Tran Thi B | 4
-- 3          | Le Van C | 3
-- 4          | Pham Thi D | 3

-- Xem assignments của teacher2 (K64)
SELECT a.assignment_id, a.title, c.class_name
FROM assignments a
JOIN classes c ON a.class_id = c.class_id
WHERE c.teacher_id = 2;

-- Xem assignments của teacher3 (K65)
SELECT a.assignment_id, a.title, c.class_name
FROM assignments a
JOIN classes c ON a.class_id = c.class_id
WHERE c.teacher_id = 3;

-- Xem assignments của teacher4 (K66)
SELECT a.assignment_id, a.title, c.class_name
FROM assignments a
JOIN classes c ON a.class_id = c.class_id
WHERE c.teacher_id = 4;
```

---

## 📝 NOTES

- **File cũ `seed_test_data.sql`**: Chứa 1 assignment cho teacher1
- **File mới `add_assignments_multiple_teachers.sql`**: Thêm 10 assignments cho 4 giáo viên
- **Bạn có thể chạy cả 2 file** mà không bị lỗi trùng lặp
- **Nếu chạy lại 2 lần**, kiểm tra dữ liệu bằng query trước khi chạy

---

## 🎓 TÓMO TẮT

| Giáo viên | Class ID | Class Name | Assignments | ID Bài Tập |
|-----------|----------|-----------|--------------|-----------|
| Nguyen Van A (teacher1) | 1 | Lap trinh Python KTPM | 1 | 1 |
| Tran Thi B (teacher2) | 2 | Lap trinh Python K64 | 4 | 12-15 |
| Le Van C (teacher3) | 3 | Lap trinh Python K65 | 3 | 16-18 |
| Pham Thi D (teacher4) | 4 | Lap trinh Python K66 | 3 | 19-21 |

**Tổng**: 11 assignments, 4 classes, 4 giáo viên ✅
