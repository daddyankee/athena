import sqlite3
import uuid
import time
from pathlib import Path

DB_PATH = Path(__file__).parent / "athena.db"


def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init():
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id       TEXT PRIMARY KEY,
                title    TEXT NOT NULL,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id              TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role            TEXT NOT NULL,
                content         TEXT NOT NULL,
                created_at      REAL NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        """)


def create_conversation(title: str) -> str:
    cid = str(uuid.uuid4())
    now = time.time()
    with _conn() as c:
        c.execute(
            "INSERT INTO conversations (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (cid, title[:80], now, now),
        )
    return cid


def touch_conversation(cid: str):
    with _conn() as c:
        c.execute("UPDATE conversations SET updated_at = ? WHERE id = ?", (time.time(), cid))


def save_message(cid: str, role: str, content: str):
    with _conn() as c:
        c.execute(
            "INSERT INTO messages (id, conversation_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), cid, role, content, time.time()),
        )


def list_conversations(limit: int = 15, offset: int = 0) -> list[dict]:
    with _conn() as c:
        rows = c.execute(
            "SELECT id, title, updated_at FROM conversations ORDER BY updated_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
    return [dict(r) for r in rows]


def get_messages(cid: str) -> list[dict]:
    with _conn() as c:
        rows = c.execute(
            "SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY created_at",
            (cid,),
        ).fetchall()
    return [dict(r) for r in rows]
