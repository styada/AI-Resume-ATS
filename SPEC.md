# AI Resume ATS — Full Product Specification
Version: 1.0.0 | Sprint 1

---

## 1. Feature Overview

AI Resume ATS is a web application that analyzes resumes against job descriptions using
ATS (Applicant Tracking System) scoring logic, and optionally roasts them via a brutally
honest critique engine with five distinct reviewer personalities.

The product has two core modes:

**ATS Score Mode** — Upload a resume, paste a job description, receive a structured
match score: keyword overlap, section completeness, formatting compliance, and
a final ATS compatibility percentage. Output is structured, actionable, and
exportable.

**Resume Roast Mode** — The same resume is fed to a critique engine that behaves like
a senior industry reviewer. The critique is designed to be high-signal, memorable,
and shareable. Not humiliation — surgical honesty with a personality.

---

## 2. Purpose

Most resume feedback is either too generic to act on ("use strong action verbs") or
too expensive to access (career coaches, paid services). ATS scanners exist but they
are dry, opaque, and don't explain *why* something fails.

This product bridges both gaps: it gives users the mechanical ATS truth AND the
human-readable critique in one place, for free, with personality.

The Resume Roast feature is also intentionally designed as a **viral acquisition mechanic**.
Shareable critique cards distributed on social media drive organic growth at zero cost.

---

## 3. User Problem

Job seekers submit resumes that never get seen by humans because:
- ATS filters reject them for keyword mismatches or formatting failures
- Vague impact statements read as filler to experienced recruiters
- Weak verbs and missing metrics signal junior-level thinking even for senior candidates
- They have no affordable way to get honest, specific feedback

This product solves all three: ATS mechanical scoring + human-quality critique +
shareable output that turns their moment of vulnerability into social proof.

---

## 4. Product Philosophy

**For ATS Mode:** Clarity over cleverness. The user needs to understand exactly why
their resume scored 67% and exactly what to change to get to 85%. Every data point
must map to a concrete, actionable fix. No vanity metrics.

**For Roast Mode:** The experience should feel like the most useful, slightly-uncomfortable
conversation you've ever had with a brilliant, blunt senior colleague. Not a meme.
Not cruelty. Surgical honesty delivered with voice and memorability.

The UI should feel like a live review — critiques appear progressively as if someone
is actively reading the document. The emotional arc goes: "this is slightly painful"
→ "okay this is actually right" → "I'm saving this and fixing it tonight."

The shareable cards are the product's distribution engine. They should look polished
enough that sharing them is a flex, not an embarrassment.

---

## 5. Functional Requirements

### Resume Parsing
- Accept PDF and DOCX resume uploads (max 5MB)
- Extract: name, email, phone, LinkedIn URL, sections (Summary, Experience, Education,
  Skills, Projects, Certifications), full plain text
- Detect and flag missing standard sections
- Normalize whitespace, remove headers/footers artifacts

### ATS Scoring Engine
- Accept a job description (pasted text, min 50 words)
- Extract required keywords from JD: skills, tools, job titles, qualifications
- Score resume on:
  - Keyword match rate (0-40 points): what % of JD keywords appear in resume
  - Section completeness (0-20 points): presence of required sections
  - Formatting compliance (0-20 points): no tables, no text boxes, standard fonts, no images
  - Quantified impact (0-20 points): % of bullet points containing numbers/metrics
- Return: total score (0-100), breakdown per category, list of missing keywords,
  list of matched keywords, top 5 improvement suggestions

### Resume Roast Engine
- Accept parsed resume text + selected reviewer personality
- Five personalities:
  - **Professional Recruiter**: Corporate tone, focuses on positioning and market fit
  - **FAANG Hiring Manager**: Technical bar, impact metrics, level calibration
  - **Startup Founder**: Speed-reads for signal, pattern-matches on builder evidence
  - **Blunt Reviewer**: Cuts through noise, calls out every weak phrase directly
  - **Technical Interviewer**: Focuses on specificity, depth, and credibility of technical claims
