"""Orchestrates PDF → text → LLM → ClinicalSummary and optional storage."""

from pathlib import Path
from pipeline.extract_text import extract_text_from_pdf
from pipeline.llm_extract import extract_clinical_summary
from pipeline.models import ClinicalSummary
from pipeline.store import save_summary


def run_pipeline(
    pdf_path: str | Path,
    *,
    save_to_db: bool = False,
    db_path: str | Path = "data/snapshots.db",
) -> ClinicalSummary:
    """
    Run the full pipeline: PDF → text → LLM → validated ClinicalSummary.

    Args:
        pdf_path: Path to the discharge summary PDF.
        save_to_db: If True, persist the summary to SQLite.
        db_path: Path to SQLite file (used only when save_to_db is True).

    Returns:
        Validated ClinicalSummary.

    Raises:
        FileNotFoundError: PDF not found.
        ValueError: No text extracted or LLM/validation failed.
    """
    text = extract_text_from_pdf(pdf_path)
    summary = extract_clinical_summary(text)

    if save_to_db:
        save_summary(db_path, summary)

    return summary
