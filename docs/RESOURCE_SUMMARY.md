# Resource Summary

## Subscription

- Name: `Azure subscription 1`
- ID: `bc5c2887-eabd-4354-ba62-ade1a5b53b49`
- Tenant: `ceb937d8-13f6-4d72-b8be-3f96fee7e3d5`
- Region used: Central India

## Stock Market Project

| Category | Resource |
|---|---|
| Primary group | `rg-de-sprint` |
| Storage | `hishamdelake01` |
| Containers | `bronze`, `silver`, `gold` |
| Data Factory | `adf-hisham-de` |
| Pipeline | `pl_ingest_stocks_bronze` |
| Trigger | `tr_daily_stock_ingest` |
| Databricks | `dbw-hisham-de` |
| Cluster | `single-node-dev-cluster` |
| Live notebooks | 2 |
| Synapse | `synapse-hisham-de` |
| Synapse SQL scripts | 1 |
| Dedicated SQL pools | 0 |
| Spark pools | 0 |
| Key Vault | None |
| Log Analytics | None |

Managed groups:

- `managed-rg-databricks-sprint`
- `synapseworkspace-managedrg-6f5455bf-dc2e-43d5-bae1-35bddbd64bfd`

## Clinical Trial Project

| Category | Resource |
|---|---|
| Primary group | `rg-clinical-trial` |
| Storage | `hishamclinicaldl` |
| Containers | `bronze`, `silver`, `gold`, `synapse` |
| Data Factory | `adf-clinical-trial` |
| Pipeline | `pipeline1` |
| SHIR | `SHIR-ClinicalTrial` |
| Databricks | `databricks-clinical-trial` |
| Cluster | `cluster-clinical-trial` |
| Live notebooks | 4 |
| Unity Catalog Silver tables | 18 |
| Unity Catalog Gold tables | 4 |
| Synapse | `synapse-clinical-trial` |
| Synapse SQL scripts | 3 |
| Dedicated SQL pools | 0 |
| Spark pools | 0 |
| Key Vault | `kv-clinical-trial` |
| NAT Gateway | `nat-gateway` |
| Static public IP | `nat-gw-public-ip` |
| Log Analytics | None |

Managed groups:

- `databricks-rg-databricks-clinical-trial-fb3q547qdfrdw`
- `synapseworkspace-managedrg-a9fc877b-d1c4-4369-a05e-97f4a9bfd18a`

## Shared

- Unity Catalog metastore: `3062739e-98b0-4152-8d52-4246e35cb7fc`
- Network Watcher group: `NetworkWatcherRG`
- Power BI Azure resources found: none
- Standalone Azure SQL databases found: none

## Backup Counts Expected

- Live Databricks notebooks: 6
- Notebook forms: Jupyter + source for each, plus 2 DBC workspace archives
- ADF factories: 2
- Synapse SQL scripts: 4
- Unity Catalog external project tables: 22
- Primary ADLS containers: 7 across both projects
- Resource groups: 7
- Azure Resource Manager resources: 26
