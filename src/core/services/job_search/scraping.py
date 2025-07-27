from typing import List, Optional
from browser_use.llm import ChatGoogle
from browser_use import Agent, Controller
from browser_use.browser import BrowserProfile
from dotenv import load_dotenv
from src.core.schemas.job_posting import JobPosting, JobPostingList
from src.core.database.job_postings import save_job_postings, update_content_doc
from src.core.file_storage.file_manager import FileManager
from src.core.file_storage.paths import FileStoragePaths
from src.core.services.utils.generate_random_data import generate_random_string
from urllib.parse import quote

load_dotenv()

# Browser profile and LLM configuration
profile = BrowserProfile(
  stealth=True,
  wait_between_actions=5,
  user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
)
llm = ChatGoogle(model="gemini-2.5-flash")

# File storage initialization
file_paths = FileStoragePaths()
file_manager = FileManager(file_paths)


async def get_job_search_urls(keyword: str) -> List[str]:
  """검색 키워드에 대한 채용 사이트 URL 목록을 생성합니다."""
  encoded_keyword = quote(keyword)
  return [
    f"https://www.jobkorea.co.kr/Search/?stext={encoded_keyword}",
    f"https://www.wanted.co.kr/search?query={encoded_keyword}&tab=overview",
    f"https://www.saramin.co.kr/zf_user/search?search_area=main&search_done=y&search_optional_item=n&searchType=search&searchword={encoded_keyword}",
  ]


async def collect_job_postings(search_page_url: str) -> List[JobPosting]:
  """
  (목록 페이지용) 검색 결과 목록에서 'JobPosting' 객체 리스트를 추출하여 반환합니다.
  """
  controller = Controller(output_model=JobPostingList)
  task = (
    f"현재 페이지({search_page_url})에서 채용 공고 목록을 추출해줘. "
    "각 공고마다 'title', 'company', 'location', 상세 정보 'url'을 포함한 'JobPosting' 객체를 생성해줘. "
    "목록 페이지에서 상세 설명(description)이나 등록일(posted_at)을 알 수 없다면 비워둬도 괜찮아. "
    "content_doc은 비워둬."
  )

  agent = Agent(
    task=task,
    llm=llm,
    profile=profile,
    controller=controller,
    initial_actions=[{"go_to_url": {"url": search_page_url}}],
  )
  print(f"Collecting job postings from: {search_page_url}...")
  result_json = await agent.run()

  if not result_json:
    print(f"  -> No postings found from {search_page_url}")
    return []
  try:
    # 결과를 JobPostingList 모델로 파싱하고 내부의 postings 리스트를 반환
    parsed_data = JobPostingList.model_validate_json(result_json)
    print(f"  -> Collected {len(parsed_data.data_list)} postings.")
    return parsed_data.data_list
  except Exception as e:
    print(f"  -> Error parsing postings from {search_page_url}: {e}")
    return []


async def extract_job_detail_content(detail_url: str) -> Optional[str]:
  """
  채용 공고 상세 페이지에서 상세 내용을 추출하여 마크다운 형식으로 반환합니다.
  """
  controller = Controller()
  task = (
    f"이 채용 공고 페이지({detail_url})의 모든 상세 정보를 마크다운 형식으로 추출해줘. "
    "포함할 내용: 직무명, 회사명, 근무지역, 채용 상세 내용, 자격 요건, 우대 사항, "
    "근무 조건, 복리후생, 채용 절차 등 모든 관련 정보를 체계적으로 정리해줘."
  )

  agent = Agent(
    task=task,
    llm=llm,
    profile=profile,
    controller=controller,
    initial_actions=[{"go_to_url": {"url": detail_url}}],
  )
  print(f"Extracting detail content from: {detail_url}...")
  result = await agent.run()

  if result:
    print("  -> Successfully extracted content")
    return result
  else:
    print("  -> Failed to extract content")
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
    print(f"🔍 Found {len(search_urls)} search pages for keyword '{keyword}'.")
    print("-" * 30)

    # Step 2: 모든 검색 페이지에서 JobPosting 객체 목록 수집
    initial_postings: List[JobPosting] = []
    for url in search_urls:
      try:
        postings = await collect_job_postings(url)
        initial_postings.extend(postings)
      except Exception as e:
        print(f"Error collecting postings from {url}: {e}")

    # 중복 URL을 가진 객체 제거
    unique_postings = {p.url: p for p in initial_postings if p.url}.values()
    print(f"\nTotal unique job postings found from lists: {len(unique_postings)}")
    print("-" * 30)

    # Step 3: DB에 JobPosting 저장 (content_doc은 비어있음)
    postings_to_save = list(unique_postings)[:5]  # 데모를 위해 5개만 실행
    save_job_postings(postings_to_save)
    print(f"Saved {len(postings_to_save)} job postings to database")

    # Step 4: 각 공고의 상세 URL로 접속하여 상세 내용 추출 및 파일 저장
    for posting in postings_to_save:
      try:
        # 상세 내용 추출
        detail_content = await extract_job_detail_content(posting.url)

        if detail_content:
          # 파일명 생성
          random_str = generate_random_string()
          filename = f"{posting.id}_{random_str}.md"

          # 파일 저장
          file_path = file_paths.get_job_content_path(filename)
          success = await file_manager.write_file_async(file_path, detail_content)

          if success:
            # content_doc 업데이트
            if posting.id:
              update_content_doc(posting.id, filename)
              posting.content_doc = filename
              print(f"  -> Saved content to {filename} and updated database")
            else:
              print("  -> Warning: Job posting has no ID, cannot update content_doc")
          else:
            print(f"  -> Failed to save content file for {posting.url}")
        else:
          print(f"  -> No content extracted for {posting.url}")

        final_results.append(posting)

      except Exception as e:
        print(f"Error processing detail for {posting.url}: {e}")
        final_results.append(posting)  # 에러가 있어도 기본 정보는 포함

    # 최종 결과 출력
    print("\n" + "=" * 50)
    print(f"🎉 Total job postings processed: {len(final_results)}")
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
    print(f"An error occurred in the job postings collection process: {e}")

  return final_results
