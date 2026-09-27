# Troubleshooting & Operations Guide

## Common Operational Scenarios

### 1. Server Startup Issues

**Error: Port 8000 already in use**
```bash
# Check process listening on port 8000 (Windows PowerShell)
Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess
# Or start on another port:
python -m uvicorn app.main:app --port 8080 --reload
```

**Error: Missing dependencies**
```bash
pip install -r requirements.txt
pip install fastapi uvicorn sqlalchemy python-multipart
```

---

### 2. LLM Provider Connectivity

**Symptom: LLM rate limit or connection timeout**
- The system automatically catches API connection errors and falls back to deterministic local heuristic matching.
- Verify your `.env` configuration:
  ```env
  LLM_PRIMARY_PROVIDER=openrouter
  OPENROUTER_API_KEY=your_key_here
  OPENROUTER_MODEL=meta-llama/llama-3.3-70b-instruct
  ```

---

### 3. Database & Seeding Verification

**Symptom: Missing initial mappings on a clean database**
- The application automatically seeds initial data on startup. If you delete `app.db` or need to manually re-seed:
```bash
python -c "from app.database import engine, Base, SessionLocal; from app.services.seed_service import seed_existing_phase1_data; Base.metadata.create_all(bind=engine); db = SessionLocal(); seed_existing_phase1_data(db); db.close(); print('Re-seed complete.')"
```

---

### 4. Running Automated Tests

Run the full suite (36 tests):
```bash
pytest tests/ -v
```

Run only core Phase 1 intelligence tests:
```bash
pytest tests/test_*.py -k "not api" -v
```

Run only Web API & Integration tests:
```bash
pytest tests/test_api_endpoints.py -v
```
