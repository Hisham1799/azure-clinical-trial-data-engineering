# Azure Clinical Trial Data Engineering Project

An end-to-end Azure data engineering portfolio project that ingests clinical-trial data from local MySQL, stores it in an ADLS Gen2 lakehouse, transforms it with Azure Databricks and Delta Lake, governs tables through Unity Catalog, and serves Gold marts through Synapse serverless SQL for Power BI consumption.

The project was built in two stages:

- **Version 1:** a complete full-load lakehouse using overwrite-based processing.
- **Version 2:** a production-style upgrade with metadata-driven incremental ingestion, per-table watermarks, incremental Silver Delta MERGE, deterministic Gold publishing, and end-to-end validation.

This is a validated portfolio implementation, not a claim of enterprise production readiness. Remaining production improvements are documented in [FUTURE_IMPROVEMENTS.md](FUTURE_IMPROVEMENTS.md).

## Architecture

```text
Local MySQL
    |
    | SHIR-ClinicalTrial
    v
Azure Data Factory
    |
    | metadata-driven full/incremental extraction
    v
ADLS Gen2 Bronze (Parquet)
    |
    | Databricks: transform_silver() + Delta MERGE
    v
ADLS Gen2 Silver (Delta) + Unity Catalog
    |
    | Databricks: full Gold publish
    v
ADLS Gen2 Gold (Delta) + Unity Catalog
    |
    v
Synapse Serverless SQL
    |
    v
Power BI-ready serving layer
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed V1 and V2 diagrams and component responsibilities.

## Technology stack

| Layer | Technology | Purpose |
|---|---|---|
| Source | MySQL 8 | Clinical source tables and watermark metadata |
| Connectivity | Self-hosted Integration Runtime | Secure bridge from ADF to local MySQL |
| Orchestration | Azure Data Factory | Metadata lookup, table iteration, extraction, watermark handling |
| Storage | ADLS Gen2 | Bronze Parquet and Silver/Gold Delta data |
| Processing | Azure Databricks / Apache Spark | Transformation, MERGE, Gold publishing |
| Lakehouse | Delta Lake | ACID Silver and Gold tables |
| Governance | Unity Catalog | Catalog, schemas, external table registration |
| Serving | Synapse serverless SQL | External tables and reporting queries |
| Reporting target | Power BI | Consumption-ready SQL serving layer |

## Version 1 and Version 2

| Capability | Version 1 | Version 2 |
|---|---|---|
| Ingestion | Full load | Metadata-driven full/incremental extraction |
| Bronze | Full source extracts | Changed/new rows for incremental tables |
| Silver | Overwrite | Primary-key Delta MERGE |
| Empty batches | Not central to design | Safely skipped |
| Gold | Full publish | Full publish from latest trusted Silver |
| Watermarks | Not used | Per-table watermarks |
| Validation | Baseline layer counts | Inserts, updates, bulk changes, reruns, duplicate checks |
| Main notebooks | `01_bronze_to_silver_gold` | `02_incremental_bronze_to_silver_merge`, `03_silver_to_gold_publish` |

Gold remains a full publish by design. The four Gold datasets are small business marts containing joins and derived metrics; rebuilding them from trusted Silver is currently simpler and more deterministic than maintaining incremental join state.

## Implemented datasets

Silver contains 18 clinical tables. Gold contains four reporting marts:

- `patient_study_summary`
- `lab_summary`
- `safety_adverse_events`
- `visit_summary`

Final validated Gold/Synapse counts:

| Dataset | Rows |
|---|---:|
| `patient_study_summary` | 241 |
| `lab_summary` | 7,715 |
| `safety_adverse_events` | 245 |
| `visit_summary` | 1,108 |

## Key validation results

- A patient inserted without an enrollment reached Silver but correctly did not enter `patient_study_summary`.
- Adding a valid enrollment caused that patient to appear in Gold.
- Updating `enrollment_status` propagated through ADF, Silver, Gold, and Synapse.
- Forty patients and their enrollments were loaded in bulk, increasing `patient_study_summary` to 241.
- Seven selected enrollment statuses were updated and verified in Synapse.
- A final no-change rerun preserved counts and returned no duplicate patient IDs.

Full evidence is documented in [TEST_EVIDENCE.md](TEST_EVIDENCE.md). Local validation screenshots are intentionally excluded from the public repository.


## How to run

The current workflow is deliberately explicit:

1. Start local MySQL and confirm `clinical_trial_db` is reachable.
2. Confirm the Windows machine is online and the `SHIR-ClinicalTrial` service/node is available.
3. Run ADF `pipeline1`.
4. Run Databricks notebook `02_incremental_bronze_to_silver_merge`.
5. Run Databricks notebook `03_silver_to_gold_publish`.
6. Query the four Gold external tables in Synapse database `clinical_trial_serving`.

See [RUNBOOK.md](RUNBOOK.md) for prerequisites, verification queries, and troubleshooting.

## Documentation map

- [ARCHITECTURE.md](ARCHITECTURE.md) — detailed design and data flow
- [V1_FULL_LOAD.md](V1_FULL_LOAD.md) — original full-load lakehouse
- [V2_INCREMENTAL_FRAMEWORK.md](V2_INCREMENTAL_FRAMEWORK.md) — incremental upgrade
- [TEST_EVIDENCE.md](TEST_EVIDENCE.md) — completed validation tests
- [RUNBOOK.md](RUNBOOK.md) — operational execution guide
- [FUTURE_IMPROVEMENTS.md](FUTURE_IMPROVEMENTS.md) — prioritized next steps

## Operational boundaries

- MySQL is hosted locally, so MySQL, Windows, network connectivity, and SHIR must all be online during ADF extraction.
- Closing the SHIR desktop application does not necessarily stop its Windows service; node/service health is the relevant check.
- Databricks notebooks are currently run after ADF rather than orchestrated automatically.
- Bronze is incremental in row selection, but immutable batch history is a future improvement.
- Silver MERGE provides business-key upsert behavior; avoiding physical updates for unchanged rows is a future optimization.
- Gold full publish is intentional at the current scale.

