from typing import List, Dict, Any
from pydantic import BaseModel, Field
from src.core.schemas.job_search import JobSearchState
from src.core.database.users import get_user_by_id
from src.core.file_storage.file_manager import FileManager
from src.core.file_storage.paths import FileStoragePaths
from src.core.llm.providers import get_job_analysis_model
from langchain_core.prompts import PromptTemplate
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
    resume_content = file_manager.read_file_sync(user.resume_file)
    if resume_content:
      state["resume_content"] = resume_content
      print(f"Successfully loaded resume for user {user.name} from {user.resume_file}")
    else:
      state["resume_content"] = None
      print(f"Resume file content is empty or could not be read: {user.resume_file}")
  except Exception as e:
    print(f"Error reading resume file {user.resume_file}: {e}")
    state["resume_content"] = None

  return state


async def extract_keywords_from_resume_node(state: JobSearchState) -> JobSearchState:
  """LLM을 사용하여 이력서에서 핵심 직무 키워드를 추출합니다."""
  print("--- Extracting Keywords from Resume ---")
  resume_content = state.get("resume_content")
  if not resume_content:
    state["job_keywords"] = []
    print("No resume content to extract keywords from.")
    return state

  llm = get_job_analysis_model()
  prompt = PromptTemplate(
    template="""
        당신은 전문 채용 컨설턴트입니다. 주어진 이력서 내용을 분석하여 가장 적합한 직무와 관련된 핵심 키워드를 5개만 추출해주세요.
        키워드는 채용 공고 검색에 직접 사용될 수 있도록 간결하고 명확해야 합니다.
        예시: "백엔드 개발자", "Python", "Django", "PostgreSQL", "AWS"

        ## 이력서 내용:
        {resume}

        ## 추출된 키워드 (쉼표로 구분된 리스트 형식):
        """,
    input_variables=["resume"],
  )

  try:
    chain = prompt | llm
    result = await chain.ainvoke({"resume": resume_content})
    keywords = [
      keyword.strip() for keyword in result.content.split(",") if keyword.strip()
    ]
    state["job_keywords"] = keywords
    print(f"Extracted keywords: {keywords}")
  except Exception as e:
    print(f"Error extracting keywords from resume: {e}")
    state["job_keywords"] = []

  return state


async def search_and_scrape_jobs_node(state: JobSearchState) -> JobSearchState:
  """추출된 키워드를 사용하여 채용 공고를 검색하고 상세 정보를 한번에 수집합니다."""
  print("--- Searching and Scraping Job Postings ---")
  keywords = state.get("job_keywords")
  if not keywords:
    state["scraped_results"] = []
    print("No keywords to search for jobs.")
    return state

  print(f"Collecting and extracting job postings for query: {' '.join(keywords)}")

  all_results: List[Dict[str, Any]] = []
  for keyword in keywords:
    try:
      # collect_and_extract_job_postings 함수를 사용하여 검색과 스크래핑을 한 번에 수행
      results = await collect_and_extract_job_postings(keyword=keyword)

      # JobPostingExtractionState 객체를 딕셔너리로 변환하여 저장
      for r in results:
        all_results.append(
          {
            "url": r.job_url,
            "success": r.success,
            "job_posting": r.job_posting,
            "error": getattr(r, "error_message", None),
          }
        )
      print(f"Found and scraped {len(results)} job postings for keyword '{keyword}'")
    except Exception as e:
      print(f"Error during job search and scraping for keyword '{keyword}': {e}")

  state["scraped_results"] = all_results
  print(f"Finished searching and scraping. Total results: {len(all_results)}")

  return state
