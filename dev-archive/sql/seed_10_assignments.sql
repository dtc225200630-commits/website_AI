-- ==========================================
-- THÊM 10 BÀI TẬP MỚI (ASSIGNMENT 2-11)
-- ==========================================

-- ==========================================
-- ASSIGNMENT 2: Kiểm tra số chẵn/lẻ
-- ==========================================

INSERT INTO assignments (class_id, title, description, due_date, programming_language)
VALUES
(
    1,
    'Viết chương trình kiểm tra số chẵn hay lẻ',
    'Nhập một số và kiểm tra xem nó là số chẵn hay số lẻ, in ra kết quả.',
    '2026-12-31 23:59:00',
    'Python'
);

INSERT INTO assignment_requirements (assignment_id, requirement_text, weight)
VALUES
(2, 'Có dùng input()', 10),
(2, 'Có phép chia lấy dư (%) hoặc biểu thức điều kiện', 10),
(2, 'Có print() kết quả "chẵn" hoặc "lẻ"', 10);

INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight)
VALUES
(2, '4\n', 'chẵn', 10),
(2, '7\n', 'lẻ', 10),
(2, '0\n', 'chẵn', 10);

-- ==========================================
-- ASSIGNMENT 3: Tính giai thừa
-- ==========================================

INSERT INTO assignments (class_id, title, description, due_date, programming_language)
VALUES
(
    1,
    'Viết chương trình tính giai thừa',
    'Nhập một số n, tính và in ra giai thừa n! (n * (n-1) * (n-2) * ... * 1).',
    '2027-01-05 23:59:00',
    'Python'
);

INSERT INTO assignment_requirements (assignment_id, requirement_text, weight)
VALUES
(3, 'Có dùng input() và int()', 10),
(3, 'Có sử dụng vòng lặp (for hoặc while)', 10),
(3, 'Có tính toán và in ra kết quả giai thừa', 10);

INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight)
VALUES
(3, '5\n', '120', 10),
(3, '3\n', '6', 10),
(3, '0\n', '1', 10);

-- ==========================================
-- ASSIGNMENT 4: Tính tổng các số từ 1 đến n
-- ==========================================

INSERT INTO assignments (class_id, title, description, due_date, programming_language)
VALUES
(
    1,
    'Viết chương trình tính tổng từ 1 đến n',
    'Nhập một số n, tính tổng các số từ 1 đến n, in ra kết quả.',
    '2027-01-10 23:59:00',
    'Python'
);

INSERT INTO assignment_requirements (assignment_id, requirement_text, weight)
VALUES
(4, 'Có dùng input() để nhập số n', 10),
(4, 'Có sử dụng vòng lặp hoặc công thức tính tổng', 10),
(4, 'Có print() kết quả tổng', 10);

INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight)
VALUES
(4, '5\n', '15', 10),
(4, '10\n', '55', 10),
(4, '1\n', '1', 10);

-- ==========================================
-- ASSIGNMENT 5: Kiểm tra số nguyên tố
-- ==========================================

INSERT INTO assignments (class_id, title, description, due_date, programming_language)
VALUES
(
    1,
    'Viết chương trình kiểm tra số nguyên tố',
    'Nhập một số, kiểm tra xem nó có phải là số nguyên tố không (chỉ chia hết cho 1 và chính nó).',
    '2027-01-15 23:59:00',
    'Python'
);

INSERT INTO assignment_requirements (assignment_id, requirement_text, weight)
VALUES
(5, 'Có dùng input() để nhập số', 10),
(5, 'Có vòng lặp để kiểm tra chia hết', 10),
(5, 'Có print() kết quả "là số nguyên tố" hoặc "không là số nguyên tố"', 10);

INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight)
VALUES
(5, '7\n', 'là số nguyên tố', 10),
(5, '4\n', 'không là số nguyên tố', 10),
(5, '2\n', 'là số nguyên tố', 10);

-- ==========================================
-- ASSIGNMENT 6: Đảo ngược chuỗi
-- ==========================================

INSERT INTO assignments (class_id, title, description, due_date, programming_language)
VALUES
(
    1,
    'Viết chương trình đảo ngược chuỗi',
    'Nhập một chuỗi ký tự, in ra chuỗi đó nhưng theo thứ tự đảo ngược.',
    '2027-01-20 23:59:00',
    'Python'
);

INSERT INTO assignment_requirements (assignment_id, requirement_text, weight)
VALUES
(6, 'Có dùng input() để nhập chuỗi', 10),
(6, 'Có cách đảo ngược chuỗi (slicing hoặc vòng lặp)', 10),
(6, 'Có print() chuỗi đảo ngược', 10);

INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight)
VALUES
(6, 'hello\n', 'olleh', 10),
(6, 'Python\n', 'nohtyP', 10),
(6, 'abc\n', 'cba', 10);

-- ==========================================
-- ASSIGNMENT 7: Tính trung bình cộng
-- ==========================================

INSERT INTO assignments (class_id, title, description, due_date, programming_language)
VALUES
(
    1,
    'Viết chương trình tính trung bình cộng',
    'Nhập 3 số, tính trung bình cộng của 3 số đó và in ra kết quả (làm tròn 2 chữ số thập phân).',
    '2027-01-25 23:59:00',
    'Python'
);

INSERT INTO assignment_requirements (assignment_id, requirement_text, weight)
VALUES
(7, 'Có dùng input() để nhập 3 số', 10),
(7, 'Có tính tổng 3 số rồi chia cho 3', 10),
(7, 'Có print() kết quả trung bình cộng (làm tròn)', 10);

INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight)
VALUES
(7, '5\n10\n15\n', '10.00', 10),
(7, '7\n8\n9\n', '8.00', 10),
(7, '3\n6\n9\n', '6.00', 10);

