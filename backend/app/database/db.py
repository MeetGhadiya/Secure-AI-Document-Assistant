"""
SQLite persistence layer for document metadata.

Only metadata lives here (filenames, session ownership, status, timestamps).
Actual chunk text + embeddings live in ChromaDB, always filtered by session_id.
"""
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Optional

from app.config import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    stored_filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    chunk_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'processing',
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_documents_session ON documents(session_id);

CREATE TABLE IF NOT EXISTS query_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    question TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.SQLITE_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()


@contextmanager
def db_cursor():
    conn = get_connection()
    try:
        yield conn.cursor()
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Document CRUD (all operations are scoped by session_id to enforce isolation)
# ---------------------------------------------------------------------------

def insert_document(
    doc_id: str,
    session_id: str,
    original_filename: str,
    stored_filename: str,
    file_type: str,
    file_size_bytes: int,
) -> None:
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO documents
                (id, session_id, original_filename, stored_filename,
                 file_type, file_size_bytes, chunk_count, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 0, 'processing', ?)
            """,
            (
                doc_id,
                session_id,
                original_filename,
                stored_filename,
                file_type,
                file_size_bytes,
                datetime.utcnow().isoformat(),
            ),
        )


def update_document_status(doc_id: str, status: str, chunk_count: Optional[int] = None) -> None:
    with db_cursor() as cur:
        if chunk_count is not None:
            cur.execute(
                "UPDATE documents SET status = ?, chunk_count = ? WHERE id = ?",
                (status, chunk_count, doc_id),
            )
        else:
            cur.execute("UPDATE documents SET status = ? WHERE id = ?", (status, doc_id))


def list_documents(session_id: str) -> list:
    with db_cursor() as cur:
        cur.execute(
            "SELECT * FROM documents WHERE session_id = ? ORDER BY created_at DESC",
            (session_id,),
        )
        return [dict(row) for row in cur.fetchall()]


def get_document(doc_id: str, session_id: str) -> Optional[dict]:
    """Fetch a document but ONLY if it belongs to the requesting session."""
    with db_cursor() as cur:
        cur.execute(
            "SELECT * FROM documents WHERE id = ? AND session_id = ?",
            (doc_id, session_id),
        )
        row = cur.fetchone()
        return dict(row) if row else None


def delete_document(doc_id: str, session_id: str) -> bool:
    """Delete a document row, scoped to the owning session. Returns True if deleted."""
    with db_cursor() as cur:
        cur.execute(
            "DELETE FROM documents WHERE id = ? AND session_id = ?",
            (doc_id, session_id),
        )
        return cur.rowcount > 0


def log_query(session_id: str, question: str) -> None:
    with db_cursor() as cur:
        cur.execute(
            "INSERT INTO query_log (session_id, question, created_at) VALUES (?, ?, ?)",
            (session_id, question, datetime.utcnow().isoformat()),
        )
