-- ============================================================
-- DropoffDesk: Core SQL Analysis
-- Analyst: Tanishka Suryawanshi
-- Database: dropoffdesk (PostgreSQL)
-- Purpose: Investigate 23% offer acceptance decline and
--          46% increase in time-to-hire (Q4)
-- Note: ::date casts required because pandas to_sql loads
--       date columns as text by default
-- ============================================================


-- ============================================================
-- QUERY 1: Stage Conversion Rate by Recruiter
-- Business Question: At which stage do we lose the most
-- candidates, and which recruiters have the worst conversion?
-- ============================================================

WITH stage_counts AS (
    SELECT
        pe.recruiter_id,
        r.name                                                  AS recruiter_name,
        pe.stage_name,
        COUNT(DISTINCT pe.candidate_id)                         AS total_candidates,
        COUNT(DISTINCT CASE WHEN pe.outcome = 'pass'
                       THEN pe.candidate_id END)               AS passed
    FROM pipeline_events pe
    JOIN recruiters r ON pe.recruiter_id = r.recruiter_id
    GROUP BY pe.recruiter_id, r.name, pe.stage_name
)
SELECT
    recruiter_name,
    stage_name,
    total_candidates,
    passed,
    ROUND(100.0 * passed / NULLIF(total_candidates, 0), 1)     AS conversion_pct
FROM stage_counts
ORDER BY recruiter_name, stage_name;


-- ============================================================
-- QUERY 2: Median and P90 Time-in-Stage
-- Business Question: Where is time being lost in the pipeline?
-- Why PERCENTILE_CONT not AVG: outliers (e.g. a role on hold
-- for months) inflate the mean and mislead the analysis.
-- ============================================================

WITH stage_with_next AS (
    SELECT
        candidate_id,
        stage_name,
        event_date::date,
        LEAD(event_date::date) OVER (
            PARTITION BY candidate_id
            ORDER BY event_date::date
        )                                                       AS next_event_date
    FROM pipeline_events
)
SELECT
    stage_name,
    ROUND(
        PERCENTILE_CONT(0.5) WITHIN GROUP (
            ORDER BY (next_event_date - event_date)
        )::numeric, 1
    )                                                           AS median_days,
    ROUND(
        PERCENTILE_CONT(0.9) WITHIN GROUP (
            ORDER BY (next_event_date - event_date)
        )::numeric, 1
    )                                                           AS p90_days,
    COUNT(*)                                                    AS n_candidates
FROM stage_with_next
WHERE next_event_date IS NOT NULL
GROUP BY stage_name
ORDER BY median_days DESC;


-- ============================================================
-- QUERY 3: Source Channel ROI
-- Business Question: Which sourcing channels convert best
-- from application all the way to accepted offer?
-- ============================================================

WITH channel_funnel AS (
    SELECT
        c.source_channel,
        COUNT(DISTINCT c.candidate_id)                          AS applications,
        COUNT(DISTINCT o.candidate_id)                         AS offers_extended,
        COUNT(DISTINCT CASE WHEN o.accepted = TRUE
                       THEN o.candidate_id END)                AS offers_accepted
    FROM candidates c
    LEFT JOIN offers o ON c.candidate_id = o.candidate_id
    GROUP BY c.source_channel
)
SELECT
    source_channel,
    applications,
    offers_extended,
    offers_accepted,
    ROUND(100.0 * offers_extended / NULLIF(applications, 0), 1)    AS offer_rate_pct,
    ROUND(100.0 * offers_accepted / NULLIF(offers_extended, 0), 1) AS acceptance_rate_pct,
    ROUND(100.0 * offers_accepted / NULLIF(applications, 0), 2)    AS source_quality_index
FROM channel_funnel
WHERE applications >= 10
ORDER BY source_quality_index DESC;


-- ============================================================
-- QUERY 4: Monthly Offer Acceptance Rate Trend
-- Business Question: When exactly did acceptance rate start
-- declining? Is Q4 a one-off or a continuing trend?
-- ============================================================

SELECT
    DATE_TRUNC('month', offer_date::date)                      AS month,
    COUNT(*)                                                    AS offers_extended,
    SUM(CASE WHEN accepted = TRUE THEN 1 ELSE 0 END)          AS accepted,
    ROUND(
        100.0 * SUM(CASE WHEN accepted = TRUE THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0), 1
    )                                                           AS acceptance_rate_pct
