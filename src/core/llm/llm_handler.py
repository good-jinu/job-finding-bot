from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.core.llm.providers import get_chat_model, get_summarization_model
from typing import TypedDict, List
from src.core.schemas.job_posting import JobPosting
import json
from pathlib import Path


class MessageDict(TypedDict):
  name: str
  content: str


llm = get_chat_model()


# Load default prompt from file storage
def load_default_prompt() -> str:
  """Load default prompt from file storage."""
  prompt_file = Path(".file_storage/prompts/default_prompt.md")
  if prompt_file.exists():
    with open(prompt_file, "r", encoding="utf-8") as f:
      return f.read()
  return ""


default_prompt = load_default_prompt()

job_prompt_template = PromptTemplate(
  input_variables=["default_prompt", "job_context", "messages"],
  template="""{default_prompt}

    구인공고 정보는 다음과 같습니다:
    {job_context}

    다음 채팅의 답변을 해주세요
    ---
    {messages}

    ---

    위의 메세지 다음으로 적합한 답변을 작성해주세요.
    """,
)
job_llm_chain = job_prompt_template | llm | StrOutputParser()

general_prompt_template = PromptTemplate(
  input_variables=["default_prompt", "messages"],
  template="""{default_prompt}

다음 채팅의 답변을 해주세요
---
{messages}

---

위의 메세지 다음으로 적합한 태백이의 답변을 작성해주세요.
""",
)
general_llm_chain = general_prompt_template | llm | StrOutputParser()

summary_prompt_template = PromptTemplate(
  input_variables=["jobs"],
  template="""
    Analyze the following job listings data:
    {jobs}
    
    Based on the data, provide a summary covering:
    - Key job roles and titles.
    - Prominent skills or technologies mentioned.
    - Geographical distribution of jobs.
    - Any other notable trends.
    """,
)


def convert_messages_to_string(messages: List[MessageDict]) -> str:
  return "\n".join([f"{msg['name']}: {msg['content']}" for msg in messages])


async def get_job_ai_response(messages: List[MessageDict], job_info_context):
  context_string = ""
  if job_info_context:
    for i, job in enumerate(job_info_context):
      if job.get("title") is None:
        continue
      context_string += (
        f"--- Job {i + 1} ---\n"
        f"Title: {job.get('title', 'N/A')}\n"
        f"Company: {job.get('company', 'N/A')}\n"
        f"Link: {job.get('link', 'N/A')}\n"
      )
    if not context_string.strip():
      context_string = (
        "No specific job information found for this query in the loaded data."
      )
  else:
    context_string = (
      "No specific job information found for this query in the loaded data."
    )

  messages_string = convert_messages_to_string(messages)

  try:
    response = await job_llm_chain.ainvoke(
      {
        "default_prompt": default_prompt,
        "job_context": context_string,
        "messages": messages_string,
      }
    )
    return response
  except Exception as e:
    print(f"Error calling LangChain LLM: {e}")
    return (
      "Sorry, I'm having trouble processing your request with the AI at the moment."
    )


async def get_general_llm_response(messages: List[MessageDict]):
  messages_string = convert_messages_to_string(messages)

  try:
    response = await general_llm_chain.ainvoke(
      {"default_prompt": default_prompt, "messages": messages_string}
    )
    return response
  except Exception as e:
    print(f"Error calling LangChain LLM: {e}")
    return (
      "Sorry, I'm having trouble processing your request with the AI at the moment."
    )


async def get_summary_from_jobs(jobs: List[JobPosting]) -> str:
  """Generates a summary of the job listings."""
  llm = get_summarization_model()
  chain = summary_prompt_template | llm | StrOutputParser()

  jobs_dict = [job.model_dump() for job in jobs]
  jobs_str = json.dumps(jobs_dict, ensure_ascii=False)

  summary = await chain.ainvoke({"jobs": jobs_str})
  return summary
