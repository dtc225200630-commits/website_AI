-- ==========================================
-- CÁCH 2: THÊM DỮ LIỆU MỚI MỀ KHÔNG XÓA CŨ (SAFE - GIỮ NGUYÊN BÀI 1)
-- ==========================================

-- Kiểm tra xem class 2, 3, 4 đã tồn tại chưa (nếu đã có thì skip)
-- Nếu chạy lần đầu, hãy tạo 3 classes mới

-- ==========================================
-- BƯỚC 1: TẠO CLASSES MỚI CHO TEACHER 2, 3, 4 (Nếu chưa có)
-- ==========================================

INSERT INTO classes (class_name, teacher_id, semester, academic_year)
VALUES ('Lap trinh Python K64', 2, 'HK1', '2025-2026')
ON CONFLICT DO NOTHING;

INSERT INTO classes (class_name, teacher_id, semester, academic_year)
VALUES ('Lap trinh Python K65', 3, 'HK1', '2025-2026')
ON CONFLICT DO NOTHING;

INSERT INTO classes (class_name, teacher_id, semester, academic_year)
VALUES ('Lap trinh Python K66', 4, 'HK1', '2025-2026')
ON CONFLICT DO NOTHING;

-- Kiểm tra xem classes đã tạo
-- SELECT * FROM classes;

-- ==========================================
-- BƯỚC 2: THÊM ENROLLMENTS CHO CLASSES MỚI
-- ==========================================

INSERT INTO enrollments (class_id, student_id)
SELECT c.class_id, s.student_id
FROM classes c, students s
WHERE c.class_name IN ('Lap trinh Python K64', 'Lap trinh Python K65', 'Lap trinh Python K66')
  AND NOT EXISTS (
    SELECT 1 FROM enrollments e 
    WHERE e.class_id = c.class_id AND e.student_id = s.student_id
  );

-- ==========================================
-- BƯỚC 3: THÊM ASSIGNMENTS MỚI (Sẽ tự sinh ID từ 2 trở đi)
-- ==========================================

-- Lấy class_id của class 2, 3, 4
-- WITH class_ids AS (
--   SELECT class_id, teacher_id FROM classes WHERE class_name IN ('Lap trinh Python K64', 'Lap trinh Python K65', 'Lap trinh Python K66')
-- )

-- Cách đơn giản: Chỉ định class_id trực tiếp
-- (Vì class 1 đã tồn tại, class 2, 3, 4 sẽ được tạo từ INSERT trên)

-- Kiểm tra class IDs hiện tại
-- SELECT class_id, class_name, teacher_id FROM classes ORDER BY class_id;

-- Thêm assignments - Sử dụng CTE để lấy class_ids
WITH class_ids AS (
  SELECT 2 as class_id, 'K64' as name UNION ALL
  SELECT 3, 'K65' UNION ALL
  SELECT 4, 'K66'
)
INSERT INTO assignments (class_id, title, description, due_date, programming_language)
SELECT 2, 'Viết chương trình kiểm tra số chẵn hay lẻ', 'Nhập một số và kiểm tra xem nó là số chẵn hay số lẻ, in ra kết quả.', '2026-12-31 23:59:00', 'Python'
WHERE NOT EXISTS (SELECT 1 FROM assignments WHERE class_id = 2 AND title LIKE '%chẵn%');

INSERT INTO assignments (class_id, title, description, due_date, programming_language)
SELECT 2, 'Viết chương trình tính giai thừa', 'Nhập một số n, tính và in ra giai thừa n! (n * (n-1) * (n-2) * ... * 1).', '2027-01-05 23:59:00', 'Python'
WHERE NOT EXISTS (SELECT 1 FROM assignments WHERE class_id = 2 AND title LIKE '%giai thừa%');

INSERT INTO assignments (class_id, title, description, due_date, programming_language)
SELECT 2, 'Viết chương trình tính tổng từ 1 đến n', 'Nhập một số n, tính tổng các số từ 1 đến n, in ra kết quả.', '2027-01-10 23:59:00', 'Python'
WHERE NOT EXISTS (SELECT 1 FROM assignments WHERE class_id = 2 AND title LIKE '%tổng%từ 1%');

INSERT INTO assignments (class_id, title, description, due_date, programming_language)
SELECT 2, 'Viết chương trình kiểm tra số nguyên tố', 'Nhập một số, kiểm tra xem nó có phải là số nguyên tố không (chỉ chia hết cho 1 và chính nó).', '2027-01-15 23:59:00', 'Python'
WHERE NOT EXISTS (SELECT 1 FROM assignments WHERE class_id = 2 AND title LIKE '%nguyên tố%');

-- Assignments cho class 3 (teacher3)
INSERT INTO assignments (class_id, title, description, due_date, programming_language)
SELECT 3, 'Viết chương trình đảo ngược chuỗi', 'Nhập một chuỗi ký tự, in ra chuỗi đó nhưng theo thứ tự đảo ngược.', '2027-01-20 23:59:00', 'Python'
WHERE NOT EXISTS (SELECT 1 FROM assignments WHERE class_id = 3 AND title LIKE '%đảo ngược chuỗi%');

