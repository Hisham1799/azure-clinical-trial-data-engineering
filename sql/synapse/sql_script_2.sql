USE clinical_trial_serving;

SELECT 'patient_study_summary' AS table_name, COUNT(*) AS row_count FROM patient_study_summary
UNION ALL
SELECT 'lab_summary',          COUNT(*) FROM lab_summary
UNION ALL
SELECT 'safety_adverse_events', COUNT(*) FROM safety_adverse_events
UNION ALL
SELECT 'visit_summary',         COUNT(*) FROM visit_summary
ORDER BY table_name;
