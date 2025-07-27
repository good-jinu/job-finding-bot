from langgraph.graph import StateGraph, END
from src.core.schemas.resume_maker import ResumeMakerState
from src.core.services.resume_maker.nodes import (
  load_resume_sources_node,
  plan_resume_node,
  generate_resume_node,
  save_resume_node,
  update_user_resume_file_node,
)


def build_resume_maker_workflow():
  """Resume maker 워크플로우를 구축합니다."""

  # 워크플로우 그래프 생성
  workflow = StateGraph(ResumeMakerState)

  # 노드 추가
  workflow.add_node("load_resume_sources", load_resume_sources_node)
  workflow.add_node("plan_resume", plan_resume_node)
  workflow.add_node("generate_resume", generate_resume_node)
  workflow.add_node("save_resume", save_resume_node)
  workflow.add_node("update_user_resume_file", update_user_resume_file_node)

  # 엣지 연결 (순차적 실행)
  workflow.set_entry_point("load_resume_sources")
  workflow.add_edge("load_resume_sources", "plan_resume")
  workflow.add_edge("plan_resume", "generate_resume")
  workflow.add_edge("generate_resume", "save_resume")
  workflow.add_edge("save_resume", "update_user_resume_file")
  workflow.add_edge("update_user_resume_file", END)

  return workflow.compile()


async def run_resume_maker(job_target: str = "", user_id: str = ""):
  """Resume maker를 실행합니다."""

  # 초기 상태 설정 (단순화된 State에 맞게 수정)
  initial_state = ResumeMakerState(
    user_id=user_id,
    job_target=job_target,
  )

  # 워크플로우 실행
  workflow = build_resume_maker_workflow()
  final_state = await workflow.ainvoke(initial_state)

  return final_state
