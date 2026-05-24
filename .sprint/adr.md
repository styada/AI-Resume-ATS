# Architecture Decision Record — Sprint 1

## ADR-001: Stateless backend, no database for MVP
Decision: No database. Resume text is passed in request body. No persistence.
Rationale: MVP scope. Eliminates auth, migrations, infrastructure. Can add later.
Consequences: No history. That's fine — localStorage in v2 frontend.

## ADR-002: SSE for streaming roast critiques
Decision: POST /api/roast returns Server-Sent Events stream, not a single JSON blob.
Rationale: Critiques are generated one at a time. SSE enables progressive UI appearance
without polling. Frontend reads the stream and appends cards as they arrive.
Implementation: FastAPI StreamingResponse with media_type="text/event-stream".

## ADR-003: spaCy for NLP keyword extraction, not paid APIs
Decision: spaCy (en_core_web_sm) for NER and keyword extraction from job descriptions.
No OpenAI calls for ATS scoring — purely local NLP.
Rationale: ATS scoring is deterministic and rule-based. No need for expensive LLM calls.
Saving AI budget for the roast engine where personality matters.

## ADR-004: AI critique calls are configurable via env vars
Decision: roast_engine.py uses OPENAI_API_BASE + OPENAI_API_KEY + OPENAI_MODEL env vars.
Default to a sensible free-tier endpoint. If env is not set, use rule-based fallback critiques.
Rationale: Don't break if no AI key is configured. Fallback ensures the app always works.

## ADR-005: React 18 + Vite + TypeScript + Tailwind
Decision: Frontend uses Vite for fast builds, Tailwind for utility-first styling,
TypeScript strict mode for correctness.
Rationale: Fast setup, modern DX, Tailwind eliminates CSS file proliferation.
No Next.js — overkill for a single-page tool with a local backend.

## ADR-006: html2canvas for shareable card export
Decision: Each critique card can be exported as PNG via html2canvas.
The card is a styled hidden DOM element that gets captured.
Rationale: No server-side rendering needed. Client-side only. Zero infra cost.

## ADR-007: File structure is backend/ + frontend/ at repo root
See SPEC.md section 8 for full directory tree. Engineers must follow it exactly.
