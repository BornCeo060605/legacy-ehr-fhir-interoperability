# Legacy EHR → FHIR R4 Interoperability Platform

### Autonomous Semantic Discovery and Evidence-Based FHIR R4 Mapping

[![Specification](https://img.shields.io/badge/FHIR-R4.0.1-blue.svg)](https://hl7.org/fhir/R4/)
[![Tests](https://img.shields.io/badge/Tests-36%20Passed-brightgreen.svg)](#6-automated-test-suite)
[![Evaluation](https://img.shields.io/badge/Normalized%20Accuracy-92.2%25-teal.svg)](#7-independent-ground-truth-benchmark)

---

## 1. Project Overview

The **Legacy EHR → FHIR R4 Interoperability Platform** is an enterprise healthcare system designed to bridge disparate legacy hospital electronic health record (EHR) databases with the international HL7 FHIR R4 healthcare standard. 

By unifying statistical database profiling, dense vector search, clinical ontology caching, and multi-model LLM reasoning, the platform automatically discovers table semantics, determines FHIR resource alignments, and generates auditable mapping specifications with human-in-the-loop clinical review.

---

## 2. Key Capabilities

- **Deterministic Schema Profiler**: Computes null rates, uniqueness ratios, candidate identifiers, and value overlap patterns across arbitrary relational databases.
- **Hybrid Evidence Retrieval**: Combines ChromaDB dense semantic vector search with exact lexical lookup against cached medical ontologies (**HL7 FHIR R4**, **LOINC**, **RxNorm**, **UCUM**, **SNOMED CT**).
- **Multi-Provider LLM Failover**: Intelligent LLM routing supporting OpenRouter models with automated fallback handling, multi-key rotation, and rate-limit mitigation.
- **Deterministic Confidence & Decision Engine**: Multi-factor scoring (semantic fit, evidence anchor strength, schema compatibility, penalties) ensuring auditable triage (`ACCEPTED`, `REVIEW`, `UNSUPPORTED`).
- **Clinical Review Workspace**: Modern, zero-dependency human-in-the-loop review interface preserving provenance while allowing clinicians to verify or adjust mappings.
- **Publication-Grade Evaluation & Visualizations**: Automatically generates 10 high-resolution (300 DPI) publication-ready charts and vector PDFs evaluating cross-hospital generalization and accuracy.

---

## 3. Technology Stack

- **Backend**: Python 3.10+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Uvicorn
- **Persistence**: SQLite with foreign key enforcement and indexed audit trail
- **Knowledge Ontologies**: ChromaDB vector store, official HL7 FHIR R4 definitions, LOINC 2.76, RxNorm, UCUM, SNOMED CT
- **LLM Reasoning**: OpenRouter (`meta-llama/llama-3.3-70b-instruct`) with automated fallback handling
- **Frontend**: Vanilla ES6+ modules, CSS design tokens, SVG/Canvas chart rendering, responsive sidebar shell, dark/light theme support
- **Testing**: Pytest (36 unit, integration, and E2E tests passing)

---

## 4. System Architecture

```
Legacy Hospital EHR (SQLite)
            ↓
1. Deterministic Schema Profiler
            ↓
2. Schema Intelligence Agent
            ↓
3. Deterministic Retrieval Strategy
            ↓
4. Hybrid Evidence Retrieval (FHIR R4, LOINC, RxNorm, UCUM, SNOMED)
            ↓
5. Clinical Semantic Agent
            ↓
6. FHIR Mapping Agent
            ↓
7. Deterministic Confidence & Decision Engine
            ↓
     ┌──────────────┬──────────────┐
     ▼              ▼              ▼
  ACCEPTED        REVIEW      UNSUPPORTED
 (Automated)   (Human Queue)  (Out of Scope)
     │              │              │
     └──────────────┴──────────────┘
            ↓
8. Verified Mapping Specification & Governance Audit Trail
```

---

## 5. Quick Start & Execution

### Prerequisites
- Python 3.10+
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  pip install fastapi uvicorn sqlalchemy python-multipart
  ```

### Start the Application
Launch the unified FastAPI server:
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser to:
- **Web Interface**: `http://localhost:8000/`
- **Interactive API Documentation (Swagger UI)**: `http://localhost:8000/api/docs`

---

## 6. Automated Test Suite

Run the full automated test suite (36 unit, integration, and end-to-end tests):
```bash
pytest tests/ -v
```

### Test Coverage Highlights:
- **Core Pipeline (26 Tests)**: Schema profiling, schema intelligence, hybrid retrieval strategy, ontology matching, semantic reasoning, and confidence decision rules.
- **Application Services & API (10 Tests)**: Health checks, project management, database ingestion, mapping search/filtering, clinical review persistence, and audit logging.

---

## 7. Independent Ground-Truth Benchmark

Evaluated against 90 multi-hospital ground-truth fields across clean (`hospital_a.db`), coded (`hospital_b.db`), and cryptic held-out (`hospital_c.db`) schemas:

| Metric | Performance |
| :--- | :---: |
| **Semantic Meaning Accuracy** | **97.8%** (88/90) |
| **Normalized / Usable Element Accuracy** | **92.2%** (83/90) |
| **Accepted Mapping Precision** | **91.3%** (73/80) |
| **Strict Exact Element Accuracy** | **75.6%** (68/90) |
| **Terminology Anchor Accuracy** | **100.0%** (12/12) |
| **Overall Coverage** | **96.7%** (87/90) |

All 10 benchmark evaluation figures are available in `outputs/reports/charts/` and accessible directly in the application's Reporting Center.

---

## 8. Documentation Index

- [Architecture & Technical Specification](docs/architecture.md)
- [REST API Specification](docs/api.md)
- [Security & Healthcare Data Governance](docs/security.md)
- [Troubleshooting & Operations Guide](docs/troubleshooting.md)
- [Team Collaboration & Role Matrix](COLLABORATION.md)

---

## 9. Engineering Team & Branch Ownership

| Engineer | Industry Engineering Role | Assigned Branch | Primary Modules & Contributions |
| :--- | :--- | :--- | :--- |
| **Vishnupriyaa K** (`vishnupriyaakm@gmail.com`) | **Lead AI & Semantic Intelligence Architect** | `feature/ai-semantic-retrieval` | Core LLM Reasoning Agents, ChromaDB Hybrid Retrieval, Medical Ontologies, Confidence Decision Engine |
| **Arutselvy M** (`arutselvy.manicannane@gmail.com`) | **Data Platform & Database Infrastructure Engineer** | `feature/backend-pipeline-engine` | Deterministic Schema Profiler, SQLite Persistence Layer, Database Ingestion APIs, Profiler Test Suite |
| **Dheshna B** (`dheshnavasuki05@gmail.com`) | **Full-Stack Application & Applied AI Evaluation Engineer** | `feature/clinical-review-ui-eval` | Application REST Services (Review, Mapping, Reports), Zero-Dependency SPA, AI Provenance Drawer, 10 Publication AI Charts |

For full architectural ownership boundaries and PR workflow, see [COLLABORATION.md](COLLABORATION.md).