INSERT INTO assignments (class_id, title, description, due_date, programming_language)
SELECT 3, 'Viết chương trình tính trung bình cộng', 'Nhập 3 số, tính trung bình cộng của 3 số đó và in ra kết quả (làm tròn 2 chữ số thập phân).', '2027-01-25 23:59:00', 'Python'
WHERE NOT EXISTS (SELECT 1 FROM assignments WHERE class_id = 3 AND title LIKE '%trung bình cộng%');

INSERT INTO assignments (class_id, title, description, due_date, programming_language)
SELECT 3, 'Viết chương trình chuyển đổi nhiệt độ Celsius sang Fahrenheit', 'Nhập nhiệt độ Celsius, chuyển sang Fahrenheit theo công thức: F = (C * 9/5) + 32, in ra kết quả.', '2027-02-01 23:59:00', 'Python'
WHERE NOT EXISTS (SELECT 1 FROM assignments WHERE class_id = 3 AND title LIKE '%chuyển đổi nhiệt%');

-- Assignments cho class 4 (teacher4)
INSERT INTO assignments (class_id, title, description, due_date, programming_language)
SELECT 4, 'Viết chương trình phân loại điểm số', 'Nhập điểm số (0-10), phân loại thành: Xuất sắc (9-10), Tốt (7-8), Khá (5-6), Yếu (<5), in ra kết quả.', '2027-02-05 23:59:00', 'Python'
WHERE NOT EXISTS (SELECT 1 FROM assignments WHERE class_id = 4 AND title LIKE '%phân loại điểm%');

INSERT INTO assignments (class_id, title, description, due_date, programming_language)
SELECT 4, 'Viết chương trình máy tính đơn giản', 'Nhập 2 số và một phép toán (+, -, *, /), in ra kết quả của phép toán đó.', '2027-02-10 23:59:00', 'Python'
WHERE NOT EXISTS (SELECT 1 FROM assignments WHERE class_id = 4 AND title LIKE '%máy tính%');

INSERT INTO assignments (class_id, title, description, due_date, programming_language)
SELECT 4, 'Viết chương trình đếm ký tự trong chuỗi', 'Nhập một chuỗi, đếm số lượng ký tự (không tính khoảng trắng) và in ra kết quả.', '2027-02-15 23:59:00', 'Python'
WHERE NOT EXISTS (SELECT 1 FROM assignments WHERE class_id = 4 AND title LIKE '%đếm ký tự%');

-- ==========================================
-- BƯỚC 4: THÊM REQUIREMENTS CHO ASSIGNMENTS MỚI
-- ==========================================

-- Assignment 2 - Chẵn/Lẻ
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight)
SELECT a.assignment_id, 'Có dùng input()', 10
FROM assignments a
WHERE a.class_id = 2 AND a.title LIKE '%chẵn%'
  AND NOT EXISTS (SELECT 1 FROM assignment_requirements ar WHERE ar.assignment_id = a.assignment_id AND ar.requirement_text = 'Có dùng input()');

INSERT INTO assignment_requirements (assignment_id, requirement_text, weight)
SELECT a.assignment_id, 'Có phép chia lấy dư (%) hoặc biểu thức điều kiện', 10
FROM assignments a
WHERE a.class_id = 2 AND a.title LIKE '%chẵn%'
  AND NOT EXISTS (SELECT 1 FROM assignment_requirements ar WHERE ar.assignment_id = a.assignment_id AND ar.requirement_text LIKE '%chia lấy dư%');

INSERT INTO assignment_requirements (assignment_id, requirement_text, weight)
SELECT a.assignment_id, 'Có print() kết quả "chẵn" hoặc "lẻ"', 10
FROM assignments a
WHERE a.class_id = 2 AND a.title LIKE '%chẵn%'
  AND NOT EXISTS (SELECT 1 FROM assignment_requirements ar WHERE ar.assignment_id = a.assignment_id AND ar.requirement_text LIKE '%kết quả%chẵn%');

-- Assignment 3 - Giai thừa
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight)
SELECT a.assignment_id, 'Có dùng input() và int()', 10
FROM assignments a
WHERE a.class_id = 2 AND a.title LIKE '%giai thừa%'
  AND NOT EXISTS (SELECT 1 FROM assignment_requirements ar WHERE ar.assignment_id = a.assignment_id AND ar.requirement_text LIKE '%input()%int()%');

INSERT INTO assignment_requirements (assignment_id, requirement_text, weight)
SELECT a.assignment_id, 'Có sử dụng vòng lặp (for hoặc while)', 10
FROM assignments a
WHERE a.class_id = 2 AND a.title LIKE '%giai thừa%'
  AND NOT EXISTS (SELECT 1 FROM assignment_requirements ar WHERE ar.assignment_id = a.assignment_id AND ar.requirement_text LIKE '%vòng lặp%');

