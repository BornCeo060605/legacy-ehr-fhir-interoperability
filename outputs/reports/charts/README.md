# Phase 1 Ground-Truth Evaluation Charts Index

This directory contains report-ready, publication-grade academic visualizations (PNG at 300 DPI and vector PDF) illustrating the evaluation of the **Phase 1 Legacy EHR → HL7 FHIR R4 Interoperability Engine** against the independent ground truth (90 fields evaluated across three hospital dialects).

---

## Chart Catalog & Summary of Results

| # | Filename | Visualization Purpose | Metric / Key Finding |
| :-: | :--- | :--- | :--- |
| **01** | [`01_overall_evaluation_metrics.png`](./01_overall_evaluation_metrics.png) | Comprehensive overview of accuracy & coverage metrics | **Semantic Accuracy: 97.8%** (88/90), **Mapping Coverage: 96.7%** (87/90), **Normalized Element: 92.2%** (83/90), **Strict Exact Element: 75.6%** (68/90). |
| **02** | [`02_fhir_element_accuracy.png`](./02_fhir_element_accuracy.png) | Strict literal path matching vs. normalized FHIR R4 equivalence | **Strict Exact: 75.6%** vs. **Normalized / Usable: 92.2%** (+16.6% difference due to choice types, sub-elements, and patient subject reference resolution). |
| **03** | [`03_hospital_generalization.png`](./03_hospital_generalization.png) | Cross-dialect performance across Hospital A, B, and C | **Hospital A:** 96.7% normalized / 83.3% strict<br>**Hospital B:** 93.3% normalized / 76.7% strict<br>**Hospital C [HELD-OUT TEST]:** 86.7% normalized / 66.7% strict. |
| **04** | [`04_accepted_mapping_precision.png`](./04_accepted_mapping_precision.png) | Reliability and precision of automatically accepted mappings | **Overall Accepted Precision: 91.3%** (73/80).<br>Hospital A: **100.0%** (26/26), Hospital B: **92.6%** (25/27), Hospital C: **81.5%** (22/27). |
| **05** | [`05_decision_distribution.png`](./05_decision_distribution.png) | Breakdown of pipeline decision engine outputs | **ACCEPTED: 80** (88.9%), **REVIEW: 7** (7.8%), **UNSUPPORTED: 3** (3.3%). |
| **06** | [`06_decision_correctness.png`](./06_decision_correctness.png) | Alignment between deterministic decision categories and ground truth | **ACCEPTED:** 73 correct / 7 incorrect (91.3% precision)<br>**REVIEW:** 7 correct / 0 incorrect (100.0% safety)<br>**UNSUPPORTED:** 3 correct / 0 incorrect (100.0% specificity). |
| **07** | [`07_confidence_vs_accuracy.png`](./07_confidence_vs_accuracy.png) | Confidence score calibration versus observed accuracy | **0.00–0.49:** 100.0% (3/3)<br>**0.50–0.74:** 100.0% (5/5)<br>**0.75–0.89:** 93.8% (30/32)<br>**0.90–1.00:** 90.0% (45/50; identifies 5 overconfident errors). |
| **08** | [`08_mapping_errors.png`](./08_mapping_errors.png) | Exhaustive itemization of all 7 observed mapping discrepancies | `Encounter.subject → Patient.identifier` (2)<br>`Condition.identifier → Observation.identifier` (2)<br>`Encounter.identifier → Observation.identifier` (1)<br>`Encounter.period.start → Observation.effectiveDateTime` (1)<br>`Encounter.period.end → Observation.effectiveDateTime` (1). |
| **09** | [`09_error_type_summary.png`](./09_error_type_summary.png) | Mutually exclusive root-cause categorization of the 7 errors | **Wrong FHIR Resource:** 5 (71.4%) — conflating event/condition tables with Observation.<br>**Relationship Error:** 2 (28.6%) — mapping patient FK to Patient.identifier rather than Encounter.subject. |
| **10** | [`10_retrieval_vs_reasoning_errors.png`](./10_retrieval_vs_reasoning_errors.png) | Architectural failure location (retrieval vs. downstream reasoning) | **Retrieval Failures: 0 / 7 (0.0%)**<br>**Reasoning / Mapping Errors: 7 / 7 (100.0%)** — in all cases, correct FHIR target definitions were present in retrieved evidence. |

---

## Technical Specifications
- **Resolution:** 300 DPI (PNG)
- **Vector Source:** PDF included for all figures (`.pdf`)
- **Visual Palette:** Academic Navy (`#1f4e79`), Slate Teal (`#2e8b57`), Light Steel (`#5b9bd5`), Coral Error (`#d9534f`), Amber Triage (`#ec971f`)
- **Typography:** Standardized sans-serif (Arial / Helvetica / DejaVu Sans)
- **Scale:** Fixed 0–100% bounds on percentage charts to prevent distortion.
