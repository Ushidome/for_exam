"""SQLite persistence helpers for the Study RPG dashboard."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "study_rpg.sqlite3"

APPLIED_INFO_FIELDS = [
    "セキュリティ",
    "ネットワーク",
    "データベース",
    "アルゴリズム",
    "マネジメント",
    "システムアーキテクチャ",
]

HAZARDOUS_CLASSES = ["第1類", "第2類", "第3類", "第4類", "第5類", "第6類"]


def connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the database and seed progress rows when missing."""
    with closing(connect()) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS xp_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                study_date TEXT NOT NULL,
                exam TEXT NOT NULL,
                action TEXT NOT NULL,
                xp INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS progress_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exam TEXT NOT NULL,
                category TEXT NOT NULL,
                completed_units INTEGER NOT NULL DEFAULT 0,
                target_units INTEGER NOT NULL DEFAULT 10,
                UNIQUE(exam, category)
            );

            CREATE TABLE IF NOT EXISTS chemicals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                class_type TEXT NOT NULL,
                formula_memo TEXT,
                properties TEXT,
                hazards TEXT,
                encyclopedia_level INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            );
            """
        )
        seed_progress_items(conn)
        conn.commit()


def seed_progress_items(conn: sqlite3.Connection) -> None:
    items = [("応用情報", field, 0, 10) for field in APPLIED_INFO_FIELDS]
    items.extend(("危険物甲種", class_name, 0, 10) for class_name in HAZARDOUS_CLASSES)
    conn.executemany(
        """
        INSERT OR IGNORE INTO progress_items (exam, category, completed_units, target_units)
        VALUES (?, ?, ?, ?)
        """,
        items,
    )


def add_xp_event(exam: str, action: str, xp: int) -> None:
    now = datetime.now()
    with closing(connect()) as conn:
        conn.execute(
            """
            INSERT INTO xp_events (created_at, study_date, exam, action, xp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (now.isoformat(timespec="seconds"), now.date().isoformat(), exam, action, xp),
        )
        conn.commit()


def increment_progress(exam: str, category: str, amount: int = 1) -> None:
    with closing(connect()) as conn:
        conn.execute(
            """
            UPDATE progress_items
            SET completed_units = MIN(target_units, completed_units + ?)
            WHERE exam = ? AND category = ?
            """,
            (amount, exam, category),
        )
        conn.commit()


def total_xp() -> int:
    with closing(connect()) as conn:
        row = conn.execute("SELECT COALESCE(SUM(xp), 0) AS total FROM xp_events").fetchone()
    return int(row["total"])


def today_xp() -> int:
    with closing(connect()) as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(xp), 0) AS total FROM xp_events WHERE study_date = ?",
            (date.today().isoformat(),),
        ).fetchone()
    return int(row["total"])


def today_logs() -> list[sqlite3.Row]:
    with closing(connect()) as conn:
        rows = conn.execute(
            """
            SELECT * FROM xp_events
            WHERE study_date = ?
            ORDER BY created_at DESC
            """,
            (date.today().isoformat(),),
        ).fetchall()
    return list(rows)


def recent_logs(limit: int = 10) -> list[sqlite3.Row]:
    with closing(connect()) as conn:
        rows = conn.execute(
            """
            SELECT * FROM xp_events
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return list(rows)


def study_dates() -> list[date]:
    with closing(connect()) as conn:
        rows = conn.execute(
            "SELECT DISTINCT study_date FROM xp_events ORDER BY study_date DESC"
        ).fetchall()
    return [date.fromisoformat(row["study_date"]) for row in rows]


def current_streak() -> int:
    dates = set(study_dates())
    if not dates:
        return 0

    cursor = date.today()
    if cursor not in dates:
        cursor -= timedelta(days=1)

    streak = 0
    while cursor in dates:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def progress_items(exam: str) -> list[sqlite3.Row]:
    with closing(connect()) as conn:
        rows = conn.execute(
            """
            SELECT * FROM progress_items
            WHERE exam = ?
            ORDER BY id
            """,
            (exam,),
        ).fetchall()
    return list(rows)


def progress_rate(exam: str) -> float:
    items = progress_items(exam)
    total_target = sum(item["target_units"] for item in items)
    if total_target == 0:
        return 0.0
    total_completed = sum(item["completed_units"] for item in items)
    return min(1.0, total_completed / total_target)


def add_chemical(
    name: str,
    class_type: str,
    formula_memo: str,
    properties: str,
    hazards: str,
    encyclopedia_level: int,
) -> int:
    now = datetime.now().isoformat(timespec="seconds")
    with closing(connect()) as conn:
        cursor = conn.execute(
            """
            INSERT INTO chemicals (
                name, class_type, formula_memo, properties, hazards,
                encyclopedia_level, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (name, class_type, formula_memo, properties, hazards, encyclopedia_level, now),
        )
        conn.commit()
        return int(cursor.lastrowid)


def chemicals() -> list[sqlite3.Row]:
    with closing(connect()) as conn:
        rows = conn.execute(
            "SELECT * FROM chemicals ORDER BY created_at DESC, id DESC"
        ).fetchall()
    return list(rows)


def level_up_chemical(chemical_id: int) -> None:
    with closing(connect()) as conn:
        conn.execute(
            """
            UPDATE chemicals
            SET encyclopedia_level = encyclopedia_level + 1
            WHERE id = ?
            """,
            (chemical_id,),
        )
        conn.commit()


def first_category(items: Iterable[sqlite3.Row]) -> str | None:
    for item in items:
        if item["completed_units"] < item["target_units"]:
            return str(item["category"])
    return None