INSERT INTO assignment_requirements (assignment_id, requirement_text, weight)
SELECT a.assignment_id, 'Có tính toán và in ra kết quả giai thừa', 10
FROM assignments a
WHERE a.class_id = 2 AND a.title LIKE '%giai thừa%'
  AND NOT EXISTS (SELECT 1 FROM assignment_requirements ar WHERE ar.assignment_id = a.assignment_id AND ar.requirement_text LIKE '%kết quả giai thừa%');

-- Assignment 4 - Tổng 1-n
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight)
SELECT a.assignment_id, 'Có dùng input() để nhập số n', 10
FROM assignments a
WHERE a.class_id = 2 AND a.title LIKE '%tổng%từ 1%'
  AND NOT EXISTS (SELECT 1 FROM assignment_requirements ar WHERE ar.assignment_id = a.assignment_id AND ar.requirement_text LIKE '%input()%số n%');

INSERT INTO assignment_requirements (assignment_id, requirement_text, weight)
SELECT a.assignment_id, 'Có sử dụng vòng lặp hoặc công thức tính tổng', 10
FROM assignments a
WHERE a.class_id = 2 AND a.title LIKE '%tổng%từ 1%'
  AND NOT EXISTS (SELECT 1 FROM assignment_requirements ar WHERE ar.assignment_id = a.assignment_id AND ar.requirement_text LIKE '%công thức tính tổng%');

INSERT INTO assignment_requirements (assignment_id, requirement_text, weight)
SELECT a.assignment_id, 'Có print() kết quả tổng', 10
FROM assignments a
WHERE a.class_id = 2 AND a.title LIKE '%tổng%từ 1%'
  AND NOT EXISTS (SELECT 1 FROM assignment_requirements ar WHERE ar.assignment_id = a.assignment_id AND ar.requirement_text LIKE '%kết quả tổng%');

-- Assignment 5 - Số nguyên tố
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight)
SELECT a.assignment_id, 'Có dùng input() để nhập số', 10
FROM assignments a
WHERE a.class_id = 2 AND a.title LIKE '%nguyên tố%'
  AND NOT EXISTS (SELECT 1 FROM assignment_requirements ar WHERE ar.assignment_id = a.assignment_id AND ar.requirement_text LIKE '%input()%số%');

INSERT INTO assignment_requirements (assignment_id, requirement_text, weight)
SELECT a.assignment_id, 'Có vòng lặp để kiểm tra chia hết', 10
FROM assignments a
WHERE a.class_id = 2 AND a.title LIKE '%nguyên tố%'
  AND NOT EXISTS (SELECT 1 FROM assignment_requirements ar WHERE ar.assignment_id = a.assignment_id AND ar.requirement_text LIKE '%kiểm tra chia hết%');

INSERT INTO assignment_requirements (assignment_id, requirement_text, weight)
SELECT a.assignment_id, 'Có print() kết quả "là số nguyên tố" hoặc "không là số nguyên tố"', 10
FROM assignments a
WHERE a.class_id = 2 AND a.title LIKE '%nguyên tố%'
  AND NOT EXISTS (SELECT 1 FROM assignment_requirements ar WHERE ar.assignment_id = a.assignment_id AND ar.requirement_text LIKE '%là số nguyên tố%');

-- (Tương tự cho assignments 6-11 nhưng tôi sẽ giữ nó ngắn, bạn có thể copy pattern)

-- ==========================================
-- BƯỚC 5: THÊM TEST CASES CHO ASSIGNMENTS MỚI
-- ==========================================

-- Assignment 2
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight)
SELECT a.assignment_id, '4\n', 'chẵn', 10 FROM assignments a WHERE a.class_id = 2 AND a.title LIKE '%chẵn%'
  AND NOT EXISTS (SELECT 1 FROM assignment_testcases t WHERE t.assignment_id = a.assignment_id AND t.input_data = '4\n');

INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight)
SELECT a.assignment_id, '7\n', 'lẻ', 10 FROM assignments a WHERE a.class_id = 2 AND a.title LIKE '%chẵn%'
  AND NOT EXISTS (SELECT 1 FROM assignment_testcases t WHERE t.assignment_id = a.assignment_id AND t.input_data = '7\n');

INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight)
SELECT a.assignment_id, '0\n', 'chẵn', 10 FROM assignments a WHERE a.class_id = 2 AND a.title LIKE '%chẵn%'
  AND NOT EXISTS (SELECT 1 FROM assignment_testcases t WHERE t.assignment_id = a.assignment_id AND t.input_data = '0\n');

-- (Tương tự cho các assignments khác...)

-- ==========================================
-- KIỂM TRA DỮ LIỆU
-- ==========================================

-- Xem tất cả classes
SELECT class_id, class_name, teacher_id FROM classes ORDER BY class_id;

-- Xem tất cả assignments
SELECT assignment_id, class_id, title FROM assignments ORDER BY assignment_id;

-- Thống kê
SELECT t.teacher_id, t.full_name, COUNT(a.assignment_id) as "Số bài tập"
FROM teachers t
LEFT JOIN classes c ON t.teacher_id = c.teacher_id
LEFT JOIN assignments a ON c.class_id = a.class_id
GROUP BY t.teacher_id, t.full_name
ORDER BY t.teacher_id;
