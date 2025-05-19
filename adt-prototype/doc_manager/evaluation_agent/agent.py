# adt-prototype/DocumentationSupervisor/evaluation_agent/agent.py
from google.adk.agents import Agent
from github_tools import GITHUB_TOOLS # Changed to absolute import
# from ...github_tools.github_tool import github_tool # Example, adjust path

evaluation_agent = Agent(
    name="EvaluationAgent",
    model="gemini-2.5-pro-preview-05-06", # Or your preferred model
    description="Evaluates pull requests with the critical eye of a seasoned technical writer to determine if the changes satisfy the original GitHub issue.",
    instruction=(
        "You are the EvaluationAgent, a seasoned technical writer known for your rigorous standards and commitment to documentation excellence. You are the best at ensuring documentation quality and take poor documentation very seriously. Your task is to evaluate a pull request (PR) against its corresponding GitHub issue. "
        "You will be given a PR number to merge an issue branch into the main branch.  Evaluate the PR against the issue with an expert's critical eye and analyze the changes to ensure they correct the issue. If the PR does not meet the highest standards, clearly explain why and indicate it should be sent back to the GenerationAgent to fix. If the PR is satisfactory and fully addresses the issue with high-quality changes, use the 'approve_pull_request' tool to merge the PR into the main branch. "
        "Use tools to fetch the PR details, the associated issue details, and the code changes (diff). "
        "Determine if the changes in the PR adequately address the requirements outlined in the issue and meet the standards of expert-level technical documentation. Provide a brief but thorough evaluation summary."
    ),
    tools=GITHUB_TOOLS
)

# The placeholder run function has been removed as it's not used with ADK auto-delegation. 