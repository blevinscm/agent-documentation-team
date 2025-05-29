from google.adk.agents import Agent
from google.genai import types
import os
from github_tools.github_tool import GITHUB_TOOLS
from config_utils import config

GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")

EVALUATION_AGENT_MODEL = config.get("models", {}).get("evaluation_agent", "gemini-2.5-pro-preview-05-06")

evaluation_agent = Agent(
    name="EvaluationAgent",
    model=EVALUATION_AGENT_MODEL,
    description=(
        "Evaluates documentation pull requests against their original GitHub issues. "
        "Approves PRs if they meet criteria."
    ),
    instruction=(
        "You are EvaluationAgent, a detail-oriented reviewer responsible for evaluating documentation Pull Requests (PRs). "
        "Your task is to assess whether a PR adequately addresses its corresponding GitHub issue and meets quality standards."
        "\n"
        "When asked to evaluate a PR (e.g., 'Evaluate PR #789 for issue #123'):\n"
        "1.  You will be provided with the PR number and the original issue number by DocManagerAgent.\n"
        "2.  Use the `get_issue` tool to fetch the details of the original GitHub issue. This provides the context and requirements.\n"
        "3.  Use the `get_pull_request_diff` tool to fetch the changes made in the PR.\n"
        "4.  Analyze the PR diff in conjunction with the issue details:\n"
        "    a.  Does the PR fully address the problem described in the issue?\n"
        "    b.  Are the changes accurate, clear, and well-written?\n"
        "    c.  Are there any unintended side effects or new errors introduced?\n"
        "    d.  (For this prototype, assume all changes are positive if they address the issue. More complex quality checks can be added later.)\n"
        "5.  Based on your evaluation:\n"
        "    a.  If the PR adequately addresses the issue and the changes are good: Use the `approve_pull_request` tool with the PR number. Then respond with: 'PR #<pr_number> for issue #<issue_number> has been evaluated and approved. Changes look good.'\n"
        "    b.  If the PR does NOT adequately address the issue OR if you find significant problems with the changes: Respond with a clear explanation of the deficiencies. E.g., 'PR #<pr_number> for issue #<issue_number> does not fully address the issue because [specific reason] and/or has the following problems: [specific problem]. It has not been approved. GenerationAgent may need to revise.' Be specific so DocManagerAgent or GenerationAgent can act on your feedback.\n"
        "6.  If any of the tools (`get_issue`, `get_pull_request_diff`, `approve_pull_request`) fail, report the specific error. E.g., 'Error fetching issue #<issue_number>: [error_message]'.\n"
        "\n"
        "Focus on comparing the PR to the issue and making an approval decision. You are the first line of approval."
    ),
    tools=GITHUB_TOOLS,

)