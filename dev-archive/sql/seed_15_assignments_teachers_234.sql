-- =============================================================================
-- Seed: 15 bài tập chia đều cho giáo viên teacher_id = 2, 3, 4 (mỗi GV 5 bài)
-- + Giao ngẫu nhiên cho một phần sinh viên trong lớp (assignment_targets)
--
-- Điều kiện: PostgreSQL; đã có bảng teachers, students, classes, assignments,
-- assignment_requirements, assignment_testcases, enrollments (đúng schema app).
--
-- Cách chạy: mở pgAdmin / psql → chọn đúng database → dán toàn bộ file → Execute.
-- =============================================================================

-- Bảng phụ (app cũng tạo IF NOT EXISTS khi GV tạo bài có chọn SV)
CREATE TABLE IF NOT EXISTS assignment_targets (
    assignment_id INT REFERENCES assignments (assignment_id) ON DELETE CASCADE,
    student_id INT REFERENCES students (student_id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (assignment_id, student_id)
);

-- Nếu GV 2/3/4 chưa có lớp nào → tạo 1 lớp tối thiểu cho mỗi GV
INSERT INTO classes (class_name, teacher_id, semester, academic_year)
SELECT v.class_name, v.tid, 'HK2', '2025-2026'
FROM (
    VALUES
        ('Lap trinh Python - Auto seed (GV2)', 2),
        ('Lap trinh Python - Auto seed (GV3)', 3),
        ('Lap trinh Python - Auto seed (GV4)', 4)
) AS v(class_name, tid)
WHERE NOT EXISTS (SELECT 1 FROM classes c WHERE c.teacher_id = v.tid);

-- Lớp của GV 2/3/4 mà chưa có enrollment → gán ngẫu nhiên 6–10 SV từ bảng students
INSERT INTO enrollments (class_id, student_id)
SELECT c.class_id, s.student_id
FROM classes c
CROSS JOIN LATERAL (
    SELECT student_id
    FROM students
    ORDER BY random()
    LIMIT (6 + floor(random() * 5)::int)
) AS s
WHERE c.teacher_id IN (2, 3, 4)
  AND NOT EXISTS (SELECT 1 FROM enrollments e WHERE e.class_id = c.class_id);

-- =============================================================================
-- Chèn 15 bài: luân phiên teacher 2 → 3 → 4; class_id chọn ngẫu nhiên trong lớp
-- của GV đó; mỗi bài 2 requirement + 1 testcase; targets: subset ngẫu nhiên SV.
-- =============================================================================

DO $$
DECLARE
    i           int;
    tid         int;
    cid         int;
    aid         int;
    sc          int;
    pick_n      int;
    langs       text[] := ARRAY['python', 'python', 'java', 'cpp', 'javascript'];
    lang        text;
    titles      text[] := ARRAY[
        'BT01 - Tong hai so nguyen',
        'BT02 - Kiem tra so nguyen to',
        'BT03 - Tim UCLN bang Euclidean',
        'BT04 - Dao nguoc chuoi ky tu',
        'BT05 - Dem nguyen am trong chuoi',
        'BT06 - Tinh tong day so Fibonacci',
        'BT07 - Chuyen doi nhiet do C/F',
        'BT08 - Sap xep mang tang dan',
        'BT09 - Tim phan tu lon thu hai',
        'BT10 - Kiem tra nam nhuan',
        'BT11 - Tinh giai thua n (n nho)',
        'BT12 - In tam giac sao can doi',
        'BT13 - Dem tu trong cau',
        'BT14 - Kiem tra chuoi palindrome',
        'BT15 - Tim BCNN hai so'
    ];
    teacher_ids int[] := ARRAY[2, 3, 4];
BEGIN
    FOR i IN 1..15 LOOP
        tid := teacher_ids[1 + ((i - 1) % 3)];

        SELECT c.class_id
        INTO cid
        FROM classes c
        WHERE c.teacher_id = tid
        ORDER BY random()
        LIMIT 1;

        IF cid IS NULL THEN
            RAISE NOTICE 'Bo qua bai %: khong tim thay lop cho teacher_id=%', i, tid;
            CONTINUE;
        END IF;

        lang := langs[1 + floor(random() * array_length(langs, 1))::int];

        INSERT INTO assignments (class_id, title, description, due_date, programming_language)
        VALUES (
            cid,
            titles[i],
            'Bai tap seed tu script SQL — GV ' || tid::text || ', lop class_id=' || cid::text
                || '. Sinh vien doc de bai va nop code dung ngon ngu da chon.',
            (CURRENT_TIMESTAMP + (i * interval '4 days') + (random() * interval '12 hours')),
            lang
        )
        RETURNING assignment_id INTO aid;

        INSERT INTO assignment_requirements (assignment_id, requirement_text, weight)
        VALUES
            (aid, 'Code phai bien dich/chay duoc, khong loi cu phap nghiem trong', 10),
            (aid, 'Co it nhat mot ham hoac khoi logic ro rang, co the kem comment', 5);

        INSERT INTO assignment_testcases (assignment_id, input_data, expected_output, score_weight)
        VALUES (aid, '1' || E'\n' || '2', '3', 10);

        SELECT count(*)::int INTO sc FROM enrollments WHERE class_id = cid;

        IF sc > 1 THEN
            pick_n := 1 + floor(random() * (sc - 1))::int;
            IF pick_n < sc THEN
                INSERT INTO assignment_targets (assignment_id, student_id)
                SELECT aid, e.student_id
                FROM enrollments e
                WHERE e.class_id = cid
                ORDER BY random()
                LIMIT pick_n;
            END IF;
        END IF;

        RAISE NOTICE 'Da tao assignment_id=% title=% teacher=% class_id=% targets~%', aid, titles[i], tid, cid,
            (SELECT count(*)::text FROM assignment_targets WHERE assignment_id = aid);
    END LOOP;
END $$;

-- Kiem tra nhanh (chay sau khoi DO)
-- SELECT a.assignment_id, a.title, c.teacher_id, c.class_id,
--        (SELECT count(*) FROM assignment_targets t WHERE t.assignment_id = a.assignment_id) AS so_sv_giao
-- FROM assignments a
-- JOIN classes c ON c.class_id = a.class_id
-- WHERE c.teacher_id IN (2, 3, 4)
-- ORDER BY a.assignment_id DESC
-- LIMIT 20;
