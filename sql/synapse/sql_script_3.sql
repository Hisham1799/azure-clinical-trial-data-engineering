USE clinical_trial_serving;

-- 1. Enrollment status breakdown by study
SELECT
    study_code,
    study_title,
    enrollment_status,
    COUNT(*) AS patient_count
FROM patient_study_summary
GROUP BY study_code, study_title, enrollment_status
ORDER BY study_code, enrollment_status;

-- 2. Adverse event risk distribution
SELECT
    ae_risk_category,
    ae_status,
    COUNT(*) AS total_events
FROM safety_adverse_events
GROUP BY ae_risk_category, ae_status
ORDER BY total_events DESC;

-- 3. Lab toxicity summary by study
SELECT
    study_id,
    toxicity_risk_category,
    COUNT(*) AS total_lab_results
FROM lab_summary
GROUP BY study_id, toxicity_risk_category
ORDER BY study_id, toxicity_risk_category;

-- 4. Visit compliance by site
SELECT
    site_id,
    visit_timing_status,
    COUNT(*) AS total_visits
FROM visit_summary
GROUP BY site_id, visit_timing_status
ORDER BY site_id, visit_timing_status;