-- ==========================================
-- ASSIGNMENT 8: Chuyển đổi nhiệt độ
-- ==========================================

INSERT INTO assignments (class_id, title, description, due_date, programming_language)
VALUES
(
    1,
    'Viết chương trình chuyển đổi nhiệt độ Celsius sang Fahrenheit',
    'Nhập nhiệt độ Celsius, chuyển sang Fahrenheit theo công thức: F = (C * 9/5) + 32, in ra kết quả.',
    '2027-02-01 23:59:00',
    'Python'
);

INSERT INTO assignment_requirements (assignment_id, requirement_text, weight)
VALUES
(8, 'Có dùng input() để nhập độ Celsius', 10),
(8, 'Có công thức chuyển đổi đúng: F = (C * 9/5) + 32', 10),
(8, 'Có print() kết quả nhiệt độ Fahrenheit', 10);

INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight)
VALUES
(8, '0\n', '32.0', 10),
(8, '100\n', '212.0', 10),
(8, '25\n', '77.0', 10);

-- ==========================================
-- ASSIGNMENT 9: Phân loại điểm
-- ==========================================

INSERT INTO assignments (class_id, title, description, due_date, programming_language)
VALUES
(
    1,
    'Viết chương trình phân loại điểm số',
    'Nhập điểm số (0-10), phân loại thành: Xuất sắc (9-10), Tốt (7-8), Khá (5-6), Yếu (<5), in ra kết quả.',
    '2027-02-05 23:59:00',
    'Python'
);

INSERT INTO assignment_requirements (assignment_id, requirement_text, weight)
VALUES
(9, 'Có dùng input() để nhập điểm số', 10),
(9, 'Có sử dụng if-elif-else hoặc cấu trúc điều kiện', 10),
(9, 'Có print() kết quả phân loại đúng theo khoảng điểm', 10);

INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight)
VALUES
(9, '9\n', 'Xuất sắc', 10),
(9, '7\n', 'Tốt', 10),
(9, '4\n', 'Yếu', 10);

-- ==========================================
-- ASSIGNMENT 10: Máy tính đơn giản
-- ==========================================

INSERT INTO assignments (class_id, title, description, due_date, programming_language)
VALUES
(
    1,
    'Viết chương trình máy tính đơn giản',
    'Nhập 2 số và một phép toán (+, -, *, /), in ra kết quả của phép toán đó.',
    '2027-02-10 23:59:00',
    'Python'
);

INSERT INTO assignment_requirements (assignment_id, requirement_text, weight)
VALUES
(10, 'Có dùng input() để nhập 2 số và phép toán', 10),
(10, 'Có sử dụng if-elif hoặc cấu trúc xử lý phép toán', 10),
(10, 'Có print() kết quả phép toán', 10);

INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight)
VALUES
(10, '10\n5\n+\n', '15', 10),
(10, '10\n5\n-\n', '5', 10),
(10, '10\n5\n*\n', '50', 10);

-- ==========================================
-- ASSIGNMENT 11: Đếm ký tự trong chuỗi
-- ==========================================

INSERT INTO assignments (class_id, title, description, due_date, programming_language)
VALUES
(
    1,
    'Viết chương trình đếm số ký tự trong chuỗi',
    'Nhập một chuỗi, đếm số lượng ký tự (không tính khoảng trắng) và in ra kết quả.',
    '2027-02-15 23:59:00',
    'Python'
);

INSERT INTO assignment_requirements (assignment_id, requirement_text, weight)
VALUES
(11, 'Có dùng input() để nhập chuỗi', 10),
(11, 'Có hàm len() hoặc vòng lặp để đếm ký tự', 10),
(11, 'Có print() số lượng ký tự (loại bỏ khoảng trắng)', 10);

INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight)
VALUES
(11, 'hello world\n', '10', 10),
(11, 'python\n', '6', 10),
(11, 'a b c\n', '3', 10);

-- ==========================================
-- THÊM SUBMISSIONS CHO 10 BÀI TẬP MỚI
-- ==========================================

-- Assignment 2 submissions (Even/Odd Check)
INSERT INTO submissions (assignment_id, student_id, file_name, source_code)
VALUES
(2, 1, 'bai2.py', 'n = int(input())\nif n % 2 == 0:\n    print("chẵn")\nelse:\n    print("lẻ")'),
(2, 2, 'bai2.py', 'num = int(input())\nif num % 2 == 0:\n    print("chẵn")\nelse:\n    print("lẻ")'),
(2, 3, 'bai2.py', 'x = int(input())\nif x % 2:\n    print("lẻ")\nelse:\n    print("chẵn")'),
(2, 4, 'bai2.py', 'n = int(input())\nprint("chẵn" if n % 2 == 0 else "lẻ")'),
(2, 5, 'bai2.py', 'a = int(input())\nif a % 2 == 0:\n    print("chẵn")\nelse:\n    print("lẻ")'),
(2, 6, 'bai2.py', 'num = int(input())\nif num % 2:\n    print("lẻ")\nelse:\n    print("chẵn")'),
(2, 7, 'bai2.py', 'n = int(input())\nif n % 2 == 0:\n    print("chẵn")\nelse:\n    print("lẻ")'),
(2, 8, 'bai2.py', 'x = int(input())\nprint("chẵn" if x % 2 == 0 else "lẻ")'),
(2, 9, 'bai2.py', 'n = int(input())\nif n % 2 == 0:\n    print("chẵn")\nelse:\n    print("lẻ")'),
(2, 10, 'bai2.py', 'num = int(input())\nif num % 2 == 0:\n    print("chẵn")\nelse:\n    print("lẻ")');

