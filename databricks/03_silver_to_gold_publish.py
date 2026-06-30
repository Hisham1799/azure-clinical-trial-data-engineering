# Databricks notebook source
# MAGIC %sql
# MAGIC SHOW TABLES IN databricks_clinical_trial.gold;

# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE TABLE databricks_clinical_trial.gold.patient_study_summary;

# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE TABLE databricks_clinical_trial.gold.lab_summary;

# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE TABLE databricks_clinical_trial.gold.safety_adverse_events;

# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE TABLE databricks_clinical_trial.gold.visit_summary;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     (SELECT COUNT(*) FROM databricks_clinical_trial.gold.patient_study_summary) AS patient_study_summary,
# MAGIC     (SELECT COUNT(*) FROM databricks_clinical_trial.gold.lab_summary) AS lab_summary,
# MAGIC     (SELECT COUNT(*) FROM databricks_clinical_trial.gold.safety_adverse_events) AS safety_adverse_events,
# MAGIC     (SELECT COUNT(*) FROM databricks_clinical_trial.gold.visit_summary) AS visit_summary;

# COMMAND ----------

print("=" * 70)
print("Publishing Gold Table : patient_study_summary")

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE databricks_clinical_trial.gold.patient_study_summary
# MAGIC USING DELTA
# MAGIC LOCATION 'abfss://gold@hishamclinicaldl.dfs.core.windows.net/patient_study_summary/'
# MAGIC AS
# MAGIC SELECT
# MAGIC     p.patient_id,
# MAGIC     p.patient_code,
# MAGIC     p.gender,
# MAGIC     p.race,
# MAGIC     p.ethnicity,
# MAGIC     p.date_of_birth,
# MAGIC     floor(datediff(current_date(), p.date_of_birth) / 365.25) AS age_years,
# MAGIC
# MAGIC     e.enrollment_id,
# MAGIC     e.enrollment_date,
# MAGIC     e.status                AS enrollment_status,
# MAGIC
# MAGIC     s.study_id,
# MAGIC     s.study_code,
# MAGIC     s.study_title,
# MAGIC     s.therapeutic_area,
# MAGIC     s.phase,
# MAGIC
# MAGIC     a.arm_id,
# MAGIC     a.arm_name,
# MAGIC
# MAGIC     r.site_id,
# MAGIC     r.site_name
# MAGIC FROM databricks_clinical_trial.silver.patients          p
# MAGIC INNER JOIN databricks_clinical_trial.silver.enrollments e
# MAGIC     ON p.patient_id = e.patient_id
# MAGIC INNER JOIN databricks_clinical_trial.silver.clinical_studies s
# MAGIC     ON e.study_id = s.study_id
# MAGIC LEFT JOIN  databricks_clinical_trial.silver.study_arms  a
# MAGIC     ON e.arm_id = a.arm_id
# MAGIC LEFT JOIN  databricks_clinical_trial.silver.research_sites r
# MAGIC     ON e.site_id = r.site_id;
# MAGIC
# MAGIC SELECT COUNT(*) AS row_count FROM databricks_clinical_trial.gold.patient_study_summary;

# COMMAND ----------

count = spark.sql("""
SELECT COUNT(*) AS cnt
FROM databricks_clinical_trial.gold.patient_study_summary
""").collect()[0]["cnt"]

print(f"Rows Published : {count}")
print("Status         : SUCCESS")
print("=" * 70)

# COMMAND ----------

