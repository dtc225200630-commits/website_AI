-- ==========================================
-- PostgreSQL Migration Script
-- Add 2 new columns to evaluation_sessions table
-- ==========================================
-- Purpose: Add code_analysis_score and llm_score columns to support backend evaluation system
-- Run this if you have an existing database with evaluation_sessions table

-- Add code_analysis_score column
ALTER TABLE evaluation_sessions
ADD COLUMN IF NOT EXISTS code_analysis_score DECIMAL(5,2) DEFAULT 0;

-- Add llm_score column
ALTER TABLE evaluation_sessions
ADD COLUMN IF NOT EXISTS llm_score DECIMAL(5,2) DEFAULT 0;

-- Verify columns were added
-- SELECT column_name, data_type, column_default
-- FROM information_schema.columns
-- WHERE table_name = 'evaluation_sessions'
-- ORDER BY ordinal_position;
