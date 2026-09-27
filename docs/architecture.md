# System Architecture & Technical Specification

## Overview
The **Legacy EHR → FHIR R4 Interoperability Platform** is an enterprise-grade clinical data mapping system designed to autonomously profile legacy Electronic Health Record (EHR) schemas, discover clinical semantics, retrieve multi-source terminology evidence, propose FHIR R4 candidate target paths, and deterministically triage mappings into `ACCEPTED`, `REVIEW`, and `UNSUPPORTED` tiers.

---

## Strict Scope Boundary: Phase 1 Only

```
┌────────────────────────────────────────────────────────────────────────┐
│                   PHASE 1 (IMPLEMENTED & OPERATIONAL)                  │
├────────────────────────────────────────────────────────────────────────┤
│ Legacy EHR SQLite Databases                                            │
│    ↓                                                                   │
│ Deterministic Schema Profiling (null %, distinct %, PKs, overlaps)     │
│    ↓                                                                   │
│ Schema Intelligence & Clinical Role Detection                         │
│    ↓                                                                   │
│ Deterministic Retrieval Strategy Planning                             │
│    ↓                                                                   │
│ Hybrid Evidence Retrieval (FHIR R4, LOINC, RxNorm, UCUM, SNOMED)      │
│    ↓                                                                   │
│ Clinical Semantic Agent (concept inference & classification)           │
│    ↓                                                                   │
│ FHIR Mapping Agent (target element candidate proposal)                 │
│    ↓                                                                   │
│ Deterministic Confidence & Decision Engine                             │
│    ↓                                                                   │
│ Triage: ACCEPTED (Green) | REVIEW (Amber) | UNSUPPORTED (Coral)        │
│    ↓                                                                   │
│ Human-in-the-Loop Clinical Review Queue (preserves automated decision) │
│    ↓                                                                   │
│ Institutional Reports, 300 DPI Charts, & Immutable Governance Audit    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                         ⛔ STOP: PHASE 1 BOUNDARY
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                    PHASE 2 (INTENTIONALLY OUT OF SCOPE)                │
├────────────────────────────────────────────────────────────────────────┤
│ ✕ Patient-level row transformation into live FHIR JSON instances      │
│ ✕ HL7 FHIR Bundle generation                                           │
│ ✕ Production FHIR server upload (POST/PUT to HAPI / GCP / Azure FHIR)  │
│ ✕ Live terminology runtime translation during patient extract          │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Layered Component Architecture

```
                       ┌─────────────────────────┐
                       │   Clinical Web UI SPA   │
                       │ (HTML5, CSS3, ES6 SPA)  │
                       └────────────┬────────────┘
                                    │ REST / SSE
                                    ▼
                       ┌─────────────────────────┐
                       │   FastAPI Web Engine    │
                       │   (app/main.py, api/)   │
                       └────────────┬────────────┘
                                    │
                ┌───────────────────┴───────────────────┐
                ▼                                       ▼
    ┌──────────────────────┐                ┌──────────────────────┐
    │ Application Services │                │ Research Intelligence│
    │ (app/services/)      │                │ Engine (Phase 1 Core)│
    │  - ProjectService    │                │  - Schema Profiler   │
    │  - DatabaseService   │───────────────▶│  - Hybrid Retriever  │
    │  - MappingService    │                │  - Semantic Agent    │
    │  - ReviewService     │                │  - FHIR Mapping Agent│
    │  - ResourceService   │                │  - Confidence Engine │
    │  - AnalysisService   │                └───────────┬──────────┘
    └───────────┬──────────┘                            │
                │                                       ▼
                ▼                           ┌──────────────────────┐
    ┌──────────────────────┐                │ Knowledge Resources  │
    │ SQLite Persistence   │                │  - FHIR R4 Specs     │
    │ (app.db)             │                │  - LOINC / UCUM      │
    │  - Projects          │                │  - RxNorm / SNOMED   │
    │  - Databases         │                │  - Vector Indexes    │
    │  - Analysis Runs     │                └──────────────────────┘
    │  - Mappings          │
    │  - Review Records    │
    │  - Audit Events      │
    └──────────────────────┘
```

---

## Deterministic Rule vs. LLM Authority Principle
1. **LLM Authority Boundary**:
   - The LLM acts exclusively as an *inquisitive clinical reasoning copilot* that generates candidate interpretations and proposes candidate FHIR R4 target elements based on supplied schema facts and retrieved terminology evidence.
2. **Deterministic Governance**:
   - Final decisions (`ACCEPTED`, `REVIEW`, `UNSUPPORTED`) are strictly controlled by the deterministic Confidence & Decision Engine (`models/confidence_decision_engine.py`).
   - Hard thresholding, penalty rules for high null rates or missing evidence, and required clinical reviews cannot be overridden by prompt manipulation.
3. **Human Review Traceability**:
   - A clinician's manual sign-off in the Review Queue creates an explicit `ReviewRecord` linked to the mapping.
   - The original `automated_decision` is never mutated or overwritten, ensuring complete regulatory auditability.
