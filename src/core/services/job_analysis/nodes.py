from datetime import datetime
from langchain_core.prompts import PromptTemplate
from src.core.llm.providers import get_job_analysis_model
from src.core.schemas.job_analysis import JobAnalysisState
from src.core.database.job_postings import get_unread_job_posting
from src.core.file_storage.paths import FileStoragePaths
from src.core.file_storage.file_manager import FileManager
from src.core.database.users import get_all_users
import random


# Initialize file storage
file_paths = FileStoragePaths()
file_manager = FileManager(file_paths)


async def scrape_job_details_node(state: JobAnalysisState) -> JobAnalysisState:
  """채용공고 텍스트 파일을 읽어서 상세 정보를 가져옵니다."""
  print("--- Reading Job Details from Content File ---")

  try:
    # Get job posting from database
    job_posting = get_unread_job_posting()

    if not job_posting:
      print("No unread job posting found")
      state["detailed_job_info"] = state["job_description"]
      return state

    # Read content from content_doc file
    if job_posting.content_doc:
      content_file = file_paths.get_job_content_path(job_posting.content_doc)
      text_content = file_manager.read_file_sync(content_file)
      if text_content:
        state["detailed_job_info"] = text_content
        print(f"Successfully read job details from {content_file}")
      else:
        print(f"Content file not found: {content_file}")
        state["detailed_job_info"] = job_posting.description
    else:
      # Fallback to description if content_doc is not provided
      state["detailed_job_info"] = job_posting.description

  except Exception as e:
    print(f"Error reading job details: {e}")
    state["detailed_job_info"] = state.get("job_description", "")

  return state


def load_resume_node(state: JobAnalysisState) -> JobAnalysisState:
  """이력서 파일을 로드합니다."""
  print("--- Loading Resume ---")

  # Get a random user and their resume file
  users = get_all_users()
  if not users:
    state["resume_content"] = "사용자가 없습니다."
    return state

  # Select random user if no specific user_id is provided
  if hasattr(state, "user_id") and state.user_id:
    selected_user = next((user for user in users if user.id == state.user_id), None)
    if not selected_user:
      selected_user = random.choice(users)
  else:
    selected_user = random.choice(users)

  if selected_user and selected_user.resume_file:
    resume_path = file_paths.get_resume_path(selected_user.resume_file)
    resume_content = file_manager.read_file_sync(resume_path)
    if resume_content:
      state["resume_content"] = resume_content
      state["user_id"] = selected_user.id  # Store which user's resume we used
      print(f"Loaded resume for user {selected_user.name} from {resume_path}")
    else:
      state["resume_content"] = "이력서 파일을 찾을 수 없습니다."
      print("Resume file not found")
  else:
    state["resume_content"] = "이력서가 없습니다."
    print("No resume file available")

  return state


async def analyze_job_fit_node(state: JobAnalysisState) -> JobAnalysisState:
  """채용공고와 이력서의 적합성을 분석합니다."""
  print("--- Starting Job Fit Analysis ---")

  # LLM 설정 - providers에서 가져오기
  llm = get_job_analysis_model()

  prompt = PromptTemplate(
    template="""
당신은 전문적인 채용 컨설턴트입니다. 주어진 채용공고와 이력서를 분석하여 
적합성을 평가하고 상세한 분석 보고서를 작성해주세요.

## 채용공고 정보:
{job_info}

## 이력서:
{resume}

## 분석 요구사항:
1. 지원자의 강점과 약점 식별
2. 보완해야 할 점과 개선 방안 제시
3. 지원 시 강조해야 할 포인트 제안
4. 전반적인 적합성 평가

다음과 같은 문서 형식으로 분석 결과를 작성해주세요:

# 채용공고 분석 보고서

## 📋 기본 정보
- **채용공고**: [직무 제목]
- **회사**: [회사명]
- **근무지**: [위치]

## ✅ 지원자 강점
[지원자의 강점을 상세히 분석]

## ⚠️ 보완 필요 사항
[보완해야 할 점들을 제시]

## 🔧 개선 방안
[개선 방안들을 구체적으로 제안]

## 💡 지원 전략
[지원 시 활용할 전략적 제안]

## 📝 종합 평가
[전반적인 적합성 평가 및 결론]
""",
    input_variables=["job_info", "resume"],
  )

  try:
    chain = prompt | llm
    result = await chain.ainvoke(
      {"job_info": state["detailed_job_info"], "resume": state["resume_content"]}
    )
    print("Job analysis completed successfully")
    state["analysis_result"] = str(result.content)

  except Exception as e:
    print(f"Error in job analysis: {e}")
    state["analysis_result"] = f"분석 중 오류가 발생했습니다: {str(e)}"

  return state


def generate_report_node(state: JobAnalysisState) -> JobAnalysisState:
  """분석 결과를 바탕으로 상세한 보고서를 생성합니다."""
  print("--- Generating Analysis Report ---")

  try:
    analysis_data = state["analysis_result"]

    print(f"Analysis result: {analysis_data[:100]}...")  # Show first 100 chars

    # Use the analysis result as-is since it's already formatted text
    report = f"""# 채용공고 분석 보고서

{analysis_data}

---
*분석 일시: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

    state["report_content"] = report

    # 파일로 저장
    output_path = file_paths.get_output_report_path("job_analysis")
    file_manager.write_file_sync(output_path, report)

    print(f"Report saved to: {output_path}")

  except Exception as e:
    print(f"Error generating report: {e}")
    state["report_content"] = "보고서 생성 중 오류가 발생했습니다."

  return state