-- Assignment 3 submissions (Factorial)
INSERT INTO submissions (assignment_id, student_id, file_name, source_code)
VALUES
(3, 1, 'bai3.py', 'n = int(input())\nresult = 1\nfor i in range(1, n + 1):\n    result *= i\nprint(result)'),
(3, 2, 'bai3.py', 'n = int(input())\nfact = 1\nfor i in range(2, n + 1):\n    fact *= i\nprint(fact)'),
(3, 3, 'bai3.py', 'n = int(input())\nkq = 1\ni = 1\nwhile i <= n:\n    kq *= i\n    i += 1\nprint(kq)'),
(3, 4, 'bai3.py', 'import math\nn = int(input())\nprint(math.factorial(n))'),
(3, 5, 'bai3.py', 'n = int(input())\nresult = 1\nfor i in range(1, n + 1):\n    result = result * i\nprint(result)'),
(3, 6, 'bai3.py', 'n = int(input())\nfact = 1\nfor j in range(1, n+1):\n    fact = fact * j\nprint(fact)'),
(3, 7, 'bai3.py', 'n = int(input())\nresult = 1\nfor i in range(1, n + 1):\n    result *= i\nprint(result)'),
(3, 8, 'bai3.py', 'n = int(input())\nfact = 1\nfor i in range(1, n+1):\n    fact *= i\nprint(fact)'),
(3, 9, 'bai3.py', 'n = int(input())\nresult = 1\nfor i in range(1, n + 1):\n    result *= i\nprint(result)'),
(3, 10, 'bai3.py', 'n = int(input())\nresult = 1\nfor i in range(2, n+1):\n    result *= i\nprint(result)');

-- Assignment 4 submissions (Sum from 1 to n)
INSERT INTO submissions (assignment_id, student_id, file_name, source_code)
VALUES
(4, 1, 'bai4.py', 'n = int(input())\nsum = 0\nfor i in range(1, n + 1):\n    sum += i\nprint(sum)'),
(4, 2, 'bai4.py', 'n = int(input())\nprint(n * (n + 1) // 2)'),
(4, 3, 'bai4.py', 'n = int(input())\ntotal = 0\nfor i in range(1, n + 1):\n    total += i\nprint(total)'),
(4, 4, 'bai4.py', 'n = int(input())\nresult = sum(range(1, n + 1))\nprint(result)'),
(4, 5, 'bai4.py', 'n = int(input())\nsum_val = 0\nfor i in range(1, n + 1):\n    sum_val += i\nprint(sum_val)'),
(4, 6, 'bai4.py', 'n = int(input())\nsum = 0\ni = 1\nwhile i <= n:\n    sum += i\n    i += 1\nprint(sum)'),
(4, 7, 'bai4.py', 'n = int(input())\ns = 0\nfor i in range(1, n + 1):\n    s += i\nprint(s)'),
(4, 8, 'bai4.py', 'n = int(input())\nprint(sum(range(1, n + 1)))'),
(4, 9, 'bai4.py', 'n = int(input())\nsum = 0\nfor i in range(1, n + 1):\n    sum += i\nprint(sum)'),
(4, 10, 'bai4.py', 'n = int(input())\nprint(n * (n + 1) // 2)');

-- Assignment 5 submissions (Prime Number Check)
INSERT INTO submissions (assignment_id, student_id, file_name, source_code)
VALUES
(5, 1, 'bai5.py', 'n = int(input())\nif n < 2:\n    print("không là số nguyên tố")\nelse:\n    is_prime = True\n    for i in range(2, n):\n        if n % i == 0:\n            is_prime = False\n            break\n    print("là số nguyên tố" if is_prime else "không là số nguyên tố")'),
(5, 2, 'bai5.py', 'n = int(input())\nif n < 2:\n    print("không là số nguyên tố")\nelse:\n    prime = True\n    for i in range(2, int(n**0.5) + 1):\n        if n % i == 0:\n            prime = False\n            break\n    print("là số nguyên tố" if prime else "không là số nguyên tố")'),
(5, 3, 'bai5.py', 'n = int(input())\nif n <= 1:\n    print("không là số nguyên tố")\nelse:\n    for i in range(2, n):\n        if n % i == 0:\n            print("không là số nguyên tố")\n            break\n    else:\n        print("là số nguyên tố")'),
(5, 4, 'bai5.py', 'n = int(input())\nif n < 2:\n    print("không là số nguyên tố")\nelse:\n    is_prime = True\n    for i in range(2, n):\n        if n % i == 0:\n            is_prime = False\n            break\n    if is_prime:\n        print("là số nguyên tố")\n    else:\n        print("không là số nguyên tố")'),
(5, 5, 'bai5.py', 'n = int(input())\nif n < 2:\n    print("không là số nguyên tố")\nelse:\n    is_prime = True\n    for i in range(2, n):\n        if n % i == 0:\n            is_prime = False\n            break\n    print("là số nguyên tố" if is_prime else "không là số nguyên tố")'),
(5, 6, 'bai5.py', 'n = int(input())\nif n < 2:\n    print("không là số nguyên tố")\nelse:\n    found = False\n    for i in range(2, n):\n        if n % i == 0:\n            found = True\n            break\n    print("là số nguyên tố" if not found else "không là số nguyên tố")'),
(5, 7, 'bai5.py', 'n = int(input())\nif n < 2:\n    print("không là số nguyên tố")\nelse:\n    is_prime = True\n    for i in range(2, n):\n        if n % i == 0:\n            is_prime = False\n            break\n    print("là số nguyên tố" if is_prime else "không là số nguyên tố")'),
(5, 8, 'bai5.py', 'n = int(input())\nif n <= 1:\n    print("không là số nguyên tố")\nelse:\n    for i in range(2, n):\n        if n % i == 0:\n            print("không là số nguyên tố")\n            exit()\n    print("là số nguyên tố")'),
(5, 9, 'bai5.py', 'n = int(input())\nif n < 2:\n    print("không là số nguyên tố")\nelse:\n    is_prime = True\n    for i in range(2, n):\n        if n % i == 0:\n            is_prime = False\n            break\n    print("là số nguyên tố" if is_prime else "không là số nguyên tố")'),
(5, 10, 'bai5.py', 'n = int(input())\nif n < 2:\n    print("không là số nguyên tố")\nelse:\n    is_prime = True\n    for i in range(2, int(n**0.5) + 1):\n        if n % i == 0:\n            is_prime = False\n            break\n    print("là số nguyên tố" if is_prime else "không là số nguyên tố")');

