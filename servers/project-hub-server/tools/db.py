"""Database initialization and connection management."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from .config import get_db_path_from_config


def get_db_path() -> Path:
    path = get_db_path_from_config()
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def db_connection() -> Generator[sqlite3.Connection, None, None]:
    """Context manager that ensures the connection is always closed."""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    """Create all tables if they do not exist yet."""
    conn = get_connection()
    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS projects (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                slug        TEXT    NOT NULL UNIQUE,
                name        TEXT    NOT NULL,
                type        TEXT    NOT NULL DEFAULT 'generic',
                status      TEXT    NOT NULL DEFAULT 'active',
                description TEXT    NOT NULL DEFAULT '',
                market      TEXT    NOT NULL DEFAULT '',
                products    TEXT    NOT NULL DEFAULT '',
                phase       TEXT    NOT NULL DEFAULT '',
                go_live     TEXT    NOT NULL DEFAULT '',
                budget      TEXT    NOT NULL DEFAULT '',
                notes       TEXT    NOT NULL DEFAULT '',
                docs_path   TEXT    NOT NULL DEFAULT '',
                created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
                updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS contacts (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id  INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                name        TEXT    NOT NULL,
                role        TEXT    NOT NULL DEFAULT '',
                type        TEXT    NOT NULL DEFAULT 'internal',
                email       TEXT    NOT NULL DEFAULT '',
                phone       TEXT    NOT NULL DEFAULT '',
                company     TEXT    NOT NULL DEFAULT '',
                notes       TEXT    NOT NULL DEFAULT '',
                created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS notes (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id  INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                title       TEXT    NOT NULL,
                type        TEXT    NOT NULL DEFAULT 'note',
                content     TEXT    NOT NULL DEFAULT '',
                agenda      TEXT    NOT NULL DEFAULT '',
                created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS session (
                id              INTEGER PRIMARY KEY CHECK (id = 1),
                project_id      INTEGER REFERENCES projects(id),
                last_skill      TEXT    NOT NULL DEFAULT '',
                updated_at      TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            INSERT OR IGNORE INTO session (id) VALUES (1);
        """)
    conn.close()
