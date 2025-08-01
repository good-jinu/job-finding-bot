from typing import List, Optional
from browser_use.llm import ChatGoogle
from browser_use import Agent
from browser_use.browser import BrowserProfile
from dotenv import load_dotenv
from src.core.schemas.job_posting import JobPosting, JobPostingList
from src.core.database.job_postings import save_job_postings, update_content_doc
from src.core.file_storage.file_manager import FileManager
from src.core.file_storage.paths import FileStoragePaths
from src.core.services.utils.generate_random_data import generate_random_string
from urllib.parse import quote
from src.core.llm.providers import get_structured_output_model

load_dotenv()

# Browser profile and LLM configuration
profile = BrowserProfile(
  stealth=True,
  wait_between_actions=5,
  user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
)
# This LLM is used by the browser agent for navigation and simple extraction tasks.
llm = ChatGoogle(model="gemini-2.5-flash")

# File storage initialization
file_paths = FileStoragePaths()
file_manager = FileManager(file_paths)


async def get_job_search_urls(keyword: str) -> List[str]:
  """검색 키워드에 대한 채용 사이트 URL 목록을 생성합니다."""
  encoded_keyword = quote(keyword)
  return [
    f"https://www.jobkorea.co.kr/Search/?stext={encoded_keyword}",
    # f"https://www.wanted.co.kr/search?query={encoded_keyword}&tab=overview",
    # f"https://www.saramin.co.kr/zf_user/search?search_area=main&search_done=y&search_optional_item=n&searchType=search&searchword={encoded_keyword}",
  ]


async def collect_job_postings(search_page_url: str) -> List[JobPosting]:
  """
  (목록 페이지용) 검색 결과 목록에서 'JobPosting' 객체 리스트를 추출하여 반환합니다.
  브라우저로 텍스트를 스크랩한 후 LLM을 사용하여 JobPostingList로 구조화합니다.
  """
  task = (
    f"현재 페이지({search_page_url})에서 채용 공고 목록을 텍스트로 추출해줘. "
    "각 공고마다 'title', 'company', 'location', 상세 정보 'url'을 포함해야 해. "
    "최대한 많은 공고를 수집하기 위해 필요하다면 스크롤을 내려줘. 그런데 딱 한페이지만 스크랩해줘. "
  )

  agent = Agent(
    task=task,
    llm=llm,
    profile=profile,
    initial_actions=[{"go_to_url": {"url": search_page_url}}],
  )
  print(f"Collecting job postings from: {search_page_url}...")

  try:
    history = await agent.run()
    scraped_text = history.final_result()

    if not scraped_text or not scraped_text.strip():
      print("  -> Agent가 비어있는 최종 결과를 반환했습니다.")
      return []

    # LLM을 사용하여 텍스트를 구조화합니다.
    structured_llm = get_structured_output_model().with_structured_output(
      JobPostingList
    )

    prompt = f"""다음 텍스트에서 채용 공고 정보를 추출하여 JSON 형식으로 만들어줘.
각 공고는 'title', 'company', 'location', 'url' 필드를 포함해야 해.
결과는 'jobs'라는 키를 가진 JSON 객체여야 해.

---
{scraped_text}
---
"""

    job_posting_list = await structured_llm.ainvoke(prompt)

    if job_posting_list and hasattr(job_posting_list, "jobs"):
      print(
        f"  -> LLM이 {len(job_posting_list.jobs)}개의 공고를 성공적으로 구조화했습니다."
      )
      return job_posting_list.jobs
    else:
      print("  -> LLM이 텍스트에서 공고를 구조화하지 못했습니다.")
      return []

  except Exception as e:
    print(f"  -> 공고 수집 중 오류 발생: {e}")
    return []


async def extract_and_structure_job_detail(detail_url: str) -> Optional[JobPosting]:
  """
  채용 공고 상세 페이지에서 상세 내용을 추출하고 JobPosting 객체로 변환합니다.
  """
  task = (
    f"이 채용 공고 페이지({detail_url})의 모든 상세 정보를 마크다운 형식으로 추출해줘. "
    "포함할 내용: 직무명, 회사명, 근무지역, 채용 상세 내용, 자격 요건, 우대 사항, "
    "근무 조건, 복리후생, 채용 절차 등 모든 관련 정보를 체계적으로 정리해줘."
  )

  agent = Agent(
    task=task,
    llm=llm,
    profile=profile,
    initial_actions=[{"go_to_url": {"url": detail_url}}],
  )
  print(f"Extracting detail content from: {detail_url}...")

  try:
    history = await agent.run()
    scraped_text = history.final_result()

    if not scraped_text or not scraped_text.strip():
      print("  -> 에이전트 응답에서 콘텐츠를 찾을 수 없습니다.")
      return None

    print("  -> 성공적으로 상세 내용을 텍스트로 추출했습니다. 이제 구조화합니다...")

    # LLM을 사용하여 텍스트를 구조화합니다.
    structured_llm = get_structured_output_model().with_structured_output(JobPosting)

    prompt = f"""다음 채용 공고 텍스트를 분석해서 JobPosting 객체에 맞는 JSON으로 만들어줘.
- 'url' 필드는 '{detail_url}' 로 설정해줘.
- 'title', 'company', 'location' 필드를 텍스트에서 추출해줘.
- 'description' 필드에는 전체 공고 내용을 마크다운 형식으로 정리해서 넣어줘.
- 'posted_at' 필드는 등록일 또는 마감일을 'YYYY-MM-DD' 형식으로 추출하거나, '상시채용' 같은 텍스트를 넣어줘. 찾을 수 없으면 비워둬.
- 'id', 'created_at', 'updated_at', 'content_doc' 필드는 비워둬.

---
{scraped_text}
---
"""

    job_posting = await structured_llm.ainvoke(prompt)

    if job_posting:
      print("  -> 성공적으로 상세 내용을 구조화했습니다.")
      return job_posting
    else:
      print("  -> LLM이 텍스트에서 공고 상세 정보를 구조화하지 못했습니다.")
      return None

  except Exception as e:
    print(f"  -> 상세 내용 추출 및 구조화 중 오류 발생: {e}")
    return None


