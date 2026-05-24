# CONTEXT.md — Current Codebase State
Last updated: Sprint 1 kickoff by Hermes

## Entry Points
- Backend: backend/main.py (FastAPI app)
- Frontend: frontend/src/App.tsx
- Tests: cd backend && pytest
- Dev server: cd backend && uvicorn main:app --reload | cd frontend && npm run dev

## API Routes (as of Sprint 1 start)
- POST /api/parse-resume — upload PDF/DOCX, returns parsed sections + text
- POST /api/ats-score   — resume_text + job_description → score breakdown
- POST /api/roast       — resume_text + personality → streaming SSE critiques

## Data Models
See backend/models.py (Pydantic)
- ResumeParseResponse: sections, text, name, email, contact, missing_sections
- ATSScoreRequest/Response: total_score, breakdown, matched_keywords, missing_keywords, suggestions
- RoastRequest/Response: personality (5 options), critiques list with quote/why/psychology/rewrite/severity

## Change Log
### Sprint 1 kickoff — Hermes
- Repo cloned, dev branch created, 4 feature branches created
- SPEC.md written (full product spec with 10 sections)
- AGENTS.md written (team context, git flow, coding standards)
- CONTEXT.md initialized
- .sprint/state.json initialized with 4 stories