print("=" * 70)
print("Publishing Gold Table : lab_summary")

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE databricks_clinical_trial.gold.lab_summary
# MAGIC USING DELTA
# MAGIC LOCATION 'abfss://gold@hishamclinicaldl.dfs.core.windows.net/lab_summary/'
# MAGIC AS
# MAGIC SELECT
# MAGIC     l.lab_result_id,
# MAGIC     l.visit_id,
# MAGIC     l.patient_id,
# MAGIC
# MAGIC     p.patient_code,
# MAGIC     p.gender,
# MAGIC     floor(datediff(current_date(), p.date_of_birth) / 365.25) AS age_years,
# MAGIC
# MAGIC     v.enrollment_id,
# MAGIC     e.study_id,
# MAGIC     e.site_id,
# MAGIC
# MAGIC     l.lab_test_name,
# MAGIC     l.lab_test_code,
# MAGIC     l.lab_panel,
# MAGIC     l.result_value,
# MAGIC     l.result_unit,
# MAGIC     l.normal_range_low,
# MAGIC     l.normal_range_high,
# MAGIC     l.is_abnormal,
# MAGIC     l.toxicity_grade,
# MAGIC
# MAGIC     CASE WHEN l.is_abnormal = true THEN 'Abnormal' ELSE 'Normal' END AS lab_status,
# MAGIC
# MAGIC     CASE
# MAGIC         WHEN l.toxicity_grade >= 3 THEN 'High Risk'
# MAGIC         WHEN l.toxicity_grade = 2  THEN 'Moderate Risk'
# MAGIC         ELSE 'Low Risk'
# MAGIC     END AS toxicity_risk_category,
# MAGIC
# MAGIC     l.collection_datetime,
# MAGIC     l.result_datetime
# MAGIC FROM databricks_clinical_trial.silver.lab_results       l
# MAGIC LEFT JOIN databricks_clinical_trial.silver.patients     p
# MAGIC     ON l.patient_id = p.patient_id
# MAGIC LEFT JOIN databricks_clinical_trial.silver.clinical_visits v
# MAGIC     ON l.visit_id = v.visit_id
# MAGIC LEFT JOIN databricks_clinical_trial.silver.enrollments  e
# MAGIC     ON v.enrollment_id = e.enrollment_id;
# MAGIC
# MAGIC SELECT COUNT(*) AS row_count FROM databricks_clinical_trial.gold.lab_summary;

# COMMAND ----------

count = spark.sql("""
SELECT COUNT(*) AS cnt
FROM databricks_clinical_trial.gold.lab_summary
""").collect()[0]["cnt"]

print(f"Rows Published : {count}")
print("Status         : SUCCESS")
print("=" * 70)

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE databricks_clinical_trial.gold.safety_adverse_events
# MAGIC USING DELTA
# MAGIC LOCATION 'abfss://gold@hishamclinicaldl.dfs.core.windows.net/safety_adverse_events/'
# MAGIC AS
# MAGIC SELECT
# MAGIC     ae.ae_id,
# MAGIC     ae.patient_id,
# MAGIC     ae.visit_id,
# MAGIC     ae.enrollment_id,
# MAGIC     ae.reporter_investigator_id,
# MAGIC
# MAGIC     p.patient_code,
# MAGIC     p.gender,
# MAGIC     floor(datediff(current_date(), p.date_of_birth) / 365.25) AS age_years,
# MAGIC
# MAGIC     e.study_id,
# MAGIC     e.site_id,
# MAGIC
# MAGIC     ae.ae_term,
# MAGIC     ae.meddra_pt_code,
# MAGIC     ae.severity,
# MAGIC     ae.ctcae_grade,
# MAGIC     ae.onset_date,
# MAGIC     ae.resolution_date,
# MAGIC     ae.outcome,
# MAGIC     ae.is_serious,
# MAGIC     ae.sae_category,
# MAGIC     ae.causality,
# MAGIC     ae.action_taken,
# MAGIC     ae.is_expected,
# MAGIC
# MAGIC     CASE
# MAGIC         WHEN ae.is_serious = true    THEN 'Serious AE'
# MAGIC         WHEN ae.ctcae_grade >= 3     THEN 'High Grade AE'
# MAGIC         WHEN ae.ctcae_grade = 2      THEN 'Moderate AE'
# MAGIC         ELSE 'Low Grade AE'
# MAGIC     END AS ae_risk_category,
# MAGIC
# MAGIC     CASE
# MAGIC         WHEN ae.resolution_date IS NULL THEN 'Ongoing'
# MAGIC         ELSE 'Resolved'
# MAGIC     END AS ae_status,
# MAGIC
# MAGIC     datediff(ae.resolution_date, ae.onset_date) AS ae_duration_days,
# MAGIC
# MAGIC     ae.created_at,
# MAGIC     ae.updated_at
# MAGIC FROM databricks_clinical_trial.silver.adverse_events    ae
# MAGIC LEFT JOIN databricks_clinical_trial.silver.patients     p
# MAGIC     ON ae.patient_id = p.patient_id
# MAGIC LEFT JOIN databricks_clinical_trial.silver.enrollments  e
# MAGIC     ON ae.enrollment_id = e.enrollment_id;
# MAGIC
# MAGIC SELECT COUNT(*) AS row_count FROM databricks_clinical_trial.gold.safety_adverse_events;

