-- ==========================================
-- KIỂM TRA CLASSES
-- ==========================================
SELECT class_id, class_name, teacher_id FROM classes ORDER BY class_id;

-- ==========================================
-- THÊM ASSIGNMENTS CHO TEACHER 2, 3, 4
-- ==========================================

-- TEACHER 2 (Class 2) - 4 bài
INSERT INTO assignments (class_id, title, description, due_date, programming_language)
VALUES (2, 'Viết chương trình kiểm tra số chẵn hay lẻ', 'Nhập một số và kiểm tra xem nó là số chẵn hay số lẻ, in ra kết quả.', '2026-12-31 23:59:00', 'Python');

INSERT INTO assignments (class_id, title, description, due_date, programming_language)
VALUES (2, 'Viết chương trình tính giai thừa', 'Nhập một số n, tính và in ra giai thừa n! (n * (n-1) * (n-2) * ... * 1).', '2027-01-05 23:59:00', 'Python');

INSERT INTO assignments (class_id, title, description, due_date, programming_language)
VALUES (2, 'Viết chương trình tính tổng từ 1 đến n', 'Nhập một số n, tính tổng các số từ 1 đến n, in ra kết quả.', '2027-01-10 23:59:00', 'Python');

INSERT INTO assignments (class_id, title, description, due_date, programming_language)
VALUES (2, 'Viết chương trình kiểm tra số nguyên tố', 'Nhập một số, kiểm tra xem nó có phải là số nguyên tố không (chỉ chia hết cho 1 và chính nó).', '2027-01-15 23:59:00', 'Python');

-- TEACHER 3 (Class 3) - 3 bài
INSERT INTO assignments (class_id, title, description, due_date, programming_language)
VALUES (3, 'Viết chương trình đảo ngược chuỗi', 'Nhập một chuỗi ký tự, in ra chuỗi đó nhưng theo thứ tự đảo ngược.', '2027-01-20 23:59:00', 'Python');

INSERT INTO assignments (class_id, title, description, due_date, programming_language)
VALUES (3, 'Viết chương trình tính trung bình cộng', 'Nhập 3 số, tính trung bình cộng của 3 số đó và in ra kết quả (làm tròn 2 chữ số thập phân).', '2027-01-25 23:59:00', 'Python');

INSERT INTO assignments (class_id, title, description, due_date, programming_language)
VALUES (3, 'Viết chương trình chuyển đổi nhiệt độ Celsius sang Fahrenheit', 'Nhập nhiệt độ Celsius, chuyển sang Fahrenheit theo công thức: F = (C * 9/5) + 32, in ra kết quả.', '2027-02-01 23:59:00', 'Python');

-- TEACHER 4 (Class 4) - 3 bài
INSERT INTO assignments (class_id, title, description, due_date, programming_language)
VALUES (4, 'Viết chương trình phân loại điểm số', 'Nhập điểm số (0-10), phân loại thành: Xuất sắc (9-10), Tốt (7-8), Khá (5-6), Yếu (<5), in ra kết quả.', '2027-02-05 23:59:00', 'Python');

INSERT INTO assignments (class_id, title, description, due_date, programming_language)
VALUES (4, 'Viết chương trình máy tính đơn giản', 'Nhập 2 số và một phép toán (+, -, *, /), in ra kết quả của phép toán đó.', '2027-02-10 23:59:00', 'Python');

INSERT INTO assignments (class_id, title, description, due_date, programming_language)
VALUES (4, 'Viết chương trình đếm ký tự trong chuỗi', 'Nhập một chuỗi, đếm số lượng ký tự (không tính khoảng trắng) và in ra kết quả.', '2027-02-15 23:59:00', 'Python');

-- ==========================================
-- THÊM REQUIREMENTS CHO ASSIGNMENTS 2-11
-- ==========================================

