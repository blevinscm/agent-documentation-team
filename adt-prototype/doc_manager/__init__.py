# adt-prototype/agents/__init__.py

# Import the main agent instance from the local agent.py module
# ADK web expects to find the main agent for the package here.
from .agent import root_agent # Import the agent instance defined in agent.py

# Expose the agent instance at the package level.
# While ADK might just look for the variable name 'agent',
# explicitly assigning and using __all__ is good practice.
agent = root_agent

# Explicitly list the agent instance for ADK discovery
__all__ = ["agent"]

# You can optionally import the run function if you need to call it directly from outside
# from .agent import run
# __all__.append("run")

# Imports for the sub-agents' run functions are NOT needed here
# because the orchestration logic is now back in agents/agent.py's run function.

# Imports for the sub-agent objects themselves are NOT needed here for ADK web discovery
# They are implicitly part of the root agent's team if added via `sub_agents=[]`
from .qa_agent.agent import qa_agent
from .generation_agent.agent import generation_agent
from .evaluation_agent.agent import evaluation_agent

# This file makes doc_manager a Python sub-package
# and optionally re-exports its constituent agents for easier imports elsewhere if needed,
# though for ADK discovery, only the root_agent in the top-level __init__.py matters primarily.

__all__ = [
    "root_agent",
    "qa_agent",
    "generation_agent",
    "evaluation_agent",
]