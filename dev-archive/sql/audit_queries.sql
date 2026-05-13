-- 1) Full requirements + weights by assignment
SELECT
  a.assignment_id,
  a.title,
  r.requirement_id,
  r.requirement_text,
  r.weight
FROM assignments a
LEFT JOIN assignment_requirements r
  ON a.assignment_id = r.assignment_id
ORDER BY a.assignment_id, r.requirement_id;

-- 2) Full testcases + weights by assignment
SELECT
  assignment_id,
  testcase_id,
  input_data,
  expected_output,
  score_weight
FROM assignment_testcases
ORDER BY assignment_id, testcase_id;

-- 3) Latest evaluation score breakdown
SELECT
  es.session_id,
  es.submission_id,
  s.assignment_id,
  a.title,
  s.student_id,
  st.full_name AS student_name,
  es.syntax_score,
  es.requirement_score,
  es.structure_score,
  es.test_score,
  es.llm_score,
  es.total_score,
  es.created_at
FROM evaluation_sessions es
JOIN submissions s ON s.submission_id = es.submission_id
JOIN assignments a ON a.assignment_id = s.assignment_id
JOIN students st ON st.student_id = s.student_id
ORDER BY es.created_at DESC
LIMIT 50;

-- 4) One submission deep audit (replace :submission_id manually)
-- Example: WHERE es.submission_id = 11
SELECT
  es.session_id,
  es.submission_id,
  s.assignment_id,
  a.title,
  s.student_id,
  st.full_name AS student_name,
  es.syntax_score,
  es.code_analysis_score,
  es.requirement_score,
  es.structure_score,
  es.test_score,
  es.llm_score,
  es.total_score,
  es.final_feedback,
  es.agent_details,
  es.created_at
FROM evaluation_sessions es
JOIN submissions s ON s.submission_id = es.submission_id
JOIN assignments a ON a.assignment_id = s.assignment_id
JOIN students st ON st.student_id = s.student_id
WHERE es.submission_id = 11
ORDER BY es.created_at DESC
LIMIT 1;
