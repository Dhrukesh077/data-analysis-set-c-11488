-- ============================================================================
-- Training Performance Analysis — Set C
-- sql/queries.sql
--
-- SQL dialect : SQLite 3 (version 3.45+)
-- Run sql/setup.sql first, then run this file against the same database.
-- ============================================================================

-- --------------------------------------------------------------------------
-- S2a — Average score by department (lowest first, highlights underperformance)
-- --------------------------------------------------------------------------
SELECT
    c.department,
    ROUND(AVG(a.score), 2) AS avg_score
FROM assessments a
JOIN courses c ON a.course_id = c.course_id
GROUP BY c.department
ORDER BY avg_score ASC;

-- --------------------------------------------------------------------------
-- S2b — Underperforming courses: average score below 60
-- --------------------------------------------------------------------------
SELECT
    c.course_id,
    c.course,
    ROUND(AVG(a.score), 2) AS avg_score
FROM assessments a
JOIN courses c ON a.course_id = c.course_id
GROUP BY c.course_id, c.course
HAVING AVG(a.score) < 60
ORDER BY avg_score ASC;

-- --------------------------------------------------------------------------
-- S2c — Top two batches by average score (alphabetical order breaks ties)
-- --------------------------------------------------------------------------
SELECT
    a.batch,
    ROUND(AVG(a.score), 2) AS avg_score
FROM assessments a
GROUP BY a.batch
ORDER BY avg_score DESC, a.batch ASC
LIMIT 2;

-- --------------------------------------------------------------------------
-- S3 — Diagnostic integrity check: every course_id in the fact table must
-- match a lookup row. LEFT JOIN from courses to assessments; any course
-- with zero matching assessments (unlikely here) still confirms integrity
-- by showing no NULL course_id gaps. Zero unmatched keys expected.
-- --------------------------------------------------------------------------
SELECT
    c.course_id,
    c.course,
    COUNT(a.assessment_id) AS assessment_count
FROM courses c
LEFT JOIN assessments a ON c.course_id = a.course_id
GROUP BY c.course_id, c.course
ORDER BY c.course_id;

-- Explicit unmatched-key check (should return 0 rows)
SELECT a.course_id
FROM assessments a
LEFT JOIN courses c ON a.course_id = c.course_id
WHERE c.course_id IS NULL;
