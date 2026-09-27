# Phase 1 Pipeline & Ground-Truth Evaluation Specification

## The 8-Stage Phase 1 Analysis Pipeline

The platform executes eight deterministic and agentic stages to evaluate an uploaded EHR database:

1. **Deterministic Schema Profiler (`tools/schema_profiler.py`)**:
   - Inspects physical SQLite table schemas, data types, primary keys, and foreign keys.
   - Calculates null percentage, distinct value counts, and uniqueness ratios.
   - Discovers observed cross-table value overlaps (Jaccard coefficient) without conflating them with declared foreign keys.

2. **Schema Intelligence Agent (`agents/schema_intelligence.py`)**:
   - Classifies column roles (e.g., Primary Identifier, Foreign Key Reference, Clinical Code, Unit of Measure, Timestamp, Free Text).
   - Generates contextual hypotheses for downstream retrieval planning.

3. **Deterministic Retrieval Strategy (`retrieval/strategy.py`)**:
   - Formulates targeted queries tailored to the specific role of the field (e.g., querying LOINC for vital signs, RxNorm for medications, FHIR StructureDefinitions for identifiers).

4. **Hybrid Evidence Retrieval (`retrieval/hybrid_retriever.py`)**:
   - Executes exact lexical match against local SQLite terminology caches.
   - Executes dense semantic retrieval against pre-computed ChromaDB vector embeddings.
   - Gathers multi-source evidence anchors (FHIR R4 official spec, LOINC, UCUM, RxNorm, SNOMED CT, OHDSI).

5. **Clinical Semantic Agent (`agents/semantic_agent.py`)**:
   - Synthesizes observed column facts with retrieved terminology candidates.
   - Infers clinical meaning and categorizes the semantic domain.

6. **FHIR Mapping Agent (`agents/fhir_mapping_agent.py`)**:
   - Proposes candidate target FHIR R4 resource (e.g., `Patient`, `Observation`, `Condition`, `Encounter`, `MedicationRequest`) and target element path.
   - Formulates clinical rationale explaining the semantic alignment.

7. **Deterministic Confidence & Decision Engine (`models/confidence_decision_engine.py`)**:
   - Calculates compound confidence score based on:
     - Semantic interpretation confidence
     - Evidence retrieval quality score
     - Resource structure compatibility
     - Null rate and uniqueness penalty adjustments
   - Assigns triage tier:
     - `ACCEPTED`: High confidence ($\ge 0.80$), strong multi-source evidence.
     - `REVIEW`: Ambiguous dialect, moderate confidence, or clinical sign-off required.
     - `UNSUPPORTED`: Unmapped, null-dominant, or out-of-scope fields.

8. **Phase 1 Reporting & Governance Audit (`services/analysis_service.py`)**:
   - Generates comprehensive markdown evaluation report.
   - Records full provenance trail and immutable audit events in SQLite database.

---

## Independent Ground-Truth Evaluation Benchmark

The system was evaluated against 90 multi-hospital ground-truth fields across three distinct legacy dialects:
- **Hospital A**: Clean / Normalized Dialect
- **Hospital B**: Abbreviated / Coded Dialect
- **Hospital C**: Cryptic / Held-Out Test Dialect

### Quantitative Benchmark Results:
| Metric | System Performance | Benchmark Interpretation |
| :--- | :---: | :--- |
| **Semantic Meaning Accuracy** | **97.8%** (88/90) | High clinical concept comprehension across cryptic abbreviations |
| **Normalized / Usable Element Accuracy** | **92.2%** (83/90) | Correct functional FHIR target path |
| **Accepted Precision** | **91.3%** (73/80) | High reliability for automated ingest without human intervention |
| **Strict Exact Element Accuracy** | **75.6%** (68/90) | Exact character-for-character match with human reference key |
| **Terminology Anchor Accuracy** | **100.0%** (12/12) | Correct LOINC / RxNorm code discovery on coded legacy fields |
| **Coverage** | **96.7%** (87/90) | Only 3 fields correctly classified as unsupported |

---

## 300 DPI Publication-Grade Figures

All 10 benchmark evaluation charts are generated in both PNG (300 DPI) and vector PDF formats in `outputs/reports/charts/`:
1. `01_overall_evaluation_metrics.png` - Overall accuracy, strict, normalized, accepted precision, and coverage.
2. `02_fhir_element_accuracy.png` - Strict vs. normalized performance per resource.
3. `03_hospital_generalization.png` - Cross-dialect generalization across Hospital A, B, and C.
4. `04_accepted_mapping_precision.png` - Clinical safety and precision of automated accept decisions.
5. `05_decision_distribution.png` - Decision breakdown across hospitals.
6. `06_decision_correctness.png` - Automated decision vs. ground truth correctness.
7. `07_confidence_vs_accuracy.png` - Confidence calibration curve.
8. `08_mapping_errors.png` - Error rate breakdown across dialects.
9. `09_error_type_summary.png` - Categorization of discrepancies (Strict vs. True Discrepancies).
10. `10_retrieval_vs_reasoning_errors.png` - Root-cause analysis of mapping uncertainty.
