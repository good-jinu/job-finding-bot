import aiohttp
from datetime import datetime
from langchain_core.prompts import PromptTemplate
from src.core.llm.providers import get_structured_output_model, get_summarization_model
from src.core.schemas.job_posting import JobPosting, JobPostingExtractionState
from src.core.file_storage.paths import FileStoragePaths
from src.core.file_storage.file_manager import FileManager
from src.core.database.job_postings import save_job_postings
from src.core.database.job_postings_users_map import save_job_posting_user_map
from src.core.schemas.job_posting_user_map import JobPostingUserMap
from src.core.database.job_postings import get_latest_job_postings
import markitdown

# Initialize file storage and utilities
file_paths = FileStoragePaths()
file_manager = FileManager(file_paths)
md = markitdown.MarkItDown()


async def fetch_html_node(
  state: JobPostingExtractionState,
) -> JobPostingExtractionState:
  """URL에서 HTML 콘텐츠를 가져옵니다."""
  print("--- Fetching HTML from URL ---")

  try:
    async with aiohttp.ClientSession() as session:
      async with session.get(state.job_url) as response:
        if response.status == 200:
          html_content = await response.text()
          state.html_content = html_content
          print(f"Successfully fetched HTML from {state.job_url}")
        else:
          raise Exception(f"HTTP {response.status}: Failed to fetch URL")

  except Exception as e:
    state.error_message = str(e)
    state.success = False
    print(f"Error fetching HTML: {e}")

  return state


async def convert_to_markdown_node(
  state: JobPostingExtractionState,
) -> JobPostingExtractionState:
  """HTML을 마크다운으로 변환합니다."""
  print("--- Converting HTML to Markdown ---")

  if not state.html_content:
    state.error_message = "No HTML content to convert"
    state.success = False
    return state

  try:
    # Create a temporary file for the HTML content
    temp_html_path = file_paths.output_dir / "temp_job.html"
    file_manager.write_file_sync(temp_html_path, state.html_content)

    # Convert HTML to markdown using markitdown
    result = md.convert_file(str(temp_html_path))
    markdown_content = result.text_content

    state.markdown_content = markdown_content

    # Clean up temporary file
    if temp_html_path.exists():
      temp_html_path.unlink()

    print(f"Successfully converted HTML to markdown ({len(markdown_content)} chars)")

  except Exception as e:
    state.error_message = str(e)
    state.success = False
    print(f"Error converting to markdown: {e}")

  return state


async def extract_job_details_node(
  state: JobPostingExtractionState,
) -> JobPostingExtractionState:
  """채용공고 세부 정보를 LLM을 사용하여 추출합니다."""
  print("--- Extracting job details with LLM ---")

  if not state.markdown_content:
    state.error_message = "No markdown content to process"
    state.success = False
    return state

  try:
    # LLM 설정
    llm = get_structured_output_model().with_structured_output(JobPosting)

    prompt = PromptTemplate(
      template="""
당신은 전문적인 채용공고 분석가입니다. 제공된 마크다운 형식의 채용공고를 분석하여 다음 정보들을 정확하게 추출해주세요.

## 추출할 정보:
1. **title**: 채용 직무 제목
2. **company**: 회사 이름
3. **location**: 근무 위치
4. **posted_at**: 게시일 (YYYY-MM-DD 형식)
5. **description**: 전체 채용공고 요약

추출하려는 채용공고 마크다운:
{markdown_content}

각 필드를 한국어로 작성해주세요.
""",
      input_variables=["markdown_content"],
    )

    # LLM 호출
    chain = prompt | llm
    result = await chain.ainvoke({"markdown_content": state.markdown_content})

    job_posting = JobPosting(
      title=result.get("title", ""),
      company=result.get("company", ""),
      location=result.get("location", ""),
      description=result.get("description", ""),
      posted_at=result.get("posted_at", None),
      url=state.job_url,
      content_doc=None,
    )

    state.job_posting = job_posting

    print("Successfully extracted job details with LLM")

  except Exception as e:
    state.error_message = str(e)
    state.success = False
    print(f"Error extracting job details: {e}")

  return state


async def save_job_posting_node(
  state: JobPostingExtractionState,
) -> JobPostingExtractionState:
  """추출한 채용공고를 데이터베이스와 파일로 저장합니다."""
  print("--- Saving job posting ---")

  if not state.job_posting:
    state.error_message = "No job posting to save"
    state.success = False
    return state

  try:
    job_posting = state.job_posting

    # 파일로 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_company = "".join(
      c for c in job_posting.company if c.isalnum() or c in (" ", "-", "_")
    ).rstrip()
    safe_title = "".join(
      c for c in job_posting.title if c.isalnum() or c in (" ", "-", "_")
    ).rstrip()

    filename = f"{safe_company}_{safe_title}_{timestamp}.md"
    file_path = file_paths.get_job_content_path(filename)

    # 상세한 마크다운 파일 생성
    input_content = f"""
Raw Markdown Content:
{state.markdown_content}

---

Raw content 에서 채용공고 내용만 필터링해주세요.

추출하려는 채용공고는 다음과 같습니다:
* 채용공고: {job_posting.title}
* 회사: {job_posting.company}
* 위치: {job_posting.location or "미지정"}
* 게시일: {job_posting.posted_at or "지정 안됨"}
* URL: {job_posting.url}

## 채용공고 내용 Full
"""

    llm = get_summarization_model()
    content = llm.invoke(input=input_content)

    # 파일 저장
    file_manager.write_file_sync(file_path, content)
    state.saved_file_path = str(file_path)

    # content_doc 필드 업데이트
    job_posting.content_doc = filename

    # 데이터베이스에 저장
    save_job_postings([job_posting])

    # 방금 저장한 job_posting의 ID 가져오기
    latest_jobs = get_latest_job_postings(limit=1)
    if latest_jobs:
      state.job_posting_id = latest_jobs[0].id

    state.extraction_content = content
    state.success = True
    print(f"Successfully saved job posting to {file_path}")

  except Exception as e:
    state.error_message = str(e)
    state.success = False
    print(f"Error saving job posting: {e}")

  return state


async def create_user_mapping_node(
  state: JobPostingExtractionState,
) -> JobPostingExtractionState:
  """사용자와 채용공고를 매핑합니다."""
  print("--- Creating user-job posting mapping ---")

  if not hasattr(state, "user_id") or not hasattr(state, "job_posting_id"):
    state.error_message = "Missing user_id or job_posting_id"
    state.success = False
    return state

  try:
    # 사용자와 채용공고 매핑 생성
    mapping = JobPostingUserMap(
      user_id=state.user_id, job_posting_id=state.job_posting_id
    )

    save_job_posting_user_map(mapping)

    print("Successfully created user-job posting mapping")

  except Exception as e:
    state.error_message = str(e)
    state.success = False
    print(f"Error creating user mapping: {e}")

  return state
