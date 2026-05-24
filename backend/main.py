"""FastAPI application entry point for AI-Resume-ATS."""
from __future__ import annotations
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from models import ATSScoreRequest, RoastRequest, ResumeParseResponse
from parsers import detect_missing_sections, extract_contact, extract_sections, parse_docx, parse_pdf
from ats_engine import score_resume
from roast_engine import stream_roast

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_EXTENSIONS = {".pdf", ".docx"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="AI-Resume-ATS API",
    version="1.0.0",
    description="ATS scoring and resume roast backend.",
    lifespan=lifespan,
)

_raw_origins = os.getenv("CORS_ORIGINS", "*")
cors_origins = ["*"] if _raw_origins.strip() == "*" else [o.strip() for o in _raw_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=cors_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc), "status_code": 500},
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/parse-resume", response_model=ResumeParseResponse)
async def parse_resume(file: UploadFile = File(...)) -> ResumeParseResponse:
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type '{ext}'. Upload a PDF or DOCX.")

    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File exceeds the 5 MB size limit.")

    try:
        text = parse_pdf(file_bytes) if ext == ".pdf" else parse_docx(file_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    sections = extract_sections(text)
    contact = extract_contact(text)
    missing = detect_missing_sections(sections)

    return ResumeParseResponse(
        sections=sections,
        text=text,
        name=contact.get("name"),
        email=contact.get("email"),
        phone=contact.get("phone"),
        linkedin=contact.get("linkedin"),
        missing_sections=missing,
    )


@app.post("/api/ats-score")
async def ats_score(request: ATSScoreRequest):
    result = score_resume(request.resume_text, request.job_description)
    return result


@app.post("/api/roast")
async def roast(request: RoastRequest):
    def event_stream():
        for chunk in stream_roast(request.resume_text, request.personality):
            yield chunk

    return StreamingResponse(event_stream(), media_type="text/event-stream")
