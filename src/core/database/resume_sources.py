import sqlite3
from typing import List, Optional
from src.core.schemas.resume_source import ResumeSource
from src.core.database.config import DB_FILE


def _get_db_connection():
  """Internal function to get a database connection."""
  conn = sqlite3.connect(DB_FILE)
  conn.row_factory = sqlite3.Row
  return conn


def init_resume_sources_db():
  """Initializes the resume_sources table if it doesn't exist."""
  print("--- Initializing Resume Sources Storage ---")
  with _get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS resume_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                source_file_name TEXT NOT NULL,
                original_file_name TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
    conn.commit()
  print("Resume Sources storage initialized successfully.")


def save_resume_source(resume_source: ResumeSource):
  """Saves a resume source to the database."""
  with _get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(
      """
            INSERT INTO resume_sources (user_id, source_file_name, original_file_name)
            VALUES (?, ?, ?)
            """,
      (resume_source.user_id, resume_source.source_file_name, resume_source.original_file_name),
    )
    conn.commit()
    return cursor.lastrowid


def get_resume_sources_by_user(user_id: str) -> List[ResumeSource]:
  """Fetches all resume sources for a given user."""
  with _get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(
      """
            SELECT id, user_id, source_file_name, original_file_name
            FROM resume_sources
            WHERE user_id = ?
            """,
      (user_id,),
    )
    rows = cursor.fetchall()
    return [
      ResumeSource(
        id=row["id"], 
        user_id=row["user_id"], 
        source_file_name=row["source_file_name"],
        original_file_name=row["original_file_name"]
      )
      for row in rows
    ]


def get_resume_source_by_id(resume_source_id: int) -> Optional[ResumeSource]:
  """Fetches a resume source by ID."""
  with _get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(
      """
            SELECT id, user_id, source_file_name, original_file_name
            FROM resume_sources
            WHERE id = ?
            """,
      (resume_source_id,),
    )
    row = cursor.fetchone()
    if row:
      return ResumeSource(
        id=row["id"], 
        user_id=row["user_id"], 
        source_file_name=row["source_file_name"],
        original_file_name=row["original_file_name"]
      )
    return None


def get_resume_source_content_by_id(resume_source_id: int) -> Optional[str]:
  """Fetches the content of a resume source by ID."""
  from src.core.file_storage.file_manager import FileManager
  from pathlib import Path
  
  resume_source = get_resume_source_by_id(resume_source_id)
  if not resume_source:
    return None
  
  file_manager = FileManager()
  content = file_manager.read_file_sync(Path(resume_source.source_file_name))
  return content


def delete_resume_source(resume_source_id: int):
  """Deletes a resume source by ID."""
  with _get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(
      """
            DELETE FROM resume_sources WHERE id = ?
            """,
      (resume_source_id,),
    )
    conn.commit()


if __name__ == "__main__":
  init_resume_sources_db()