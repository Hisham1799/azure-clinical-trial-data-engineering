# End-to-End Test Evidence

## Scope

These tests validate the implemented V2 flow:

```text
MySQL -> ADF -> Bronze -> Silver MERGE -> Gold publish -> Synapse
```

All tests below were completed and verified. Local screenshots were reviewed while preparing this record but are intentionally excluded from the public repository.

## Final validated counts

| Dataset | Final rows |
|---|---:|
| `patient_study_summary` | 241 |
| `lab_summary` | 7,715 |
| `safety_adverse_events` | 245 |
| `visit_summary` | 1,108 |

## Test A — Single patient insert

**Source change:** Inserted `patient_id = 201` into MySQL `patients`.

**Expected result:**

- ADF extracts one patient row.
- Silver `patients` increases from 200 to 201.
- Gold `patient_study_summary` remains 200 because the new patient has no enrollment.

**Actual result:**

- Bronze contained one patient change.
- Silver contained 201 patients.
- Gold remained at 200.

**Status:** **PASS**

**What it proved:** Gold membership follows business relationships, not the count of one source table.


## Test B — Enrollment insert for patient 201

**Source change:** Inserted a valid enrollment for patient 201 using:

- `study_id = 5`
- `arm_id = 10`
- `site_id = 6`
- `investigator_id = 14`

**Expected result:** After ADF, Silver MERGE, and Gold publish, patient 201 appears in `patient_study_summary`.

**Actual result:** Gold increased from 200 to 201 and the patient appeared with the related study/enrollment context.

**Status:** **PASS**

**What it proved:** The Gold join requires valid related data and correctly incorporates a newly completed relationship.

## Test C — Idempotency rerun

**Source change:** None. The pipeline sequence was rerun.

**Expected result:** Gold counts remain stable and patient 201 is not duplicated.

**Actual result:** Counts stayed stable and no duplicate `patient_study_summary` record was created.

**Status:** **PASS**

**What it proved:** Re-execution is idempotent at the business-record level.

## Test D — Update patient attributes

**Source change:** Updated `weight_kg` and `bmi` for patient 201 in MySQL.

**Expected result:**

- Silver `patients` reflects the updated attributes.
- `patient_study_summary` does not expose those fields, so Gold is not the correct place to validate them.

**Actual result:** The fields updated in Silver. Their absence from Gold was consistent with the Gold schema.

**Status:** **PASS**

**What it proved:** Validation must target the layer that actually owns the field.

## Test E — Update enrollment status

**Source change:** Changed patient 201's enrollment status from `Active` to `Inactive`.

**Expected result:** The change propagates through Bronze, Silver, Gold publish, and Synapse.

**Actual result:** Synapse returned `patient_id = 201` with `enrollment_status = Inactive`.

**Status:** **PASS**

**Observed value:** Patient 201 changed from `Active` to `Inactive` in the Synapse serving result.


**What it proved:** Existing-record updates propagate through the complete serving chain.

## Test F — Bulk insert

**Source change:**

- inserted patients 202 through 241;
- inserted matching enrollments for all 40 patients.

**Expected result:** `patient_study_summary` increases from 201 to 241.

**Actual result:** Synapse returned 241 rows.

**Status:** **PASS**


**What it proved:** The framework handles a multi-row incremental batch and preserves Gold relationship logic.

## Test G — Bulk update

**Source change:** Changed enrollment status to `Inactive` for patient IDs:

```text
29, 30, 107, 110, 198, 210, 220
```

**Expected result:** All seven business rows show `Inactive` in Synapse after the full pipeline sequence.

**Actual result:** Synapse returned all seven IDs with `Inactive`.

**Status:** **PASS**


**What it proved:** Multiple updates are merged and published correctly in one cycle.

## Test H — Final idempotency and duplicate check

**Source change:** None. Reran the complete process after the bulk tests.

**Expected result:**

- final counts remain stable;
- a grouped duplicate query returns no patient IDs with count greater than one.

**Actual result:** Counts remained stable and the duplicate query returned no rows.

**Status:** **PASS**


**What it proved:** The final serving mart is idempotent at its patient business key.

## Supporting Silver evidence

- An empty `patients` batch returned zero rows and was handled safely.
- The Silver MERGE processed `lab_results` and retained the expected 7,715 count.


## Testing lessons

1. **Validate relationships, not isolated counts.** A patient needs a valid enrollment to enter the patient-study mart.
2. **Validate at the owning layer.** Raw/conformed patient attributes belong in Silver checks; business-facing enrollment status belongs in Gold/Synapse checks.
3. **Test inserts and updates.** Insert-only testing does not prove MERGE update behavior.
4. **Use both single-row and bulk tests.** Single-row tests isolate logic; bulk tests exercise realistic batches.
5. **Rerun without changes.** A final no-change execution is necessary to prove business-level idempotency.
6. **Check duplicates directly.** Stable counts alone can hide one missing and one duplicated record.

