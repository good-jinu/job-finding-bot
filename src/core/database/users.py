import sqlite3
from typing import List, Optional
from src.core.schemas.user import User
from src.core.database.config import DB_FILE


def _get_db_connection():
  """Internal function to get a database connection."""
  conn = sqlite3.connect(DB_FILE)
  conn.row_factory = sqlite3.Row
  return conn


def init_users_db():
  """Initializes the users table if it doesn't exist."""
  print("--- Initializing Users Storage ---")
  with _get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                short_description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    conn.commit()
  print("Users storage initialized successfully.")


def save_user(user: User):
  """Saves a single user to the database."""
  with _get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(
      """
            INSERT INTO users (name, short_description)
            VALUES (?, ?)
            """,
      (user.name, user.short_description),
    )
    conn.commit()
    return cursor.lastrowid


def get_user_by_id(user_id: int) -> Optional[User]:
  """Fetches a user by ID."""
  with _get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(
      """
            SELECT id, name, short_description, created_at
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
        short_description=row["short_description"],
        created_at=row["created_at"],
      )
    return None


def get_all_users() -> List[User]:
  """Fetches all users from the database."""
  with _get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(
      """
            SELECT id, name, short_description, created_at
            FROM users
            ORDER BY created_at DESC
            """
    )
    rows = cursor.fetchall()
    return [
      User(
        id=row["id"],
        name=row["name"],
        short_description=row["short_description"],
        created_at=row["created_at"],
      )
      for row in rows
    ]


def update_user(
  user_id: int, name: Optional[str] = None, short_description: Optional[str] = None
):
  """Updates user information."""
  with _get_db_connection() as conn:
    cursor = conn.cursor()
    updates = []
    params = []
    if name is not None:
      updates.append("name = ?")
      params.append(name)
    if short_description is not None:
      updates.append("short_description = ?")
      params.append(short_description)
    if updates:
      params.append(user_id)
      query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
      cursor.execute(query, params)
      conn.commit()


def delete_user(user_id: int):
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
  init_users_db()
