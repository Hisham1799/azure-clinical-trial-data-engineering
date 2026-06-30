# Security Notes

- No passwords, API keys, tokens, storage keys, connection strings, client secrets, or private credentials are committed.
- A Twelve Data API key found in the original ADF dataset export was replaced with `<REDACTED_TWELVE_DATA_API_KEY>`.
- ADF `encryptedCredential` values were replaced with `<REDACTED>`.
- Databricks notebook outputs and execution history were removed from committed `.ipynb` files.
- Clinical SQL files are schema-only DDL; bulk INSERT data remains only in the private offline backup.
- DBC archives, Parquet files, installers, authentication profiles, logs, and full backup exports are excluded.
- Rebuilds must provide fresh secrets through Azure Key Vault, managed identity, or local environment configuration.

The private source archive is intentionally not part of this Git repository.