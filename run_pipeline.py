#!/usr/bin/env python3
"""
CLI to run the clinical document pipeline on a PDF.

Usage:
    python run_pipeline.py path/to/discharge_summary.pdf
    python run_pipeline.py path/to/file.pdf --save
"""
import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

from pipeline.pipeline import run_pipeline

load_dotenv()


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract structured clinical summary from a PDF.")
    parser.add_argument("pdf_path", type=Path, help="Path to the discharge summary PDF")
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save the result to SQLite (data/snapshots.db)",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("data/snapshots.db"),
        help="SQLite path when using --save (default: data/snapshots.db)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print summary as JSON instead of a short table",
    )
    args = parser.parse_args()

    summary = run_pipeline(
        args.pdf_path,
        save_to_db=args.save,
        db_path=args.db,
    )

    if args.json:
        print(json.dumps(summary.model_dump(), indent=2))
    else:
        print(f"Patient: {summary.patient_name}, Age: {summary.age}")
        print(f"Conditions: {len(summary.conditions)}")
        for c in summary.conditions:
            print(f"  - {c.name} ({c.status})")
        print(f"Medications: {len(summary.medications)}")
        for m in summary.medications:
            print(f"  - {m.name} {m.dose} {m.frequency}")
        print(f"Follow-ups: {len(summary.follow_ups)}")
        for f in summary.follow_ups:
            print(f"  - {f.specialty}: {f.recommended_timeframe}")
        print(f"Recent events: {len(summary.recent_events)}")
        for e in summary.recent_events:
            print(f"  - {e.type} ({e.date}): {e.reason}")

    if args.save:
        print("\nSaved to database.")


if __name__ == "__main__":
    main()
