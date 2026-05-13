-- =============================================================================
-- Đồng bộ các SERIAL liên quan assignment (sau import/restore khiến sequence lệch).
-- Chạy trong pgAdmin / psql khi gặp duplicate key trên:
--   assignments_pkey, assignment_requirements_pkey, assignment_testcases_pkey
-- =============================================================================

DO $$
DECLARE
  seq_name text;
  mx integer;
BEGIN
  seq_name := pg_get_serial_sequence('assignments', 'assignment_id');
  IF seq_name IS NULL THEN
    RAISE NOTICE 'Không tìm thấy SERIAL/IDENTITY cho assignments.assignment_id.';
    RETURN;
  END IF;

  SELECT COALESCE(MAX(assignment_id), 0) INTO mx FROM assignments;
  IF mx <= 0 THEN
    RAISE NOTICE 'Bảng assignments trống — không chỉnh sequence.';
    RETURN;
  END IF;

  PERFORM setval(seq_name::regclass, mx);
  RAISE NOTICE 'Đã setval % → % (lần INSERT SERIAL tiếp theo sẽ > %).', seq_name, mx, mx;
END $$;

-- assignment_requirements.requirement_id
DO $$
DECLARE
  seq_name text;
  mx integer;
BEGIN
  seq_name := pg_get_serial_sequence('assignment_requirements', 'requirement_id');
  IF seq_name IS NULL THEN
    RAISE NOTICE 'Không tìm thấy SERIAL cho assignment_requirements.requirement_id.';
    RETURN;
  END IF;
  SELECT COALESCE(MAX(requirement_id), 0) INTO mx FROM assignment_requirements;
  IF mx <= 0 THEN
    RAISE NOTICE 'Bảng assignment_requirements trống — bỏ qua.';
    RETURN;
  END IF;
  PERFORM setval(seq_name::regclass, mx);
  RAISE NOTICE 'Đã setval % → %.', seq_name, mx;
END $$;

-- assignment_testcases.testcase_id
DO $$
DECLARE
  seq_name text;
  mx integer;
BEGIN
  seq_name := pg_get_serial_sequence('assignment_testcases', 'testcase_id');
  IF seq_name IS NULL THEN
    RAISE NOTICE 'Không tìm thấy SERIAL cho assignment_testcases.testcase_id.';
    RETURN;
  END IF;
  SELECT COALESCE(MAX(testcase_id), 0) INTO mx FROM assignment_testcases;
  IF mx <= 0 THEN
    RAISE NOTICE 'Bảng assignment_testcases trống — bỏ qua.';
    RETURN;
  END IF;
  PERFORM setval(seq_name::regclass, mx);
  RAISE NOTICE 'Đã setval % → %.', seq_name, mx;
END $$;
