# Databricks notebook source
# MAGIC %md
# MAGIC ### Connection and Testing

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE EXTERNAL LOCATION IF NOT EXISTS `clinical-trial-silver`
# MAGIC URL 'abfss://silver@hishamclinicaldl.dfs.core.windows.net/'
# MAGIC WITH (
# MAGIC     STORAGE CREDENTIAL `cred-clinical-adls`
# MAGIC )
# MAGIC COMMENT 'Silver layer cleaned Delta tables';

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE EXTERNAL LOCATION IF NOT EXISTS `clinical-trial-gold`
# MAGIC URL 'abfss://gold@hishamclinicaldl.dfs.core.windows.net/'
# MAGIC WITH (
# MAGIC     STORAGE CREDENTIAL `cred-clinical-adls`
# MAGIC )
# MAGIC COMMENT 'Gold layer business-ready Delta tables';

# COMMAND ----------

# MAGIC %md
# MAGIC ### Exploratory Data Analysis

# COMMAND ----------

tables = [
    "adverse_events",
    "clinical_studies",
    "clinical_visits",
    "concomitant_medications",
    "dropouts",
    "drug_administration",
    "enrollments",
    "investigators",
    "lab_results",
    "medical_history",
    "medications",
    "patients",
    "protocol_deviations",
    "questionnaires",
    "research_sites",
    "study_arms",
    "study_sites",
    "vital_signs"
]

# COMMAND ----------

for table in tables:
    print("=" * 80)
    print(f"TABLE: {table}")

    df = spark.read.parquet(
        f"abfss://bronze@hishamclinicaldl.dfs.core.windows.net/{table}/"
    )

    print(f"Rows: {df.count()}")

    df.printSchema()

    print("\n")

# COMMAND ----------

# MAGIC %md
# MAGIC # Silver Layer Design - Clinical Trial Lakehouse
# MAGIC
# MAGIC ## Objective
# MAGIC Transform Bronze Parquet data into clean, conformed Delta tables stored in ADLS Gen2 Silver layer.
# MAGIC
# MAGIC ## Scope
# MAGIC - 18 clinical trial tables
# MAGIC - No joins in Silver
# MAGIC - Standardization, data quality, and type normalization only
# MAGIC
# MAGIC ## Output
# MAGIC - Delta tables in abfss://silver@hishamclinicaldl.dfs.core.windows.net/<table_name>

# COMMAND ----------

# MAGIC %md
# MAGIC # Silver Layer Principles
# MAGIC
# MAGIC 1. Preserve original business entities (no joins)
# MAGIC 2. Standardize data types (especially decimals and timestamps)
# MAGIC 3. Add audit columns for traceability
# MAGIC 4. Ensure schema consistency across all tables
# MAGIC 5. Maintain one Delta table per source table

# COMMAND ----------

# MAGIC %md
# MAGIC # Data Quality Observations from Bronze
# MAGIC
# MAGIC - No null values detected in sampled tables
# MAGIC - No duplicate rows detected across key tables
# MAGIC - Decimal precision is excessively high (decimal(38,18))
# MAGIC - Schema is already well-structured from ADF ingestion

# COMMAND ----------

BRONZE_PATH = "abfss://bronze@hishamclinicaldl.dfs.core.windows.net/"
SILVER_PATH = "abfss://silver@hishamclinicaldl.dfs.core.windows.net/"

tables = [
    "adverse_events",
    "clinical_studies",
    "clinical_visits",
    "concomitant_medications",
    "dropouts",
    "drug_administration",
    "enrollments",
    "investigators",
    "lab_results",
    "medical_history",
    "medications",
    "patients",
    "protocol_deviations",
    "questionnaires",
    "research_sites",
    "study_arms",
    "study_sites",
    "vital_signs"
]

# COMMAND ----------

# MAGIC %md
# MAGIC # Silver Transformation Rules (Core Logic)
# MAGIC ## Standardization, Audit Columns, and Decimal Normalization

# COMMAND ----------

from pyspark.sql.functions import col
from pyspark.sql.types import DecimalType

def normalize_decimals(df):

    for field in df.schema.fields:
        if str(field.dataType).startswith("DecimalType"):

            df = df.withColumn(
                field.name,
                col(field.name).cast(DecimalType(12, 2))
            )

    return df

# COMMAND ----------

# MAGIC %md
# MAGIC # Silver Transformation Engine v3
# MAGIC ## Full pipeline: audit + normalization

# COMMAND ----------

from pyspark.sql.functions import current_timestamp, lit, col
from pyspark.sql.types import DecimalType

def normalize_decimals(df):

    for field in df.schema.fields:
        if str(field.dataType).startswith("DecimalType"):
            df = df.withColumn(
                field.name,
                col(field.name).cast(DecimalType(12, 2))
            )

    return df


def transform_silver(df, table_name):

    # audit columns
    df = df.withColumn("silver_loaded_at", current_timestamp()) \
           .withColumn("source_table", lit(table_name))

    # normalize decimals
    df = normalize_decimals(df)

    return df

# COMMAND ----------

# MAGIC %md
# MAGIC # Silver Load Execution
# MAGIC ## Applying transformation engine across all tables

# COMMAND ----------

for table in tables:

    print(f"Processing Silver table: {table}")

    bronze_path = f"{BRONZE_PATH}{table}/"
    silver_path = f"{SILVER_PATH}{table}/"

    # Read Bronze
    df = spark.read.parquet(bronze_path)

    # Transform
    df_silver = transform_silver(df, table)

    # Write to Silver (Delta)
    df_silver.write \
        .format("delta") \
        .mode("overwrite") \
        .save(silver_path)

    print(f"Completed: {table}")

# COMMAND ----------

# MAGIC %md
# MAGIC # Gold Layer Design (Business Data Products)
# MAGIC ## Building analytical views from Silver layer entities

