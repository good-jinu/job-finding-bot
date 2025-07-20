from src.core.database.job_postings import (
  init_job_postings_db,
)
from src.core.database.users import init_users_db
from src.core.database.resume_sources import init_resume_sources_db
from src.core.database.job_postings_users_map import (
  init_job_postings_users_map_db,
)


def init_all_database():
  """initialize all databases."""
  init_users_db()
  init_job_postings_db()
  init_resume_sources_db()
  init_job_postings_users_map_db()


if __name__ == "__main__":
  init_all_database()
