-- ==========================================
-- XÓA TOÀN BỘ BẢNG CŨ
-- ==========================================

DROP TABLE IF EXISTS agent_logs CASCADE;
DROP TABLE IF EXISTS evaluation_sessions CASCADE;
DROP TABLE IF EXISTS submissions CASCADE;
DROP TABLE IF EXISTS assignment_testcases CASCADE;
DROP TABLE IF EXISTS assignment_requirements CASCADE;
DROP TABLE IF EXISTS assignments CASCADE;
DROP TABLE IF EXISTS enrollments CASCADE;
DROP TABLE IF EXISTS classes CASCADE;
DROP TABLE IF EXISTS students CASCADE;
DROP TABLE IF EXISTS teachers CASCADE;

-- ==========================================
-- TEACHERS
-- ==========================================

CREATE TABLE teachers (
    teacher_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- STUDENTS
-- ==========================================

CREATE TABLE students (
    student_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- CLASSES
-- ==========================================

CREATE TABLE classes (
    class_id SERIAL PRIMARY KEY,
    class_name VARCHAR(100) NOT NULL,
    teacher_id INT REFERENCES teachers(teacher_id) ON DELETE SET NULL,
    semester VARCHAR(20),
    academic_year VARCHAR(20)
);

-- ==========================================
-- ENROLLMENTS
-- ==========================================

CREATE TABLE enrollments (
    class_id INT REFERENCES classes(class_id) ON DELETE CASCADE,
    student_id INT REFERENCES students(student_id) ON DELETE CASCADE,
    enrolled_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (class_id, student_id)
);

-- ==========================================
-- ASSIGNMENTS
-- ==========================================

CREATE TABLE assignments (
    assignment_id SERIAL PRIMARY KEY,
    class_id INT REFERENCES classes(class_id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    due_date TIMESTAMPTZ NOT NULL,
    programming_language VARCHAR(50)
);

-- ==========================================
-- REQUIREMENTS
-- ==========================================

CREATE TABLE assignment_requirements (
    requirement_id SERIAL PRIMARY KEY,
    assignment_id INT REFERENCES assignments(assignment_id) ON DELETE CASCADE,
    requirement_text TEXT NOT NULL,
    weight DECIMAL(5,2) DEFAULT 10
);

-- ==========================================
-- TEST CASES
-- ==========================================

CREATE TABLE assignment_testcases (
    testcase_id SERIAL PRIMARY KEY,
    assignment_id INT REFERENCES assignments(assignment_id) ON DELETE CASCADE,
    input_data TEXT,
    expected_output TEXT,
    score_weight DECIMAL(5,2) DEFAULT 10
);

-- ==========================================
-- SUBMISSIONS
-- ==========================================

CREATE TABLE submissions (
    submission_id SERIAL PRIMARY KEY,
    assignment_id INT REFERENCES assignments(assignment_id) ON DELETE CASCADE,
    student_id INT REFERENCES students(student_id) ON DELETE CASCADE,
    file_name VARCHAR(255),
    source_code TEXT NOT NULL,
    submitted_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (assignment_id, student_id)
);

-- ==========================================
-- EVALUATION SESSIONS
-- ==========================================

CREATE TABLE evaluation_sessions (
    session_id SERIAL PRIMARY KEY,
    submission_id INT REFERENCES submissions(submission_id) ON DELETE CASCADE,

    syntax_score DECIMAL(5,2),
    code_analysis_score DECIMAL(5,2) DEFAULT 0,
    structure_score DECIMAL(5,2),
    requirement_score DECIMAL(5,2),
    test_score DECIMAL(5,2),
    llm_score DECIMAL(5,2) DEFAULT 0,

    total_score DECIMAL(5,2),
    final_feedback TEXT,

    agent_details JSONB,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- AGENT LOGS
-- ==========================================

CREATE TABLE agent_logs (
    log_id SERIAL PRIMARY KEY,
    submission_id INT REFERENCES submissions(submission_id) ON DELETE CASCADE,
    agent_name VARCHAR(50),
    result TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- DỮ LIỆU MẪU GIÁO VIÊN
-- ==========================================

INSERT INTO teachers (username, password_hash, full_name, email)
VALUES
('teacher1', '123456', 'Nguyen Van A', 'teacher1@example.com'),
('teacher2', '123456', 'Tran Thi B', 'teacher2@example.com'),
('teacher3', '123456', 'Le Van C', 'teacher3@example.com'),
('teacher4', '123456', 'Pham Thi D', 'teacher4@example.com');

-- ==========================================
-- DỮ LIỆU MẪU SINH VIÊN
-- ==========================================

INSERT INTO students (username, password_hash, full_name, email)
VALUES
('student1', '123456', 'Tran Van B', 'student1@example.com'),
('student2', '123456', 'Le Thi C', 'student2@example.com'),
('student3', '123456', 'Hoang Van D', 'student3@example.com'),
('student4', '123456', 'Nguyen Thi E', 'student4@example.com'),
('student5', '123456', 'Vu Van F', 'student5@example.com'),
('student6', '123456', 'Tran Thi G', 'student6@example.com'),
('student7', '123456', 'Dang Van H', 'student7@example.com'),
('student8', '123456', 'Mai Thi I', 'student8@example.com'),
('student9', '123456', 'Bui Van J', 'student9@example.com'),
('student10', '123456', 'Ngo Thi K', 'student10@example.com');

-- ==========================================
-- DỮ LIỆU MẪU LỚP
-- ==========================================

INSERT INTO classes (class_name, teacher_id, semester, academic_year)
VALUES
('Lap trinh Python KTPM', 1, 'HK1', '2025-2026');

-- ==========================================
-- ENROLLMENTS
-- ==========================================

INSERT INTO enrollments (class_id, student_id)
VALUES
(1, 1),
(1, 2),
(1, 3),
(1, 4),
(1, 5),
(1, 6),
(1, 7),
(1, 8),
(1, 9),
(1, 10);

-- ==========================================
-- ASSIGNMENT
-- ==========================================

INSERT INTO assignments (class_id, title, description, due_date, programming_language)
VALUES
(
    1,
    'Viết chương trình cộng 2 số',
    'Nhập 2 số và in ra tổng',
    '2026-12-30 23:59:00',
    'Python'
);

-- ==========================================
-- REQUIREMENTS
-- ==========================================

INSERT INTO assignment_requirements (assignment_id, requirement_text, weight)
VALUES
(1, 'Có dùng input()', 10),
(1, 'Có phép cộng', 10),
(1, 'Có print()', 10);

-- ==========================================
-- TEST CASES
-- ==========================================

INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight)
VALUES
(1, '2\n3\n', '5', 10),
(1, '10\n20\n', '30', 10),
(1, '7\n8\n', '15', 10);

-- ==========================================
-- DEMO SUBMISSION
-- ==========================================

INSERT INTO submissions (assignment_id, student_id, file_name, source_code)
VALUES
(
    1,
    1,
    'bai1.py',
    'a=int(input())\nb=int(input())\nprint(a+b)'
),
(
    1,
    2,
    'bai1.py',
    'x = int(input())\ny = int(input())\nsum = x + y\nprint(sum)'
),
(
    1,
    3,
    'bai1.py',
    'a = int(input())\nb = int(input())\nprint(a + b)'
),
(
    1,
    4,
    'bai1.py',
    'num1 = int(input())\nnum2 = int(input())\nresult = num1 + num2\nprint(result)'
),
(
    1,
    5,
    'bai1.py',
    'n1 = int(input())\nn2 = int(input())\nprint(n1 + n2)'
),
(
    1,
    6,
    'bai1.py',
    'a, b = int(input()), int(input())\nprint(a + b)'
),
(
    1,
    7,
    'bai1.py',
    'x = int(input())\ny = int(input())\nprint(x + y)'
),
(
    1,
    8,
    'bai1.py',
    'first = int(input())\nsecond = int(input())\nsum = first + second\nprint(sum)'
),
(
    1,
    9,
    'bai1.py',
    'a=int(input())\nb=int(input())\nprint(a+b)'
),
(
    1,
    10,
    'bai1.py',
    'num_a = int(input())\nnum_b = int(input())\ntotal = num_a + num_b\nprint(total)'
);

-- ==========================================
-- DEMO EVALUATION
-- ==========================================

INSERT INTO evaluation_sessions
(
    submission_id,
    syntax_score,
    code_analysis_score,
    structure_score,
    requirement_score,
    test_score,
    llm_score,
    total_score,
    final_feedback,
    agent_details
)
VALUES
(
    1,
    20,
    18,
    20,
    20,
    20,
    19,
    95,
    'Code đúng yêu cầu, nên thêm comment.',
    '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'
),
(
    2,
    20,
    19,
    22,
    20,
    20,
    20,
    95,
    'Code tốt, có tên biến rõ ràng. Đạt điểm cao.',
    '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}'
),
(
    3,
    20,
    18,
    20,
    20,
    20,
    19,
    95,
    'Hoàn thành toàn bộ yêu cầu.',
    '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'
),
(
    4,
    20,
    17,
    19,
    18,
    20,
    20,
    94,
    'Tốt nhưng cần tối ưu hóa biến.',
    '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'
),
(
    5,
    20,
    16,
    18,
    16,
    16,
    17,
    89,
    'Yêu cầu được đáp ứng nhưng cần cải thiện cấu trúc.',
    '{"syntax":"pass","structure":"good","requirement":"pass","test":"2/3"}'
),
(
    6,
    18,
    14,
    15,
    16,
    14,
    16,
    83,
    'Code hoạt động nhưng có lỗi nhỏ.',
    '{"syntax":"pass","structure":"fair","requirement":"partial","test":"2/3"}'
),
(
    7,
    20,
    18,
    19,
    18,
    18,
    19,
    94,
    'Rất tốt, logic rõ ràng.',
    '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'
),
(
    8,
    20,
    19,
    20,
    20,
    20,
    20,
    97,
    'Xuất sắc! Code sạch và hiệu quả.',
    '{"syntax":"pass","structure":"excellent","requirement":"pass","test":"3/3"}'
),
(
    9,
    20,
    18,
    20,
    20,
    20,
    19,
    95,
    'Code chính xác, thực hiện đúng yêu cầu.',
    '{"syntax":"pass","structure":"good","requirement":"pass","test":"3/3"}'
),
(
    10,
    20,
    17,
    18,
    17,
    17,
    18,
    91,
    'Tốt nhưng cần có thêm comments.',
    '{"syntax":"pass","structure":"good","requirement":"pass","test":"2/3"}'
);

-- ==========================================
-- DEMO AGENT LOGS
-- ==========================================

INSERT INTO agent_logs (submission_id, agent_name, result)
VALUES
(1, 'SyntaxAgent', 'No syntax error'),
(1, 'RequirementAgent', 'Requirement satisfied'),
(1, 'StructureAgent', 'Good structure'),
(1, 'TestAgent', 'Passed 3/3'),
(2, 'SyntaxAgent', 'No syntax error'),
(2, 'RequirementAgent', 'Requirement satisfied'),
(2, 'StructureAgent', 'Excellent structure'),
(2, 'TestAgent', 'Passed 3/3'),
(3, 'SyntaxAgent', 'No syntax error'),
(3, 'RequirementAgent', 'Requirement satisfied'),
(3, 'StructureAgent', 'Good structure'),
(3, 'TestAgent', 'Passed 3/3'),
(4, 'SyntaxAgent', 'No syntax error'),
(4, 'RequirementAgent', 'Requirement satisfied'),
(4, 'StructureAgent', 'Good structure'),
(4, 'TestAgent', 'Passed 3/3'),
(5, 'SyntaxAgent', 'No syntax error'),
(5, 'RequirementAgent', 'Requirement partially satisfied'),
(5, 'StructureAgent', 'Good structure'),
(5, 'TestAgent', 'Passed 2/3'),
(6, 'SyntaxAgent', 'No syntax error'),
(6, 'RequirementAgent', 'Requirement partially satisfied'),
(6, 'StructureAgent', 'Fair structure'),
(6, 'TestAgent', 'Passed 2/3'),
(7, 'SyntaxAgent', 'No syntax error'),
(7, 'RequirementAgent', 'Requirement satisfied'),
(7, 'StructureAgent', 'Good structure'),
(7, 'TestAgent', 'Passed 3/3'),
(8, 'SyntaxAgent', 'No syntax error'),
(8, 'RequirementAgent', 'Requirement satisfied'),
(8, 'StructureAgent', 'Excellent structure'),
(8, 'TestAgent', 'Passed 3/3'),
(9, 'SyntaxAgent', 'No syntax error'),
(9, 'RequirementAgent', 'Requirement satisfied'),
(9, 'StructureAgent', 'Good structure'),
(9, 'TestAgent', 'Passed 3/3'),
(10, 'SyntaxAgent', 'No syntax error'),
(10, 'RequirementAgent', 'Requirement satisfied'),
(10, 'StructureAgent', 'Good structure'),
(10, 'TestAgent', 'Passed 2/3');