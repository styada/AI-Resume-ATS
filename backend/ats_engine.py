"""ATS scoring engine — keyword matching, section completeness, formatting, impact."""
from __future__ import annotations
import re

# ---------------------------------------------------------------------------
# Stopwords for keyword filtering
# ---------------------------------------------------------------------------
STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "must", "we", "our",
    "you", "your", "their", "this", "that", "these", "those", "it", "its",
    "as", "if", "than", "so", "yet", "both", "either", "not", "only",
    "own", "same", "too", "very", "just", "also", "well", "new", "other",
    "such", "no", "up", "out", "about", "into", "through", "during",
    "before", "after", "above", "below", "between", "each", "more",
    "most", "under", "again", "further", "then", "once",
}

# Patterns that indicate a skill/requirement boundary in JD
SKILL_TRIGGERS = re.compile(
    r"(?:required?|prefer(?:red)?|experience (?:with|in)|"
    r"proficien(?:t|cy) (?:in|with)|knowledge of|familiarity with|"
    r"expertise in|background in|ability to|strong (?:in|with))",
    re.IGNORECASE,
)

METRIC_RE = re.compile(
    r"\d+[%$kKmMbB+]?|\$\d|million|billion|thousand|\d+x\b|[0-9]+",
    re.IGNORECASE,
)

BULLET_RE = re.compile(r"^[\s]*[-•*◦▪▸]|\d+\.\s", re.MULTILINE)


def _extract_keywords(text: str) -> list[str]:
    """Extract meaningful keywords from text using regex + stopword filter."""
    tokens = re.findall(r"\b[a-zA-Z][a-zA-Z0-9.#+\-/]{1,40}\b", text)
    seen: set[str] = set()
    keywords: list[str] = []
    for tok in tokens:
        lower = tok.lower()
        if lower in STOPWORDS or len(lower) < 3:
            continue
        if lower not in seen:
            seen.add(lower)
            keywords.append(tok)
    return keywords


def _match_keywords(jd_keywords: list[str], resume_text: str) -> tuple[list[str], list[str]]:
    """Return (matched, missing) from JD keywords against resume text."""
    resume_lower = resume_text.lower()
    matched: list[str] = []
    missing: list[str] = []
    for kw in jd_keywords:
        # Case-insensitive, allow partial: 'Python' matches 'Python3', 'python3.9'
        pattern = re.compile(r"\b" + re.escape(kw.lower()), re.IGNORECASE)
        if pattern.search(resume_lower):
            matched.append(kw)
        else:
            missing.append(kw)
    return matched, missing


def _section_score(resume_text: str) -> tuple[int, list[str]]:
    """Score section completeness (0-20) and return list of missing sections."""
    text_lower = resume_text.lower()
    sections = {
        "Experience": ["experience", "work history", "employment"],
        "Education": ["education", "academic"],
        "Skills": ["skills", "expertise", "competencies", "technologies"],
        "Summary": ["summary", "profile", "objective"],
    }
    found: set[str] = set()
    for name, aliases in sections.items():
        if any(alias in text_lower for alias in aliases):
            found.add(name)

    score = 0
    missing: list[str] = []
    for name in ["Experience", "Education", "Skills"]:
        if name in found:
            score += 6
        else:
            missing.append(name)
    if "Summary" in found:
        score += 2  # bonus
    return min(score, 20), missing


def _formatting_score(resume_text: str) -> int:
    """Heuristic formatting compliance score (0-20)."""
    score = 20
    lines = resume_text.split("\n")

    # Check for weird unicode bullets (not -, *, •)
    weird_chars = sum(1 for c in resume_text if ord(c) > 127 and c not in "•–—…''""é")
    if weird_chars > 10:
        score -= 5

    # Very long lines suggest table layout
    long_lines = sum(1 for l in lines if len(l) > 200)
    if long_lines > 3:
        score -= 5

    # No whitespace between sections (wall of text)
    if resume_text.count("\n\n") < 3 and len(resume_text) > 500:
        score -= 5

    # Whole paragraphs in ALL CAPS
    allcaps_paras = sum(1 for l in lines if l.strip().isupper() and len(l.strip()) > 30)
    if allcaps_paras > 2:
        score -= 5

    return max(score, 0)


def _quantified_impact_score(resume_text: str) -> int:
    """Score quantified impact (0-20) based on metrics in bullet points."""
    bullets = BULLET_RE.findall(resume_text)
    # Collect bullet point lines
    bullet_lines: list[str] = []
    for line in resume_text.split("\n"):
        stripped = line.strip()
        if BULLET_RE.match(stripped):
            bullet_lines.append(stripped)

    if not bullet_lines:
        return 5  # can't fully evaluate

    quantified = sum(1 for b in bullet_lines if METRIC_RE.search(b))
    ratio = quantified / len(bullet_lines)
    return min(int(ratio * 20), 20)


def _generate_suggestions(
    keyword_score: int,
    section_score: int,
    formatting_score: int,
    impact_score: int,
    missing_keywords: list[str],
    missing_sections: list[str],
) -> list[str]:
    """Generate up to 5 ranked, actionable suggestions."""
    suggestions: list[str] = []

    if missing_sections:
        for s in missing_sections[:2]:
            suggestions.append(f"Add a {s} section — ATS systems expect it and penalise its absence.")

    if keyword_score < 20 and missing_keywords:
        top = missing_keywords[:5]
        suggestions.append(
            f"Add these missing skills to your Skills section: {', '.join(top)}."
        )

    if impact_score < 10:
        suggestions.append(
            "Quantify your bullet points. Aim for 70%+ to include numbers, percentages, or scale."
        )

    if formatting_score < 15:
        suggestions.append(
            "Simplify formatting — avoid tables, multiple columns, and special Unicode characters."
        )

    if missing_keywords:
        suggestions.append(
            f"Highest-impact missing keyword to add: '{missing_keywords[0]}'."
        )

    return suggestions[:5]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def score_resume(resume_text: str, job_description: str) -> dict:
    """Score a resume against a job description.

    Args:
        resume_text: Plain text of the resume.
        job_description: Plain text of the job description.

    Returns:
        Dict matching ATSScoreResponse schema.
    """
    jd_keywords = _extract_keywords(job_description)
    matched, missing = _match_keywords(jd_keywords, resume_text)

    keyword_score = min(int((len(matched) / max(len(jd_keywords), 1)) * 40), 40)
    section_score, missing_sections = _section_score(resume_text)
    formatting_score = _formatting_score(resume_text)
    impact_score = _quantified_impact_score(resume_text)

    total = keyword_score + section_score + formatting_score + impact_score

    suggestions = _generate_suggestions(
        keyword_score, section_score, formatting_score, impact_score,
        missing[:15], missing_sections,
    )

    return {
        "total_score": total,
        "breakdown": {
            "keyword_match": keyword_score,
            "section_completeness": section_score,
            "formatting_compliance": formatting_score,
            "quantified_impact": impact_score,
        },
        "matched_keywords": matched,
        "missing_keywords": missing[:15],
        "suggestions": suggestions,
    }
