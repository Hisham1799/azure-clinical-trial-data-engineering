# Operational Runbook

## Purpose

This runbook executes the current validated workflow:

```text
ADF ingestion -> Silver MERGE -> Gold publish -> Synapse validation
```

The steps are manual by current design. Do not schedule ADF independently unless the local source and SHIR availability can be guaranteed.

## Prerequisites

- Windows host is powered on and connected to the internet.
- MySQL 8 service is running.
- Database `clinical_trial_db` is available on port 3306.
- `SHIR-ClinicalTrial` Windows service/node is online.
- ADF linked services can connect.
- Databricks user has access to catalog `databricks_clinical_trial`.
- Databricks compute/serverless execution is available.
- Synapse user can query database `clinical_trial_serving`.

## 1. Start and verify MySQL

From Windows Services:

1. Locate `MySQL80`.
2. Start the service if it is stopped.
3. Confirm the service remains in `Running` state.
4. Confirm the expected database is available.

Optional command-line checks:

```powershell
Get-Service MySQL80
Test-NetConnection localhost -Port 3306
```

Do not begin ADF ingestion if MySQL is unavailable.

## 2. Start and verify SHIR

1. Locate Microsoft Integration Runtime service `DIAHostService`.
2. Start it if needed.
3. Open Integration Runtime Configuration Manager if node status must be inspected.
4. Confirm the node is connected/online.
5. In ADF, test the MySQL linked service if there is any uncertainty.

```powershell
Get-Service DIAHostService
```

Important: closing the SHIR desktop application does not necessarily stop its Windows service. Check service/node health rather than UI presence.

## 3. Confirm source change

Before running, identify:

- affected table;
- expected inserted/updated row count;
- expected watermark movement;
- target-layer field used for validation.

Examples:

- patient demographic updates should be checked in Silver `patients`;
- enrollment status should be checked in Gold/Synapse `patient_study_summary`.

## 4. Run ADF `pipeline1`

In Azure Data Factory:

1. Open `adf-clinical-trial`.
2. Open pipeline `pipeline1`.
3. Run Debug for controlled development validation or use the intended trigger/manual run path.
4. Monitor `LKP_GetTableList`.
5. Monitor `FE_LoopTables`.
6. Confirm copy and watermark activities succeed for every active table.
7. Record the ADF run ID.

Expected behavior:

- active table metadata is returned;
- incremental SQL uses per-table watermark configuration;
- changed rows are written to Bronze;
- no-change tables can produce empty batches;
- the table watermark advances only through the configured post-copy logic.

Do not continue if any relevant table iteration failed.

## 5. Run Silver notebook 02

In Databricks:

1. Open `02_incremental_bronze_to_silver_merge`.
2. Use the documented production cells: configuration, `transform_silver()`, all-table MERGE loop, validation.
3. Run the notebook.
4. Review per-table output.
5. Confirm empty batches are skipped.
6. Confirm changed tables report `MERGED`.
7. Validate affected table counts and values.

Example validations:

```sql
SELECT COUNT(*)
FROM databricks_clinical_trial.silver.patients;
```

```sql
SELECT patient_id, weight_kg, bmi
FROM databricks_clinical_trial.silver.patients
WHERE patient_id = 201;
```

Stop if the MERGE fails or the expected source change is absent.

## 6. Run Gold notebook 03

1. Open `03_silver_to_gold_publish`.
2. Run the full notebook.
3. Confirm all four `CREATE OR REPLACE TABLE` operations succeed.
4. Review count validation.

Expected final baseline after the completed tests:

| Gold table | Rows |
|---|---:|
| `patient_study_summary` | 241 |
| `lab_summary` | 7,715 |
| `safety_adverse_events` | 245 |
| `visit_summary` | 1,108 |

Counts should change only when source/business relationships justify a change.

## 7. Validate Synapse

Connect to serverless database `clinical_trial_serving`.

Count validation:

```sql
SELECT COUNT(*) AS patient_study_summary
FROM dbo.patient_study_summary;

SELECT COUNT(*) AS lab_summary
FROM dbo.lab_summary;

SELECT COUNT(*) AS safety_adverse_events
FROM dbo.safety_adverse_events;

SELECT COUNT(*) AS visit_summary
FROM dbo.visit_summary;
```

Business update validation:

```sql
SELECT patient_id, enrollment_status
FROM dbo.patient_study_summary
WHERE patient_id = 201;
```

Duplicate validation:

```sql
SELECT patient_id, COUNT(*) AS row_count
FROM dbo.patient_study_summary
GROUP BY patient_id
HAVING COUNT(*) > 1;
```

Expected duplicate result: no rows.

## 8. Record the run

Until a logging table is implemented, record manually:

- execution timestamp;
- source change;
- ADF run ID and status;
- affected Bronze table/count;
- Silver result/count;
- Gold result/count;
- Synapse result;
- anomalies and corrective action.

## Troubleshooting

### ADF cannot connect to MySQL

Check, in order:

1. Windows is online.
2. `MySQL80` is running.
3. Port 3306 is listening.
4. `DIAHostService` is running.
5. SHIR node reports online.
6. MySQL linked-service connection test succeeds.
7. Credentials and firewall/network conditions have not changed.

### ADF succeeds but Bronze is empty

Possible explanations:

- there were no source changes after `last_watermark`;
- the expected source row has a null/incorrect watermark;
- the table is disabled in metadata;
- the wrong source field was updated;
- the stored watermark already includes the change.

Inspect source values and `pipeline_watermark_config` before resetting a watermark.

### Silver did not change

Check:

- Bronze batch count;
- table/primary-key configuration;
- `transform_silver()` output;
- source primary key;
- MERGE output/error;
- whether the field being tested exists in Silver.

### Gold did not change

Check business dependencies. A new patient alone does not enter `patient_study_summary`; a valid enrollment and related study/site/arm data are required.

Also confirm the changed field is part of the Gold schema. `weight_kg` and `bmi` are Silver validation fields, not `patient_study_summary` fields.

### Synapse shows an old value

Check:

1. Silver contains the new value.
2. Notebook 03 completed after notebook 02.
3. Gold contains the new value.
4. Synapse query uses `clinical_trial_serving` and the correct external table.
5. The query/result UI was refreshed.

### Duplicate check returns rows

Do not hide the symptom with `DISTINCT`. Investigate:

- source primary-key uniqueness;
- table/primary-key configuration;
- Silver MERGE match expression;
- Gold join cardinality;
- duplicate dimension/reference rows.

## Safe rerun guidance

- ADF extraction depends on current watermark state; understand the intended window before manually changing metadata.
- Silver MERGE is safe at the business-key level for the tested cases.
- Gold full publish is deterministic from current Silver.
- A no-change rerun should preserve Gold counts and return no duplicate business keys.

