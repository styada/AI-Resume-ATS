# AGENTS.md — Team Context

## Project
AI Resume ATS Analyzer with Resume Roast Mode — Sprint 1
Repo: https://github.com/styada/AI-Resume-ATS
Stack: Python 3.11 + FastAPI (backend), React 18 + Vite + TypeScript + Tailwind (frontend)

## Roles
- Hermes: orchestrator, approver, git merge authority
- Optimist Principal: pragmatic arch reviews, finds fastest paths
- Skeptic Principal: adversarial reviews, catches security/edge-case issues
- Engineer (STORY-001): backend foundation — FastAPI app, file parsing (PDF/DOCX), Pydantic models
- Engineer (STORY-002): ATS scoring engine — keyword extraction, spaCy NLP, scoring logic
- Engineer (STORY-003): Resume Roast engine — 5 personalities, critique formatting, SSE streaming
- UI Engineer (STORY-UI): React frontend — full UI, dark mode, progressive critique reveal, shareable cards

## Architecture
- See SPEC.md for full product spec (read it before writing a single line)
- See .sprint/adr.md for architecture decisions
- Stateless backend — no database in MVP
- SSE (Server-Sent Events) for streaming roast critiques to frontend
- All AI calls go through roast_engine.py — configurable via env vars

## Git Flow
- main ← dev ← feature/{story_id}-{slug}
- Engineers work ONLY on their assigned branch
- Never push to main or dev directly
- Hermes merges feature → dev after both principals approve
- Hermes merges dev → main after QA passes + tags v1.0.0

## Coding Standards
- Python: PEP8, functions under 40 lines, type hints on all signatures
- TypeScript: strict mode, no any, components under 150 lines
- Error handling on all IO and all HTTP calls
- Every public function/component has a docstring or JSDoc
- Tests in backend/tests/ (pytest) and frontend/src/__tests__/ (vitest)
- No commented-out code in commits

## Communication Protocol
- Read CONTEXT.md before starting — it tracks what's built and where
- Append to CONTEXT.md after completing your story (never overwrite)
- Write your story plan to .sprint/{story_id}_plan.md before coding
- If you find a conflict or blocker, note it in your story plan and continue with best judgment
- All arch decisions go to .sprint/adr.md
