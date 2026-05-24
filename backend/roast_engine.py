"""Resume Roast engine — 5 reviewer personalities, SSE streaming, rule-based fallback."""
from __future__ import annotations
import json
import os
import re
import time
from typing import Generator

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Personality system prompts
# ---------------------------------------------------------------------------

SYSTEM_PROMPTS: dict[str, str] = {
    "professional_recruiter": (
        "You are a senior corporate recruiter with 15 years of experience at Fortune 500 companies. "
        "You speak in professional, direct language. You focus on market positioning, career narrative, "
        "and whether this candidate can clear an ATS before a human sees them. You are helpful but unsparing."
    ),
    "faang_hiring_manager": (
        "You are a Staff+ Engineering hiring manager at a major tech company (FAANG level). "
        "You care deeply about scope, scale, ownership, and measurable impact. You calibrate "
        "experience to levels (L3/L4/L5/L6). You're skeptical of vague claims and reward specificity."
    ),
    "startup_founder": (
        "You are a technical founder who has hired 50+ engineers at early-stage startups. "
        "You speed-read resumes in 30 seconds. You look for evidence of building, shipping, owning. "
        "You are blunt, informal, and allergic to corporate-speak. You respect hustle."
    ),
    "blunt_reviewer": (
        "You are the most honest person this candidate has ever met. You say exactly what you think. "
        "No softening, no corporate politeness. You call out every weak phrase, every vague claim, "
        "every missed opportunity. You are not cruel — you are surgical."
    ),
    "technical_interviewer": (
        "You are a principal engineer conducting a technical screen. You evaluate every technical "
        "claim for specificity, depth, and credibility. 'Built a distributed system' means nothing "
        "to you without scale, architecture, and your role in it. You probe ambiguity ruthlessly."
    ),
}

# ---------------------------------------------------------------------------
# Rule-based critique patterns
# ---------------------------------------------------------------------------

WEAK_VERBS = [
    "responsible for", "helped", "assisted with", "worked on", "involved in",
    "participated in", "contributed to", "supported", "aided", "collaborated on",
]

BUZZWORDS = [
    "synergy", "leverage", "leveraged", "spearhead", "spearheaded", "dynamic",
    "results-driven", "team player", "hardworking", "go-getter", "thought leader",
    "proactive", "self-starter", "detail-oriented", "passionate about",
]

VAGUE_IMPACT_RE = re.compile(
    r"\b(improved|increased|reduced|enhanced|optimized|streamlined|boosted|drove)\s+"
    r"(?!by\s*\d|[\d%$])\w+",
    re.IGNORECASE,
)

BULLET_LINE_RE = re.compile(r"^\s*[-•*◦▪▸]\s*|^\s*\d+\.\s+", re.MULTILINE)
METRIC_RE = re.compile(r"\d+[%$kKmMbB+]?|\$\d|million|billion|thousand|\d+x\b", re.IGNORECASE)


def _make_critique(quote: str, why: str, psychology: str, rewrite: str,
                   severity: str) -> dict:
    return {"quote": quote, "why": why, "psychology": psychology,
            "rewrite": rewrite, "severity": severity}


