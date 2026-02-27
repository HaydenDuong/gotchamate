"""Lightweight SQLite storage for ClinicalSummary records."""

import sqlite3
from pathlib import Path
from pipeline.models import ClinicalSummary, Condition, Medication, FollowUp, Event


def _init_db(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            age INTEGER NOT NULL,
            discharge_date TEXT DEFAULT 'N/A',
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS conditions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            summary_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            status TEXT,
            notes TEXT,
            FOREIGN KEY (summary_id) REFERENCES summaries(id)
        );
        CREATE TABLE IF NOT EXISTS medications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            summary_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            dose TEXT,
            frequency TEXT,
            status TEXT DEFAULT 'N/A',
            FOREIGN KEY (summary_id) REFERENCES summaries(id)
        );
        CREATE TABLE IF NOT EXISTS follow_ups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            summary_id INTEGER NOT NULL,
            specialty TEXT NOT NULL,
            recommended_timeframe TEXT,
            due_date TEXT DEFAULT 'N/A',
            FOREIGN KEY (summary_id) REFERENCES summaries(id)
        );
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            summary_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            date TEXT,
            reason TEXT,
            FOREIGN KEY (summary_id) REFERENCES summaries(id)
        );
    """)


def save_summary(db_path: str | Path, summary: ClinicalSummary) -> int:
    """
    Persist a ClinicalSummary to SQLite. Creates DB and tables if needed.

    Returns:
        The assigned summary id (summary_id).
    """
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    try:
        _init_db(conn)
        cur = conn.execute(
            "INSERT INTO summaries (patient_name, age, discharge_date) VALUES (?, ?, ?)",
            (summary.patient_name, summary.age, summary.discharge_date),
        )
        summary_id = cur.lastrowid
        for c in summary.conditions:
            conn.execute(
                "INSERT INTO conditions (summary_id, name, status, notes) VALUES (?, ?, ?, ?)",
                (summary_id, c.name, c.status, c.notes),
            )
        for m in summary.medications:
            conn.execute(
                "INSERT INTO medications (summary_id, name, dose, frequency, status) VALUES (?, ?, ?, ?, ?)",
                (summary_id, m.name, m.dose, m.frequency, m.status),
            )
        for f in summary.follow_ups:
            conn.execute(
                "INSERT INTO follow_ups (summary_id, specialty, recommended_timeframe, due_date) VALUES (?, ?, ?, ?)",
                (summary_id, f.specialty, f.recommended_timeframe, f.due_date),
            )
        for e in summary.recent_events:
            conn.execute(
                "INSERT INTO events (summary_id, type, date, reason) VALUES (?, ?, ?, ?)",
                (summary_id, e.type, e.date, e.reason),
            )
        conn.commit()
        return summary_id
    finally:
        conn.close()


def list_summaries(db_path: str | Path) -> list[dict]:
    """
    Return a list of all summaries, most recent first.
    Returns empty list if DB doesn't exist yet.
    """
    path = Path(db_path)
    if not path.exists():
        return []
    conn = sqlite3.connect(path)
    try:
        _init_db(conn)
        rows = conn.execute(
            "SELECT id, patient_name, age, discharge_date, created_at FROM summaries ORDER BY id DESC"
        ).fetchall()
        return [
            {
                "id": r[0],
                "patient_name": r[1],
                "age": r[2],
                "discharge_date": r[3],
                "created_at": r[4],
            }
            for r in rows
        ]
    finally:
        conn.close()


def load_summary(db_path: str | Path, summary_id: int) -> ClinicalSummary | None:
    """Load a single ClinicalSummary by id. Returns None if not found."""
    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute(
            "SELECT patient_name, age, discharge_date FROM summaries WHERE id = ?",
            (summary_id,),
        ).fetchone()
        if not row:
            return None
        patient_name, age, discharge_date = row
        conditions = [
            Condition(name=r[0], status=r[1] or "", notes=r[2] or "")
            for r in conn.execute(
                "SELECT name, status, notes FROM conditions WHERE summary_id = ? ORDER BY id",
                (summary_id,),
            )
        ]
        medications = [
            Medication(name=r[0], dose=r[1] or "N/A", frequency=r[2] or "N/A", status=r[3] or "N/A")
            for r in conn.execute(
                "SELECT name, dose, frequency, status FROM medications WHERE summary_id = ? ORDER BY id",
                (summary_id,),
            )
        ]
        follow_ups = [
            FollowUp(specialty=r[0], recommended_timeframe=r[1] or "N/A", due_date=r[2] or "N/A")
            for r in conn.execute(
                "SELECT specialty, recommended_timeframe, due_date FROM follow_ups WHERE summary_id = ? ORDER BY id",
                (summary_id,),
            )
        ]
        events = [
            Event(type=r[0], date=r[1] or "", reason=r[2] or "")
            for r in conn.execute(
                "SELECT type, date, reason FROM events WHERE summary_id = ? ORDER BY id",
                (summary_id,),
            )
        ]
        return ClinicalSummary(
            patient_name=patient_name,
            age=age,
            discharge_date=discharge_date or "N/A",
            conditions=conditions,
            medications=medications,
            follow_ups=follow_ups,
            recent_events=events,
        )
    finally:
        conn.close()


def delete_summary(db_path: str | Path, summary_id: int) -> bool:
    """
    Delete a summary and all its related rows from the database.

    Returns:
        True if a row was deleted, False if not found.
    """
    conn = sqlite3.connect(db_path)
    try:
        for table in ("conditions", "medications", "follow_ups", "events"):
            conn.execute(f"DELETE FROM {table} WHERE summary_id = ?", (summary_id,))
        cur = conn.execute("DELETE FROM summaries WHERE id = ?", (summary_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
