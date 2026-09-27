# REST API Specification

The backend provides a RESTful API built with **FastAPI** adhering to OpenAPI 3.1 standards.
Interactive Swagger documentation is accessible at: `http://localhost:8000/api/docs`.

---

## 1. System Health & Dashboard

### `GET /api/health`
Returns health status, application uptime, and status of connected database, vector index, and LLM providers.
- **Response**: `200 OK` (`SystemHealthResponse`)

### `GET /api/dashboard/stats`
Aggregates live KPI statistics, acceptance rates, cross-hospital breakdowns, and FHIR resource distribution.
- **Query Parameters**:
  - `project_id` *(optional, string)*: Filter metrics to a specific project.
- **Response**: `200 OK` (`DashboardStatsResponse`)

---

## 2. Projects Management

### `GET /api/projects`
List all registered healthcare interoperability projects.
- **Response**: `200 OK` (`List[ProjectResponse]`)

### `POST /api/projects`
Create a new project.
- **Body**:
  ```json
  {
    "name": "Statewide Health Network Migration",
    "description": "Multi-dialect mapping project",
    "fhir_version": "4.0.1"
  }
  ```
- **Response**: `200 OK` (`ProjectResponse`)

### `GET /api/projects/{project_id}`
Retrieve project details and statistics.

### `DELETE /api/projects/{project_id}`
Delete a project and its associated mapping metadata.

---

## 3. Database Ingestion & Profiling

### `GET /api/databases`
List registered legacy EHR SQLite databases.
- **Query Parameters**: `project_id` *(optional)*.

### `GET /api/databases/{database_id}`
Retrieve database details, cryptographic SHA-256 fingerprint, and comprehensive schema profile.

### `POST /api/databases/upload`
Upload a legacy EHR database (`.db`, `.sqlite`, `.db3`). Computes SHA-256 checksum, profiles tables/columns/overlaps, and registers the database.
- **Form Data**:
  - `file`: Binary SQLite file.
  - `project_id`: Project identifier.

---

## 4. Phase 1 Analysis Runs & Live SSE Streaming

### `GET /api/analysis/runs`
List previous analysis runs and their field triage summaries.

### `POST /api/analysis/start`
Launch the 8-stage Phase 1 analysis pipeline in the background.
- **Body**:
  ```json
  {
    "project_id": "...",
    "database_id": "...",
    "llm_provider": "openrouter",
    "llm_model": "meta-llama/llama-3.3-70b-instruct"
  }
  ```
- **Response**: `200 OK` (`AnalysisRunResponse`)

### `GET /api/analysis/{run_id}/stream`
Real-time **Server-Sent Events (SSE)** connection broadcasting live pipeline events:
- `stage_started`: Pipeline stage transition.
- `field_started`: Active column being mapped.
- `field_completed`: Mapping candidate discovered and triaged.
- `run_completed`: Successful analysis completion.
- `run_failed`: Error details and failure context.

---

## 5. Mappings Workspace

### `GET /api/mappings`
Query and filter candidate FHIR R4 mappings.
- **Query Parameters**:
  - `project_id`: Filter by project.
  - `run_id`: Filter by specific analysis run.
  - `database_name`: Filter by hospital database.
  - `decision`: Filter by `ACCEPTED`, `REVIEW`, or `UNSUPPORTED`.
  - `resource`: Filter by FHIR resource (e.g., `Patient`, `Observation`).
  - `search`: Case-insensitive search on column name, meaning, or FHIR path.
  - `skip`: Pagination offset.
  - `limit`: Pagination limit (default: 100).
- **Response**: `200 OK` (`List[MappingRecordResponse]`)

### `GET /api/mappings/{mapping_id}`
Retrieve complete mapping details, including observed facts, inferred clinical semantics, retrieved terminology evidence anchors, and full audit provenance trail.

---

## 6. Clinical Review Queue

### `GET /api/reviews/queue`
Retrieve mappings flagged for clinical sign-off (`decision == "REVIEW"`).
- **Query Parameters**: `project_id` *(optional)*.
- **Response**: `200 OK` (`List[MappingRecordResponse]`)

### `POST /api/reviews`
Submit a human review decision without overwriting the automated decision.
- **Body**:
  ```json
  {
    "mapping_id": "...",
    "reviewer": "Dr. Sarah Miller, MD",
    "human_decision": "ACCEPTED",
    "target_fhir_element_override": null,
    "comment": "Confirmed clinical alignment with Observation.valueQuantity."
  }
  ```
- **Response**: `200 OK` (`ReviewResponse`)

---

## 7. Reports & Knowledge Resources

### `GET /api/reports`
List generated Markdown reports.

### `GET /api/reports/{filename}`
Retrieve raw Markdown report content.

### `GET /api/reports/evaluation/charts`
List all 10 evaluation charts with direct download links for 300 DPI PNG and vector PDF.

### `GET /api/reports/evaluation/summary`
Retrieve quantitative benchmark metrics (strict accuracy, normalized accuracy, accepted precision).

### `GET /api/resources`
List external and local clinical knowledge resources (FHIR R4, LOINC, UCUM, RxNorm, SNOMED CT, OHDSI) with versioning and cache integrity.

### `GET /api/audit`
Retrieve immutable platform governance audit trail events.
