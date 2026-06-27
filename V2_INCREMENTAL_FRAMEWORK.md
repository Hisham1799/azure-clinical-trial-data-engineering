# Version 2 — Incremental Framework

## Objective

Version 2 upgrades the completed V1 platform into a production-style incremental framework while preserving the existing lakehouse and serving layers.

The design separates:

- metadata-driven source extraction;
- incremental Bronze delivery;
- conformed Silver upserts;
- deterministic Gold publishing;
- SQL serving validation.

## ADF metadata model

ADF reads MySQL table `pipeline_watermark_config`. Each active row describes how one source table should be processed.

Core fields include:

| Field | Role |
|---|---|
| `table_name` | Source table and Bronze dataset identifier |
| `primary_key_column` | Silver MERGE match key |
| `load_type` | Full or incremental extraction behavior |
| `watermark_column` | Source column used for incremental bounds |
| `last_watermark` | Last stored extraction checkpoint |
| `is_active` | Enables/disables processing |

The lookup returns all active table configurations. ADF's `ForEach` processes the returned rows, allowing one pipeline to support all 18 tables.


## ADF activity flow

```text
LKP_GetTableList
    |
    v
FE_LoopTables
    |
    +-- CP_MySQLToADLS
    |      Builds full/incremental source SQL from metadata
    |      Writes Parquet to the table's Bronze path
    |
    +-- LKP_GetNewWatermark
    |      Determines the successfully extracted upper bound
    |
    +-- LKP_UpdateWatermark
           Updates per-table watermark metadata
```

Table iterations are independent. There is no global watermark.

## SHIR operational dependency

MySQL is local to the Windows development machine. ADF cannot directly reach `localhost`; `SHIR-ClinicalTrial` provides the bridge.

Before an ADF run:

- Windows must be online;
- MySQL must be running;
- `DIAHostService`/the SHIR node must be healthy;
- outbound Azure connectivity must work.

SHIR availability is not a missing architecture component. It is a deliberate operational dependency of the current portfolio setup.

## Incremental Bronze

For an incrementally configured table, ADF extracts only rows inside the current watermark window. A no-change source therefore produces an empty or zero-row batch rather than a full table refresh.

Configuration/full-load tables may still reload fully according to `load_type`.

Bronze remains source-shaped. Business transformations are deferred to Silver.

## Silver transformation and MERGE

Notebook `02_incremental_bronze_to_silver_merge` contains the production execution path:

- table/primary-key configuration;
- `transform_silver()`;
- the all-table MERGE loop;
- validation counts.

Old exploratory cells are not part of the documented production path.

For each table:

1. Read the table's Bronze batch.
2. Count the batch.
3. If empty, log/skip without failing.
4. Apply `transform_silver()`.
5. Obtain the target Delta table.
6. MERGE on the primary key.
7. Update matched records.
8. Insert unmatched records.
9. Validate the resulting target count.

```python
target.alias("t").merge(
    silver_batch.alias("s"),
    "t.primary_key = s.primary_key"
).whenMatchedUpdateAll() \
 .whenNotMatchedInsertAll() \
 .execute()
```

The snippet is conceptual; each table uses its configured primary key.

### Empty-batch handling

An empty Bronze batch is a valid incremental outcome. It should not attempt a MERGE or fail the overall process.


### Successful MERGE evidence

The all-table process handled the configured tables, including a 7,715-row `lab_results` batch.


## Gold publish

Notebook `03_silver_to_gold_publish` rebuilds the four Gold tables from the latest Silver state using `CREATE OR REPLACE TABLE`.

Gold was intentionally not converted to incremental MERGE.

### Why full Gold publish is correct here

- Gold contains joins across patients, enrollments, studies, sites, arms, visits, labs, and safety data.
- One source-table change can alter derived output membership.
- Current row volumes are small.
- A complete rebuild is deterministic.
- Count and business-rule validation are straightforward.
- The approach avoids maintaining complex affected-key propagation.

Incremental Gold should be reconsidered only when scale or SLA makes full publishing materially expensive.

## Business relationship behavior

`patient_study_summary` is driven by valid business joins. Inserting a patient alone changes Silver but does not necessarily change Gold. Once the patient has a valid enrollment, the Gold mart includes that patient.

This behavior was explicitly tested and is evidence of correct relationship handling, not a pipeline failure.

## Idempotency definition

The validated project demonstrates **business-level idempotency**:

- rerunning without source changes does not create duplicate business records;
- Gold counts remain stable;
- Synapse duplicate queries return no repeated `patient_id`.

There is still a future optimization: the current Silver `whenMatchedUpdateAll()` can physically update a matched Delta row even if its business values did not change. A change predicate or row hash would reduce unnecessary Delta rewrites.

## Completed outcome

V2 demonstrates:

- metadata-driven ingestion;
- per-table watermarks;
- incremental Bronze row selection;
- safe empty-batch handling;
- primary-key Silver Delta MERGE;
- deterministic Gold publishing;
- update propagation to Synapse;
- bulk insert/update handling;
- stable no-change reruns and no duplicate business keys.

