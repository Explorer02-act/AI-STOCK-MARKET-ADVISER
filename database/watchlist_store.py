from __future__ import annotations

import sqlite3
from pathlib import Path

from backend.market.indian_market import normalize_indian_symbol

DB_PATH = Path(__file__).with_name("watchlists.db")


def init_watchlist_db(db_path: Path = DB_PATH) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS watchlist_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                list_name TEXT NOT NULL DEFAULT 'default',
                ticker TEXT NOT NULL,
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(list_name, ticker)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS portfolio_positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                quantity REAL NOT NULL,
                average_price REAL NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def add_watchlist_item(ticker: str, list_name: str = "default", notes: str = "") -> str:
    init_watchlist_db()
    normalized = normalize_indian_symbol(ticker)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO watchlist_items (list_name, ticker, notes)
            VALUES (?, ?, ?)
            """,
            (list_name.strip() or "default", normalized, notes.strip()),
        )
    return normalized


def remove_watchlist_item(ticker: str, list_name: str = "default") -> None:
    init_watchlist_db()
    normalized = normalize_indian_symbol(ticker)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "DELETE FROM watchlist_items WHERE list_name = ? AND ticker = ?",
            (list_name.strip() or "default", normalized),
        )


def list_watchlist_items(list_name: str = "default") -> list[dict]:
    init_watchlist_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT ticker, notes, created_at
            FROM watchlist_items
            WHERE list_name = ?
            ORDER BY created_at DESC
            """,
            (list_name.strip() or "default",),
        ).fetchall()
    return [dict(row) for row in rows]


def upsert_position(ticker: str, quantity: float, average_price: float) -> str:
    init_watchlist_db()
    normalized = normalize_indian_symbol(ticker)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO portfolio_positions (ticker, quantity, average_price)
            VALUES (?, ?, ?)
            """,
            (normalized, quantity, average_price),
        )
    return normalized


def list_positions() -> list[dict]:
    init_watchlist_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT ticker, SUM(quantity) AS quantity, AVG(average_price) AS average_price
            FROM portfolio_positions
            GROUP BY ticker
            ORDER BY ticker
            """
        ).fetchall()
    return [dict(row) for row in rows]
