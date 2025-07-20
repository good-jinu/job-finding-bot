from langchain_community.chat_models import ChatDeepInfra
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_google_genai import ChatGoogleGenerativeAI

# LLM Model Configuration
STRUCTURED_OUTPUT_MODEL = "gemini-2.5-flash-lite-preview-06-17"
SUMMARIZATION_MODEL = "mistralai/Mistral-Small-3.2-24B-Instruct-2506"
AGENT_MODEL = "mistralai/Mistral-Small-3.2-24B-Instruct-2506"
CHAT_MODEL = "meta-llama/Llama-4-Scout-17B-16E-Instruct"
JOB_ANALYSIS_MODEL = "mistralai/Mistral-Small-3.2-24B-Instruct-2506"
RESUME_GENERATION_MODEL = "meta-llama/Llama-4-Scout-17B-16E-Instruct"


def get_chat_model():
  """Returns the configured chat model for general conversation."""
  limiter = InMemoryRateLimiter(
    requests_per_second=0.25,
    check_every_n_seconds=0.25,
    max_bucket_size=3,
  )
  return ChatDeepInfra(
    model=CHAT_MODEL, temperature=0.9, rate_limiter=limiter, max_tokens=20000
  )


def get_agent_model():
  """Returns the configured agent model."""
  limiter = InMemoryRateLimiter(
    requests_per_second=2,
    check_every_n_seconds=2,
    max_bucket_size=50,
  )
  return ChatDeepInfra(
    model=AGENT_MODEL,
    temperature=0.7,
    rate_limiter=limiter,
    max_tokens=20000,
  )


def get_structured_output_model():
  """Returns the configured structured output model."""
  limiter = InMemoryRateLimiter(
    requests_per_second=1,
    check_every_n_seconds=1,
    max_bucket_size=50,
  )
  return ChatGoogleGenerativeAI(
    model=STRUCTURED_OUTPUT_MODEL,
    temperature=0.0,
    rate_limiter=limiter,
    max_tokens=120000,
  )


def get_summarization_model():
  """Returns the configured summarization model."""
  limiter = InMemoryRateLimiter(
    requests_per_second=1,
    check_every_n_seconds=1,
    max_bucket_size=1,
  )
  return ChatDeepInfra(
    model=SUMMARIZATION_MODEL, temperature=0.1, rate_limiter=limiter, max_tokens=20000
  )


def get_job_analysis_model():
  """Returns the configured job analysis model."""
  limiter = InMemoryRateLimiter(
    requests_per_second=1,
    check_every_n_seconds=1,
    max_bucket_size=10,
  )
  return ChatDeepInfra(
    model=JOB_ANALYSIS_MODEL,
    temperature=0.8,
    rate_limiter=limiter,
    max_tokens=20000,
    max_retries=3,
  )

def get_resume_generation_model():
  """Returns the configured resume generation model."""
  limiter = InMemoryRateLimiter(
    requests_per_second=1,
    check_every_n_seconds=1,
    max_bucket_size=10,
  )
  return ChatDeepInfra(
    model=RESUME_GENERATION_MODEL,
    temperature=0.99,
    rate_limiter=limiter,
    max_tokens=20000,
    max_retries=3,
  )