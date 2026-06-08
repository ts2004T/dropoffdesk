-- DropoffDesk: Hiring Funnel Intelligence Platform
-- Schema Version 1.0
-- Author: Tanishka Suryawanshi

-- Drop tables if they exist (allows re-running this script cleanly)
DROP TABLE IF EXISTS offers CASCADE;
DROP TABLE IF EXISTS pipeline_events CASCADE;
DROP TABLE IF EXISTS candidates CASCADE;
DROP TABLE IF EXISTS recruiters CASCADE;
DROP TABLE IF EXISTS roles CASCADE;

-- ROLES: open positions the company is trying to fill
CREATE TABLE roles (
    role_id       SERIAL PRIMARY KEY,
    title         VARCHAR(100) NOT NULL,          -- e.g. "Senior Software Engineer"
    department    VARCHAR(50) NOT NULL,            -- e.g. "Engineering", "Marketing"
    level         VARCHAR(20) NOT NULL,            -- "Junior", "Mid", "Senior", "Lead"
    headcount_target INT NOT NULL DEFAULT 1,       -- how many people to hire into this role
    open_date     DATE NOT NULL,
    closed_date   DATE                             -- NULL means still open
);

-- RECRUITERS: the people managing the hiring process
CREATE TABLE recruiters (
    recruiter_id  SERIAL PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    team          VARCHAR(50),                     -- e.g. "Tech Hiring", "Business Hiring"
    join_date     DATE NOT NULL,
    region        VARCHAR(50)                      -- e.g. "Bangalore", "Mumbai"
);

-- CANDIDATES: every person who applied
CREATE TABLE candidates (
    candidate_id     SERIAL PRIMARY KEY,
    name             VARCHAR(100) NOT NULL,
    source_channel   VARCHAR(50),                 -- WHERE they came from: LinkedIn, Naukri, etc.
    application_date DATE NOT NULL,
    role_level       VARCHAR(20),                 -- seniority they applied for
    department       VARCHAR(50)
);

-- PIPELINE_EVENTS: one row per stage each candidate passed through
-- This is the most important table — it's where the funnel analysis lives
CREATE TABLE pipeline_events (
    event_id      SERIAL PRIMARY KEY,
    candidate_id  INT REFERENCES candidates(candidate_id),
    stage_name    VARCHAR(50) NOT NULL,           -- "Application Review", "Phone Screen", etc.
    event_date    DATE NOT NULL,
    recruiter_id  INT REFERENCES recruiters(recruiter_id),
    outcome       VARCHAR(20),                    -- "pass", "fail", "withdrawn", "pending"
    reject_reason VARCHAR(100)                    -- only filled when outcome = "fail"
);

-- OFFERS: extended to candidates who passed all stages
CREATE TABLE offers (
    offer_id      SERIAL PRIMARY KEY,
    candidate_id  INT REFERENCES candidates(candidate_id),
    offer_date    DATE NOT NULL,
    offer_expiry  DATE NOT NULL,
    accepted      BOOLEAN,                        -- TRUE = accepted, FALSE = declined, NULL = pending
    join_date     DATE,                           -- actual first day at work (only if accepted)
    salary_band   VARCHAR(20)                     -- "Band 1" through "Band 5"
);