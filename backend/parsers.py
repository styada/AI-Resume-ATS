"""Resume file parsers — PDF, DOCX, section extraction, contact extraction."""
from __future__ import annotations
import io
import re


# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------

def parse_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file.

    Args:
        file_bytes: Raw PDF bytes.

    Returns:
        Extracted plain text.

    Raises:
        ValueError: If the file cannot be parsed as a PDF.
    """
    try:
        import pdfplumber
    except ImportError as e:
        raise ImportError("pdfplumber is required: pip install pdfplumber") from e

    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        return "\n".join(pages).strip()
    except Exception as e:
        raise ValueError(f"Could not parse PDF: {e}") from e


def parse_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX file.

    Args:
        file_bytes: Raw DOCX bytes.

    Returns:
        Extracted plain text.

    Raises:
        ValueError: If the file cannot be parsed as a DOCX.
    """
    try:
        from docx import Document
    except ImportError as e:
        raise ImportError("python-docx is required: pip install python-docx") from e

    try:
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [para.text for para in doc.paragraphs]
        return "\n".join(paragraphs).strip()
    except Exception as e:
        raise ValueError(f"Could not parse DOCX: {e}") from e


# ---------------------------------------------------------------------------
# Section extraction
# ---------------------------------------------------------------------------

SECTION_PATTERNS: dict[str, list[str]] = {
    "Summary": ["summary", "profile", "objective", "about me", "professional summary"],
    "Experience": ["experience", "work history", "employment", "work experience", "professional experience"],
    "Education": ["education", "academic background", "academic history", "degrees"],
    "Skills": ["skills", "technical skills", "core competencies", "expertise", "technologies"],
    "Projects": ["projects", "personal projects", "key projects", "notable projects"],
    "Certifications": ["certifications", "certificates", "awards", "honors", "publications"],
}


def extract_sections(text: str) -> dict[str, str]:
    """Detect resume sections from raw text.

    Args:
        text: Plain text resume.

    Returns:
        Dict mapping section name to section content.
    """
    if not text.strip():
        return {}

    lines = text.split("\n")
    sections: dict[str, str] = {}
    current_section: str | None = None
    current_lines: list[str] = []

    def flush():
        if current_section:
            sections[current_section] = "\n".join(current_lines).strip()

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current_section:
                current_lines.append(line)
            continue

        # Detect heading: all-caps, or matches known section name, or short line ending with colon
        normalized = stripped.lower().rstrip(":")
        matched_section = None
        for section_name, aliases in SECTION_PATTERNS.items():
            if normalized in aliases or normalized == section_name.lower():
                matched_section = section_name
                break
            # Also check all-caps short lines
            if stripped.isupper() and len(stripped) < 40:
                for alias in aliases:
                    if alias in normalized:
                        matched_section = section_name
                        break

        if matched_section:
            flush()
            current_section = matched_section
            current_lines = []
        else:
            current_lines.append(line)

    flush()
    return sections


# ---------------------------------------------------------------------------
# Contact extraction
# ---------------------------------------------------------------------------

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[a-z]{2,}", re.IGNORECASE)
PHONE_RE = re.compile(
    r"(?:\+?1[-.\s]?)?"
    r"(?:\(?\d{3}\)?[-.\s]?)?"
    r"\d{3}[-.\s]?\d{4}"
)
LINKEDIN_RE = re.compile(r"linkedin\.com/in/[\w-]+", re.IGNORECASE)


def extract_contact(text: str) -> dict[str, str | None]:
    """Extract contact information from resume text.

    Args:
        text: Plain text resume.

    Returns:
        Dict with keys: name, email, phone, linkedin (values may be None).
    """
    email_match = EMAIL_RE.search(text)
    phone_match = PHONE_RE.search(text)
    linkedin_match = LINKEDIN_RE.search(text)

    # Heuristic: name is likely the first non-empty line that looks like a name
    name = None
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        # Skip if it looks like an email, URL, or is all-caps (section header)
        if "@" in stripped or "http" in stripped.lower() or stripped.isupper():
            continue
        # Name: 2-4 words, mostly alphabetic
        words = stripped.split()
        if 1 < len(words) <= 5 and all(w.replace("-", "").replace("'", "").isalpha() for w in words):
            name = stripped
            break

    return {
        "name": name,
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0) if phone_match else None,
        "linkedin": linkedin_match.group(0) if linkedin_match else None,
    }


# ---------------------------------------------------------------------------
# Missing section detection
# ---------------------------------------------------------------------------

REQUIRED_SECTIONS = {"Experience", "Education", "Skills"}
RECOMMENDED_SECTIONS = {"Summary"}


def detect_missing_sections(sections: dict[str, str]) -> list[str]:
    """Report which required and recommended sections are absent.

    Args:
        sections: Dict of detected sections from extract_sections().

    Returns:
        List of missing section names (required first, then recommended).
    """
    missing: list[str] = []
    for req in sorted(REQUIRED_SECTIONS):
        if req not in sections:
            missing.append(req)
    for rec in sorted(RECOMMENDED_SECTIONS):
        if rec not in sections:
            missing.append(f"{rec} (recommended)")
    return missing