-- Assignment 6 submissions (Reverse String)
INSERT INTO submissions (assignment_id, student_id, file_name, source_code)
VALUES
(6, 1, 'bai6.py', 's = input()\nprint(s[::-1])'),
(6, 2, 'bai6.py', 'text = input()\nprint(text[::-1])'),
(6, 3, 'bai6.py', 's = input()\nreverse = ""\nfor char in s:\n    reverse = char + reverse\nprint(reverse)'),
(6, 4, 'bai6.py', 's = input()\nreverse = ""\ni = len(s) - 1\nwhile i >= 0:\n    reverse += s[i]\n    i -= 1\nprint(reverse)'),
(6, 5, 'bai6.py', 'text = input()\nprint(text[::-1])'),
(6, 6, 'bai6.py', 's = input()\nreverse_s = ""\nfor i in range(len(s) - 1, -1, -1):\n    reverse_s += s[i]\nprint(reverse_s)'),
(6, 7, 'bai6.py', 's = input()\nprint(s[::-1])'),
(6, 8, 'bai6.py', 'text = input()\nreverse = ""\nfor char in text:\n    reverse = char + reverse\nprint(reverse)'),
(6, 9, 'bai6.py', 's = input()\nprint(s[::-1])'),
(6, 10, 'bai6.py', 'text = input()\nprint(text[::-1])');

-- Assignment 7 submissions (Average)
INSERT INTO submissions (assignment_id, student_id, file_name, source_code)
VALUES
(7, 1, 'bai7.py', 'a = int(input())\nb = int(input())\nc = int(input())\navg = (a + b + c) / 3\nprint(f"{avg:.2f}")'),
(7, 2, 'bai7.py', 'n1 = int(input())\nn2 = int(input())\nn3 = int(input())\naverage = (n1 + n2 + n3) / 3\nprint(f"{average:.2f}")'),
(7, 3, 'bai7.py', 'x = int(input())\ny = int(input())\nz = int(input())\nprint(f"{(x + y + z) / 3:.2f}")'),
(7, 4, 'bai7.py', 'a = int(input())\nb = int(input())\nc = int(input())\navg = (a + b + c) / 3\nprint("{:.2f}".format(avg))'),
(7, 5, 'bai7.py', 'a = int(input())\nb = int(input())\nc = int(input())\navg = (a + b + c) / 3\nprint(round(avg, 2))'),
(7, 6, 'bai7.py', 'num1 = int(input())\nnum2 = int(input())\nnum3 = int(input())\naverage = (num1 + num2 + num3) / 3\nprint(f"{average:.2f}")'),
(7, 7, 'bai7.py', 'a = int(input())\nb = int(input())\nc = int(input())\nprint(f"{(a + b + c) / 3:.2f}")'),
(7, 8, 'bai7.py', 'x = int(input())\ny = int(input())\nz = int(input())\nprint(f"{(x + y + z) / 3:.2f}")'),
(7, 9, 'bai7.py', 'a = int(input())\nb = int(input())\nc = int(input())\navg = (a + b + c) / 3\nprint(f"{avg:.2f}")'),
(7, 10, 'bai7.py', 'a = int(input())\nb = int(input())\nc = int(input())\naverage = (a + b + c) / 3\nprint(f"{average:.2f}")');

-- Assignment 8 submissions (Temperature Conversion)
INSERT INTO submissions (assignment_id, student_id, file_name, source_code)
VALUES
(8, 1, 'bai8.py', 'c = int(input())\nf = (c * 9/5) + 32\nprint(f)'),
(8, 2, 'bai8.py', 'celsius = int(input())\nfahrenheit = (celsius * 9/5) + 32\nprint(fahrenheit)'),
(8, 3, 'bai8.py', 'c = float(input())\nf = c * 9/5 + 32\nprint(f)'),
(8, 4, 'bai8.py', 'temp_c = int(input())\ntemp_f = (temp_c * 9 / 5) + 32\nprint(float(temp_f))'),
(8, 5, 'bai8.py', 'c = int(input())\nf = (c * 9 / 5) + 32\nprint(float(f))'),
(8, 6, 'bai8.py', 'celsius = int(input())\nfahrenheit = celsius * 9 / 5 + 32\nprint(fahrenheit)'),
(8, 7, 'bai8.py', 'c = int(input())\nf = (c * 9/5) + 32\nprint(f)'),
(8, 8, 'bai8.py', 'temp = int(input())\nresult = (temp * 9/5) + 32\nprint(result)'),
(8, 9, 'bai8.py', 'c = int(input())\nf = (c * 9/5) + 32\nprint(f)'),
(8, 10, 'bai8.py', 'c = int(input())\nf = (c * 9 / 5) + 32\nprint(float(f))');

