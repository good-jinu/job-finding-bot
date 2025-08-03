from typing import List
from pydantic import BaseModel, Field

from src.core.schemas.job_search import JobSearchState
from src.core.database.users import get_user_by_id
from src.core.file_storage.file_manager import FileManager
from src.core.file_storage.paths import FileStoragePaths
from src.core.schemas.job_posting import JobPosting
from src.core.services.job_search.scraping import collect_and_extract_job_postings



# Initialize file storage
file_paths = FileStoragePaths()
file_manager = FileManager(file_paths)


class JobSearchResult(BaseModel):
  urls: List[str] = Field(..., description="A list of relevant job posting URLs found.")


def get_resume_content_node(state: JobSearchState) -> JobSearchState:
  """사용자 ID를 기반으로 이력서 내용을 로드합니다."""
  print("--- Loading Resume for Job Search ---")
  user_id = state.get("user_id")
  if not user_id:
    raise ValueError("User ID is required to get resume content.")
  
  user = get_user_by_id(user_id)
  if not user or not user.resume_file:
    state["resume_content"] = None
    print(f"No resume found for user: {user_id}")
    return state

  try:
    file_path = file_paths.get_resume_path(user.resume_file)
    resume_content = file_manager.read_file_sync(file_path)
    if resume_content:
      state["resume_content"] = resume_content
      print(f"Successfully loaded resume for user {user.name} from {file_path}")
    else:
      state["resume_content"] = None
      print(f"Resume file content is empty or could not be read: {user.resume_file}")
  except Exception as e:
    print(f"Error reading resume file {user.resume_file}: {e}")
    state["resume_content"] = None

  return state


async def search_and_scrape_jobs_node(state: JobSearchState) -> JobSearchState:
  """추출된 키워드를 사용하여 채용 공고를 검색하고 상세 정보를 한번에 수집합니다."""
  print("--- Searching and Scraping Job Postings ---")
  keywords = state.get("job_keywords", [])
  if not keywords:
    state["scraped_results"] = []
    print("No keywords to search for jobs.")
    return state

  print(f"Collecting and extracting job postings for query: {' '.join(keywords)}")

  all_results: List[JobPosting] = []
  for keyword in keywords:
    try:
      # collect_and_extract_job_postings 함수를 사용하여 검색과 스크래핑을 한 번에 수행
      results = await collect_and_extract_job_postings(keyword=keyword)
      all_results.extend(results)
      print(f"Found and scraped {len(results)} job postings for keyword '{keyword}'")
    except Exception as e:
      print(f"Error during job search and scraping for keyword '{keyword}': {e}")

  state["scraped_results"] = all_results
  print(f"Finished searching and scraping. Total results: {len(all_results)}")

  return state
