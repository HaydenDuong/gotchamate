"""Extract raw text from text-based PDFs using pdfplumber."""

import pdfplumber
from pathlib import Path


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """
    Extract text from a PDF file. Best for text-based (non-scanned) PDFs.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Concatenated text from all pages.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the PDF appears to be empty or unreadable.
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    text_parts: list[str] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            raw = page.extract_text()
            if raw:
                text_parts.append(raw)

    if not text_parts:
        raise ValueError(f"No text could be extracted from {path} (may be scanned/image-only).")

    return "\n\n".join(text_parts).strip()
