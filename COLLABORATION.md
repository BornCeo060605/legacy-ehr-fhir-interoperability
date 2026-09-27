# Team Collaboration & Architectural Role Matrix

## Legacy EHR → FHIR R4 Interoperability Platform

This document formally specifies the multidisciplinary engineering division, branch governance, and ownership matrix among the three collaborating project engineers.

---

## 1. Engineering Roster & Role Specification

| Team Member | Industry Engineering Role | Primary Branch | Key Modules & Architectural Ownership |
| :--- | :--- | :--- | :--- |
| **Vishnupriyaa K**<br>`vishnupriyaakm@gmail.com` | **Lead AI & Semantic Intelligence Architect** *(Core AI)* | `feature/ai-semantic-retrieval` | • Multi-Stage LLM Reasoning Pipeline (`agents/`)<br>• Hybrid Vector & Lexical Knowledge Engine (`retrieval/`, ChromaDB)<br>• HL7 FHIR R4, LOINC, RxNorm, UCUM & SNOMED CT Ontologies<br>• Multi-Factor Confidence Scoring Engine (`models/confidence_decision_engine.py`)<br>• Multi-Provider LLM Failover & Key Rotation (`models/llm_provider.py`) |
| **Arutselvy M**<br>`arutselvy.manicannane@gmail.com` | **Data Platform & Database Infrastructure Engineer** *(Data/Database Backend)* | `feature/backend-pipeline-engine` | • Deterministic Schema Profiler & Overlap Analyzer (`tools/`, `scripts/profile_database.py`)<br>• Database Engine & SQLite Persistence Layer (`app/database.py`)<br>• Relational Entity Models & Schemas (`app/models/entities.py`, `app/schemas/`)<br>• Database Upload, SHA-256 Fingerprinting & Ingestion API (`app/api/databases.py`, `app/services/database_service.py`)<br>• System Diagnostics & Profiler Test Suite (`app/api/health.py`, `tests/test_schema_profiler.py`) |
| **Dheshna B**<br>`dheshnavasuki05@gmail.com` | **Full-Stack Application & Applied AI Evaluation Engineer** *(App Backend + Frontend + AI Eval)* | `feature/clinical-review-ui-eval` | • **Application Backend Services**: Clinical Review APIs (`app/api/reviews.py`, `app/services/review_service.py`), Mapping Query Endpoints (`app/api/mappings.py`), Report Microservice (`app/api/reports.py`, `app/api/analysis.py`), Project & Audit APIs (`app/api/audit.py`, `app/api/projects.py`), API Integration Tests (`tests/test_api_endpoints.py`)<br>• **Frontend Web Application**: Zero-Dependency Clinical Review SPA (`static/`, HTML5/CSS3/ES6+), AI Provenance Drawer, Human Review Queue<br>• **Applied AI Evaluation**: Multi-Hospital Ground-Truth AI Benchmark, 10 Publication-Grade (300 DPI) Analytical Charts (`outputs/reports/charts/`) |

---

## 2. Module Ownership & Architectural Boundaries

```
legacy-ehr-fhir-interoperability/
├── [Vishnupriyaa K] ──── Core AI Architecture & Terminology Knowledge
│   ├── agents/                   # Schema Intelligence, Semantic & Mapping Agents
│   ├── retrieval/                # ChromaDB Vector Store & Exact Lexical Search
│   ├── terminology/              # LOINC, RxNorm, UCUM & SNOMED Caches
│   ├── fhir/                     # HL7 FHIR R4 Resource Schemas & Definitions
│   └── models/confidence_decision.py # Mathematical Multi-Factor Confidence Engine
│
├── [Arutselvy M] ─────── Data Platform & Database Infrastructure Backend
│   ├── tools/schema_profiler.py  # Statistical Profiler & Value Overlap Detection
│   ├── scripts/profile_database.py # Database Inspection CLI & Analytics
│   ├── app/database.py           # SQLite Engine, Session Management & Pooling
│   ├── app/models/entities.py    # Relational Database Tables & Foreign Keys
│   ├── app/schemas/              # Pydantic Ingestion Schemas & DTOs
│   ├── app/api/databases.py      # Database Upload & Ingestion REST Endpoints
│   ├── app/services/database_service.py # Ingestion & Fingerprinting Service
│   └── tests/test_schema_profiler.py # Profiler & Relational Integrity Tests
│
└── [Dheshna B] ───────── Application Backend, Frontend SPA & Applied AI Evaluation
    ├── app/api/reviews.py        # Clinical Review REST API (Preserves Provenance)
    ├── app/services/review_service.py  # Human Sign-Off & Audit Queue Logic
    ├── app/api/mappings.py       # Mapping Search & Multi-Attribute Filter API
    ├── app/services/mapping_service.py # Mapping Query Engine
    ├── app/api/reports.py        # Benchmark Reporting & Export Endpoints
    ├── app/api/analysis.py       # Pipeline Analysis & SSE Event Streaming
    ├── app/api/audit.py          # Governance Audit Trail REST Endpoints
    ├── app/main.py               # FastAPI App Router Assembly & Static Mounts
    ├── tests/test_api_endpoints.py # API Service Integration Tests
    ├── static/                   # Zero-Dependency Clinical Review SPA (HTML5/CSS/JS)
    ├── scripts/generate_evaluation_charts.py # AI Benchmark Plotting Engine
    └── outputs/reports/charts/   # 10 Publication-Ready 300 DPI Figures & PDFs
```

---

## 3. Clear Backend Division: Data Tier vs. Application Tier

The backend is cleanly split across two complementary engineering layers:

1. **Database & Data Platform Layer (Lead: Arutselvy M)**:
   - Focuses on the **data tier**: scanning physical SQLite files, computing column statistics (null %, distinct %), finding foreign key containment overlaps, managing the SQLite database connection lifecycle, and handling database uploads.
2. **Application & Business Services Layer (Lead: Dheshna B)**:
   - Focuses on the **application tier**: exposing business logic through REST endpoints, managing clinical review sign-offs, filtering candidate mappings, serving real-time analysis events, generating markdown reports, and wiring the FastAPI app to the frontend SPA.

---

## 4. Branching Strategy & Git Workflow

The project follows a Trunk-Based Collaborative Workflow with isolated feature streams:

1. **`main`**:
   - The authoritative production and submission branch.
   - Contains integrated milestones validated against all 36 automated pytest suites.

2. **`feature/backend-pipeline-engine` (Owner: Arutselvy M)**:
   - Dedicated branch for data tier engineering: schema profiler algorithms, SQLite engine configuration, database ingestion endpoints, and data tests.

3. **`feature/ai-semantic-retrieval` (Owner: Vishnupriyaa K)**:
   - Dedicated branch for core AI architecture: multi-stage LLM agents, ChromaDB vector retrieval, ontology lookup caches, and confidence engine scoring.

4. **`feature/clinical-review-ui-eval` (Owner: Dheshna B)**:
   - Dedicated branch for full-stack application engineering: clinical review & mapping REST services, zero-dependency SPA, and publication-ready AI benchmark charts.

---

## 5. Pull Request & Review Governance

All feature contributions undergo cross-peer review prior to integration into `main`:
- **PR #1: Data Platform, Database Engine & Schema Profiler** (Authored by Arutselvy M, Merged into `main`)
- **PR #2: AI Semantic Intelligence & Terminology Knowledge Retrieval** (Authored by Vishnupriyaa K, Merged into `main`)
- **PR #3: Full-Stack Application APIs, Clinical UI & AI Benchmarks** (Authored by Dheshna B, Merged into `main`)
