# Databricks notebook source
# MAGIC %md
# MAGIC # Clinical Trial Azure Data Engineering Pipeline
# MAGIC ## Bronze â†’ Silver â†’ Gold Medallion Architecture
# MAGIC
# MAGIC **Project:** Clinical Trial Lakehouse on Azure
# MAGIC **Stack:** Azure Data Factory Â· ADLS Gen2 Â· Databricks Â· Unity Catalog Â· Delta Lake
# MAGIC **Catalog:** `databricks_clinical_trial`
# MAGIC **Author:** Hisham Mohammed Afzal

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 â€” Infrastructure Setup
# MAGIC ### Register External Locations in Unity Catalog
# MAGIC Points Unity Catalog to the Bronze, Silver, and Gold containers in ADLS Gen2 using the `cred-clinical-adls` storage credential (Azure Managed Identity). This must run once before any data reads or writes.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE EXTERNAL LOCATION IF NOT EXISTS `clinical-trial-adls`
# MAGIC URL 'abfss://bronze@hishamclinicaldl.dfs.core.windows.net/'
# MAGIC WITH (STORAGE CREDENTIAL `cred-clinical-adls`)
# MAGIC COMMENT 'Bronze layer - raw Parquet ingested via ADF';
# MAGIC
# MAGIC CREATE EXTERNAL LOCATION IF NOT EXISTS `clinical-trial-silver`
# MAGIC URL 'abfss://silver@hishamclinicaldl.dfs.core.windows.net/'
# MAGIC WITH (STORAGE CREDENTIAL `cred-clinical-adls`)
# MAGIC COMMENT 'Silver layer - cleaned Delta tables';
# MAGIC
# MAGIC CREATE EXTERNAL LOCATION IF NOT EXISTS `clinical-trial-gold`
# MAGIC URL 'abfss://gold@hishamclinicaldl.dfs.core.windows.net/'
# MAGIC WITH (STORAGE CREDENTIAL `cred-clinical-adls`)
# MAGIC COMMENT 'Gold layer - business-ready Delta tables';

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 â€” Unity Catalog Schema Setup
# MAGIC Creates the Silver and Gold schemas inside the `databricks_clinical_trial` catalog. Schemas are like folders inside the catalog â€” they group related tables together.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE SCHEMA IF NOT EXISTS databricks_clinical_trial.silver;
# MAGIC CREATE SCHEMA IF NOT EXISTS databricks_clinical_trial.gold;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 â€” Bronze Layer Exploration
# MAGIC ### Schema Discovery Across All 18 Tables
# MAGIC Reads each Bronze Parquet table directly from ADLS Gen2 and prints the row count and column schema. Bronze is the raw, immutable copy of the source MySQL data â€” no transformations applied.

# COMMAND ----------

tables = [
    "adverse_events", "clinical_studies", "clinical_visits",
    "concomitant_medications", "dropouts", "drug_administration",
    "enrollments", "investigators", "lab_results", "medical_history",
    "medications", "patients", "protocol_deviations", "questionnaires",
    "research_sites", "study_arms", "study_sites", "vital_signs"
]

for table in tables:
    print("=" * 80)
    print(f"TABLE: {table}")
    df = spark.read.parquet(f"abfss://bronze@hishamclinicaldl.dfs.core.windows.net/{table}/")
    print(f"Rows: {df.count()}")
    df.printSchema()
    print()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 â€” Silver Layer Transformation
# MAGIC ### Design Principles
# MAGIC 1. One Delta table per source table â€” no joins in Silver
# MAGIC 2. Normalize excessive decimal precision (`decimal(38,18)` â†’ `decimal(12,2)`)
# MAGIC 3. Add audit columns: `silver_loaded_at` (timestamp) and `source_table` (string)
# MAGIC 4. Preserve all original columns â€” cleaning only, no business logic
# MAGIC 5. Write as Delta format for ACID transactions and time travel

# COMMAND ----------

from pyspark.sql.functions import current_timestamp, lit, col
from pyspark.sql.types import DecimalType

BRONZE_PATH = "abfss://bronze@hishamclinicaldl.dfs.core.windows.net/"
SILVER_PATH = "abfss://silver@hishamclinicaldl.dfs.core.windows.net/"

def normalize_decimals(df):
    """Cast all decimal(38,18) columns to decimal(12,2) for storage efficiency."""
    for field in df.schema.fields:
        if str(field.dataType).startswith("DecimalType"):
            df = df.withColumn(field.name, col(field.name).cast(DecimalType(12, 2)))
    return df

def transform_silver(df, table_name):
    """Apply Silver transformations: audit columns + decimal normalization."""
    df = df.withColumn("silver_loaded_at", current_timestamp()) \
           .withColumn("source_table", lit(table_name))
    df = normalize_decimals(df)
    return df

# COMMAND ----------

