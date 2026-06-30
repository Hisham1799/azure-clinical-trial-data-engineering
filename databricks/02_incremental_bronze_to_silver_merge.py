# Databricks notebook source
dbutils.fs.ls("abfss://bronze@hishamclinicaldl.dfs.core.windows.net/")

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW TABLES IN databricks_clinical_trial.silver;

# COMMAND ----------

df = spark.read.parquet("abfss://bronze@hishamclinicaldl.dfs.core.windows.net/patients/")
print(df.count())
display(df.limit(10))

# COMMAND ----------

from delta.tables import DeltaTable
from pyspark.sql.functions import current_timestamp

table_name = "patients"
bronze_path = f"abfss://bronze@hishamclinicaldl.dfs.core.windows.net/{table_name}/"
silver_table = f"databricks_clinical_trial.silver.{table_name}"
primary_key = "patient_id"

print("=" * 60)
print(f"Processing table : {table_name}")

df_bronze = spark.read.parquet(bronze_path)

batch_count = df_bronze.count()
print(f"Bronze batch rows : {batch_count}")

if batch_count == 0:
    print("Action : SKIPPED (No new data)")
else:
    df_bronze = df_bronze.withColumn("silver_updated_at", current_timestamp())

    target = DeltaTable.forName(spark, silver_table)

    (
        target.alias("t")
        .merge(
            df_bronze.alias("s"),
            f"t.{primary_key} = s.{primary_key}"
        )
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )

    print("Action : MERGED")

print("=" * 60)

# COMMAND ----------

from delta.tables import DeltaTable
from pyspark.sql.functions import current_timestamp

BRONZE_BASE_PATH = "abfss://bronze@hishamclinicaldl.dfs.core.windows.net/"
SILVER_CATALOG = "databricks_clinical_trial"
SILVER_SCHEMA = "silver"

table_configs = [
    ("adverse_events", "ae_id"),
    ("clinical_studies", "study_id"),
    ("clinical_visits", "visit_id"),
    ("concomitant_medications", "conmed_id"),
    ("dropouts", "dropout_id"),
    ("drug_administration", "administration_id"),
    ("enrollments", "enrollment_id"),
    ("investigators", "investigator_id"),
    ("lab_results", "lab_result_id"),
    ("medical_history", "history_id"),
    ("medications", "medication_id"),
    ("patients", "patient_id"),
    ("protocol_deviations", "deviation_id"),
    ("questionnaires", "questionnaire_id"),
    ("research_sites", "site_id"),
    ("study_arms", "arm_id"),
    ("study_sites", "study_site_id"),
    ("vital_signs", "vital_id")
]

for table_name, primary_key in table_configs:
    print("=" * 70)
    print(f"Processing table : {table_name}")
    print(f"Primary key      : {primary_key}")

    bronze_path = f"{BRONZE_BASE_PATH}{table_name}/"
    silver_table = f"{SILVER_CATALOG}.{SILVER_SCHEMA}.{table_name}"

    df_bronze = spark.read.parquet(bronze_path)
    batch_count = df_bronze.count()

    print(f"Bronze batch rows: {batch_count}")

    if batch_count == 0:
        print("Action           : SKIPPED")
        print("Reason           : No new rows in Bronze batch")
        continue

from pyspark.sql.functions import current_timestamp, lit

df_bronze = (
    df_bronze
    .withColumn("silver_loaded_at", current_timestamp())
    .withColumn("source_table", lit(table_name))
)

    target = DeltaTable.forName(spark, silver_table)

    (
        target.alias("t")
        .merge(
            df_bronze.alias("s"),
            f"t.{primary_key} = s.{primary_key}"
        )
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )

    print("Action           : MERGED")

print("=" * 70)
print("All table processing completed.")

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW TABLES IN databricks_clinical_trial.silver;

# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE TABLE databricks_clinical_trial.silver.adverse_events;

# COMMAND ----------

df = spark.read.parquet("abfss://bronze@hishamclinicaldl.dfs.core.windows.net/adverse_events/")
df.printSchema()
print(df.count())

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) FROM databricks_clinical_trial.silver.adverse_events;

# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE EXTENDED databricks_clinical_trial.silver.adverse_events;

# COMMAND ----------

from delta.tables import DeltaTable

table = "adverse_events"
primary_key = "ae_id"

bronze_path = f"{BRONZE_PATH}{table}/"
silver_table = f"databricks_clinical_trial.silver.{table}"

df = spark.read.parquet(bronze_path)
print("Bronze rows:", df.count())

df_silver = transform_silver(df, table)
print("Transformed rows:", df_silver.count())

display(df_silver.limit(5))

# COMMAND ----------

BRONZE_PATH = "abfss://bronze@hishamclinicaldl.dfs.core.windows.net/"
SILVER_PATH = "abfss://silver@hishamclinicaldl.dfs.core.windows.net/"

table = "adverse_events"

df = spark.read.parquet(f"{BRONZE_PATH}{table}/")

print(df.count())
df.printSchema()

# COMMAND ----------

from pyspark.sql.functions import current_timestamp, lit, col
from pyspark.sql.types import DecimalType

BRONZE_PATH = "abfss://bronze@hishamclinicaldl.dfs.core.windows.net/"

def normalize_decimals(df):
    for field in df.schema.fields:
        if str(field.dataType).startswith("DecimalType"):
            df = df.withColumn(field.name, col(field.name).cast(DecimalType(12, 2)))
    return df

def transform_silver(df, table_name):
    df = df.withColumn("silver_loaded_at", current_timestamp()) \
           .withColumn("source_table", lit(table_name))
    df = normalize_decimals(df)
    return df

table = "adverse_events"

df = spark.read.parquet(f"{BRONZE_PATH}{table}/")
df_silver = transform_silver(df, table)

print("Bronze rows:", df.count())
print("Transformed rows:", df_silver.count())
df_silver.printSchema()

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) AS before_count
# MAGIC FROM databricks_clinical_trial.silver.adverse_events;

# COMMAND ----------

from delta.tables import DeltaTable

table = "adverse_events"
primary_key = "ae_id"

df = spark.read.parquet(f"{BRONZE_PATH}{table}/")
df_silver = transform_silver(df, table)

batch_count = df_silver.count()
print(f"Transformed batch rows: {batch_count}")

if batch_count == 0:
    print("Action: SKIPPED")
else:
    target = DeltaTable.forName(
        spark,
        f"databricks_clinical_trial.silver.{table}"
    )

    (
        target.alias("t")
        .merge(
            df_silver.alias("s"),
            f"t.{primary_key} = s.{primary_key}"
        )
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )

    print("Action: MERGED")

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) AS after_count
# MAGIC FROM databricks_clinical_trial.silver.adverse_events;

# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE HISTORY databricks_clinical_trial.silver.adverse_events;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 'adverse_events' AS table_name, COUNT(*) AS rows FROM databricks_clinical_trial.silver.adverse_events
# MAGIC UNION ALL SELECT 'patients', COUNT(*) FROM databricks_clinical_trial.silver.patients
# MAGIC UNION ALL SELECT 'lab_results', COUNT(*) FROM databricks_clinical_trial.silver.lab_results;

# COMMAND ----------

for t in ["adverse_events", "patients", "lab_results"]:
    df = spark.read.parquet(f"abfss://bronze@hishamclinicaldl.dfs.core.windows.net/{t}/")
    print(t, df.count())

# COMMAND ----------

print(transform_silver)

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT ae_id, COUNT(*) AS cnt
# MAGIC FROM databricks_clinical_trial.silver.adverse_events
# MAGIC GROUP BY ae_id
# MAGIC HAVING COUNT(*) > 1;

# COMMAND ----------

from delta.tables import DeltaTable

table = "lab_results"
primary_key = "lab_result_id"

df = spark.read.parquet(f"{BRONZE_PATH}{table}/")
df_silver = transform_silver(df, table)

batch_count = df_silver.count()
print(f"Table: {table}")
print(f"Transformed batch rows: {batch_count}")

