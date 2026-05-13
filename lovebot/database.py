"""SQLite persistence layer for LoveBot.

Stores one row per Telegram user with all their preferences, and uses a
``seen_items`` table to make sure quotes / advice / challenges don't repeat
until the entire catalogue has been shown.
"""

from __future__ import annotations

import logging
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Iterator, Optional

logger = logging.getLogger(__name__)


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id            INTEGER PRIMARY KEY,
    chat_id            INTEGER NOT NULL,
    delivery_chat_id   INTEGER,        -- when set, daily messages go here instead of chat_id
    language           TEXT    NOT NULL DEFAULT 'fa',
    state              TEXT    NOT NULL DEFAULT 'idle',
    user_name          TEXT,
    partner_name       TEXT,
    relationship_start TEXT,        -- YYYY-MM-DD
    user_birthday      TEXT,        -- MM-DD
    partner_birthday   TEXT,        -- MM-DD
    daily_hour         INTEGER NOT NULL DEFAULT 9,
    daily_minute       INTEGER NOT NULL DEFAULT 0,
    timezone           TEXT    NOT NULL DEFAULT 'Asia/Tehran',
    daily_enabled      INTEGER NOT NULL DEFAULT 1,
    love_score         INTEGER NOT NULL DEFAULT 0,
    streak             INTEGER NOT NULL DEFAULT 0,
    last_checkin       TEXT,        -- YYYY-MM-DD
    created_at         TEXT    NOT NULL,
    updated_at         TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS seen_items (
    user_id   INTEGER NOT NULL,
    category  TEXT    NOT NULL,
    item_id   INTEGER NOT NULL,
    seen_at   TEXT    NOT NULL,
    PRIMARY KEY (user_id, category, item_id)
);