-- Assignment 9 submissions (Grade Classification)
INSERT INTO submissions (assignment_id, student_id, file_name, source_code)
VALUES
(9, 1, 'bai9.py', 'diem = int(input())\nif diem >= 9:\n    print("Xuất sắc")\nelif diem >= 7:\n    print("Tốt")\nelif diem >= 5:\n    print("Khá")\nelse:\n    print("Yếu")'),
(9, 2, 'bai9.py', 'score = int(input())\nif score >= 9:\n    print("Xuất sắc")\nelif score >= 7:\n    print("Tốt")\nelif score >= 5:\n    print("Khá")\nelse:\n    print("Yếu")'),
(9, 3, 'bai9.py', 'diem = int(input())\nif 9 <= diem <= 10:\n    print("Xuất sắc")\nelif 7 <= diem <= 8:\n    print("Tốt")\nelif 5 <= diem <= 6:\n    print("Khá")\nelse:\n    print("Yếu")'),
(9, 4, 'bai9.py', 'diem = int(input())\nif diem >= 9:\n    print("Xuất sắc")\nelif diem >= 7:\n    print("Tốt")\nelif diem >= 5:\n    print("Khá")\nelse:\n    print("Yếu")'),
(9, 5, 'bai9.py', 'diem = int(input())\nif diem > 8:\n    print("Xuất sắc")\nelif diem > 6:\n    print("Tốt")\nelif diem > 4:\n    print("Khá")\nelse:\n    print("Yếu")'),
(9, 6, 'bai9.py', 'diem = int(input())\nif diem >= 9:\n    print("Xuất sắc")\nelif diem >= 7:\n    print("Tốt")\nelif diem >= 5:\n    print("Khá")\nelse:\n    print("Yếu")'),
(9, 7, 'bai9.py', 'score = int(input())\nif score >= 9:\n    print("Xuất sắc")\nelif score >= 7:\n    print("Tốt")\nelif score >= 5:\n    print("Khá")\nelse:\n    print("Yếu")'),
(9, 8, 'bai9.py', 'diem = int(input())\nif diem >= 9:\n    print("Xuất sắc")\nelif diem >= 7:\n    print("Tốt")\nelif diem >= 5:\n    print("Khá")\nelse:\n    print("Yếu")'),
(9, 9, 'bai9.py', 'diem = int(input())\nif diem >= 9:\n    print("Xuất sắc")\nelif diem >= 7:\n    print("Tốt")\nelif diem >= 5:\n    print("Khá")\nelse:\n    print("Yếu")'),
(9, 10, 'bai9.py', 'diem = int(input())\nif diem >= 9:\n    print("Xuất sắc")\nelif diem >= 7:\n    print("Tốt")\nelif diem >= 5:\n    print("Khá")\nelse:\n    print("Yếu")');

-- Assignment 10 submissions (Simple Calculator)
INSERT INTO submissions (assignment_id, student_id, file_name, source_code)
VALUES
(10, 1, 'bai10.py', 'a = int(input())\nb = int(input())\nop = input()\nif op == "+":\n    print(a + b)\nelif op == "-":\n    print(a - b)\nelif op == "*":\n    print(a * b)\nelif op == "/":\n    print(a // b)'),
(10, 2, 'bai10.py', 'num1 = int(input())\nnum2 = int(input())\nphep = input()\nif phep == "+":\n    print(num1 + num2)\nelif phep == "-":\n    print(num1 - num2)\nelif phep == "*":\n    print(num1 * num2)\nelif phep == "/":\n    print(num1 // num2)'),
(10, 3, 'bai10.py', 'x = int(input())\ny = int(input())\nphep_toan = input()\nif phep_toan == "+":\n    print(x + y)\nelif phep_toan == "-":\n    print(x - y)\nelif phep_toan == "*":\n    print(x * y)\nelif phep_toan == "/":\n    print(x // y)'),
(10, 4, 'bai10.py', 'a = int(input())\nb = int(input())\nop = input()\nif op == "+":\n    result = a + b\nelif op == "-":\n    result = a - b\nelif op == "*":\n    result = a * b\nelse:\n    result = a // b\nprint(result)'),
(10, 5, 'bai10.py', 'a = int(input())\nb = int(input())\nphep = input()\nif phep == "+":\n    print(a + b)\nelif phep == "-":\n    print(a - b)\nelif phep == "*":\n    print(a * b)\nelif phep == "/":\n    print(a // b)'),
(10, 6, 'bai10.py', 'n1 = int(input())\nn2 = int(input())\nop = input()\nif op == "+":\n    print(n1 + n2)\nelif op == "-":\n    print(n1 - n2)\nelif op == "*":\n    print(n1 * n2)\nelse:\n    print(n1 // n2)'),
(10, 7, 'bai10.py', 'a = int(input())\nb = int(input())\nop = input()\nif op == "+":\n    print(a + b)\nelif op == "-":\n    print(a - b)\nelif op == "*":\n    print(a * b)\nelif op == "/":\n    print(a // b)'),
(10, 8, 'bai10.py', 'x = int(input())\ny = int(input())\nphep = input()\nif phep == "+":\n    print(x + y)\nelif phep == "-":\n    print(x - y)\nelif phep == "*":\n    print(x * y)\nelif phep == "/":\n    print(x // y)'),
(10, 9, 'bai10.py', 'a = int(input())\nb = int(input())\nop = input()\nif op == "+":\n    print(a + b)\nelif op == "-":\n    print(a - b)\nelif op == "*":\n    print(a * b)\nelif op == "/":\n    print(a // b)'),
(10, 10, 'bai10.py', 'a = int(input())\nb = int(input())\nphep = input()\nif phep == "+":\n    print(a + b)\nelif phep == "-":\n    print(a - b)\nelif phep == "*":\n    print(a * b)\nelse:\n    print(a // b)');

