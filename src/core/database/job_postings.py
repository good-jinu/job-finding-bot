import sqlite3
from typing import List, Optional
from src.core.schemas.job_posting import JobPosting
from datetime import datetime
from src.core.database.config import DB_FILE


def _get_db_connection():
  """Internal function to get a database connection."""
  conn = sqlite3.connect(DB_FILE)
  conn.row_factory = sqlite3.Row
  return conn


def init_job_postings_db():
  """Initializes the database and creates tables if they don't exist."""
  print("--- Initializing Storage ---")
  with _get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_postings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT,
                description TEXT,
                url TEXT NOT NULL UNIQUE,
                posted_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                read_at TIMESTAMP NULL,
                content_doc TEXT
            )
        """)
    conn.commit()
  print("Storage initialized successfully.")


def _parse_posted_at(posted_at: Optional[str]) -> Optional[str]:
  """Parse posted_at string to a consistent format."""
  if not posted_at:
    return None
  try:
    # Try to parse common date formats
    for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y년 %m월 %d일"]:
      try:
        dt = datetime.strptime(posted_at, fmt)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
      except ValueError:
        continue
    return posted_at
  except Exception:
    return posted_at


def save_job_postings(jobs: List[JobPosting]):
  """Saves a list of job postings to the database, ignoring duplicates."""
  if not jobs:
    return

  with _get_db_connection() as conn:
    cursor = conn.cursor()
    for job in jobs:
      posted_at_ts = _parse_posted_at(job.posted_at)
      cursor.execute(
        """
                INSERT OR IGNORE INTO job_postings (title, company, location, description, url, posted_at, content_doc)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
        (
          job.title,
          job.company,
          job.location,
          job.description,
          job.url,
          posted_at_ts,
          job.content_doc,
        ),
      )
    conn.commit()


def get_unread_job_posting() -> Optional[JobPosting]:
  """Fetches one unread job posting (read_at is NULL)."""
  with _get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(
      """
            SELECT title, company, location, description, url, posted_at, created_at, content_doc
            FROM job_postings
            WHERE read_at IS NULL
            ORDER BY created_at ASC
            LIMIT 1
        """
    )
    row = cursor.fetchone()
    if row:
      return JobPosting(
        title=row["title"],
        company=row["company"],
        location=row["location"],
        posted_at=row["posted_at"],
        description=row["description"],
        url=row["url"],
        content_doc=row["content_doc"],
      )
    return None


def mark_job_as_read(job_url: str):
  """Marks a job posting as read by setting read_at timestamp."""
  with _get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(
      """
            UPDATE job_postings
            SET read_at = CURRENT_TIMESTAMP
            WHERE url = ?
        """,
      (job_url,),
    )
    conn.commit()


def get_latest_job_postings_by_day(days: int) -> List[JobPosting]:
  """Fetches job postings created within the last N days."""
  with _get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(
      """
            SELECT title, company, location, description, url, posted_at, created_at, content_doc
            FROM job_postings
            ORDER BY created_at DESC
        """,
      (days,),
    )
    rows = cursor.fetchall()
    return [
      JobPosting(
        title=row["title"],
        company=row["company"],
        location=row["location"],
        posted_at=row["posted_at"],
        description=row["description"],
        url=row["url"],
        content_doc=row["content_doc"],
      )
      for row in rows
    ]


def get_latest_job_postings(limit: int = 10) -> List[JobPosting]:
  """Fetches the latest job postings with a limit."""
  with _get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(
      """
            SELECT id, title, company, location, description, url, posted_at, created_at, content_doc
            FROM job_postings
            ORDER BY created_at DESC
            LIMIT ?
        """,
      (limit,),
    )
    rows = cursor.fetchall()
    return [
      JobPosting(
        id=row["id"],
        title=row["title"],
        company=row["company"],
        location=row["location"],
        posted_at=row["posted_at"],
        description=row["description"],
        url=row["url"],
        content_doc=row["content_doc"],
      )
      for row in rows
    ]


def reset_all_read_at():
  """모든 job_postings의 read_at 필드를 NULL로 초기화합니다."""
  with _get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(
      """
      UPDATE job_postings
      SET read_at = NULL
      """
    )
    conn.commit()
  print("All read_at fields have been reset to NULL.")


def update_content_doc(job_id: int, content_doc: str):
  """특정 id의 채용공고의 content_doc을 수정합니다."""
  with _get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(
      """
      UPDATE job_postings
      SET content_doc = ?
      WHERE id = ?
      """,
      (content_doc, job_id),
    )
    conn.commit()
    print(f"content_doc updated for job_id: {job_id}")


if __name__ == "__main__":
  sample_jobs = [
    # JobPosting(
    #     title="title",
    #     company="company",
    #     location="location",
    #     posted_at="2025-07-01",
    #     description="description",
    #     url="https://job.com/",
    #     content_doc="job_developer_20250701.md"
    # )
  ]

  save_job_postings(sample_jobs)
  reset_all_read_at()
  print("샘플 채용공고가 저장되었습니다.")
