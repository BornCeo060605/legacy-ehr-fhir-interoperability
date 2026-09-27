# Security & Healthcare Data Governance

## Healthcare Data Handling Principles

### 1. Protection of Protected Health Information (PHI)
- **Local-First Processing**: The application executes schema profiling, relationship analysis, and vector retrieval on the local host.
- **Metadata-Only Reasoning**: The intelligence pipeline reason primarily over schema metadata, column naming conventions, physical constraints, and data type profiles. Raw patient-level data is never sent to external LLMs.
- **No Patient Data Logging**: Application logs record column names and profiling metrics, never patient row contents or identifiers.

### 2. API Key Isolation
- All external API credentials (`OPENROUTER_API_KEY`, `GROQ_API_KEY`, `GEMINI_API_KEY`) are managed strictly through server-side environment variables (`.env`).
- API keys are never bundled, transmitted, or accessible via the client-side Single Page Application.

### 3. File Upload Safety
- Files uploaded via `/api/databases/upload` undergo strict validation:
  - Extension whitelist: `.sqlite`, `.db`, `.db3`.
  - Secure filename sanitization (`os.path.basename`) preventing directory traversal attacks.
  - Verification of valid SQLite header bytes (`SQLite format 3\000`).
  - Cryptographic SHA-256 fingerprint computed upon upload for non-repudiation.

### 4. Immutable Clinical Audit Trail
- Regulatory healthcare compliance requires that machine suggestions and human approvals are auditable.
- Every project creation, database import, pipeline run, and clinical review sign-off is logged in the `audit_events` table with:
  - Event type identifier
  - Description and JSON context payload
  - Acting user/role
  - UTC ISO-8601 timestamp