FROM offers
GROUP BY DATE_TRUNC('month', offer_date::date)
ORDER BY month;


-- ============================================================
-- QUERY 5: Median Time-to-Hire by Department
-- Business Question: Is the TTH increase everywhere,
-- or concentrated in Engineering specifically?
-- ============================================================

WITH hire_times AS (
    SELECT
        c.department,
        c.candidate_id,
        c.application_date::date,
        o.offer_date::date,
        (o.offer_date::date - c.application_date::date)        AS days_to_offer
    FROM candidates c
    JOIN offers o ON c.candidate_id = o.candidate_id
    WHERE o.accepted = TRUE
)
SELECT
    department,
    COUNT(*)                                                    AS hires,
    ROUND(
        PERCENTILE_CONT(0.5) WITHIN GROUP (
            ORDER BY days_to_offer
        )::numeric, 0
    )                                                           AS median_tth_days,
    ROUND(AVG(days_to_offer)::numeric, 0)                      AS mean_tth_days
FROM hire_times
GROUP BY department
ORDER BY median_tth_days DESC;


-- ============================================================
-- QUERY 6: Recruiter Performance Variance
-- Business Question: Are specific recruiters creating the
-- time-in-stage bottleneck we see in the aggregate data?
-- ============================================================

WITH recruiter_tth AS (
    SELECT
        pe.recruiter_id,
        r.name                                                  AS recruiter_name,
        pe.candidate_id,
        MIN(pe.event_date::date)                               AS first_contact,
        MAX(pe.event_date::date)                               AS last_event,
        (MAX(pe.event_date::date) - MIN(pe.event_date::date)) AS recruiter_tth
    FROM pipeline_events pe
    JOIN recruiters r ON pe.recruiter_id = r.recruiter_id
    GROUP BY pe.recruiter_id, r.name, pe.candidate_id
)
SELECT
    recruiter_name,
    COUNT(DISTINCT candidate_id)                                AS candidates_handled,
    ROUND(
        PERCENTILE_CONT(0.5) WITHIN GROUP (
            ORDER BY recruiter_tth
        )::numeric, 1
    )                                                           AS median_tth_days,
    ROUND(AVG(recruiter_tth)::numeric, 1)                      AS avg_tth_days
FROM recruiter_tth
GROUP BY recruiter_name
ORDER BY median_tth_days DESC;


-- ============================================================
-- QUERY 7: Offer Acceptance by Role Level and Quarter
-- Business Question: Is the acceptance drop concentrated at
-- a specific seniority level (e.g. Senior/Lead candidates)?
-- ============================================================

SELECT
    c.role_level,
    DATE_TRUNC('quarter', o.offer_date::date)                  AS quarter,
    COUNT(*)                                                    AS offers,
    SUM(CASE WHEN o.accepted = TRUE THEN 1 ELSE 0 END)        AS accepted,
    ROUND(
        100.0 * SUM(CASE WHEN o.accepted = TRUE THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0), 1
    )                                                           AS acceptance_pct
FROM offers o
JOIN candidates c ON o.candidate_id = c.candidate_id
GROUP BY c.role_level, DATE_TRUNC('quarter', o.offer_date::date)
ORDER BY quarter, c.role_level;


-- ============================================================
-- QUERY 8: Rejection Reason Distribution by Recruiter
-- Business Question: Do certain recruiters reject candidates
-- for different reasons — suggesting bias or coaching needs?
-- (This feeds the chi-square test in Phase 4)
-- ============================================================

SELECT
    r.name                                                      AS recruiter_name,
    pe.reject_reason,
    COUNT(*)                                                    AS rejections,
    ROUND(
        100.0 * COUNT(*) /
        SUM(COUNT(*)) OVER (PARTITION BY r.name), 1
    )                                                           AS pct_of_recruiter_rejections
FROM pipeline_events pe
JOIN recruiters r ON pe.recruiter_id = r.recruiter_id
WHERE pe.outcome = 'fail'
  AND pe.reject_reason != 'Not Provided'
GROUP BY r.name, pe.reject_reason
ORDER BY r.name, rejections DESC;
