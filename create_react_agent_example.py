from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent


@tool
def multiply(a: int, b: int) -> int:
  """Multiply two numbers."""
  return a * b


agent = create_react_agent(model="anthropic:claude-3-7-sonnet", tools=[multiply])
agent.invoke({"messages": [{"role": "user", "content": "what's 42 x 7?"}]})
