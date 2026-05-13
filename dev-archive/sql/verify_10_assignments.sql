-- ==========================================
-- VERIFY QUERIES - KIỂM TRA DỮ LIỆU
-- ==========================================

-- 1. Kiểm tra tổng số assignments (phải = 11)
SELECT COUNT(*) as "Tổng Assignments" FROM assignments;

-- 2. Kiểm tra chi tiết tất cả assignments
SELECT assignment_id, title, due_date FROM assignments ORDER BY assignment_id;

-- 3. Kiểm tra tổng số requirements (phải = 33)
SELECT COUNT(*) as "Tổng Requirements" FROM assignment_requirements;

-- 4. Kiểm tra requirements của mỗi assignment
SELECT a.assignment_id, a.title, COUNT(ar.requirement_id) as "Số Requirements"
FROM assignments a
LEFT JOIN assignment_requirements ar ON a.assignment_id = ar.assignment_id
GROUP BY a.assignment_id, a.title
ORDER BY a.assignment_id;

-- 5. Kiểm tra chi tiết requirements của assignment 2
SELECT * FROM assignment_requirements WHERE assignment_id = 2;

-- 6. Kiểm tra chi tiết requirements của assignment 5
SELECT * FROM assignment_requirements WHERE assignment_id = 5;

-- 7. Kiểm tra tổng số test cases (phải = 33)
SELECT COUNT(*) as "Tổng Test Cases" FROM assignment_testcases;

-- 8. Kiểm tra test cases của assignment 3
SELECT * FROM assignment_testcases WHERE assignment_id = 3;

-- 9. Kiểm tra chi tiết test cases của assignment 6
SELECT * FROM assignment_testcases WHERE assignment_id = 6;

-- 10. Kiểm tra tổng số submissions (phải = 110)
SELECT COUNT(*) as "Tổng Submissions" FROM submissions;

-- 11. Kiểm tra số submissions cho mỗi assignment
SELECT a.assignment_id, a.title, COUNT(s.submission_id) as "Số Submissions"
FROM assignments a
LEFT JOIN submissions s ON a.assignment_id = s.assignment_id
GROUP BY a.assignment_id, a.title
ORDER BY a.assignment_id;

-- 12. Kiểm tra submissions của assignment 2
SELECT submission_id, student_id, file_name FROM submissions WHERE assignment_id = 2;

-- 13. Kiểm tra tổng số evaluations (phải = 110)
SELECT COUNT(*) as "Tổng Evaluations" FROM evaluation_sessions;

-- 14. Kiểm tra điểm trung bình của mỗi assignment
SELECT a.assignment_id, a.title, ROUND(AVG(es.total_score), 2) as "Điểm TB"
FROM assignments a
LEFT JOIN submissions s ON a.assignment_id = s.assignment_id
LEFT JOIN evaluation_sessions es ON s.submission_id = es.submission_id
GROUP BY a.assignment_id, a.title
ORDER BY a.assignment_id;

-- 15. Kiểm tra chi tiết evaluations của assignment 2
SELECT s.submission_id, st.student_id, st.full_name, es.total_score, es.final_feedback
FROM submissions s
JOIN students st ON s.student_id = st.student_id
JOIN evaluation_sessions es ON s.submission_id = es.submission_id
WHERE s.assignment_id = 2
ORDER BY s.student_id;

-- 16. Kiểm tra điểm cao nhất và thấp nhất
SELECT 
    ROUND(MAX(total_score), 2) as "Điểm Cao Nhất",
    ROUND(MIN(total_score), 2) as "Điểm Thấp Nhất",
    ROUND(AVG(total_score), 2) as "Điểm Trung Bình"
FROM evaluation_sessions;

-- 17. Kiểm tra agent logs (phải = 50+)
SELECT COUNT(*) as "Tổng Agent Logs" FROM agent_logs;

-- 18. Kiểm tra agent logs cho assignment 7
SELECT ag.log_id, ag.agent_name, ag.result
FROM agent_logs ag
JOIN submissions s ON ag.submission_id = s.submission_id
WHERE s.assignment_id = 7
LIMIT 5;

-- 19. Thống kê sinh viên theo điểm
SELECT st.student_id, st.full_name, COUNT(es.session_id) as "Bài Đã Nộp", ROUND(AVG(es.total_score), 2) as "Điểm TB"
FROM students st
LEFT JOIN submissions s ON st.student_id = s.student_id
LEFT JOIN evaluation_sessions es ON s.submission_id = es.submission_id
GROUP BY st.student_id, st.full_name
ORDER BY ROUND(AVG(es.total_score), 2) DESC;

-- 20. Danh sách assignments với mô tả đầy đủ
SELECT 
    a.assignment_id,
    a.title,
    a.description,
    a.due_date,
    COUNT(DISTINCT ar.requirement_id) as "Số Yêu Cầu",
    COUNT(DISTINCT atc.testcase_id) as "Số Test Case",
    COUNT(DISTINCT s.submission_id) as "Số Bài Nộp"
FROM assignments a
LEFT JOIN assignment_requirements ar ON a.assignment_id = ar.assignment_id
LEFT JOIN assignment_testcases atc ON a.assignment_id = atc.assignment_id
LEFT JOIN submissions s ON a.assignment_id = s.assignment_id
GROUP BY a.assignment_id, a.title, a.description, a.due_date
ORDER BY a.assignment_id;