-- Assignment 11 submissions (Character Count)
INSERT INTO submissions (assignment_id, student_id, file_name, source_code)
VALUES
(11, 1, 'bai11.py', 's = input()\ncount = len(s.replace(" ", ""))\nprint(count)'),
(11, 2, 'bai11.py', 'text = input()\ncount = 0\nfor char in text:\n    if char != " ":\n        count += 1\nprint(count)'),
(11, 3, 'bai11.py', 's = input()\ncount = len(s) - s.count(" ")\nprint(count)'),
(11, 4, 'bai11.py', 'text = input()\nno_spaces = text.replace(" ", "")\nprint(len(no_spaces))'),
(11, 5, 'bai11.py', 's = input()\ncount = 0\nfor c in s:\n    if c != " ":\n        count += 1\nprint(count)'),
(11, 6, 'bai11.py', 'text = input()\ncount = len(text.replace(" ", ""))\nprint(count)'),
(11, 7, 'bai11.py', 's = input()\ncount = len(s) - s.count(" ")\nprint(count)'),
(11, 8, 'bai11.py', 'text = input()\nprint(len(text.replace(" ", "")))'),
(11, 9, 'bai11.py', 's = input()\ncount = len(s.replace(" ", ""))\nprint(count)'),
(11, 10, 'bai11.py', 'text = input()\ncount = len(text) - text.count(" ")\nprint(count)');

-- ==========================================
-- THÊM EVALUATION SESSIONS CHO 10 BÀI MỚI
-- ==========================================

-- Evaluation for Assignment 2
INSERT INTO evaluation_sessions (submission_id, syntax_score, code_analysis_score, structure_score, requirement_score, test_score, llm_score, total_score, final_feedback, agent_details)
VALUES
(11, 20, 18, 20, 20, 20, 19, 97, 'Xuất sắc! Code sạch và hoạt động chính xác.', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}'),
(12, 20, 18, 20, 20, 20, 19, 97, 'Code tốt, logic rõ ràng.', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}'),
(13, 20, 17, 18, 18, 18, 18, 91, 'Tốt nhưng có thể cải thiện logic.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(14, 20, 19, 20, 20, 20, 20, 99, 'Giải pháp tối ưu với ternary operator.', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}'),
(15, 20, 18, 20, 20, 20, 19, 97, 'Code chính xác và rõ ràng.', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}'),
(16, 20, 16, 17, 18, 18, 17, 90, 'Hoạt động nhưng cần cải thiện.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(17, 20, 18, 20, 20, 20, 19, 97, 'Rất tốt, code sạch.', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}'),
(18, 20, 19, 20, 20, 20, 20, 99, 'Xuất sắc! Giải pháp tối ưu.', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}'),
(19, 20, 18, 20, 20, 20, 19, 97, 'Code hoạt động chính xác.', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}'),
(20, 20, 18, 20, 20, 20, 19, 97, 'Tốt, logic đúng.', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}');