# MAGIC %md
# MAGIC ### Silver Load Execution
# MAGIC Runs the transformation function across all 18 tables. Reads each table from Bronze (Parquet), applies cleaning, writes as Delta to the Silver container. Mode is `overwrite` â€” safe to re-run.

# COMMAND ----------

for table in tables:
    print(f"Processing: {table}")
    df = spark.read.parquet(f"{BRONZE_PATH}{table}/")
    df_silver = transform_silver(df, table)
    df_silver.write \
        .format("delta") \
        .mode("overwrite") \
        .save(f"{SILVER_PATH}{table}/")
    print(f"  Done: {table}")

print("\nAll 18 Silver tables written successfully.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5 â€” Register Silver Tables in Unity Catalog
# MAGIC Delta files now exist in ADLS. This step registers each file path as a named external table in Unity Catalog so SQL queries can reference them by three-part name (`catalog.schema.table`). No data is moved â€” this is metadata registration only.

# COMMAND ----------

silver_tables = [
    "adverse_events", "clinical_studies", "clinical_visits",
    "concomitant_medications", "dropouts", "drug_administration",
    "enrollments", "investigators", "lab_results", "medical_history",
    "medications", "patients", "protocol_deviations", "questionnaires",
    "research_sites", "study_arms", "study_sites", "vital_signs"
]

for t in silver_tables:
    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS databricks_clinical_trial.silver.{t}
        USING DELTA
        LOCATION 'abfss://silver@hishamclinicaldl.dfs.core.windows.net/{t}/'
    """)
    print(f"Registered: databricks_clinical_trial.silver.{t}")

print("\nAll 18 Silver tables registered in Unity Catalog.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6 â€” Gold Layer: Business Analytics Tables
# MAGIC ### Architecture
# MAGIC Gold tables join cleaned Silver entities into analytics-ready views. Each table serves a specific business question. All tables are external Delta tables registered in Unity Catalog and stored in the Gold container for downstream Synapse Analytics consumption.
# MAGIC
# MAGIC | Table | Grain | Source Tables | Business Purpose |
# MAGIC |---|---|---|---|
# MAGIC | `patient_study_summary` | 1 row per enrollment | patients, enrollments, clinical_studies, study_arms, research_sites | Patient-level clinical overview |
# MAGIC | `lab_summary` | 1 row per lab result | lab_results, patients, clinical_visits, enrollments | Lab analytics with toxicity risk classification |
# MAGIC | `safety_adverse_events` | 1 row per adverse event | adverse_events, patients, enrollments | Safety monitoring and AE risk categorization |
# MAGIC | `visit_summary` | 1 row per clinical visit | clinical_visits, enrollments, patients | Visit compliance and timing analysis |

# COMMAND ----------

# MAGIC %md
# MAGIC ### Gold Table 1 â€” `patient_study_summary`
# MAGIC One row per patient enrollment. Joins patient demographics with study, arm, and site context. Used for enrollment reporting and patient-level clinical overviews.
# MAGIC
# MAGIC **Expected rows:** 200

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

# MAGIC %md
# MAGIC ### Gold Table 2 â€” `lab_summary`
# MAGIC One row per lab result. Joins lab data with patient demographics and study context via the visitâ†’enrollment path (correct join path to avoid row multiplication). Adds lab status and toxicity risk classification.
# MAGIC
# MAGIC **Expected rows:** 7715

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

# MAGIC %md
# MAGIC ### Gold Table 3 â€” `safety_adverse_events`
# MAGIC One row per adverse event. Joins AE data with patient demographics and enrollment context. Adds AE risk category, resolution status, and duration in days for safety monitoring.
# MAGIC
# MAGIC **Expected rows:** 245

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

# MAGIC %md
# MAGIC ### Gold Table 4 â€” `visit_summary`
# MAGIC One row per clinical visit. Joins visit scheduling data with patient and study context. Adds visit timing status (On Time / Late / Early / Not Completed) and days deviation from scheduled date.
# MAGIC
# MAGIC **Expected rows:** 1108

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

# MAGIC %md
# MAGIC ## Step 7 â€” Final Verification
# MAGIC Confirms all four Gold tables exist in Unity Catalog and returns the correct row counts. Run this after any re-execution to validate end-to-end pipeline integrity.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 'patient_study_summary'  AS gold_table, COUNT(*) AS row_count FROM databricks_clinical_trial.gold.patient_study_summary
# MAGIC UNION ALL
# MAGIC SELECT 'lab_summary',                           COUNT(*) FROM databricks_clinical_trial.gold.lab_summary
# MAGIC UNION ALL
# MAGIC SELECT 'safety_adverse_events',                 COUNT(*) FROM databricks_clinical_trial.gold.safety_adverse_events
# MAGIC UNION ALL
# MAGIC SELECT 'visit_summary',                         COUNT(*) FROM databricks_clinical_trial.gold.visit_summary
# MAGIC ORDER BY gold_table;

# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE EXTENDED databricks_clinical_trial.gold.patient_study_summary;
