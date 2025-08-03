import sqlite3
import uuid
from typing import List, Optional
from src.core.schemas.user import User, UserCreate
from src.core.database.config import DB_FILE


def _get_db_connection():
  """Internal function to get a database connection."""
  conn = sqlite3.connect(DB_FILE)
  conn.row_factory = sqlite3.Row
  return conn


def remove_all_users():
  """Removes all users from the database."""
  with _get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users")
    conn.commit()
  print("All users removed successfully.")


def init_users_db():
  """Initializes the users table if it doesn't exist."""
  print("--- Initializing Users Storage ---")
  with _get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                resume_file TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    conn.commit()
  print("Users storage initialized successfully.")


def save_user(user: UserCreate) -> User:
  """Saves a single user to the database."""
  with _get_db_connection() as conn:
    cursor = conn.cursor()
    user_id = str(uuid.uuid4())
    cursor.execute(
      """
            INSERT INTO users (id, name, resume_file)
            VALUES (?, ?, ?)
            """,
      (user_id, user.name, user.resume_file),
    )
    conn.commit()
    return get_user_by_id(user_id)


def get_user_by_id(user_id: str) -> Optional[User]:
  """Fetches a user by ID."""
  with _get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(
      """
            SELECT id, name, resume_file, created_at
            FROM users
            WHERE id = ?
            """,
      (user_id,),
    )
    row = cursor.fetchone()
    if row:
      return User(
        id=row["id"],
        name=row["name"],
        resume_file=row["resume_file"],
        created_at=row["created_at"],
      )
    return None


def get_all_users() -> List[User]:
  """Fetches all users from the database."""
  with _get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(
      """
            SELECT id, name, resume_file, created_at
            FROM users
            ORDER BY created_at DESC
            """
    )
    rows = cursor.fetchall()
    return [
      User(
        id=row["id"],
        name=row["name"],
        resume_file=row["resume_file"],
        created_at=row["created_at"],
      )
      for row in rows
    ]


def update_user(
  user_id: str, name: Optional[str] = None, resume_file: Optional[str] = None
):
  """Updates user information."""
  with _get_db_connection() as conn:
    cursor = conn.cursor()
    updates = []
    params = []
    if name is not None:
      updates.append("name = ?")
      params.append(name)
    if resume_file is not None:
      updates.append("resume_file = ?")
      params.append(resume_file)
    if updates:
      params.append(user_id)
      query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
      cursor.execute(query, params)
      conn.commit()


def delete_user(user_id: str):
  """Deletes a user by ID."""
  with _get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(
      """
            DELETE FROM users WHERE id = ?
            """,
      (user_id,),
    )
    conn.commit()


if __name__ == "__main__":
  users = get_all_users()
  for user in users:
    print(f"User ID: {user.id}, Name: {user.name}, Resume File: {user.resume_file}")
