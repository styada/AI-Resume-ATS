"""Backend tests for AI-Resume-ATS."""
import pytest
from fastapi.testclient import TestClient
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


# ---------------------------------------------------------------------------
# ATS Score
# ---------------------------------------------------------------------------

def test_ats_score_returns_result():
    resume = (
        "John Doe\njohn@example.com\n\n"
        "Summary\nSenior Python developer with 8 years of experience.\n\n"
        "Experience\n- Led Python API development for 200k daily users\n"
        "- Reduced latency by 40% via Redis caching\n\n"
        "Skills\nPython, FastAPI, SQL, Docker, Kubernetes\n\n"
        "Education\nBS Computer Science, MIT 2016"
    )
    jd = "Looking for a Python developer with FastAPI and Docker experience."

    resp = client.post("/api/ats-score", json={"resume_text": resume, "job_description": jd})
    assert resp.status_code == 200

    data = resp.json()
    assert "total_score" in data
    assert 0 <= data["total_score"] <= 100
    assert "breakdown" in data
    assert "matched_keywords" in data
    assert "missing_keywords" in data
    assert "suggestions" in data


def test_ats_score_empty_resume():
    resp = client.post("/api/ats-score", json={"resume_text": "", "job_description": "Python developer"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_score"] < 30


def test_ats_score_perfect_keyword_match():
    jd = "Requires Python, FastAPI, Docker, Kubernetes, PostgreSQL"
    resume = (
        "Skills\nPython FastAPI Docker Kubernetes PostgreSQL\n\n"
        "Experience\n- Built Python APIs with FastAPI and Docker\n"
        "- Deployed on Kubernetes with PostgreSQL\n\n"
        "Education\nBS CS"
    )
    resp = client.post("/api/ats-score", json={"resume_text": resume, "job_description": jd})
    assert resp.status_code == 200
    data = resp.json()
    assert data["breakdown"]["keyword_match"] > 20


# ---------------------------------------------------------------------------
# Roast
# ---------------------------------------------------------------------------

def test_roast_rule_based():
    resume = (
        "Jane Smith\n\nExperience\n"
        "- Responsible for project management and team collaboration\n"
        "- Helped with product development\n"
        "- Assisted with customer support\n\n"
        "Education\nBA Business"
    )
    resp = client.post("/api/roast", json={"resume_text": resume, "personality": "blunt_reviewer"})
    assert resp.status_code == 200
    # SSE stream — check content type
    assert "text/event-stream" in resp.headers["content-type"]
    body = resp.text
    assert "data:" in body
    assert '"quote"' in body


def test_roast_all_personalities():
    resume = "Alice\nalice@test.com\n\nExperience\n- Worked on stuff\n\nSkills\nPython"
    personalities = [
        "professional_recruiter", "faang_hiring_manager", "startup_founder",
        "blunt_reviewer", "technical_interviewer",
    ]
    for p in personalities:
        resp = client.post("/api/roast", json={"resume_text": resume, "personality": p})
        assert resp.status_code == 200, f"Failed for personality: {p}"


# ---------------------------------------------------------------------------
# Parse resume endpoint (without real files — unit-level)
# ---------------------------------------------------------------------------

def test_parse_resume_wrong_type():
    resp = client.post(
        "/api/parse-resume",
        files={"file": ("resume.txt", b"plain text", "text/plain")},
    )
    assert resp.status_code == 400


def test_parse_resume_too_large():
    big_bytes = b"%PDF-1.4 " + b"x" * (6 * 1024 * 1024)
    resp = client.post(
        "/api/parse-resume",
        files={"file": ("resume.pdf", big_bytes, "application/pdf")},
    )
    assert resp.status_code == 413
