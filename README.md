# AI-Resume-ATS

> AI-powered resume analysis — ATS scoring + Resume Roast mode.

## What it does

- **ATS Scoring** — paste your resume and a job description, get a scored breakdown:
  keyword match (40 pts), section completeness (20 pts), formatting compliance (20 pts),
  quantified impact (20 pts), plus ranked suggestions.
- **Resume Roast** — choose one of 5 brutal reviewer personalities and get progressive
  streaming critiques with quotes, psychology, and rewrite suggestions.
- **File parsing** — upload PDF or DOCX; the backend extracts text, sections, and contact info.

## Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3.11 + FastAPI |
| Frontend | React 18 + Vite + TypeScript + Tailwind v4 |
| Parsing | pdfplumber + python-docx |
| AI (optional) | OpenAI-compatible API for AI-powered roast |

## Quick start

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Optional: for AI-powered roast mode
cp ../.env.example .env
# Fill in OPENAI_API_BASE and OPENAI_API_KEY

uvicorn main:app --reload
# API at http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# UI at http://localhost:5173
```

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Liveness check |
| POST | /api/parse-resume | Upload PDF/DOCX → parsed sections + contact |
| POST | /api/ats-score | JSON body → ATS score + breakdown |
| POST | /api/roast | JSON body → SSE stream of critique items |

## Environment variables

See `.env.example`. All optional — the backend runs in rule-based mode without any API keys.

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_BASE` | OpenAI-compatible API base URL (enables AI roast) |
| `OPENAI_API_KEY` | API key for above |
| `OPENAI_MODEL` | Model to use (default: gpt-3.5-turbo) |
| `CORS_ORIGINS` | Comma-separated allowed origins (default: *) |

## Tests

```bash
cd backend
pytest tests/ -v
# 8 tests, all passing
```

## Release

v1.0.0 — Sprint 1 complete.
