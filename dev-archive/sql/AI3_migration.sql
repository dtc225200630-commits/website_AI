-- ==========================================
-- PostgreSQL Migration for AI3 Database
-- Add 2 columns to evaluation_sessions table
-- Date: 2026-04-01
-- ==========================================

-- Step 1: Add code_analysis_score column
ALTER TABLE evaluation_sessions
ADD COLUMN IF NOT EXISTS code_analysis_score DECIMAL(5,2) DEFAULT 0;

-- Step 2: Add llm_score column
ALTER TABLE evaluation_sessions
ADD COLUMN IF NOT EXISTS llm_score DECIMAL(5,2) DEFAULT 0;

-- Step 3: Verify columns (run this to check if columns were added successfully)
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'evaluation_sessions'
ORDER BY ordinal_position;