async def collect_and_extract_job_postings(
  keyword: str = "프론트엔드 개발자",
) -> List[JobPosting]:
  """
  주어진 키워드로 여러 채용 사이트에서 공고 목록을 수집하고,
  각 공고의 상세 정보를 추출하여 JobPosting 리스트로 반환합니다.
  """
  final_results: List[JobPosting] = []

  try:
    # Step 1: 검색할 채용 사이트 목록 가져오기
    search_urls = await get_job_search_urls(keyword)
    print(f"🔍 '{keyword}' 키워드로 {len(search_urls)}개의 채용 사이트를 검색합니다.")
    print("-" * 30)

    # Step 2: 모든 검색 페이지에서 JobPosting 객체 목록 수집
    initial_postings: List[JobPosting] = []
    for url in search_urls:
      try:
        postings = await collect_job_postings(url)
        initial_postings.extend(postings)
      except Exception as e:
        print(f"{url} 에서 공고 수집 중 에러 발생: {e}")

    # 중복 URL을 가진 객체 제거
    unique_postings = list({p.url: p for p in initial_postings if p.url}.values())
    print(f"\n총 {len(unique_postings)}개의 고유한 채용 공고를 찾았습니다.")
    print("-" * 30)

    if not unique_postings:
      print("처리할 채용 공고가 없습니다. 작업을 종료합니다.")
      return []

    # Step 3: DB에 JobPosting 저장 (초기 정보)
    # 데모를 위해 5개만 실행 (실제 운영 시 이 부분을 조절하세요)
    initial_postings_to_process = unique_postings[:5]
    saved_postings = save_job_postings(initial_postings_to_process)
    print(
      f"{len(saved_postings)}개의 채용 공고를 데이터베이스에 저장하고 ID를 부여했습니다."
    )

    # Step 4: 각 공고의 상세 URL로 접속하여 상세 내용 추출, 구조화 및 업데이트
    for posting in saved_postings:
      try:
        if not posting.id:
          print(
            f"  -> 경고: {posting.url} 공고가 저장 후 ID가 없습니다. 상세 정보 처리를 건너뜁니다."
          )
          final_results.append(posting)
          continue

        # 상세 정보 추출 및 구조화
        detailed_posting = await extract_and_structure_job_detail(posting.url)

        if detailed_posting and detailed_posting.description:
          # 파일명 생성
          random_str = generate_random_string()
          filename = f"{posting.id}_{random_str}.md"

          # 파일 저장
          file_path = file_paths.get_job_content_path(filename)
          success = await file_manager.write_file_async(
            file_path, detailed_posting.description
          )

          if success:
            # content_doc DB 업데이트
            update_content_doc(posting.id, filename)
            posting.content_doc = filename
            print(
              f"  -> 상세 내용을 {filename}에 저장하고 데이터베이스를 업데이트했습니다."
            )

            # 참고: DB에 전체 상세내용(description, posted_at 등)을 업데이트하려면
            # `src/core/database/job_postings.py`에 `update_job_posting(id, data)`와 같은
            # 범용 업데이트 함수가 필요합니다. 현재는 메모리의 객체만 업데이트합니다.
            posting.description = detailed_posting.description
            posting.posted_at = detailed_posting.posted_at
            posting.title = detailed_posting.title or posting.title
            posting.company = detailed_posting.company or posting.company
            posting.location = detailed_posting.location or posting.location

          else:
            print(f"  -> {posting.url}의 상세 내용 파일 저장에 실패했습니다.")
        else:
          print(f"  -> {posting.url}의 상세 내용을 추출하거나 구조화하지 못했습니다.")

        final_results.append(posting)

      except Exception as e:
        print(f"{posting.url}의 상세 정보 처리 중 오류 발생: {e}")
        final_results.append(posting)

    # 최종 결과 출력
    print("\n" + "=" * 50)
    print(f"🎉 총 {len(final_results)}개의 채용 공고 처리가 완료되었습니다.")
    print("=" * 50)

    for i, job in enumerate(final_results, 1):
      print(f"\n--- Job Posting #{i} ---")
      print(f"  ID: {job.id}")
      print(f"  URL: {job.url}")
      print(f"  Title: {job.title}")
      print(f"  Company: {job.company}")
      print(f"  Location: {job.location}")
      print(f"  Posted At: {job.posted_at or 'N/A'}")
      print(f"  Content Doc: {job.content_doc or 'N/A'}")
      if job.description:
        print(f"  Description: {job.description[:100].strip()}...")

  except Exception as e:
    print(f"채용 공고 수집 프로세스에서 에러가 발생했습니다: {e}")

  return final_results