if batch_count == 0:
    print("Action: SKIPPED")
else:
    target = DeltaTable.forName(
        spark,
        f"databricks_clinical_trial.silver.{table}"
    )

    (
        target.alias("t")
        .merge(
            df_silver.alias("s"),
            f"t.{primary_key} = s.{primary_key}"
        )
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )

    print("Action: MERGED")

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) AS after_count
# MAGIC FROM databricks_clinical_trial.silver.lab_results;

# COMMAND ----------

from delta.tables import DeltaTable

table_configs = [
    ("adverse_events", "ae_id"),
    ("clinical_studies", "study_id"),
    ("clinical_visits", "visit_id"),
    ("concomitant_medications", "conmed_id"),
    ("dropouts", "dropout_id"),
    ("drug_administration", "administration_id"),
    ("enrollments", "enrollment_id"),
    ("investigators", "investigator_id"),
    ("lab_results", "lab_result_id"),
    ("medical_history", "history_id"),
    ("medications", "medication_id"),
    ("patients", "patient_id"),
    ("protocol_deviations", "deviation_id"),
    ("questionnaires", "questionnaire_id"),
    ("research_sites", "site_id"),
    ("study_arms", "arm_id"),
    ("study_sites", "study_site_id"),
    ("vital_signs", "vital_id")
]

for table, primary_key in table_configs:
    print("=" * 70)
    print(f"Processing table : {table}")
    print(f"Primary key      : {primary_key}")

    df = spark.read.parquet(f"{BRONZE_PATH}{table}/")
    df_silver = transform_silver(df, table)

    batch_count = df_silver.count()
    print(f"Transformed rows : {batch_count}")

    if batch_count == 0:
        print("Action           : SKIPPED")
        continue

    target = DeltaTable.forName(
        spark,
        f"databricks_clinical_trial.silver.{table}"
    )

    (
        target.alias("t")
        .merge(
            df_silver.alias("s"),
            f"t.{primary_key} = s.{primary_key}"
        )
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )

    print("Action           : MERGED")

print("=" * 70)
print("All Silver MERGE processing completed.")

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 'adverse_events' AS table_name, COUNT(*) AS rows FROM databricks_clinical_trial.silver.adverse_events
# MAGIC UNION ALL SELECT 'patients', COUNT(*) FROM databricks_clinical_trial.silver.patients
# MAGIC UNION ALL SELECT 'lab_results', COUNT(*) FROM databricks_clinical_trial.silver.lab_results
# MAGIC UNION ALL SELECT 'clinical_visits', COUNT(*) FROM databricks_clinical_trial.silver.clinical_visits;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     patient_id,
# MAGIC     patient_code,
# MAGIC     weight_kg,
# MAGIC     bmi,
# MAGIC     updated_at
# MAGIC FROM databricks_clinical_trial.silver.patients
# MAGIC WHERE patient_id = 201;

# COMMAND ----------

df = spark.read.parquet("abfss://bronze@hishamclinicaldl.dfs.core.windows.net/patients/")
print(df.count())
display(df)

# COMMAND ----------

from delta.tables import DeltaTable

table = "patients"
primary_key = "patient_id"

df = spark.read.parquet(f"{BRONZE_PATH}{table}/")
df_silver = transform_silver(df, table)

print("Bronze rows:", df.count())
display(df_silver)

target = DeltaTable.forName(
    spark,
    f"databricks_clinical_trial.silver.{table}"
)

(
    target.alias("t")
    .merge(
        df_silver.alias("s"),
        f"t.{primary_key} = s.{primary_key}"
    )
    .whenMatchedUpdateAll()
    .whenNotMatchedInsertAll()
    .execute()
)

print("Patients MERGE completed")

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     patient_id,
# MAGIC     patient_code,
# MAGIC     weight_kg,
# MAGIC     bmi,
# MAGIC     updated_at
# MAGIC FROM databricks_clinical_trial.silver.patients
# MAGIC WHERE patient_id = 201;
