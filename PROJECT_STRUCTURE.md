# Project Structure

```text
.
|-- adf/
|   |-- datasets/
|   |-- integration_runtimes/
|   |-- linked_services/
|   `-- pipelines/
|-- databricks/
|   |-- 01_bronze_to_silver.py / .ipynb
|   |-- 01_bronze_to_silver_gold.py / .ipynb
|   |-- 02_incremental_bronze_to_silver_merge.py / .ipynb
|   `-- 03_silver_to_gold_publish.py / .ipynb
|-- sql/
|   |-- source_ddl/       # 18 schema-only MySQL DDL files
|   `-- synapse/          # serverless SQL scripts
|-- infrastructure/      # sanitized ARM template
|-- docs/                # rebuild and resource documentation
|-- SECURITY_NOTES.md
`-- README.md
```

Notebook `.py` files are best for review and diffs. Output-free `.ipynb` files are included for direct import. ADF exports retain architecture and expressions while credentials are redacted.
