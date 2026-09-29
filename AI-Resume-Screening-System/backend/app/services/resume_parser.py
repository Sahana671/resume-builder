"""
resume_parser.py
------------------
Responsible for extracting raw text and basic contact details
(name, email, phone) out of an uploaded resume file (.pdf, .doc, .docx).

This module is intentionally kept simple and explainable so that a
BCA student can read, understand and extend it. It can later be
swapped for a more advanced parser (e.g. spaCy NER, resume-parsing
ML models) without touching the rest of the system.
"""

import re
import os

import pdfplumber
import docx


def extract_text_from_pdf(file_path: str) -> str:
    """Extract raw text from a PDF resume using pdfplumber."""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_text_from_docx(file_path: str) -> str:
    """Extract raw text from a .docx resume using python-docx."""
    document = docx.Document(file_path)
    return "\n".join(paragraph.text for paragraph in document.paragraphs)


def extract_text(file_path: str) -> str:
    """
    Dispatch to the correct extractor based on file extension.
    Supports .pdf, .docx (and .doc, treated best-effort as docx).
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in (".docx", ".doc"):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported resume file type: {ext}")


def extract_email(text: str) -> str | None:
    """Find the first email address in the resume text."""
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    """Find the first phone-number-like pattern in the resume text."""
    match = re.search(r"(\+?\d{1,3}[-.\s]?)?\d{10}", text)
    return match.group(0) if match else None


def extract_name(text: str) -> str | None:
    """
    Very simple heuristic: assume the candidate's name is on one of
    the first few non-empty lines of the resume and does not contain
    common resume header words.
    """
    ignore_words = {"resume", "curriculum vitae", "cv", "profile"}
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for line in lines[:5]:
        lower_line = line.lower()
        if any(word in lower_line for word in ignore_words):
            continue
        # A plausible name line: short, mostly alphabetic
        word_count = len(line.split())
        if 1 <= word_count <= 4 and re.match(r"^[A-Za-z .]+$", line):
            return line.title()
    return lines[0].title() if lines else None


def parse_resume(file_path: str) -> dict:
    """
    Main entry point used by the routes: extracts text and basic
    contact information from a resume file.

    Returns a dict with keys: raw_text, name, email, phone
    """
    raw_text = extract_text(file_path)

    return {
        "raw_text": raw_text,
        "name": extract_name(raw_text),
        "email": extract_email(raw_text),
        "phone": extract_phone(raw_text),
    }
