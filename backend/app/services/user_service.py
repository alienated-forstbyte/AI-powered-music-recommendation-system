import sqlite3
import os
from threading import local

DB_PATH = os.environ.get("USER_DB_PATH", "data/user_history.db")
_thread_local = local()

SKIP_LIMIT = 10


def _get_db():
    if not hasattr(_thread_local, "conn") or _thread_local.conn is None:
        _thread_local.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _thread_local.conn.row_factory = sqlite3.Row
        _thread_local.conn.execute("PRAGMA journal_mode=WAL")
        _thread_local.conn.execute("PRAGMA synchronous=NORMAL")
    return _thread_local.conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    conn = _get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS play_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            video_id TEXT NOT NULL,
            played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_play_events_user
            ON play_events(user_id, played_at)
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tag_skips (
            user_id TEXT NOT NULL,
            tag TEXT NOT NULL,
            count INTEGER NOT NULL DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, tag)
        )
    """)
    conn.commit()


def log_user_play(user_id: str, video_id: str):
    conn = _get_db()
    conn.execute(
        "INSERT INTO play_events (user_id, video_id) VALUES (?, ?)",
        (user_id, video_id),
    )
    conn.commit()


def get_user_history(user_id: str):
    conn = _get_db()
    cursor = conn.execute(
        "SELECT video_id FROM play_events WHERE user_id = ? ORDER BY played_at",
        (user_id,),
    )
    return [row["video_id"] for row in cursor.fetchall()]


def get_all_play_events():
    conn = _get_db()
    cursor = conn.execute(
        "SELECT user_id, video_id, played_at FROM play_events ORDER BY played_at"
    )
    return [dict(row) for row in cursor.fetchall()]


def increment_tag_skips(user_id: str, tags: list):
    conn = _get_db()
    for tag in tags:
        tag_lower = tag.lower().strip()
        if not tag_lower:
            continue
        conn.execute("""
            INSERT INTO tag_skips (user_id, tag, count, updated_at)
            VALUES (?, ?, 1, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, tag) DO UPDATE SET
                count = count + 1,
                updated_at = CURRENT_TIMESTAMP
        """, (user_id, tag_lower))
    conn.commit()


def get_excluded_tags(user_id: str):
    conn = _get_db()
    cursor = conn.execute(
        "SELECT tag FROM tag_skips WHERE user_id = ? AND count >= ?",
        (user_id, SKIP_LIMIT),
    )
    return {row["tag"] for row in cursor.fetchall()}


init_db()
