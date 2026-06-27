# Version 1 — Full-Load Lakehouse

## Objective

Version 1 established the complete technical path before incremental complexity was introduced:

```text
MySQL -> ADF -> Bronze -> Databricks -> Silver -> Gold
      -> Unity Catalog -> Synapse Serverless
```

It answered the foundational question: can the source data be ingested, transformed into a lakehouse, governed, and queried through a reporting-oriented SQL layer?

## Processing model

V1 used full extraction and overwrite-style processing.

- ADF copied complete source tables to Bronze Parquet.
- Databricks notebook `01_bronze_to_silver_gold` read the Bronze datasets.
- Silver tables were transformed and overwritten as Delta tables.
- Four Gold marts were recreated from Silver.
- Silver and Gold external tables were registered in Unity Catalog.
- Synapse serverless external tables exposed Gold data.

## Original ADF ingestion

The original pipeline enumerated source tables and copied them to the data lake. This was an appropriate first implementation because it minimized moving parts while proving connectivity and schema handling.


## Databricks notebook

`01_bronze_to_silver_gold` performed:

1. external-location and schema setup;
2. reads from 18 Bronze tables;
3. type normalization and audit-column creation;
4. Silver Delta overwrite;
5. registration of Silver external tables;
6. full creation/replacement of four Gold marts;
7. count validation.

## Gold marts

| Gold table | Purpose |
|---|---|
| `patient_study_summary` | Patient enrollment and study context |
| `lab_summary` | Reporting-ready laboratory observations |
| `safety_adverse_events` | Safety and adverse-event analysis |
| `visit_summary` | Visit and compliance-oriented reporting |

V1 baseline validation:

| Gold table | Baseline rows |
|---|---:|
| `patient_study_summary` | 200 |
| `lab_summary` | 7,715 |
| `safety_adverse_events` | 245 |
| `visit_summary` | 1,108 |


## What V1 proved

- Local MySQL could be reached through ADF and SHIR.
- The source model could be represented in ADLS.
- Databricks could transform all 18 clinical tables.
- Delta Lake and Unity Catalog worked with external storage locations.
- Gold marts could be generated from conformed Silver data.
- Synapse serverless could query the Gold serving layer.
- The solution was structurally ready for Power BI connectivity.

## Why V1 was retained

The V2 work was an upgrade, not a rebuild. Keeping V1 provides:

- a known full-refresh recovery path;
- a clear baseline for explaining the system's evolution;
- a simple reference implementation;
- evidence that incremental complexity was introduced only after the end-to-end platform worked.

## V1 limitations

Full refresh is easy to reason about but becomes inefficient as source data grows:

- unchanged rows are repeatedly extracted and processed;
- overwrite work increases with total table size;
- source, network, storage, and compute usage grow together;
- there is no per-table incremental checkpoint;
- frequent refreshes can become expensive.

These limitations motivated Version 2. They do not mean V1 was incorrect; V1 was the appropriate baseline for proving the architecture.

