"""Utilities for extracting resume context via Mistral OCR."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Tuple

from mistralai import Mistral
from mistralai.models import DocumentURLChunk


@dataclass(frozen=True)
class ResumeContext:
    markdown: str
    pages_processed: int


class ResumeOCRError(RuntimeError):
    """Raised when resume OCR extraction fails."""


def extract_resume_context(mistral_api_key: str, resume_path: str) -> ResumeContext:
    """Run Mistral OCR over the resume and return markdown plus usage stats."""

    client = Mistral(api_key=mistral_api_key)

    try:
        with open(resume_path, "rb") as resume_file:
            resume_bytes = resume_file.read()
    except FileNotFoundError as exc:
        raise ResumeOCRError(f"Resume file not found at {resume_path}") from exc

    if not resume_bytes:
        raise ResumeOCRError("Resume file is empty; cannot perform OCR.")

    file_name = os.path.basename(resume_path) or "resume.pdf"

    upload_response = client.files.upload(
        file={
            "file_name": file_name,
            "content": resume_bytes,
        },
        purpose="ocr",
    )

    signed_url = client.files.get_signed_url(file_id=upload_response.id, expiry=1)

    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document=DocumentURLChunk(document_url=signed_url.url),
        include_image_base64=False,
    )

    pages = getattr(ocr_response, "pages", []) or []
    resume_sections: list[str] = []
    for page in pages:
        markdown = getattr(page, "markdown", "").strip()
        if markdown:
            resume_sections.append(markdown)

    resume_markdown = "\n\n".join(resume_sections).strip()

    usage_info = getattr(ocr_response, "usage_info", None)
    if usage_info and getattr(usage_info, "pages_processed", 0):
        pages_processed = usage_info.pages_processed
    else:
        pages_processed = len(pages)

    return ResumeContext(markdown=resume_markdown, pages_processed=pages_processed)


