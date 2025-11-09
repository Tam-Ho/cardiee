import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Generator, List, Optional, Tuple

from .core import DB_READ_ERROR, DB_WRITE_ERROR, SUCCESS, Flashcard


def _init_database(db_path: str) -> int:
    """Initialize the database with required tables."""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    deadline TEXT,
                    delay_factor INTEGER DEFAULT 1,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        return SUCCESS
    except sqlite3.Error:
        return DB_WRITE_ERROR


class DatabaseHandler:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        _init_database(db_path)

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        try:
            yield conn
        finally:
            conn.close()

    def add_card(self, question: str, answer: str) -> Tuple[Optional[Flashcard], int]:
        """Add a new card to the database and return the inserted id, question, and answer."""
        query = """
            INSERT INTO cards (question, answer, deadline)
            VALUES (?, ?, ?)
        """
        deadline = datetime.now().strftime("%Y-%m-%d")
        values = (question, answer, deadline)

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, values)
                inserted_id = cursor.lastrowid
                conn.commit()
            return (
                Flashcard(
                    id=inserted_id, question=question, answer=answer, deadline=deadline
                ),
                SUCCESS,
            )
        except sqlite3.Error:
            return (None, DB_WRITE_ERROR)

    def remove_card(self, card_id: int) -> int:
        """Delete a card by ID."""
        query = "DELETE FROM cards WHERE id = ?"

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (card_id,))
                conn.commit()
            return SUCCESS
        except sqlite3.Error:
            return DB_WRITE_ERROR

    def clear_cards(self) -> int:
        """Delete all cards from the database."""
        query = "DELETE FROM cards"

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
            return SUCCESS
        except sqlite3.Error:
            return DB_WRITE_ERROR

    def list_cards(
        self, expired_only: bool = False
    ) -> Tuple[Optional[List[Flashcard]], int]:
        """
        Retrieve cards from the database.
        If expired_only is True, only return cards whose deadline is today or earlier.
        """
        if expired_only:
            query = "SELECT * FROM cards WHERE date(deadline) <= date('now') ORDER BY deadline ASC"
        else:
            query = "SELECT * FROM cards ORDER BY updated_at ASC"

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                flashcards = [
                    Flashcard(
                        id=row["id"],
                        question=row["question"],
                        answer=row["answer"],
                        deadline=row["deadline"],
                    )
                    for row in rows
                ]
            return (flashcards, SUCCESS)
        except sqlite3.Error:
            return (None, DB_READ_ERROR)

    def update_card_deadline(self, card_id: int, reset: bool) -> int:
        """Update the deadline of a card"""
        if reset:
            query = """
            UPDATE cards
            SET deadline = date('now', '+' || 1 || ' days'),
                delay_factor = 1
            WHERE id = ?
            """
        else:
            query = """
            UPDATE cards 
            SET deadline = date('now', '+' || CAST(ROUND(delay_factor * 1.5) AS INTEGER) || ' days'),
                delay_factor = delay_factor + 1
            WHERE id = ?
            """

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (card_id,))
                conn.commit()
            return SUCCESS
        except sqlite3.Error:
            return DB_WRITE_ERROR
