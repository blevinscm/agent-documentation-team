# Agent-Documentation-Team (ADT)

A documentation automation system powered by Google Agent Development Kit (ADK) and GitHub APIs for creating and improving documenation hosted on Github Pages.

## Overview

Doc-Agent-Team is an intelligent system that automates the creation and maintenance of technical documentation. It leverages a multi-agent architecture to monitor documentation quality, respond to user feedback, generate improvements, and evaluate changes.

## Tech Stack

- **GitHub & GitHub Pages**: Source control and documentation hosting
   [GHPages Documenation](https://docs.github.com/en/pages)
   [Github Actions Documentation](https://docs.github.com/en/Actions)  
- **Google Agent Development Kit (ADK)**: Framework for building and deploying intelligent agents
   [Google ADK Documentation](google.github.io/adk-docs/)  
- **PyGithub**: Python library for interacting with GitHub API
   [PyGithub Documentation](https://pygithub.readthedocs.io/en/latest/)


## Architecture

The system consists of a supervisor agent and four specialized sub-agents:

```
┌─────────────────────────────────────────┐
│            Supervisor Agent             │
└───────────┬─────────┬─────────┬─────────┘
            │         │         │
┌───────────▼─┐ ┌─────▼─────┐ ┌─▼─────────┐ ┌─────────────┐
│   Social    │ │    QA     │ │Generation │ │ Evaluation  │
│ Analysis    │ │   Agent   │ │   Agent   │ │   Agent     │
│   Agent     │ │           │ │           │ │             │
└─────────────┘ └───────────┘ └───────────┘ └─────────────┘
```

### Agents

1. **Social Analysis Agent**
   - Monitors social media platforms for negative sentiment about documentation
   - Analyzes feedback to identify specific documentation issues
   - Creates GitHub issues via Github API exposed as ADK Tool

2. **QA Agent**
   - Performs regular scheduled analysis of documentation
   - Evaluates tone, quality, factuality, and code correctness
   - Creates GitHub issues via Github API exposed as ADK Tool


3. **Generation Agent**
   - Triggered by new issues created in the repository
   - Generates documentation improvements addressing the issues
   - Commits changes to a dedicated GenAI branch
   - Creates pull requests to main via Github API exposed as ADK Tool

4. **Evaluation Agent**
   - Analyzes pull requests created by the Generation Agent
   - Performs quality assessment and validation of proposed changes
   - Serves as the first approver for any PR and checks the PR against the issue intent
   - Provides feedback to improve generation quality

## Workflow

1. The **Social Analysis Agent** continuously monitors social channels for documentation feedback
2. The **QA Agent** runs on scheduled intervals to analyze documentation quality
3. Both agents create GitHub issues when problems are detected
4. The **Generation Agent** responds to new issues by creating documentation improvements
5. The **Evaluation Agent** reviews and approves high-quality changes as the first PR approver and a human Technical Writer will be the final approver.



### Prerequisites


- GitHub repository with GitHub Pages enabled
- API access to desired social media platforms
- Google ADK and GitHub PAT

### Configuration

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/doc-agent-mcp.git
   cd doc-agent-mcp
   ```

2. Set up a Python virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Configure environment variables for API access:
   ```
   export GITHUB_TOKEN="your-token"
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
   export SOCIAL_MEDIA_API_KEYS="your-keys"
   ```

4. Deploy to Google Cloud Run:
   ```
   gcloud run deploy doc-agent-mcp --source .
   ```

## Usage

Once deployed, the system runs autonomously with the following touchpoints:

- **Monitoring Dashboard**: View agent activities and metrics
- **Configuration UI**: Adjust agent parameters and thresholds
- **Manual Triggers**: Force specific agent actions when needed