CREATE TABLE IF NOT EXISTS moods (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id   INTEGER NOT NULL,
    mood      TEXT    NOT NULL,
    note      TEXT,
    logged_at TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS custom_milestones (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id   INTEGER NOT NULL,
    title     TEXT    NOT NULL,
    target    TEXT    NOT NULL,        -- YYYY-MM-DD
    created_at TEXT   NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_users_state ON users(state);
CREATE INDEX IF NOT EXISTS idx_seen_user_cat ON seen_items(user_id, category);
CREATE INDEX IF NOT EXISTS idx_moods_user ON moods(user_id);
"""


class Database:
    """Thin, thread-safe wrapper around an SQLite connection."""

    def __init__(self, path: str) -> None:
        self.path = path
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(
            self.path, check_same_thread=False, isolation_level=None
        )
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("PRAGMA foreign_keys=ON;")
        with self._lock:
            self._conn.executescript(SCHEMA)
            self._migrate()
        logger.info("Database ready at %s", self.path)

    def _migrate(self) -> None:
        """Apply forward-only schema migrations for existing databases."""
        cur = self._conn.cursor()
        cur.execute("PRAGMA table_info(users)")
        cols = {row[1] for row in cur.fetchall()}
        if "delivery_chat_id" not in cols:
            logger.info("Migrating: adding users.delivery_chat_id")
            cur.execute("ALTER TABLE users ADD COLUMN delivery_chat_id INTEGER")
        cur.close()

    # ------------------------------------------------------------------ infra

    @contextmanager
    def cursor(self) -> Iterator[sqlite3.Cursor]:
        with self._lock:
            cur = self._conn.cursor()
            try:
                yield cur
            finally:
                cur.close()

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    # ------------------------------------------------------------------ users

    def upsert_user(self, user_id: int, chat_id: int) -> dict[str, Any]:
        """Create the user row if missing; always returns the current row."""
        now = datetime.utcnow().isoformat(timespec="seconds")
        with self.cursor() as c:
            c.execute(
                """
                INSERT INTO users (user_id, chat_id, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    chat_id = excluded.chat_id,
                    updated_at = excluded.updated_at
                """,
                (user_id, chat_id, now, now),
            )
        return self.get_user(user_id)  # type: ignore[return-value]

    def get_user(self, user_id: int) -> Optional[dict[str, Any]]:
        with self.cursor() as c:
            c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = c.fetchone()
        return dict(row) if row else None

    def update_user(self, user_id: int, **fields: Any) -> None:
        if not fields:
            return
        fields["updated_at"] = datetime.utcnow().isoformat(timespec="seconds")
        cols = ", ".join(f"{k} = ?" for k in fields)
        with self.cursor() as c:
            c.execute(
                f"UPDATE users SET {cols} WHERE user_id = ?",
                (*fields.values(), user_id),
            )

    def set_state(self, user_id: int, state: str) -> None:
        self.update_user(user_id, state=state)

    def set_delivery_chat(self, user_id: int, delivery_chat_id: int | None) -> None:
        """Pin daily messages for ``user_id`` to a given chat (group/private)."""
        self.update_user(user_id, delivery_chat_id=delivery_chat_id)

    def list_active_users(self) -> list[dict[str, Any]]:
        """Users who have completed onboarding and want daily messages."""
        with self.cursor() as c:
            c.execute(
                """
                SELECT * FROM users
                 WHERE state = 'ready'
                   AND daily_enabled = 1
                   AND relationship_start IS NOT NULL
                """
            )
            return [dict(r) for r in c.fetchall()]

    def list_all_users(self) -> list[dict[str, Any]]:
        with self.cursor() as c:
            c.execute("SELECT * FROM users")
            return [dict(r) for r in c.fetchall()]

    # ------------------------------------------------------------------ items

    def mark_seen(self, user_id: int, category: str, item_id: int) -> None:
        now = datetime.utcnow().isoformat(timespec="seconds")
        with self.cursor() as c:
            c.execute(
                """
                INSERT OR IGNORE INTO seen_items (user_id, category, item_id, seen_at)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, category, item_id, now),
            )

    def get_seen_ids(self, user_id: int, category: str) -> set[int]:
        with self.cursor() as c:
            c.execute(
                "SELECT item_id FROM seen_items WHERE user_id = ? AND category = ?",
                (user_id, category),
            )
            return {row[0] for row in c.fetchall()}

    def reset_category(self, user_id: int, category: str) -> None:
        with self.cursor() as c:
            c.execute(
                "DELETE FROM seen_items WHERE user_id = ? AND category = ?",
                (user_id, category),
            )

    # ------------------------------------------------------------------ moods

    def log_mood(self, user_id: int, mood: str, note: str | None = None) -> None:
        now = datetime.utcnow().isoformat(timespec="seconds")
        with self.cursor() as c:
            c.execute(
                "INSERT INTO moods (user_id, mood, note, logged_at) VALUES (?, ?, ?, ?)",
                (user_id, mood, note, now),
            )

    def recent_moods(self, user_id: int, limit: int = 7) -> list[dict[str, Any]]:
        with self.cursor() as c:
            c.execute(
                """
                SELECT mood, note, logged_at FROM moods
                 WHERE user_id = ?
                 ORDER BY id DESC
                 LIMIT ?
                """,
                (user_id, limit),
            )
            return [dict(r) for r in c.fetchall()]

    # -------------------------------------------------------- custom milestones

    def add_custom_milestone(self, user_id: int, title: str, target: str) -> int:
        now = datetime.utcnow().isoformat(timespec="seconds")
        with self.cursor() as c:
            c.execute(
                """
                INSERT INTO custom_milestones (user_id, title, target, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, title, target, now),
            )
            return int(c.lastrowid or 0)

    def list_custom_milestones(self, user_id: int) -> list[dict[str, Any]]:
        with self.cursor() as c:
            c.execute(
                """
                SELECT id, title, target FROM custom_milestones
                 WHERE user_id = ?
                 ORDER BY target ASC
                """,
                (user_id,),
            )
            return [dict(r) for r in c.fetchall()]

    def delete_custom_milestone(self, user_id: int, milestone_id: int) -> None:
        with self.cursor() as c:
            c.execute(
                "DELETE FROM custom_milestones WHERE user_id = ? AND id = ?",
                (user_id, milestone_id),
            )
