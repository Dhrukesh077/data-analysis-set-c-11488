-- ============================================================================
-- Training Performance Analysis — Set C
-- sql/setup.sql
--
-- SQL dialect : SQLite 3 (version 3.45+)
-- Run this file FIRST, then run sql/queries.sql against the same database.
-- Example (CLI):
--     sqlite3 training_performance.db < sql/setup.sql
--     sqlite3 training_performance.db < sql/queries.sql
-- ============================================================================

DROP TABLE IF EXISTS assessments;
DROP TABLE IF EXISTS courses;

-- --------------------------------------------------------------------------
-- S1a: Table definitions with primary keys and a foreign key constraint
-- --------------------------------------------------------------------------

CREATE TABLE courses (
    course_id   TEXT PRIMARY KEY,
    course      TEXT NOT NULL,
    department  TEXT NOT NULL
);

CREATE TABLE assessments (
    assessment_id   INTEGER PRIMARY KEY,
    month           TEXT NOT NULL,           -- Jan / Feb / Mar (ordered category)
    course_id       TEXT NOT NULL,
    batch           TEXT NOT NULL,           -- Morning / Evening / Weekend
    score           REAL NOT NULL,           -- 0-100
    attendance_pct  REAL NOT NULL,           -- 0-100
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

-- Enforce the foreign key at runtime (SQLite has it off by default)
PRAGMA foreign_keys = ON;

-- --------------------------------------------------------------------------
-- S1b: Data load — 4 lookup rows, then 12 fact rows.
-- The duplicate row (original assessment_id 12 appeared twice in the raw
-- 13-row CSV) is excluded here at load time.
-- --------------------------------------------------------------------------

INSERT INTO courses (course_id, course, department) VALUES
    ('C1', 'Excel',   'Business'),
    ('C2', 'PowerBI', 'Business'),
    ('C3', 'SQL',     'Technology'),
    ('C4', 'Python',  'Technology');

INSERT INTO assessments (assessment_id, month, course_id, batch, score, attendance_pct) VALUES
    (1,  'Jan', 'C1', 'Morning', 72, 90),
    (2,  'Jan', 'C2', 'Evening', 45, 70),
    (3,  'Jan', 'C3', 'Morning', 65, 85),
    (4,  'Jan', 'C4', 'Weekend', 38, 60),
    (5,  'Feb', 'C1', 'Evening', 80, 95),
    (6,  'Feb', 'C2', 'Weekend', 55, 80),
    (7,  'Feb', 'C3', 'Morning', 48, 75),
    (8,  'Feb', 'C4', 'Evening', 68, 88),
    (9,  'Mar', 'C1', 'Weekend', 90, 98),
    (10, 'Mar', 'C2', 'Morning', 60, 82),
    (11, 'Mar', 'C3', 'Evening', 75, 92),
    (12, 'Mar', 'C4', 'Weekend', 42, 65);
    -- duplicate of assessment_id 12 intentionally NOT inserted (removed here)

-- Sanity check row counts
SELECT 'courses row count'      AS check_name, COUNT(*) AS row_count FROM courses;
SELECT 'assessments row count'  AS check_name, COUNT(*) AS row_count FROM assessments;
