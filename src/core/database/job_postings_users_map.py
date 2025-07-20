import sqlite3
from typing import List
from src.core.schemas.job_posting_user_map import JobPostingUserMap
from src.core.database.config import DB_FILE


def _get_db_connection():
  """Internal function to get a database connection."""
  conn = sqlite3.connect(DB_FILE)
  conn.row_factory = sqlite3.Row
  return conn


def init_job_postings_users_map_db():
  """Initializes the job_postings_users_map table if it doesn't exist."""
  print("--- Initializing Job Postings Users Map Storage ---")
  with _get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_postings_users_map (
                user_id INTEGER,
                job_posting_id INTEGER,
                PRIMARY KEY (user_id, job_posting_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (job_posting_id) REFERENCES job_postings(id) ON DELETE CASCADE
            )
        """)
    conn.commit()
  print("Job Postings Users Map storage initialized successfully.")


def save_job_posting_user_map(mapping: JobPostingUserMap):
  """Saves a job posting and user mapping."""
  with _get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(
      """
            INSERT OR IGNORE INTO job_postings_users_map (user_id, job_posting_id)
            VALUES (?, ?)
            """,
      (mapping.user_id, mapping.job_posting_id),
    )
    conn.commit()


def get_job_postings_by_user(user_id: int) -> List[int]:
  """Fetches all job posting IDs associated with a user."""
  with _get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(
      """
            SELECT job_posting_id
            FROM job_postings_users_map
            WHERE user_id = ?
            """,
      (user_id,),
    )
    return [row["job_posting_id"] for row in cursor.fetchall()]


def get_users_by_job_posting(job_posting_id: int) -> List[int]:
  """Fetches all user IDs associated with a job posting."""
  with _get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(
      """
            SELECT user_id
            FROM job_postings_users_map
            WHERE job_posting_id = ?
            """,
      (job_posting_id,),
    )
    return [row["user_id"] for row in cursor.fetchall()]


def delete_job_posting_user_map(user_id: int, job_posting_id: int):
  """Deletes a specific user-job posting mapping."""
  with _get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(
      """
            DELETE FROM job_postings_users_map
            WHERE user_id = ? AND job_posting_id = ?
            """,
      (user_id, job_posting_id),
    )
    conn.commit()


if __name__ == "__main__":
  init_job_postings_users_map_db()
