from langgraph.graph import StateGraph, END
from src.core.schemas.job_posting import JobPostingExtractionState
from src.core.services.job_posting_extractor.nodes import (
  fetch_html_node,
  convert_to_markdown_node,
  extract_job_details_node,
  save_job_posting_node,
  create_user_mapping_node,
)


def build_job_posting_extractor_workflow():
  """채용공고 추출 워크플로우를 구축합니다."""

  # 워크플로우 그래프 생성
  workflow = StateGraph(JobPostingExtractionState)

  # 노드 추가
  workflow.add_node("fetch_html", fetch_html_node)
  workflow.add_node("convert_to_markdown", convert_to_markdown_node)
  workflow.add_node("extract_job_details", extract_job_details_node)
  workflow.add_node("save_job_posting", save_job_posting_node)
  workflow.add_node("create_user_mapping", create_user_mapping_node)

  # 엣지 연결 (순차적 실행)
  workflow.set_entry_point("fetch_html")
  workflow.add_edge("fetch_html", "convert_to_markdown")
  workflow.add_edge("convert_to_markdown", "extract_job_details")
  workflow.add_edge("extract_job_details", "save_job_posting")
  workflow.add_edge("save_job_posting", "create_user_mapping")
  workflow.add_edge("create_user_mapping", END)

  return workflow.compile()


async def run_job_posting_extractor(job_url: str, user_id: str):
  """채용공고 추출을 실행합니다."""

  # 초기 상태 설정
  initial_state = JobPostingExtractionState(
    job_url=job_url,
  )

  # 워크플로우 실행
  workflow = build_job_posting_extractor_workflow()

  # user_id를 컨텍스트로 전달하기 위해 상태에 추가
  initial_state.user_id = user_id

  final_state = await workflow.ainvoke(initial_state)

  return final_state