# COMMAND ----------

# MAGIC %md
# MAGIC # Gold Layer
# MAGIC ## patient_study_summary - Patient Level Clinical Overview

# COMMAND ----------

spark.read.format("delta").load("abfss://silver@hishamclinicaldl.dfs.core.windows.net/patients").createOrReplaceTempView("patients")
spark.read.format("delta").load("abfss://silver@hishamclinicaldl.dfs.core.windows.net/enrollments").createOrReplaceTempView("enrollments")
spark.read.format("delta").load("abfss://silver@hishamclinicaldl.dfs.core.windows.net/clinical_studies").createOrReplaceTempView("clinical_studies")
spark.read.format("delta").load("abfss://silver@hishamclinicaldl.dfs.core.windows.net/study_arms").createOrReplaceTempView("study_arms")
spark.read.format("delta").load("abfss://silver@hishamclinicaldl.dfs.core.windows.net/research_sites").createOrReplaceTempView("research_sites")

# COMMAND ----------

# MAGIC %md
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Visit Summary (Operational Analytics View)[](url)

# COMMAND ----------

# MAGIC %md
# MAGIC - ## Lab Summary - Patient Lab Analytics Layer

# COMMAND ----------

# MAGIC %md
# MAGIC ## Safety Summary - Adverse Events Analytics Layer

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE SCHEMA IF NOT EXISTS databricks_clinical_trial.silver;

# COMMAND ----------

silver_tables = [
    "adverse_events","clinical_studies","clinical_visits","concomitant_medications",
    "dropouts","drug_administration","enrollments","investigators","lab_results",
    "medical_history","medications","patients","protocol_deviations","questionnaires",
    "research_sites","study_arms","study_sites","vital_signs"
]
for t in silver_tables:
    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS databricks_clinical_trial.silver.{t}
        USING DELTA
        LOCATION 'abfss://silver@hishamclinicaldl.dfs.core.windows.net/{t}/'
    """)
    print("registered:", t)

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
# MAGIC     e.status AS enrollment_status,
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
# MAGIC FROM databricks_clinical_trial.silver.patients p
# MAGIC INNER JOIN databricks_clinical_trial.silver.enrollments e
# MAGIC     ON p.patient_id = e.patient_id
# MAGIC INNER JOIN databricks_clinical_trial.silver.clinical_studies s
# MAGIC     ON e.study_id = s.study_id
# MAGIC LEFT JOIN databricks_clinical_trial.silver.study_arms a
# MAGIC     ON e.arm_id = a.arm_id
# MAGIC LEFT JOIN databricks_clinical_trial.silver.research_sites r
# MAGIC     ON e.site_id = r.site_id;

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
# MAGIC         WHEN l.toxicity_grade = 2 THEN 'Moderate Risk'
# MAGIC         ELSE 'Low Risk'
# MAGIC     END AS toxicity_risk_category,
# MAGIC
# MAGIC     l.collection_datetime,
# MAGIC     l.result_datetime
# MAGIC FROM databricks_clinical_trial.silver.lab_results l
# MAGIC LEFT JOIN databricks_clinical_trial.silver.patients p
# MAGIC     ON l.patient_id = p.patient_id
# MAGIC LEFT JOIN databricks_clinical_trial.silver.clinical_visits v
# MAGIC     ON l.visit_id = v.visit_id
# MAGIC LEFT JOIN databricks_clinical_trial.silver.enrollments e
# MAGIC     ON v.enrollment_id = e.enrollment_id;

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
# MAGIC         WHEN ae.is_serious = true THEN 'Serious AE'
# MAGIC         WHEN ae.ctcae_grade >= 3 THEN 'High Grade AE'
# MAGIC         WHEN ae.ctcae_grade = 2 THEN 'Moderate AE'
# MAGIC         ELSE 'Low Grade AE'
# MAGIC     END AS ae_risk_category,
# MAGIC
# MAGIC     CASE WHEN ae.resolution_date IS NULL THEN 'Ongoing' ELSE 'Resolved' END AS ae_status,
# MAGIC     datediff(ae.resolution_date, ae.onset_date) AS ae_duration_days,
# MAGIC
# MAGIC     ae.created_at,
# MAGIC     ae.updated_at
# MAGIC FROM databricks_clinical_trial.silver.adverse_events ae
# MAGIC LEFT JOIN databricks_clinical_trial.silver.patients p
# MAGIC     ON ae.patient_id = p.patient_id
# MAGIC LEFT JOIN databricks_clinical_trial.silver.enrollments e
# MAGIC     ON ae.enrollment_id = e.enrollment_id;

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
# MAGIC         WHEN v.actual_visit_date IS NULL THEN 'Not Completed'
# MAGIC         WHEN v.actual_visit_date BETWEEN v.visit_window_start AND v.visit_window_end THEN 'On Time'
# MAGIC         WHEN v.actual_visit_date < v.visit_window_start THEN 'Early'
# MAGIC         WHEN v.actual_visit_date > v.visit_window_end THEN 'Late'
# MAGIC         ELSE 'Unknown'
# MAGIC     END AS visit_timing_status,
# MAGIC
# MAGIC     datediff(v.actual_visit_date, v.scheduled_date) AS days_from_scheduled,
# MAGIC
# MAGIC     v.notes,
# MAGIC     v.created_at,
# MAGIC     v.updated_at
# MAGIC FROM databricks_clinical_trial.silver.clinical_visits v
# MAGIC LEFT JOIN databricks_clinical_trial.silver.enrollments e
# MAGIC     ON v.enrollment_id = e.enrollment_id
# MAGIC LEFT JOIN databricks_clinical_trial.silver.patients p
# MAGIC     ON e.patient_id = p.patient_id;
