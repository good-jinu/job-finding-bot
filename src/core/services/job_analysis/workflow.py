from langgraph.graph import StateGraph, END
from src.core.schemas.job_analysis import JobAnalysisState
from src.core.services.job_analysis.nodes import (
  scrape_job_details_node,
  load_resume_node,
  analyze_job_fit_node,
  generate_report_node,
)


def build_job_analysis_workflow():
  """채용공고 분석 워크플로우를 구축합니다."""

  # 워크플로우 그래프 생성
  workflow = StateGraph(JobAnalysisState)

  # 노드 추가
  workflow.add_node("scrape_job_details", scrape_job_details_node)
  workflow.add_node("load_resume", load_resume_node)
  workflow.add_node("analyze_job_fit", analyze_job_fit_node)
  workflow.add_node("generate_report", generate_report_node)

  # 엣지 연결 (순차적 실행)
  workflow.set_entry_point("scrape_job_details")
  workflow.add_edge("scrape_job_details", "load_resume")
  workflow.add_edge("load_resume", "analyze_job_fit")
  workflow.add_edge("analyze_job_fit", "generate_report")
  workflow.add_edge("generate_report", END)

  return workflow.compile()


async def run_job_analysis(
  user_id: str = "",
):
  """채용공고 분석을 실행합니다."""

  # 초기 상태 설정
  initial_state = JobAnalysisState(
    resume_content="",
    detailed_job_info="",
    analysis_result="",
    report_content="",
    user_id=user_id,
  )

  # 워크플로우 실행
  workflow = build_job_analysis_workflow()
  final_state = await workflow.ainvoke(initial_state)

  return final_state
