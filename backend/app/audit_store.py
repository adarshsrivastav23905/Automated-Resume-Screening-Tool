import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


DB_PATH = Path("outputs/screening_history.db")


def save_run(
    results: pd.DataFrame,
    job_description: str,
    must_have: list[str],
    minimum_years: float,
    threshold: float,
) -> int:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS screening_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            job_description TEXT NOT NULL,
            must_have TEXT NOT NULL,
            minimum_years REAL NOT NULL,
            threshold REAL NOT NULL,
            candidate_count INTEGER NOT NULL,
            report_json TEXT NOT NULL
        )
        """
    )
    cursor = connection.execute(
        """
        INSERT INTO screening_runs (
            created_at, job_description, must_have, minimum_years,
            threshold, candidate_count, report_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now(timezone.utc).isoformat(),
            job_description,
            json.dumps(must_have),
            minimum_years,
            threshold,
            len(results),
            results.to_json(orient="records"),
        ),
    )
    connection.commit()
    run_id = int(cursor.lastrowid)
    connection.close()
    return run_id


def list_runs(limit: int = 20) -> pd.DataFrame:
    if not DB_PATH.exists():
        return pd.DataFrame(
            columns=["id", "created_at", "must_have", "minimum_years", "threshold", "candidate_count"]
        )

    connection = sqlite3.connect(DB_PATH)
    frame = pd.read_sql_query(
        """
        SELECT id, created_at, must_have, minimum_years, threshold, candidate_count
        FROM screening_runs
        ORDER BY id DESC
        LIMIT ?
        """,
        connection,
        params=(limit,),
    )
    connection.close()
    return frame


def get_run(run_id: int) -> pd.DataFrame:
    connection = sqlite3.connect(DB_PATH)
    row = connection.execute(
        "SELECT report_json FROM screening_runs WHERE id = ?",
        (run_id,),
    ).fetchone()
    connection.close()
    if not row:
        raise ValueError("Screening run not found")
    return pd.DataFrame(json.loads(row[0]))
