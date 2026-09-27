# Cross-Hospital Phase 1 Interoperability & Generalization Report

## Executive Summary

This report compares the autonomous schema understanding, terminology evidence retrieval, and FHIR R4 mapping discovery across distinct legacy EHR databases exhibiting variable naming conventions, abbreviations, and structures.

### Cross-Hospital Metrics

| Hospital Database   |   Total Columns | Accepted   |   Review |   Unsupported | Provider   | Model                             |
|---------------------|-----------------|------------|----------|---------------|------------|-----------------------------------|
| hospital_a.db       |              30 | 26 (86.7%) |        3 |             1 | openrouter | meta-llama/llama-3.3-70b-instruct |
| hospital_b.db       |              30 | 27 (90.0%) |        2 |             1 | openrouter | meta-llama/llama-3.3-70b-instruct |
| hospital_c.db       |              30 | 27 (90.0%) |        2 |             1 | openrouter | meta-llama/llama-3.3-70b-instruct |

### FHIR Target Resource Distribution

| FHIR Resource     |   hospital_a.db |   hospital_b.db |   hospital_c.db |
|-------------------|-----------------|-----------------|-----------------|
| Condition         |               5 |               4 |               4 |
| Encounter         |               7 |               4 |               1 |
| MedicationRequest |               5 |               5 |               5 |
| Observation       |               6 |               7 |              10 |
| Patient           |               7 |               9 |               9 |
| Unknown           |               0 |               1 |               1 |

### Generalization Observations

- **Primary Identifier Resolution:** Across dialects, patient identifiers were correctly mapped to `Patient.identifier` rather than `Patient.id` or `[Resource].subject`.
- **Subject Reference Consistency:** Foreign key patient links in clinical event tables consistently resolve to `[Resource].subject` with reference types.
- **Deterministic Rule Invariance:** Acceptance thresholds remained strictly governed by evidence strength, preventing LLM hallucination of ungrounded mappings.
