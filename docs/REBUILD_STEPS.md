# Rebuild Steps

This guide rebuilds both projects from the offline archive without depending on the original subscription.

## 1. Read Before Rebuilding

1. Use a new subscription and a new resource-name suffix because Azure Storage and Key Vault names are globally unique.
2. Never copy old client secrets into a new environment.
3. Create new managed identities, application credentials, and Key Vault secrets.
4. Review current Azure pricing before creating Databricks, NAT Gateway, Synapse, or any persistent compute/network resource.
5. Keep Databricks clusters terminated until notebooks and storage permissions are ready.
6. Import definitions disabled first. Start ADF triggers only after testing.

## 2. Archive Map

- `00_inventory`: authoritative inventory, action log, manifests.
- `01_architecture`: architecture documentation and original diagrams.
- `02_resource_groups`: resource group and per-resource ARM JSON.
- `03_adf`: full ADF factory and child-resource definitions.
- `04_databricks`: notebook exports, DBC archives, compute/workspace configuration.
- `05_adls_data`: storage/container ARM metadata and data-boundary notes.
- `06_sql`: Synapse SQL scripts and local MySQL table dumps.
- `07_synapse`: Synapse workspace and artifact definitions.
- `08_unity_catalog`: catalogs, schemas, tables, columns, locations, credentials, and grants.
- `09_arm_templates`: Azure-exported and custom templates.
- `10_monitoring`: ADF, Databricks, and Synapse histories.
- `11_configs`: networking, identity, Key Vault, SQL server, and RBAC metadata.
- `12_sample_data`: portable samples.
- `13_documentation`: local project snapshots and generated guides.
- `14_screenshots_needed`: manual visual evidence.
- `15_rebuild_guides`: this guide and supporting notes.

## 3. Recommended Safe Creation Order

1. Resource groups.
2. Primary ADLS Gen2 storage account and containers.
3. Key Vault and new secrets.
4. Data Factory.
5. Self-Hosted Integration Runtime for the Clinical Trial project.
6. Databricks workspaces.
7. Databricks access connectors and storage RBAC.
8. Unity Catalog objects and grants.
9. Databricks notebooks and clusters.
10. Synapse workspaces and SQL scripts.
11. Monitoring.
12. ADF triggers last.

## 4. Rebuild the Stock Market Project

### Storage

Create an ADLS Gen2 account equivalent to `hishamdelake01`:

- StorageV2
- Standard_LRS
- Hot tier
- Hierarchical namespace enabled
- Containers: `bronze`, `silver`, `gold`
- TLS 1.2 or newer
- Anonymous blob access disabled

Load the portable samples from `12_sample_data/stock_market`.

### Data Factory

Use `09_arm_templates/adf_stock_market.custom.template.json` or recreate from `03_adf/stock_market`.

Recreate:

- Pipeline `pl_ingest_stocks_bronze`
- Datasets `ds_twelvedata_source`, `ds_bronze_stocks`
- Linked services `ls_twelvedata_api`, `ls_adls_datalake`, `ls_adf_databricks`, `ls_azure_databricks`
- Trigger `tr_daily_stock_ingest`

Replace:

- Twelve Data API key
- Storage authentication
- Databricks workspace URL and authentication
- Storage account names and paths

Keep the trigger stopped until a manual pipeline run succeeds.

### Databricks

Import `04_databricks/stock_market/notebooks/user_home_export.dbc`, or import each `.ipynb`.

Recreate a low-cost single-node cluster from the archived JSON:

- Use a currently supported LTS runtime.
- Use the smallest compatible node.
- Auto-terminate in 10 minutes.
- Do not start it until needed.

Update notebook paths and credentials to point to the new data lake. The old workspace catalog was `dbw_hisham_de`.

### Synapse

Create a Synapse workspace using the Gold container/filesystem. Do not create a dedicated SQL pool.

Import:

`06_sql/synapse_stock_market/sql_serve_gold_stock_summary.sql`

Test with a very small sample to minimize serverless scan cost.

## 5. Rebuild the Clinical Trial Project

### Local MySQL

Install MySQL and create `clinical_trial_db`.

Restore the 18 scripts in:

`06_sql/clinical_local_mysql_dumps`

The scripts are the portable source-system backup. Create a new database user and password; do not reuse the plaintext password found in old documentation.

### Storage

Create an ADLS Gen2 account equivalent to `hishamclinicaldl` with containers:

- `bronze`
- `silver`
- `gold`
- `synapse`

Load portable Parquet/CSV/JSON samples from `12_sample_data/clinical_trial`.

### Self-Hosted Integration Runtime

1. Create a new SHIR named `SHIR-ClinicalTrial`.
2. Install the archived installer only if it remains compatible; otherwise install the current Microsoft version.
3. Register it using a newly generated authentication key.
4. Configure Java if Parquet writing requires it.
5. Confirm the service account can reach local MySQL and Azure.

### Data Factory

Deploy `09_arm_templates/adf_clinical_trial.custom.template.json` or recreate from `03_adf/clinical_trial`.

Recreate the MySQL and ADLS linked services with new credentials. Validate the Lookup query, ForEach items expression, parameterized Parquet dataset, and nested copy activity.

The authoritative live pipeline name was `pipeline1`, even though project documentation calls it `PL_Bronze_MySQL_To_ADLS`.

### Databricks and Unity Catalog

Import `04_databricks/clinical_trial/notebooks/user_home_export.dbc` or the four `.ipynb` files.

Create:

- Access connector with managed identity
- Storage Blob Data Contributor on the new data lake
- Storage credential equivalent to `cred-clinical-adls`
- External locations for Bronze, Silver, and Gold
- Catalog equivalent to `databricks_clinical_trial`
- Schemas `silver` and `gold`

Use `08_unity_catalog/clinical_trial` as the metadata and grants reference. Recreate tables by running notebooks after paths are updated. Compare the rebuilt table schemas to every archived `table_*.json`.

### Key Vault

Create a new Key Vault with RBAC and soft delete. Create new values for:

- `sp-client-id`
- `sp-client-secret`
- `sp-tenant-id`

Recreate the Databricks Key Vault-backed scope `clinical-trial-scope`. Never store secret values in Git or generated documentation.

### Synapse

Create a serverless-only Synapse workspace pointing to the new `synapse` filesystem.

Import the three `.sql` files from:

`06_sql/synapse_clinical_trial`

Update ADLS endpoints and credentials. Execute only after validating expected scan volume.

## 6. Validation

For each project:

1. Confirm all expected notebooks import.
2. Compare ADF child-resource counts with `_collection.json`.
3. Verify Bronze sample reads.
4. Verify expected Silver and Gold schemas.
5. Run a single controlled pipeline execution.
6. Confirm trigger remains stopped until final approval.
7. Compare reconstructed resources to `RESOURCE_SUMMARY.md`.
8. Re-run checksum manifests for locally generated artifacts.
