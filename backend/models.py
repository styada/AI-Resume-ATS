"""Pydantic models for AI-Resume-ATS API."""
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel


class ResumeParseResponse(BaseModel):
    sections: dict[str, str]
    text: str
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    missing_sections: list[str] = []


class ATSScoreRequest(BaseModel):
    resume_text: str
    job_description: str


class ATSScoreBreakdown(BaseModel):
    keyword_match: int
    section_completeness: int
    formatting_compliance: int
    quantified_impact: int


class ATSScoreResponse(BaseModel):
    total_score: int
    breakdown: ATSScoreBreakdown
    matched_keywords: list[str]
    missing_keywords: list[str]
    suggestions: list[str]


PersonalityType = Literal[
    "professional_recruiter",
    "faang_hiring_manager",
    "startup_founder",
    "blunt_reviewer",
    "technical_interviewer",
]


class RoastRequest(BaseModel):
    resume_text: str
    personality: PersonalityType


class CritiqueItem(BaseModel):
    quote: str
    why: str
    psychology: str
    rewrite: str
    severity: Literal["advisory", "significant", "critical"]


class RoastResponse(BaseModel):
    personality: str
    critiques: list[CritiqueItem]
