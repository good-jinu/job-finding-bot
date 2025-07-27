from langgraph.graph import StateGraph, END
from src.core.schemas.job_search import JobSearchState
from .nodes import (
  get_resume_content_node,
  extract_keywords_from_resume_node,
  search_and_scrape_jobs_node,
)


def create_job_search_workflow():
  """이력서 기반 채용공고 검색 및 스크래핑 워크플로우를 생성합니다."""
  workflow = StateGraph(JobSearchState)

  # Add nodes
  workflow.add_node("get_resume", get_resume_content_node)
  workflow.add_node("extract_keywords", extract_keywords_from_resume_node)
  workflow.add_node("search_and_scrape_jobs", search_and_scrape_jobs_node)

  # Set entry point
  workflow.set_entry_point("get_resume")

  # Add edges
  workflow.add_edge("get_resume", "extract_keywords")
  workflow.add_edge("extract_keywords", "search_and_scrape_jobs")
  workflow.add_edge("search_and_scrape_jobs", END)

  return workflow.compile()


async def run_job_search_workflow(user_id: str):
  """사용자 이력서 기반으로 채용공고를 검색하고 결과를 반환합니다."""
  app = create_job_search_workflow()
  initial_state = {"user_id": user_id}
  final_state = await app.ainvoke(initial_state)
  return final_state