# COMMAND ----------

count = spark.sql("""
SELECT COUNT(*) AS cnt
FROM databricks_clinical_trial.gold.safety_adverse_events
""").collect()[0]["cnt"]

print(f"Rows Published : {count}")
print("Status         : SUCCESS")
print("=" * 70)

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE databricks_clinical_trial.gold.visit_summary
# MAGIC USING DELTA
# MAGIC LOCATION 'abfss://gold@hishamclinicaldl.dfs.core.windows.net/visit_summary/'
# MAGIC AS
# MAGIC SELECT
# MAGIC     v.visit_id,
# MAGIC     v.enrollment_id,
# MAGIC     v.investigator_id,
# MAGIC     v.visit_number,
# MAGIC     v.visit_name,
# MAGIC     v.visit_type,
# MAGIC
# MAGIC     e.patient_id,
# MAGIC     p.patient_code,
# MAGIC     e.study_id,
# MAGIC     e.site_id,
# MAGIC
# MAGIC     v.scheduled_date,
# MAGIC     v.actual_visit_date,
# MAGIC     v.visit_window_start,
# MAGIC     v.visit_window_end,
# MAGIC     v.visit_status,
# MAGIC
# MAGIC     CASE
# MAGIC         WHEN v.actual_visit_date IS NULL                                           THEN 'Not Completed'
# MAGIC         WHEN v.actual_visit_date BETWEEN v.visit_window_start AND v.visit_window_end THEN 'On Time'
# MAGIC         WHEN v.actual_visit_date < v.visit_window_start                            THEN 'Early'
# MAGIC         WHEN v.actual_visit_date > v.visit_window_end                              THEN 'Late'
# MAGIC         ELSE 'Unknown'
# MAGIC     END AS visit_timing_status,
# MAGIC
# MAGIC     datediff(v.actual_visit_date, v.scheduled_date) AS days_from_scheduled,
# MAGIC
# MAGIC     v.notes,
# MAGIC     v.created_at,
# MAGIC     v.updated_at
# MAGIC FROM databricks_clinical_trial.silver.clinical_visits   v
# MAGIC LEFT JOIN databricks_clinical_trial.silver.enrollments  e
# MAGIC     ON v.enrollment_id = e.enrollment_id
# MAGIC LEFT JOIN databricks_clinical_trial.silver.patients     p
# MAGIC     ON e.patient_id = p.patient_id;
# MAGIC
# MAGIC SELECT COUNT(*) AS row_count FROM databricks_clinical_trial.gold.visit_summary;

# COMMAND ----------

count = spark.sql("""
SELECT COUNT(*) AS cnt
FROM databricks_clinical_trial.gold.visit_summary
""").collect()[0]["cnt"]

print(f"Rows Published : {count}")
print("Status         : SUCCESS")
print("=" * 70)

# COMMAND ----------

print("=" * 70)
print("Gold Publish Completed Successfully")
print("=" * 70)

summary = spark.sql("""
SELECT
    (SELECT COUNT(*) FROM databricks_clinical_trial.gold.patient_study_summary) AS patient_study_summary,
    (SELECT COUNT(*) FROM databricks_clinical_trial.gold.lab_summary) AS lab_summary,
    (SELECT COUNT(*) FROM databricks_clinical_trial.gold.safety_adverse_events) AS safety_adverse_events,
    (SELECT COUNT(*) FROM databricks_clinical_trial.gold.visit_summary) AS visit_summary
""")

display(summary)
