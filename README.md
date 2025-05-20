# Agent Documentation Team (ADT)

## Overview

The Agent Documentation Team (ADT) is a multi-agent system built using the Google Agent Development Kit (ADK). It's designed to help manage and maintain documentation within a GitHub repository. ADT automates parts of the documentation lifecycle, including identifying issues, generating content, creating pull requests, and evaluating those PRs.

The system is orchestrated by a `DocManagerAgent` which coordinates three specialized sub-agents:

1.  **`QAAgent`**: Analyzes documentation files for errors, inaccuracies, or areas needing improvement. If issues are found, it automatically creates a GitHub issue using a predefined template.
2.  **`GenerationAgent`**: Takes a GitHub issue (either created by `QAAgent` or manually), generates the necessary content fix, creates a new branch for the issue, commits the changes, and opens a pull request.
3.  **`EvaluationAgent`**: Reviews a pull request created by the `GenerationAgent` to ensure it adequately addresses the original issue and meets quality standards. It can then approve the pull request.

## Features

*   Automated QA checks on documentation files.
*   Automatic creation of GitHub issues for identified documentation errors.
*   Automated generation of documentation fixes based on GitHub issues.
*   Automatic creation of feature branches and pull requests for documentation changes.
*   Automated evaluation and approval of pull requests.
*   Configuration-driven model selection and GitHub settings.

## Prerequisites

*   Python 3.10 or higher
*   Git
*   A GitHub account
*   Access to Google's Gemini API (for the LLM driving the agents)

## Setup & Installation

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd agent-doc-team
    ```

2.  **Create and Activate a Virtual Environment (Recommended):**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    # On Windows, use: .venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    Navigate to the `adt-prototype` directory and install the required packages:
    ```bash
    cd adt-prototype
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables:**
    You'll need to configure a few environment variables. Create a file named `.env` in the `adt-prototype` directory (`adt-prototype/.env`) with the following content:

    ```env
    GITHUB_TOKEN="your_github_personal_access_token"
    GITHUB_REPOSITORY="owner/repository_name" # e.g., blevinscm/genai-docs
    GOOGLE_API_KEY="your_google_gemini_api_key"
    ```

    *   **`GITHUB_TOKEN`**: A GitHub Personal Access Token (PAT) with the `repo` scope.
    *   **`GITHUB_REPOSITORY`**: The full name of the GitHub repository you want the ADT to manage (e.g., `your-username/your-doc-repo`).
    *   **`GOOGLE_API_KEY`**: Your API key for Google's Gemini models.

5.  **Configure the Application:**
    The application uses a `config.toml` file located in the `adt-prototype` directory (`adt-prototype/config.toml`) for settings like model names and GitHub base branch. Review and customize this file as needed. See the "Configuration File" section below for more details.

## Running the Application

1.  **Ensure you are in the `adt-prototype` directory:**
    ```bash
    # If you are in the root 'agent-doc-team' directory:
    cd adt-prototype
    ```

2.  **Start the ADK Web Server:**
    ```bash
    adk web
    ```
    This will start a local web server (usually on `http://127.0.0.1:8000` or a similar port) where you can interact with the deployed agents.

3.  **Interact with the `DocManagerAgent`:**
    Open your web browser and navigate to the ADK web UI. You should see the `doc_manager_agent` listed. This is the primary agent to interact with.

## Usage Examples

In the ADK web UI, select the `doc_manager_agent` and try the following prompts:

*   **To initiate a QA check on a specific file:**
    ```
    QA file docs/intro.md
    ```
    (Replace `docs/intro.md` with the actual path to a file in your configured `GITHUB_REPOSITORY`)

*   The `DocManagerAgent` should then autonomously guide the process:
    *   `QAAgent` will analyze the file and create an issue if errors are found.
    *   `DocManagerAgent` will then trigger `GenerationAgent` with the new issue number.
    *   `GenerationAgent` will create a branch, commit a fix, and create a PR.
    *   `DocManagerAgent` will then trigger `EvaluationAgent` to review the PR.
    *   `EvaluationAgent` will approve the PR if the fix is satisfactory.

You can monitor the progress and see tool calls in the ADK web UI and the console where you ran `adk web`.

## Project Structure

*   `agent-doc-team/`
    *   `adt-prototype/`: Contains the core ADK agent implementation.
        *   `doc_manager/`: The main agent package.
            *   `agent.py`: Defines the `DocManagerAgent` (root orchestrator).
            *   `qa_agent/`, `generation_agent/`, `evaluation_agent/`: Sub-directories for the specialized agents, each with their `agent.py` definitions.
        *   `github_tools/`: Contains `github_tool.py`, which defines functions for interacting with the GitHub API.
        *   `config_utils.py`: Loads and provides access to settings from `config.toml`.
        *   `config.toml`: Configuration file for model names, GitHub settings, etc.
        *   `.env`: (You create this) For environment variables (secrets).
        *   `requirements.txt`: Python dependencies.
    *   `.gitignore`: Specifies intentionally untracked files that Git should ignore.
    *   `README.md`: (This file) Project overview and setup instructions.

## Configuration File (`adt-prototype/config.toml`)

The `config.toml` file allows you to customize various aspects of the ADT application without modifying the code directly. Here's a breakdown of its sections:

```toml
[general]
# Specifies the default base branch for GitHub operations (e.g., when creating pull requests).
github_base_branch = "main"

[models]
# Defines the specific Gemini model versions to be used by each agent.
# If a model is not specified here or the config file is missing,
# the agents will fall back to a default model specified in their definitions.
doc_manager_agent = "gemini-2.5-pro-preview-05-06"
qa_agent = "gemini-2.5-pro-preview-05-06"
generation_agent = "gemini-2.5-pro-preview-05-06"
evaluation_agent = "gemini-2.5-pro-preview-05-06"

[github_tool_settings]
# This section can be used for GitHub tool-specific settings.
# For example, a default commit message prefix (though agents currently construct these dynamically).
commit_message_prefix = "AI Doc Agent: "
```

**Key Settings:**

*   **`[general].github_base_branch`**: Sets the target branch for pull requests created by the `GenerationAgent`.
*   **`[models]`**: Allows you to specify different Gemini models for each agent. This is useful for experimenting with different model capabilities or managing costs.
*   **`[github_tool_settings]`**: Currently includes an example for `commit_message_prefix`. While not fully utilized by all agents yet (as they often generate more dynamic messages), this section is intended for future enhancements to standardize tool behaviors.

If `config.toml` is not found, or if specific settings are missing, the application will use hardcoded default values defined in `config_utils.py` and within the agent instruction prompts. 