-- Evaluation for Assignment 3
INSERT INTO evaluation_sessions (submission_id, syntax_score, code_analysis_score, structure_score, requirement_score, test_score, llm_score, total_score, final_feedback, agent_details)
VALUES
(21, 20, 18, 20, 20, 20, 19, 97, 'Code tính giai thừa đúng.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(22, 20, 19, 20, 20, 20, 20, 99, 'Tối ưu với công thức căn bậc hai.', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}'),
(23, 20, 18, 20, 20, 20, 19, 97, 'Sử dụng vòng lặp while tốt.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(24, 20, 20, 20, 20, 20, 20, 100, 'Sử dụng thư viện math, giải pháp elegant.', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}'),
(25, 20, 18, 20, 20, 20, 19, 97, 'Code tính giai thừa chính xác.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(26, 20, 17, 18, 18, 18, 18, 91, 'Hoạt động nhưng tên biến có thể cải thiện.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(27, 20, 18, 20, 20, 20, 19, 97, 'Rất tốt, logic rõ ràng.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(28, 20, 18, 19, 19, 19, 19, 94, 'Tốt, sử dụng range correctly.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(29, 20, 18, 20, 20, 20, 19, 97, 'Hoàn thành toàn bộ yêu cầu.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(30, 20, 17, 19, 18, 18, 18, 90, 'Tốt nhưng bắt đầu từ 2 chứ không phải 1.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}');

-- Evaluation for Assignment 4
INSERT INTO evaluation_sessions (submission_id, syntax_score, code_analysis_score, structure_score, requirement_score, test_score, llm_score, total_score, final_feedback, agent_details)
VALUES
(31, 20, 18, 20, 20, 20, 19, 97, 'Code sử dụng vòng lặp tốt.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(32, 20, 19, 20, 20, 20, 20, 99, 'Sử dụng công thức toán học, xuất sắc!', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}'),
(33, 20, 18, 20, 20, 20, 19, 97, 'Rất tốt, tính tổng chính xác.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(34, 20, 19, 20, 20, 20, 20, 99, 'Sử dụng sum() function, elegant solution.', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}'),
(35, 20, 18, 20, 20, 20, 19, 97, 'Code hoạt động đúng.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(36, 20, 17, 18, 19, 19, 18, 91, 'Tốt, sử dụng while loop.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(37, 20, 18, 20, 20, 20, 19, 97, 'Logic tốt, code sạch.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(38, 20, 19, 20, 20, 20, 20, 99, 'Giải pháp functional với sum().', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}'),
(39, 20, 18, 20, 20, 20, 19, 97, 'Đúng yêu cầu.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(40, 20, 19, 20, 20, 20, 20, 99, 'Sử dụng công thức, tối ưu.', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}');

-- Evaluation for Assignment 5
INSERT INTO evaluation_sessions (submission_id, syntax_score, code_analysis_score, structure_score, requirement_score, test_score, llm_score, total_score, final_feedback, agent_details)
VALUES
(41, 20, 17, 18, 19, 19, 18, 91, 'Kiểm tra số nguyên tố tốt nhưng có thể tối ưu.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(42, 20, 19, 19, 20, 20, 20, 98, 'Tối ưu với sqrt, rất tốt!', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}'),
(43, 20, 18, 19, 20, 20, 19, 96, 'Sử dụng break tốt.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(44, 20, 18, 19, 20, 20, 19, 96, 'Code rõ ràng và chính xác.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(45, 20, 18, 18, 20, 20, 19, 95, 'Hoạt động đúng.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(46, 20, 16, 17, 19, 19, 17, 88, 'Tốt nhưng logic có thể cải thiện.', '{"syntax":"pass","structure":"fair","requirement":"pass","test":"3/3"}'),
(47, 20, 18, 19, 20, 20, 19, 96, 'Code kiểm tra nguyên tố chính xác.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(48, 20, 18, 19, 20, 20, 19, 96, 'Sử dụng exit() có thể cải thiện.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(49, 20, 18, 19, 20, 20, 19, 96, 'Tốt, logic rõ ràng.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(50, 20, 19, 19, 20, 20, 20, 98, 'Tối ưu với sqrt, tốt!', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}');

-- Evaluation for Assignment 6
INSERT INTO evaluation_sessions (submission_id, syntax_score, code_analysis_score, structure_score, requirement_score, test_score, llm_score, total_score, final_feedback, agent_details)
VALUES
(51, 20, 19, 20, 20, 20, 20, 99, 'Sử dụng slicing, giải pháp tối ưu!', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}'),
(52, 20, 19, 20, 20, 20, 20, 99, 'Code sạch với slicing.', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}'),
(53, 20, 18, 19, 20, 20, 19, 96, 'Sử dụng vòng lặp, tốt.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(54, 20, 18, 18, 20, 20, 19, 95, 'Logic đảo ngược tốt.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(55, 20, 19, 20, 20, 20, 20, 99, 'Slicing solution, xuất sắc!', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}'),
(56, 20, 17, 18, 20, 20, 18, 93, 'Vòng lặp range tốt nhưng phức tạp.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(57, 20, 19, 20, 20, 20, 20, 99, 'Giải pháp pythonic với slicing.', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}'),
(58, 20, 18, 19, 20, 20, 19, 96, 'Vòng lặp với prepend string.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(59, 20, 19, 20, 20, 20, 20, 99, 'Slicing, rất tốt!', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}'),
(60, 20, 19, 20, 20, 20, 20, 99, 'Code hoàn hảo với slicing.', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}');

-- Evaluation for Assignment 7
INSERT INTO evaluation_sessions (submission_id, syntax_score, code_analysis_score, structure_score, requirement_score, test_score, llm_score, total_score, final_feedback, agent_details)
VALUES
(61, 20, 18, 20, 20, 20, 19, 97, 'Tính trung bình đúng với f-string.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(62, 20, 18, 20, 20, 20, 19, 97, 'Tốt, f-string format tốt.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(63, 20, 19, 20, 20, 20, 20, 99, 'Code gọn gàng, format đúng.', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}'),
(64, 20, 18, 19, 20, 20, 19, 96, 'Sử dụng format(), hoạt động tốt.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(65, 20, 17, 18, 20, 18, 18, 91, 'Sử dụng round() nhưng không đảm bảo định dạng.', '{"syntax":"pass","structure":"good","requirement":"partial","test":"2/3"}'),
(66, 20, 18, 20, 20, 20, 19, 97, 'F-string format tốt.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(67, 20, 19, 20, 20, 20, 20, 99, 'Gọn gàng, format đúng.', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}'),
(68, 20, 19, 20, 20, 20, 20, 99, 'Format tốt, code sạch.', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}'),
(69, 20, 18, 20, 20, 20, 19, 97, 'F-string format chính xác.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(70, 20, 18, 20, 20, 20, 19, 97, 'Tính toán và format tốt.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}');

-- Evaluation for Assignment 8
INSERT INTO evaluation_sessions (submission_id, syntax_score, code_analysis_score, structure_score, requirement_score, test_score, llm_score, total_score, final_feedback, agent_details)
VALUES
(71, 20, 18, 19, 20, 20, 19, 96, 'Công thức chuyển đổi đúng.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(72, 20, 18, 19, 20, 20, 19, 96, 'Chuyển đổi đúng, tốt.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(73, 20, 18, 19, 20, 20, 19, 96, 'Sử dụng float, tính chính xác.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(74, 20, 18, 20, 20, 20, 19, 97, 'Format tốt với .format().', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(75, 20, 17, 19, 20, 18, 18, 92, 'Tốt nhưng định dạng chưa đầy đủ.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"2/3"}'),
(76, 20, 18, 19, 20, 20, 19, 96, 'Chuyển đổi chính xác.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(77, 20, 18, 20, 20, 20, 19, 97, 'Công thức đúng, kết quả chính xác.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(78, 20, 18, 19, 20, 20, 19, 96, 'Chuyển đổi đúng, tốt.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(79, 20, 18, 19, 20, 20, 19, 96, 'Công thức chính xác.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(80, 20, 18, 20, 20, 20, 19, 97, 'Chuyển đổi đúng, format tốt.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}');

-- Evaluation for Assignment 9
INSERT INTO evaluation_sessions (submission_id, syntax_score, code_analysis_score, structure_score, requirement_score, test_score, llm_score, total_score, final_feedback, agent_details)
VALUES
(81, 20, 18, 20, 20, 20, 19, 97, 'Phân loại điểm đúng.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(82, 20, 18, 20, 20, 20, 19, 97, 'If-elif-else logic tốt.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(83, 20, 18, 20, 20, 20, 19, 97, 'Phân loại với khoảng chính xác.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(84, 20, 18, 20, 20, 20, 19, 97, 'Logic phân loại rõ ràng.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(85, 20, 17, 19, 18, 18, 18, 90, 'Logic có sai sót nhỏ ở khoảng giá trị.', '{"syntax":"pass","structure":"good","requirement":"partial","test":"2/3"}'),
(86, 20, 18, 20, 20, 20, 19, 97, 'Phân loại đúng theo yêu cầu.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(87, 20, 18, 20, 20, 20, 19, 97, 'Code phân loại chính xác.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(88, 20, 18, 20, 20, 20, 19, 97, 'Logic tốt, phân loại đúng.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(89, 20, 18, 20, 20, 20, 19, 97, 'If-elif-else tốt.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(90, 20, 18, 20, 20, 20, 19, 97, 'Phân loại điểm chính xác.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}');

-- Evaluation for Assignment 10
INSERT INTO evaluation_sessions (submission_id, syntax_score, code_analysis_score, structure_score, requirement_score, test_score, llm_score, total_score, final_feedback, agent_details)
VALUES
(91, 20, 18, 19, 20, 20, 19, 96, 'Máy tính hoạt động đúng.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(92, 20, 18, 19, 20, 20, 19, 96, 'Các phép toán xử lý tốt.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(93, 20, 18, 19, 20, 20, 19, 96, 'Logic xử lý phép toán tốt.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(94, 20, 18, 19, 20, 20, 19, 96, 'Có lưu result, code rõ ràng.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(95, 20, 18, 18, 20, 20, 19, 95, 'Hoạt động tốt, phân nhánh đúng.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(96, 20, 18, 19, 20, 20, 19, 96, 'Các phép toán xử lý chính xác.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(97, 20, 18, 19, 20, 20, 19, 96, 'Máy tính hoạt động đúng.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(98, 20, 18, 19, 20, 20, 19, 96, 'Logic phép toán tốt.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(99, 20, 18, 19, 20, 20, 19, 96, 'Các phép toán xử lý đúng.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(100, 20, 18, 19, 20, 20, 19, 96, 'Phép toán xử lý chính xác.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}');

-- Evaluation for Assignment 11
INSERT INTO evaluation_sessions (submission_id, syntax_score, code_analysis_score, structure_score, requirement_score, test_score, llm_score, total_score, final_feedback, agent_details)
VALUES
(101, 20, 18, 20, 20, 20, 19, 97, 'Đếm ký tự chính xác, loại khoảng trắng tốt.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(102, 20, 18, 19, 20, 20, 19, 96, 'Vòng lặp kiểm tra khoảng trắng tốt.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(103, 20, 18, 20, 20, 20, 19, 97, 'Công thức loại bỏ khoảng trắng tốt.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(104, 20, 19, 20, 20, 20, 20, 99, 'Giải pháp gọn gàng, tối ưu.', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}'),
(105, 20, 18, 19, 20, 20, 19, 96, 'Vòng lặp và điều kiện tốt.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(106, 20, 18, 20, 20, 20, 19, 97, 'Replace() function sử dụng tốt.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(107, 20, 18, 20, 20, 20, 19, 97, 'Công thức loại bỏ khoảng trắng đúng.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(108, 20, 19, 20, 20, 20, 20, 99, 'Giải pháp gọn gàng, xuất sắc!', '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}'),
(109, 20, 18, 20, 20, 20, 19, 97, 'Replace() function sử dụng chính xác.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'),
(110, 20, 18, 20, 20, 20, 19, 97, 'Tính toán ký tự chính xác.', '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}');

-- ==========================================
-- THÊM AGENT LOGS CHO TẤT CẢ SUBMISSIONS
-- ==========================================

-- Agent logs for Assignments 2-11 (I'll insert a sample for each)
INSERT INTO agent_logs (submission_id, agent_name, result)
VALUES
-- Assignment 2
(11, 'SyntaxAgent', 'No syntax error'),
(11, 'RequirementAgent', 'Requirement satisfied'),
(11, 'StructureAgent', 'Excellent structure'),
(11, 'TestAgent', 'Passed 3/3'),

-- Assignment 3
(21, 'SyntaxAgent', 'No syntax error'),
(21, 'RequirementAgent', 'Requirement satisfied'),
(21, 'StructureAgent', 'Good structure'),
(21, 'TestAgent', 'Passed 3/3'),

-- Assignment 4
(31, 'SyntaxAgent', 'No syntax error'),
(31, 'RequirementAgent', 'Requirement satisfied'),
(31, 'StructureAgent', 'Good structure'),
(31, 'TestAgent', 'Passed 3/3'),

-- Assignment 5
(41, 'SyntaxAgent', 'No syntax error'),
(41, 'RequirementAgent', 'Requirement satisfied'),
(41, 'StructureAgent', 'Good structure'),
(41, 'TestAgent', 'Passed 3/3'),

-- Assignment 6
(51, 'SyntaxAgent', 'No syntax error'),
(51, 'RequirementAgent', 'Requirement satisfied'),
(51, 'StructureAgent', 'Excellent structure'),
(51, 'TestAgent', 'Passed 3/3'),

-- Assignment 7
(61, 'SyntaxAgent', 'No syntax error'),
(61, 'RequirementAgent', 'Requirement satisfied'),
(61, 'StructureAgent', 'Good structure'),
(61, 'TestAgent', 'Passed 3/3'),

-- Assignment 8
(71, 'SyntaxAgent', 'No syntax error'),
(71, 'RequirementAgent', 'Requirement satisfied'),
(71, 'StructureAgent', 'Good structure'),
(71, 'TestAgent', 'Passed 3/3'),

-- Assignment 9
(81, 'SyntaxAgent', 'No syntax error'),
(81, 'RequirementAgent', 'Requirement satisfied'),
(81, 'StructureAgent', 'Good structure'),
(81, 'TestAgent', 'Passed 3/3'),

-- Assignment 10
(91, 'SyntaxAgent', 'No syntax error'),
(91, 'RequirementAgent', 'Requirement satisfied'),
(91, 'StructureAgent', 'Good structure'),
(91, 'TestAgent', 'Passed 3/3'),

-- Assignment 11
(101, 'SyntaxAgent', 'No syntax error'),
(101, 'RequirementAgent', 'Requirement satisfied'),
(101, 'StructureAgent', 'Good structure'),
(101, 'TestAgent', 'Passed 3/3');
