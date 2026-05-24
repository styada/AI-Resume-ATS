# AI-Resume-ATS

AI-powered resume analyzer with ATS scoring and a "Resume Roast" mode for blunt feedback.

## Features

- Upload PDF or DOCX resumes
- ATS keyword scoring against any job description
- Resume Roast mode — 5 reviewer personalities streaming live critiques
- Dark-mode React UI with progressive critique reveal

## Quick Start

### 1. Clone & configure

```bash
git clone git@github.com:styada/AI-Resume-ATS.git
cd AI-Resume-ATS
cp .env.example .env
# Edit .env — set OPENAI_API_BASE, OPENAI_API_KEY, OPENAI_MODEL
```

### 2. Run the backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn main:app --reload --port 8000
```

Backend runs at http://localhost:8000

### 3. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:5173. API calls are proxied to the backend automatically.

### 4. Build for production

```bash
cd frontend
npm run build
# Serve the dist/ folder from your backend or any static host
```

## Stack

- **Backend**: Python 3.11, FastAPI, pdfplumber, python-docx, spaCy, OpenAI-compatible API
- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS v4

## Environment Variables

See `.env.example` for all required variables.
