# Future Improvements

## Positioning

The current project is complete as a validated portfolio implementation. These items are improvements for reliability, security, automation, scalability, and governance; they are not claims that the existing tests failed.

## Priority 1 — Reliability and security

### Move local MySQL to a managed database

**Current state:** MySQL runs on a Windows machine and depends on SHIR.

**Improvement:** Move the source to Azure Database for MySQL or another managed source when the project requires unattended schedules.

**Benefit:** Removes workstation uptime dependency, improves backup/patching, and simplifies availability.

**Tradeoff:** Adds cloud cost and requires migration/network/security work.

### Use Key Vault for credentials

**Current state:** The inspected ADF MySQL linked service does not retrieve its password from Key Vault.

**Improvement:** Store source secrets in Azure Key Vault and grant the data factory identity only the required access.

**Benefit:** Central rotation, reduced secret exposure, and better separation of duties.

### Use a least-privilege MySQL account

Replace broad administrative access with a dedicated ingestion identity that can read required source tables and execute only the approved watermark procedure.

### Strengthen network controls

Restrict storage and service access, prefer managed identity over account keys, and evaluate private endpoints/managed networking for a production deployment.

## Priority 2 — Orchestration and observability

### Orchestrate Databricks after ADF

**Current state:** ADF ingestion, notebook 02, and notebook 03 are explicit sequential operating steps.

**Improvement:** Add Databricks Job tasks and invoke them after successful extraction, either from ADF or Databricks Workflows.

**Required dependency flow:**

```text
ADF extraction succeeds
 -> Silver MERGE succeeds
 -> Gold publish succeeds
 -> Synapse validation succeeds
```

**Benefit:** Repeatable schedules, retries, parameters, task-level history, and alerts.

### Add a durable logging/control table

Capture:

- pipeline and batch IDs;
- table name;
- source watermark bounds;
- extracted, inserted, updated, rejected counts;
- start/end timestamps;
- Bronze path;
- Silver/Gold commit status;
- error details.

This provides traceability beyond activity output screens.

### Add monitoring and alerts

Alert on:

- ADF or notebook failure;
- SHIR offline heartbeat;
- source freshness breach;
- unexpected zero-row batches;
- count deviation;
- duplicate or null-key checks;
- watermark regression;
- Synapse serving failure.

Use Azure Monitor/Log Analytics initially; evaluate a dedicated data-observability platform only if complexity justifies it.

## Priority 3 — Data correctness and efficiency

### Avoid unnecessary matched-row updates

**Current state:** Silver uses `whenMatchedUpdateAll()`.

**Improvement:** Update only when business values differ, using a canonical row hash or explicit change predicate.

**Benefit:** Fewer Delta files/versions, lower compute, and clearer change history.

**Tradeoff:** Hash calculation and null/type canonicalization must be consistent.

### Add delete handling

Define how source deletes or `is_deleted` flags should propagate:

- hard delete;
- soft delete;
- effective-date closure;
- retained historical record.

The correct policy depends on clinical audit requirements.

### Add late-arriving-data handling

Watermark-only extraction can miss rows that arrive with an older timestamp. Options include:

- overlap/lookback windows plus idempotent MERGE;
- source change-data capture;
- monotonically increasing sequence keys;
- reconciliation scans.

A short overlap window is a pragmatic next step for this project.

### Add schema evolution controls

Detect source schema changes before MERGE, classify them as compatible or breaking, and require explicit approval for target schema evolution.

### Consider immutable Bronze history

**Current state:** Bronze contains incremental row selection but does not provide a fully immutable batch archive.

**Improvement:** Store batches under run/date/table paths with a manifest containing watermark bounds, count, checksum, and status.

**Benefit:** Replay, audit, reconciliation, and easier recovery.

**Tradeoff:** More files and a retention/compaction policy.

## Priority 4 — Delivery and governance

### Add CI/CD

Place ADF artifacts, Databricks notebooks/source, Synapse SQL, metadata definitions, and infrastructure-as-code in Git.

A delivery pipeline should:

1. lint and test code;
2. validate metadata;
3. deploy to a non-production environment;
4. run smoke tests;
5. promote through approval.

### Clean notebook production paths

Move exploratory cells to a separate development notebook or archive. Keep production notebooks parameterized, ordered, restartable, and free of ambiguous manual setup.

### Add data quality rules

Start with:

- primary-key non-null and uniqueness;
- accepted status values;
- relationship integrity;
- plausible clinical ranges;
- freshness;
- source-to-Bronze and Bronze-to-Silver reconciliation.

Store results by batch and table.

### Improve governance

Add:

- catalog/schema/table ownership;
- explicit grants;
- clinical/PII classification tags;
- column masks where appropriate;
- lineage review;
- retention policies;
- documented data dictionary.

## Priority 5 — Scale only when justified

### Consider incremental Gold

Do not implement incremental Gold merely for architectural fashion.

Reconsider it when:

- full publish misses the SLA;
- Gold volumes grow materially;
- compute cost becomes significant;
- downstream consumers require more frequent updates.

Possible designs:

- affected-patient/key propagation;
- Delta Change Data Feed;
- incremental materialized tables;
- event-driven mart refresh.

The tradeoff is more state, dependency tracking, late-data handling, and test complexity. Until those benefits are measurable, full publish remains the recommended approach.

### Optimize compute and files

When data volume grows:

- use controlled job clusters and policies;
- benchmark Photon;
- compact small Delta files;
- define `OPTIMIZE`/retention policies;
- partition only where query volume and cardinality justify it.

At the current scale, unnecessary partitioning can make performance worse.

## Recommended implementation order

1. Key Vault and least-privilege credentials
2. ADF-to-Databricks job orchestration
3. Run/audit logging and alerts
4. Immutable Bronze batches
5. Change-aware Silver updates
6. Delete and late-arrival policy
7. CI/CD and infrastructure-as-code
8. Data-quality framework and governance controls
9. Incremental Gold only after scale/SLA evidence