def _rule_based_critiques(resume_text: str) -> list[dict]:
    """Generate deterministic critiques from resume text patterns."""
    critiques: list[dict] = []
    text_lower = resume_text.lower()

    # 1. Weak verbs
    for verb in WEAK_VERBS:
        if verb in text_lower:
            idx = text_lower.find(verb)
            snippet = resume_text[max(0, idx - 10): idx + len(verb) + 40].strip()
            critiques.append(_make_critique(
                quote=snippet,
                why=f"'{verb}' is passive and ownership-free. It signals you were present, not accountable.",
                psychology="Recruiters read this as 'did the minimum.' It suggests you take no credit "
                           "and likely had no real impact.",
                rewrite=f"Replace with a strong ownership verb: Led, Built, Owned, Delivered, Drove, "
                        f"Architected — then add the outcome with numbers.",
                severity="significant",
            ))

    # 2. Missing metrics (critical if > 60% of bullets have none)
    bullet_lines = [l.strip() for l in resume_text.split("\n")
                    if BULLET_LINE_RE.match(l)]
    if bullet_lines:
        unquantified = [b for b in bullet_lines if not METRIC_RE.search(b)]
        ratio = len(unquantified) / len(bullet_lines)
        if ratio > 0.6:
            critiques.append(_make_critique(
                quote=unquantified[0] if unquantified else "(multiple bullets)",
                why=f"{int(ratio*100)}% of your bullets contain no numbers. "
                    "Metrics are the only objective signal of scale and impact.",
                psychology="Without numbers, claims are indistinguishable from every other candidate. "
                           "A hiring manager cannot tell if you built something used by 10 people or 10 million.",
                rewrite="Add: how many users? what % improvement? what revenue impact? "
                        "Even rough estimates (50+ engineers, ~$2M pipeline) are better than nothing.",
                severity="critical",
            ))

    # 3. Buzzwords
    for word in BUZZWORDS:
        if word in text_lower:
            critiques.append(_make_critique(
                quote=word,
                why=f"'{word}' is filler. Every candidate uses it. It adds zero signal.",
                psychology="Experienced reviewers skip these words entirely. They're pattern-matched "
                           "as noise after reading thousands of resumes.",
                rewrite=f"Delete '{word}' and replace with a specific, concrete action or outcome.",
                severity="advisory",
            ))
            break  # One buzzword critique is enough

    # 4. Vague impact
    match = VAGUE_IMPACT_RE.search(resume_text)
    if match:
        critiques.append(_make_critique(
            quote=match.group(0),
            why="You claim an impact but provide no evidence of its magnitude.",
            psychology="'Improved performance' could mean 1% faster or 10x faster. Without the number, "
                       "it reads as the former. Vague claims invite skepticism, not benefit of the doubt.",
            rewrite=f"'{match.group(0)}' → 'Improved [metric] by [X]% by [method], resulting in [outcome]'",
            severity="significant",
        ))

    # 5. No summary/profile section
    has_summary = any(kw in text_lower for kw in ["summary", "profile", "objective"])
    if not has_summary:
        critiques.append(_make_critique(
            quote="(No summary section found)",
            why="A summary section is the only place you control the narrative. Without it, "
                "the recruiter forms their own (often wrong) impression from job titles alone.",
            psychology="Recruiters spend 6 seconds on first pass. A missing summary forces them to "
                       "do interpretation work. Most won't.",
            rewrite="Add a 2-3 sentence summary: who you are, your level, your domain expertise, "
                    "and your most impressive credential or outcome.",
            severity="significant",
        ))

    # 6. Short bullets
    short_bullets = [b for b in bullet_lines if len(b.split()) < 8]
    if len(short_bullets) >= 2:
        critiques.append(_make_critique(
            quote=short_bullets[0],
            why="Bullets this short cannot convey scope, method, or impact.",
            psychology="Short bullets read as either inexperienced (nothing to show) or lazy "
                       "(couldn't be bothered to explain). Either interpretation hurts you.",
            rewrite="Expand to: [Action verb] [what you built/owned] [for whom/at what scale] "
                    "[with what result/metric].",
            severity="advisory",
        ))

    return critiques


# ---------------------------------------------------------------------------
# SSE stream generator
# ---------------------------------------------------------------------------

def stream_roast(resume_text: str, personality: str) -> Generator[str, None, None]:
    """Stream resume critique items as SSE events.

    Tries AI mode first (if OPENAI_API_BASE is configured), falls back to
    rule-based mode.

    Args:
        resume_text: Plain text of the resume.
        personality: One of the 5 reviewer personality keys.

    Yields:
        SSE-formatted strings: 'data: {json}\\n\\n'
        Final item: 'data: {"done": true}\\n\\n'
    """
    api_base = os.getenv("OPENAI_API_BASE", "")
    api_key = os.getenv("OPENAI_API_KEY", "")

    if api_base and api_key:
        yield from _ai_stream(resume_text, personality, api_base, api_key)
    else:
        yield from _rule_stream(resume_text, personality)


def _rule_stream(resume_text: str, personality: str) -> Generator[str, None, None]:
    """Rule-based roast with simulated streaming delay."""
    critiques = _rule_based_critiques(resume_text)
    if not critiques:
        critiques = [_make_critique(
            quote="(Resume text provided)",
            why="Could not identify specific issues — the resume may be very short or incomplete.",
            psychology="A too-brief resume signals either inexperience or lack of effort in the application.",
            rewrite="Expand your resume to at least one full page with concrete experience, skills, and education.",
            severity="advisory",
        )]

    for critique in critiques:
        yield f"data: {json.dumps(critique)}\n\n"
        time.sleep(0.3)

    yield 'data: {"done": true}\n\n'


def _ai_stream(resume_text: str, personality: str,
               api_base: str, api_key: str) -> Generator[str, None, None]:
    """AI-powered roast via OpenAI-compatible API."""
    try:
        from openai import OpenAI

        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        client = OpenAI(api_key=api_key, base_url=api_base)
        system_prompt = SYSTEM_PROMPTS.get(personality, SYSTEM_PROMPTS["blunt_reviewer"])

        user_prompt = (
            "Review the following resume and return a JSON array of critique objects. "
            "Each object must have exactly these keys: quote, why, psychology, rewrite, severity. "
            "severity must be one of: advisory, significant, critical. "
            "Return ONLY valid JSON — no markdown, no explanation, just the array.\n\n"
            f"RESUME:\n{resume_text}"
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
        )

        content = response.choices[0].message.content or "[]"
        # Strip markdown code fences if present
        content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip())
        critiques = json.loads(content)

        for critique in critiques:
            # Validate required fields
            if all(k in critique for k in ("quote", "why", "psychology", "rewrite", "severity")):
                if critique["severity"] not in ("advisory", "significant", "critical"):
                    critique["severity"] = "significant"
                yield f"data: {json.dumps(critique)}\n\n"
                time.sleep(0.2)

        yield 'data: {"done": true}\n\n'

    except Exception:
        # Fallback to rule-based on any AI failure
        yield from _rule_stream(resume_text, personality)