- Each personality issues critiques that identify:
  - Vague impact statements ("helped improve performance" without numbers)
  - Weak action verbs (managed, assisted, worked on, helped)
  - Missing measurable outcomes on every experience bullet
  - Excessive buzzword density (synergy, leveraged, spearheaded)
  - Junior-level framing on senior roles
  - Narrative inconsistency (job titles vs. responsibilities don't align)
  - Technical ambiguity (claims "built a system" without architecture, scale, or stack)
- Each critique includes:
  - The problematic text (quoted directly)
  - Why this weakens the candidate
  - How recruiters/managers psychologically interpret it
  - A suggested rewrite

### Shareability
- Each critique card is exportable as a styled PNG (dark card, personality badge,
  critique text, suggested rewrite, branding watermark)
- "Share your roast" CTA with pre-filled social copy
- Export full ATS report as PDF

---

## 6. Behavioral Requirements

### AI Critique Behavior
- Never produce generic advice that applies to every resume equally
- Every critique must quote directly from the resume — no paraphrasing that loses specificity
- Rewrites must be concrete and adoptable — not abstract templates
- Severity must be calibrated: not everything is a crisis, not everything is fine
- Personality must be consistent throughout — don't switch tone mid-review
- If a section is genuinely strong, say so briefly — credibility requires balance
- Critiques should be ordered: most damaging first, stylistic last

### ATS Engine Behavior
- Keyword matching must be semantic-aware: "Python" matches "Python 3", "py", "Python 3.9"
- JD parsing must distinguish required vs. preferred qualifications (different weights)
- Score explanations must be specific: "Missing 8 of 12 required skills: Docker, Kubernetes,
  CI/CD, Terraform..." not "low keyword match"
- Formatting compliance checks are heuristic: flag tables, multi-column layouts,
  text in headers/footers that ATS bots miss
- Never return a score without a ranked list of actions to improve it

### Rate Limiting and Robustness
- Resume upload: validate file type, reject oversized files gracefully
- AI calls: retry on rate limit (3x with exponential backoff), return partial results
  if some personalities fail rather than erroring the whole request
- All user-facing errors must explain what happened and what the user can do

---

## 7. UX/UI Expectations

### Visual Language
- Dark mode as default (dark gray/near-black backgrounds, not pure black)
- Accent: electric blue or amber — must feel premium, not startup-template
- Typography: Inter or similar humanist sans-serif; hierarchy is critical —
  section headers, critique headers, body text, and metadata all at distinct weights
- Cards: rounded corners (8px), subtle drop shadows, clear visual separation

### Resume Roast UI — Interaction Model
- Critiques appear progressively after upload, not all at once (simulates live reading)
- Each critique appears as an animated card entry (slide-in from right, 200ms)
- Severity indicator: subtle left-border color (blue = advisory, amber = significant, red = critical)
- Reviewer personality selector: tabs or segmented control at top, switching personality
  re-triggers the progressive appearance animation on new critiques
- Each critique card has: quote, explanation, rewrite, severity badge, share icon
- "Share this critique" opens a preview of the exportable card with download + copy options

### ATS Score UI
- Score displayed as a large circular progress ring (0-100) with color coding:
  0-49 red, 50-74 amber, 75-100 green
- Breakdown shown as horizontal bars below the ring, one per category
- Missing keywords shown as red chips, matched keywords as green chips
- Job description input is a textarea that debounces analysis on paste
- Improvement suggestions shown as numbered action items, most impactful first

### States (all required)
- Empty state: welcoming, explains both modes, shows example output (no lorem ipsum)
- Loading state: skeleton cards during analysis, progress indicator with status text
  ("Parsing resume…", "Running ATS analysis…", "Getting your roast ready…")
- Error state: specific message, retry button, does not clear user's uploaded file
- Mobile: single-column layout, personality selector scrolls horizontally

---

## 8. Technical Expectations

### Stack
- Backend: Python 3.11 + FastAPI, deployed with uvicorn
- Resume parsing: pdfplumber (PDF) + python-docx (DOCX)
- NLP/keyword extraction: spaCy (en_core_web_sm) for NLP, no paid APIs
- AI critique generation: OpenAI-compatible API endpoint (configurable via env var)
  — defaults to a local or free-tier compatible endpoint
- Frontend: React 18 + Vite, TypeScript, Tailwind CSS
- Export: html2canvas for card PNG export, jsPDF for report PDF
- No database required for MVP — stateless, session-based

### API Design (REST, JSON)
```
POST /api/parse-resume
  body: multipart form — file (PDF|DOCX)
  returns: { sections, text, name, email, contact, missing_sections }

POST /api/ats-score
  body: { resume_text: str, job_description: str }
  returns: { total_score, breakdown, matched_keywords, missing_keywords, suggestions }

POST /api/roast
  body: { resume_text: str, personality: str }
  returns: { critiques: [{ quote, why, psychology, rewrite, severity }] }
```

### File Structure
```
/
├── backend/
│   ├── main.py              # FastAPI app, CORS, routes
│   ├── parsers.py           # PDF + DOCX parsing
│   ├── ats_engine.py        # ATS scoring logic
│   ├── roast_engine.py      # Critique generation per personality
│   ├── models.py            # Pydantic request/response models
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── ResumeUpload.tsx
│   │   │   ├── ATSScore.tsx
│   │   │   ├── RoastView.tsx
│   │   │   ├── CritiqueCard.tsx
│   │   │   └── ShareCard.tsx
│   │   ├── hooks/
│   │   │   ├── useResumeAnalysis.ts
│   │   │   └── useRoast.ts
│   │   └── api/
│   │       └── client.ts
│   ├── package.json
│   └── vite.config.ts
├── AGENTS.md
├── CONTEXT.md
├── SPEC.md
└── README.md
```

### Environment Variables
```
OPENAI_API_BASE=http://localhost:11434/v1   # or any OpenAI-compatible endpoint
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo                 # or any available model
CORS_ORIGINS=http://localhost:5173
```

### Non-Functional Requirements
- Backend cold start under 3s
- Resume parse under 2s for typical 1-2 page PDF
- ATS score returned under 5s
- Roast generation: stream critiques as they are generated (SSE preferred)
  so the progressive UI feels natural, not like a long wait
- All endpoints return appropriate HTTP status codes with structured error responses

---

## 9. Success Criteria

The sprint is done when:
1. A user can upload a PDF or DOCX resume — it parses without error
2. A user can paste a job description and receive an ATS score with breakdown
3. A user can select any of the 5 personalities and receive a full roast
4. Critiques appear progressively in the UI (not all at once)
5. At least one critique card is exportable as a PNG
6. The UI works on mobile (375px) and desktop (1280px)
7. All loading, empty, and error states are implemented and visible
8. Backend has tests covering parse, ATS score, and roast endpoints
9. Frontend has no console errors on normal paths
10. App starts with `uvicorn backend.main:app` + `npm run dev` in frontend/

---

## 10. Future Expansion

- LinkedIn profile URL ingestion (parse public profile as resume input)
- Multi-resume batch comparison ("which of these 3 resumes is stronger for this role?")
- Job description scraper (paste a LinkedIn/Indeed URL instead of raw text)
- Saved history (browser localStorage first, then optional account)
- Roast leaderboard: anonymized public wall of the most-shared critiques
- Custom personality builder: teams can create a company-specific reviewer voice
- Cover letter roast mode
- Interview question generator from ATS gaps ("these 5 missing keywords will come up — here's how to answer")
