-- ==========================================
-- CHẠY TRỰC TIẾP TRONG POSTGRESQL
-- ==========================================
-- Giải thích: psql -U postgres -d assignment_db -f "..." 
-- là câu lệnh dòng lệnh (cmd/PowerShell) để chạy file SQL
-- Dưới đây là SQL để chạy TRỰ TIẾP trong PostgreSQL GUI (pgAdmin hoặc psql interactive)

-- ==========================================
-- 1. THÊM 10 BÀI TẬP MỚI - MỘT LỚP CHO MỖI GIÁO VIÊN
-- ==========================================

-- Tạo lớp cho teacher2
INSERT INTO classes (class_name, teacher_id, semester, academic_year)
VALUES
('Lap trinh Python K64', 2, 'HK1', '2025-2026');

-- Tạo lớp cho teacher3
INSERT INTO classes (class_name, teacher_id, semester, academic_year)
VALUES
('Lap trinh Python K65', 3, 'HK1', '2025-2026');

-- Tạo lớp cho teacher4
INSERT INTO classes (class_name, teacher_id, semester, academic_year)
VALUES
('Lap trinh Python K66', 4, 'HK1', '2025-2026');

-- ==========================================
-- Kiểm tra classes đã tạo
-- ==========================================
-- SELECT * FROM classes;
-- Kết quả phải có 4 lớp (class_id 1, 2, 3, 4)

-- ==========================================
-- 2. PHÂN CÁC BÀI TẬP CHO GIÁO VIÊN KHÁC
-- ==========================================

-- ==========================================
-- BÀI TẬP CHO TEACHER 2 (Class 2)
-- ==========================================

-- Assignment 2 cho teacher2
INSERT INTO assignments (class_id, title, description, due_date, programming_language)
VALUES (2, 'Viết chương trình kiểm tra số chẵn hay lẻ', 'Nhập một số và kiểm tra xem nó là số chẵn hay số lẻ, in ra kết quả.', '2026-12-31 23:59:00', 'Python');

INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'Có dùng input()', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'Có phép chia lấy dư (%) hoặc biểu thức điều kiện', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'Có print() kết quả "chẵn" hoặc "lẻ"', 10);

INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), '4\n', 'chẵn', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), '7\n', 'lẻ', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), '0\n', 'chẵn', 10);

-- Assignment 3 cho teacher2
INSERT INTO assignments (class_id, title, description, due_date, programming_language)
VALUES (2, 'Viết chương trình tính giai thừa', 'Nhập một số n, tính và in ra giai thừa n! (n * (n-1) * (n-2) * ... * 1).', '2027-01-05 23:59:00', 'Python');

INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'Có dùng input() và int()', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'Có sử dụng vòng lặp (for hoặc while)', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'Có tính toán và in ra kết quả giai thừa', 10);

INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), '5\n', '120', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), '3\n', '6', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), '0\n', '1', 10);

-- Assignment 4 cho teacher2
INSERT INTO assignments (class_id, title, description, due_date, programming_language)
VALUES (2, 'Viết chương trình tính tổng từ 1 đến n', 'Nhập một số n, tính tổng các số từ 1 đến n, in ra kết quả.', '2027-01-10 23:59:00', 'Python');

INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'Có dùng input() để nhập số n', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'Có sử dụng vòng lặp hoặc công thức tính tổng', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'Có print() kết quả tổng', 10);

INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), '5\n', '15', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), '10\n', '55', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), '1\n', '1', 10);

-- Assignment 5 cho teacher2
INSERT INTO assignments (class_id, title, description, due_date, programming_language)
VALUES (2, 'Viết chương trình kiểm tra số nguyên tố', 'Nhập một số, kiểm tra xem nó có phải là số nguyên tố không (chỉ chia hết cho 1 và chính nó).', '2027-01-15 23:59:00', 'Python');

INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'Có dùng input() để nhập số', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'Có vòng lặp để kiểm tra chia hết', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'Có print() kết quả "là số nguyên tố" hoặc "không là số nguyên tố"', 10);

INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), '7\n', 'là số nguyên tố', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), '4\n', 'không là số nguyên tố', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), '2\n', 'là số nguyên tố', 10);

-- ==========================================
-- BÀI TẬP CHO TEACHER 3 (Class 3)
-- ==========================================

-- Assignment 6 cho teacher3
INSERT INTO assignments (class_id, title, description, due_date, programming_language)
VALUES (3, 'Viết chương trình đảo ngược chuỗi', 'Nhập một chuỗi ký tự, in ra chuỗi đó nhưng theo thứ tự đảo ngược.', '2027-01-20 23:59:00', 'Python');

INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'Có dùng input() để nhập chuỗi', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'Có cách đảo ngược chuỗi (slicing hoặc vòng lặp)', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'Có print() chuỗi đảo ngược', 10);

INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'hello\n', 'olleh', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'Python\n', 'nohtyP', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'abc\n', 'cba', 10);

-- Assignment 7 cho teacher3
INSERT INTO assignments (class_id, title, description, due_date, programming_language)
VALUES (3, 'Viết chương trình tính trung bình cộng', 'Nhập 3 số, tính trung bình cộng của 3 số đó và in ra kết quả (làm tròn 2 chữ số thập phân).', '2027-01-25 23:59:00', 'Python');

INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'Có dùng input() để nhập 3 số', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'Có tính tổng 3 số rồi chia cho 3', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'Có print() kết quả trung bình cộng (làm tròn)', 10);

INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), '5\n10\n15\n', '10.00', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), '7\n8\n9\n', '8.00', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), '3\n6\n9\n', '6.00', 10);

-- Assignment 8 cho teacher3
INSERT INTO assignments (class_id, title, description, due_date, programming_language)
VALUES (3, 'Viết chương trình chuyển đổi nhiệt độ Celsius sang Fahrenheit', 'Nhập nhiệt độ Celsius, chuyển sang Fahrenheit theo công thức: F = (C * 9/5) + 32, in ra kết quả.', '2027-02-01 23:59:00', 'Python');

INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'Có dùng input() để nhập độ Celsius', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'Có công thức chuyển đổi đúng: F = (C * 9/5) + 32', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'Có print() kết quả nhiệt độ Fahrenheit', 10);

INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), '0\n', '32.0', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), '100\n', '212.0', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), '25\n', '77.0', 10);

-- ==========================================
-- BÀI TẬP CHO TEACHER 4 (Class 4)
-- ==========================================

-- Assignment 9 cho teacher4
INSERT INTO assignments (class_id, title, description, due_date, programming_language)
VALUES (4, 'Viết chương trình phân loại điểm số', 'Nhập điểm số (0-10), phân loại thành: Xuất sắc (9-10), Tốt (7-8), Khá (5-6), Yếu (<5), in ra kết quả.', '2027-02-05 23:59:00', 'Python');

INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'Có dùng input() để nhập điểm số', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'Có sử dụng if-elif-else hoặc cấu trúc điều kiện', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'Có print() kết quả phân loại đúng theo khoảng điểm', 10);

INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), '9\n', 'Xuất sắc', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), '7\n', 'Tốt', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), '4\n', 'Yếu', 10);

-- Assignment 10 cho teacher4
INSERT INTO assignments (class_id, title, description, due_date, programming_language)
VALUES (4, 'Viết chương trình máy tính đơn giản', 'Nhập 2 số và một phép toán (+, -, *, /), in ra kết quả của phép toán đó.', '2027-02-10 23:59:00', 'Python');

INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'Có dùng input() để nhập 2 số và phép toán', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'Có sử dụng if-elif hoặc cấu trúc xử lý phép toán', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'Có print() kết quả phép toán', 10);

INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), '10\n5\n+\n', '15', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), '10\n5\n-\n', '5', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), '10\n5\n*\n', '50', 10);

-- Assignment 11 cho teacher4
INSERT INTO assignments (class_id, title, description, due_date, programming_language)
VALUES (4, 'Viết chương trình đếm ký tự trong chuỗi', 'Nhập một chuỗi, đếm số lượng ký tự (không tính khoảng trắng) và in ra kết quả.', '2027-02-15 23:59:00', 'Python');

INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'Có dùng input() để nhập chuỗi', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'Có hàm len() hoặc vòng lặp để đếm ký tự', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'Có print() số lượng ký tự (loại bỏ khoảng trắng)', 10);

INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'hello world\n', '10', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'python\n', '6', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES ((SELECT MAX(assignment_id) FROM assignments), 'a b c\n', '3', 10);

-- ==========================================
-- KIỂM TRA DỮ LIỆU ĐÃ TẠO
-- ==========================================

-- Xem tất cả classes
SELECT * FROM classes;

-- Xem tất cả assignments
SELECT assignment_id, class_id, title FROM assignments ORDER BY assignment_id;

-- Xem assignments của teacher1 (class 1)
SELECT a.assignment_id, a.title, c.class_name, t.full_name as "Giáo viên"
FROM assignments a
JOIN classes c ON a.class_id = c.class_id
JOIN teachers t ON c.teacher_id = t.teacher_id
WHERE c.teacher_id = 1
ORDER BY a.assignment_id;

-- Xem assignments của teacher2 (class 2)
SELECT a.assignment_id, a.title, c.class_name, t.full_name as "Giáo viên"
FROM assignments a
JOIN classes c ON a.class_id = c.class_id
JOIN teachers t ON c.teacher_id = t.teacher_id
WHERE c.teacher_id = 2
ORDER BY a.assignment_id;

-- Xem assignments của teacher3 (class 3)
SELECT a.assignment_id, a.title, c.class_name, t.full_name as "Giáo viên"
FROM assignments a
JOIN classes c ON a.class_id = c.class_id
JOIN teachers t ON c.teacher_id = t.teacher_id
WHERE c.teacher_id = 3
ORDER BY a.assignment_id;

-- Xem assignments của teacher4 (class 4)
SELECT a.assignment_id, a.title, c.class_name, t.full_name as "Giáo viên"
FROM assignments a
JOIN classes c ON a.class_id = c.class_id
JOIN teachers t ON c.teacher_id = t.teacher_id
WHERE c.teacher_id = 4
ORDER BY a.assignment_id;

-- Thống kê tổng bài tập của mỗi giáo viên
SELECT t.teacher_id, t.full_name, COUNT(a.assignment_id) as "Số bài tập"
FROM teachers t
LEFT JOIN classes c ON t.teacher_id = c.teacher_id
LEFT JOIN assignments a ON c.class_id = a.class_id
GROUP BY t.teacher_id, t.full_name
ORDER BY t.teacher_id;