-- Assignment 2 - Chẵn/Lẻ
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES (2, 'Có dùng input()', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES (2, 'Có phép chia lấy dư (%) hoặc biểu thức điều kiện', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES (2, 'Có print() kết quả "chẵn" hoặc "lẻ"', 10);

-- Assignment 3 - Giai thừa
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES (3, 'Có dùng input() và int()', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES (3, 'Có sử dụng vòng lặp (for hoặc while)', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES (3, 'Có tính toán và in ra kết quả giai thừa', 10);

-- Assignment 4 - Tổng 1-n
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES (4, 'Có dùng input() để nhập số n', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES (4, 'Có sử dụng vòng lặp hoặc công thức tính tổng', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES (4, 'Có print() kết quả tổng', 10);

-- Assignment 5 - Số nguyên tố
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES (5, 'Có dùng input() để nhập số', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES (5, 'Có vòng lặp để kiểm tra chia hết', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES (5, 'Có print() kết quả "là số nguyên tố" hoặc "không là số nguyên tố"', 10);

-- Assignment 6 - Đảo chuỗi
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES (6, 'Có dùng input() để nhập chuỗi', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES (6, 'Có cách đảo ngược chuỗi (slicing hoặc vòng lặp)', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES (6, 'Có print() chuỗi đảo ngược', 10);

-- Assignment 7 - Trung bình
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES (7, 'Có dùng input() để nhập 3 số', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES (7, 'Có tính tổng 3 số rồi chia cho 3', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES (7, 'Có print() kết quả trung bình cộng (làm tròn)', 10);

-- Assignment 8 - Chuyển nhiệt độ
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES (8, 'Có dùng input() để nhập độ Celsius', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES (8, 'Có công thức chuyển đổi đúng: F = (C * 9/5) + 32', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES (8, 'Có print() kết quả nhiệt độ Fahrenheit', 10);

-- Assignment 9 - Phân loại điểm
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES (9, 'Có dùng input() để nhập điểm số', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES (9, 'Có sử dụng if-elif-else hoặc cấu trúc điều kiện', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES (9, 'Có print() kết quả phân loại đúng theo khoảng điểm', 10);

-- Assignment 10 - Máy tính
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES (10, 'Có dùng input() để nhập 2 số và phép toán', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES (10, 'Có sử dụng if-elif hoặc cấu trúc xử lý phép toán', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES (10, 'Có print() kết quả phép toán', 10);

-- Assignment 11 - Đếm ký tự
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES (11, 'Có dùng input() để nhập chuỗi', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES (11, 'Có hàm len() hoặc vòng lặp để đếm ký tự', 10);
INSERT INTO assignment_requirements (assignment_id, requirement_text, weight) VALUES (11, 'Có print() số lượng ký tự (loại bỏ khoảng trắng)', 10);

-- ==========================================
-- THÊM TEST CASES CHO ASSIGNMENTS 2-11
-- ==========================================

-- Assignment 2
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES (2, '4\n', 'chẵn', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES (2, '7\n', 'lẻ', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES (2, '0\n', 'chẵn', 10);

-- Assignment 3
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES (3, '5\n', '120', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES (3, '3\n', '6', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES (3, '0\n', '1', 10);

-- Assignment 4
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES (4, '5\n', '15', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES (4, '10\n', '55', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES (4, '1\n', '1', 10);

-- Assignment 5
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES (5, '7\n', 'là số nguyên tố', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES (5, '4\n', 'không là số nguyên tố', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES (5, '2\n', 'là số nguyên tố', 10);

-- Assignment 6
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES (6, 'hello\n', 'olleh', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES (6, 'Python\n', 'nohtyP', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES (6, 'abc\n', 'cba', 10);

-- Assignment 7
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES (7, '5\n10\n15\n', '10.00', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES (7, '7\n8\n9\n', '8.00', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES (7, '3\n6\n9\n', '6.00', 10);

-- Assignment 8
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES (8, '0\n', '32.0', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES (8, '100\n', '212.0', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES (8, '25\n', '77.0', 10);

-- Assignment 9
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES (9, '9\n', 'Xuất sắc', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES (9, '7\n', 'Tốt', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES (9, '4\n', 'Yếu', 10);

-- Assignment 10
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES (10, '10\n5\n+\n', '15', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES (10, '10\n5\n-\n', '5', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES (10, '10\n5\n*\n', '50', 10);

-- Assignment 11
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES (11, 'hello world\n', '10', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES (11, 'python\n', '6', 10);
INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight) VALUES (11, 'a b c\n', '3', 10);

-- ==========================================
-- KIỂM TRA DỮ LIỆU SAU KHI THÊM
-- ==========================================

-- Xem assignments mới
SELECT assignment_id, class_id, title FROM assignments ORDER BY assignment_id;

-- Thống kê assignments của mỗi teacher
SELECT t.teacher_id, t.full_name, COUNT(a.assignment_id) as "Số bài tập"
FROM teachers t
LEFT JOIN classes c ON t.teacher_id = c.teacher_id
LEFT JOIN assignments a ON c.class_id = a.class_id
GROUP BY t.teacher_id, t.full_name
ORDER BY t.teacher_id;

-- Xem chi tiết assignments của teacher2
SELECT a.assignment_id, a.title, c.class_name
FROM assignments a
JOIN classes c ON a.class_id = c.class_id
WHERE c.teacher_id = 2;

-- Xem chi tiết assignments của teacher3
SELECT a.assignment_id, a.title, c.class_name
FROM assignments a
JOIN classes c ON a.class_id = c.class_id
WHERE c.teacher_id = 3;

-- Xem chi tiết assignments của teacher4
SELECT a.assignment_id, a.title, c.class_name
FROM assignments a
JOIN classes c ON a.class_id = c.class_id
WHERE c.teacher_id = 4;
