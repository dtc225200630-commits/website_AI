-- Migration: Add code_analysis_score to evaluation_sessions
-- This maintains backward compatibility while supporting the new code_analysis agent

ALTER TABLE evaluation_sessions ADD COLUMN IF NOT EXISTS code_analysis_score DECIMAL(5,2);
ALTER TABLE evaluation_sessions ADD COLUMN IF NOT EXISTS llm_score DECIMAL(5,2);

-- Optional: Add index for faster queries
CREATE INDEX IF NOT EXISTS idx_evaluation_sessions_submission_id 
ON evaluation_sessions(submission_id);
