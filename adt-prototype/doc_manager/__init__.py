from .agent import root_agent

agent = root_agent

__all__ = ["agent"]

from .qa_agent.agent import qa_agent
from .generation_agent.agent import generation_agent
from .evaluation_agent.agent import evaluation_agent

__all__ = [
    "root_agent",
    "qa_agent",
    "generation_agent",
    "evaluation_agent",
]