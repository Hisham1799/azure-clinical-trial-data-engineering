# Azure Clinical Trial Data Engineering

End-to-end Azure lakehouse project that ingests 18 clinical-trial tables from local MySQL through a Self-Hosted Integration Runtime, lands Parquet in ADLS Gen2, transforms data with Databricks and Delta Lake, governs external tables with Unity Catalog, and serves Gold marts through Synapse serverless SQL.

## Architecture

```text
MySQL -> SHIR -> Azure Data Factory -> ADLS Bronze
      -> Databricks / Delta Lake -> Silver -> Gold
      -> Unity Catalog -> Synapse Serverless SQL
```

## What is implemented

- Metadata-driven ADF Lookup + ForEach ingestion.
- Reusable MySQL and Parquet datasets.
- Full-load and incremental Bronze-to-Silver notebooks.
- Delta `MERGE` framework and data-quality checks.
- Deterministic Silver-to-Gold publishing.
- 18 Silver domain tables and four Gold marts.
- Synapse external-table/query scripts.
- Sanitized ADF and ARM exports.

## Repository map

| Path | Purpose |
|---|---|
| `adf/` | Pipelines, datasets, linked services, and SHIR definition |
| `databricks/` | Portable `.py` and output-free `.ipynb` notebooks |
| `sql/source_ddl/` | Schema-only DDL for 18 source tables |
| `sql/synapse/` | Synapse serverless SQL scripts |
| `infrastructure/` | Sanitized ADF ARM template |
| `docs/` | Resource summary and rebuild guide |
| `SECURITY_NOTES.md` | Redactions and secret-handling rules |
| `PROJECT_STRUCTURE.md` | Detailed file guide |

## Data flow

1. ADF queries MySQL metadata to discover source tables.
2. A parameterized ForEach copy lands one Parquet dataset per table in Bronze.
3. Databricks cleans, types, validates, and merges records into Silver Delta tables.
4. Gold notebooks produce patient/study, lab, safety-event, and visit marts.
5. Synapse serverless SQL exposes Gold data for reporting.

## Run or rebuild

The original Azure resources were archived and deleted on 2026-06-30. Rebuild using [docs/REBUILD_STEPS.md](docs/REBUILD_STEPS.md), create fresh credentials, deploy the sanitized ADF template, import the notebooks, recreate Unity Catalog locations, then run the Synapse scripts.

Never reuse identifiers or credentials from the archived environment. See [SECURITY_NOTES.md](SECURITY_NOTES.md).

## Interview talking points

- Why metadata-driven ingestion scales better than 18 copy activities.
- Why SHIR is required for a private local MySQL source.
- Parquet Bronze versus transactional Delta Silver/Gold.
- Idempotent Delta MERGE and no-change reruns.
- Managed-identity access through Unity Catalog external locations.
- Cost control through terminated clusters and serverless SQL.
- Disaster-recovery discipline: notebooks, ADF JSON, SQL, ARM, RBAC, screenshots, and rebuild guides were archived before deletion.

## Boundaries

This repository intentionally excludes secrets, raw clinical rows, full SQL dumps, Parquet/Delta data, DBC archives, installers, private logs, and the complete offline Azure backup.
