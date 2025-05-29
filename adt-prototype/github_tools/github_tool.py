import os
from github import Github
from dotenv import load_dotenv
import re
import requests

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN environment variable not set.")
if not GITHUB_REPOSITORY:
    raise ValueError("GITHUB_REPOSITORY environment variable not set (e.g., 'owner/repo_name').")

try:
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(GITHUB_REPOSITORY)
    print(f"Successfully connected to GitHub repository: {GITHUB_REPOSITORY}")
except Exception as e:
    print(f"Error connecting to GitHub: {e}")
    repo = None

def _to_kebab_case(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[\s_.:;,!?()\[\]{}]+', '-', text)
    text = re.sub(r'-+', '-', text)
    text = text.strip('-')
    return text

def create_github_issue(title: str, body: str) -> dict:
    """Creates a new GitHub issue."""
    if not repo:
        return {"status": "error", "error_message": "Not connected to GitHub repository."}
    try:
        issue = repo.create_issue(title=title, body=body)
        print(f"Created GitHub issue: {issue.html_url}")
        return {"status": "success", "issue_url": issue.html_url, "issue_number": issue.number}
    except Exception as e:
        print(f"Error creating issue: {e}")
        return {"status": "error", "error_message": str(e)}

def get_issue(issue_number: int) -> dict:
    """Gets a specific GitHub issue."""
    if not repo:
        return {"status": "error", "error_message": "Not connected to GitHub repository."}
    try:
        issue = repo.get_issue(issue_number)
        print(f"Retrieved issue #{issue.number}: {issue.title}")
        return {"status": "success", "issue": {"title": issue.title, "body": issue.body, "state": issue.state, "number": issue.number}}
    except Exception as e:
        print(f"Error getting issue {issue_number}: {e}")
        return {"status": "error", "error_message": str(e)}


def get_file_content(path: str, ref: str = "main") -> dict:
    """Gets the content of a file from a specific branch or commit."""
    if not repo:
        return {"status": "error", "error_message": "Not connected to GitHub repository."}
    try:
        contents = repo.get_contents(path, ref=ref)
        if isinstance(contents, list):
             return {"status": "error", "error_message": f"Path '{path}' is a directory, not a file."}
        print(f"Read file content from '{path}' at ref '{ref}'.")
        return {"status": "success", "content": contents.decoded_content.decode()}
    except Exception as e:
        print(f"Error reading file '{path}' at ref '{ref}': {e}")
        return {"status": "error", "error_message": str(e)}


def commit_changes(file_path: str, content: str, commit_message: str, branch: str) -> dict:
    """Commits changes to a file on a specific branch, creating the branch if it doesn't exist."""
    if not repo:
        return {"status": "error", "error_message": "Not connected to GitHub repository."}
    try:
        sha = None
        try:
            contents = repo.get_contents(file_path, ref=branch)
            if isinstance(contents, list):
                 return {"status": "error", "error_message": f"Commit target path '{file_path}' is a directory."}
            sha = contents.sha
            print(f"Found existing file '{file_path}' on branch '{branch}' with SHA {sha}.")
            commit = repo.update_file(path=file_path, message=commit_message, content=content, sha=sha, branch=branch)
            print(f"Updated file '{file_path}' on branch '{branch}'.")
        except Exception as e:
            try:
                repo.get_branch(branch)
                print(f"Branch '{branch}' exists, but file '{file_path}' not found. Creating file.")
            except:
                print(f"Branch '{branch}' does not exist. Creating branch and file.")

            commit = repo.create_file(path=file_path, message=commit_message, content=content, branch=branch)
            print(f"Created file '{file_path}' on branch '{branch}'.")


        return {"status": "success", "commit_url": commit['commit'].html_url}
    except Exception as e:
        print(f"Error committing changes to '{file_path}' on branch '{branch}': {e}")
        return {"status": "error", "error_message": str(e)}

def create_branch_and_commit_file(issue_number: int, issue_title: str, file_path: str, content: str, commit_message: str, base_branch_name: str = "main") -> dict:
    """Creates a branch based on issue details, then commits a file to it."""
    if not repo:
        return {"status": "error", "error_message": "Not connected to GitHub repository."}

    branch_name = f"{issue_number}-{_to_kebab_case(issue_title)}"
    print(f"Constructed branch name: {branch_name}")

    try:
        base_branch = repo.get_branch(base_branch_name)
        print(f"Found base branch '{base_branch_name}' with SHA: {base_branch.commit.sha}")

        try:
            repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base_branch.commit.sha)
            print(f"Successfully created new branch '{branch_name}' from '{base_branch_name}'.")
        except Exception as e:
            try:
                repo.get_branch(branch_name)
                print(f"Branch '{branch_name}' already exists. Proceeding to commit.")
            except Exception as get_branch_e:
                print(f"Error creating branch '{branch_name}': {e}. Also failed to confirm if it exists: {get_branch_e}")
                return {"status": "error", "error_message": f"Error creating branch '{branch_name}': {e}"}

        sha = None
        try:
            existing_file = repo.get_contents(file_path, ref=branch_name)
            if isinstance(existing_file, list):
                 return {"status": "error", "error_message": f"Target path '{file_path}' on branch '{branch_name}' is a directory."}
            sha = existing_file.sha
            print(f"File '{file_path}' found on branch '{branch_name}'. Updating.")
            commit_details = repo.update_file(path=file_path, message=commit_message, content=content, sha=sha, branch=branch_name)
        except Exception:
            print(f"File '{file_path}' not found on branch '{branch_name}'. Creating.")
            commit_details = repo.create_file(path=file_path, message=commit_message, content=content, branch=branch_name)
        
        print(f"Successfully committed '{file_path}' to branch '{branch_name}'. Commit URL: {commit_details['commit'].html_url}")
        return {"status": "success", "branch_name": branch_name, "commit_url": commit_details['commit'].html_url, "file_path": file_path}

    except Exception as e:
        print(f"An error occurred in create_branch_and_commit_file: {e}")
        return {"status": "error", "error_message": str(e)}

def create_pull_request(title: str, body: str, head_branch: str, base_branch: str = "main") -> dict:
    """Creates a pull request."""
    if not repo:
        return {"status": "error", "error_message": "Not connected to GitHub repository."}
    try:
        try:
            repo.get_branch(head_branch)
            print(f"Head branch '{head_branch}' found.")
        except Exception:
             return {"status": "error", "error_message": f"Head branch '{head_branch}' does not exist. Cannot create PR."}

        pr = repo.create_pull(title=title, body=body, head=head_branch, base=base_branch)
        print(f"Created pull request: {pr.html_url}")
        return {"status": "success", "pr_url": pr.html_url, "pr_number": pr.number}
    except Exception as e:
        print(f"Error creating pull request from '{head_branch}' to '{base_branch}': {e}")
        return {"status": "error", "error_message": str(e)}

def approve_pull_request(pr_number: int, message: str = "Looks good.") -> dict:
    """Approves a pull request."""
    if not repo:
        return {"status": "error", "error_message": "Not connected to GitHub repository."}
    try:
        pr = repo.get_pull(pr_number)
        if pr.state != 'open':
             print(f"PR #{pr_number} is not open (state: {pr.state}). Cannot approve.")
             return {"status": "success", "message": f"PR #{pr_number} is not open, skipping approval.", "pr_url": pr.html_url}

        existing_reviews = pr.get_reviews()
        for review in existing_reviews:
            pass


        print(f"Approving pull request #{pr_number} with message: '{message}'")
        pr.create_review(event='APPROVE', body=message)
        print(f"Approval submitted for PR #{pr_number}. PR URL: {pr.html_url}")
        pr = repo.get_pull(pr_number)
        return {"status": "success", "message": "PR approved or review submitted.", "pr_url": pr.html_url, "pr_state": pr.state}
    except Exception as e:
        print(f"Error approving pull request #{pr_number}: {e}")
        return {"status": "error", "error_message": str(e)}

def get_pull_request_diff(pr_number: int) -> dict:
    """Fetches the diff of a pull request."""
    if not repo:
        return {"status": "error", "error_message": "Not connected to GitHub repository."}
    try:
        pr = repo.get_pull(pr_number)
        diff_url = pr.diff_url
        
        response = requests.get(diff_url)
        response.raise_for_status()
        
        diff_content = response.text
        print(f"Successfully fetched diff for PR #{pr_number}.")
        return {"status": "success", "diff_content": diff_content, "pr_number": pr_number}
    except Exception as e:
        print(f"Error fetching diff for PR #{pr_number}: {e}")
        return {"status": "error", "error_message": str(e)}

def get_open_issues() -> dict:
    """Gets all open issues from the repository."""
    if not repo:
        return {"status": "error", "error_message": "Not connected to GitHub repository."}
    try:
        open_issues = repo.get_issues(state='open')
        issues_list = []
        for issue in open_issues:
            issues_list.append({
                "number": issue.number,
                "title": issue.title,
                "body": issue.body,
                "state": issue.state,
                "url": issue.html_url
            })
        print(f"Successfully fetched {len(issues_list)} open issues.")
        return {"status": "success", "open_issues": issues_list}
    except Exception as e:
        print(f"Error fetching open issues: {e}")
        return {"status": "error", "error_message": str(e)}

# List of tools to expose to ADK agents.  Make sure you add the tools to the config.toml file. 
GITHUB_TOOLS = [
    create_github_issue,
    get_issue,
    get_file_content,
    commit_changes,
    create_branch_and_commit_file,
    create_pull_request,
    approve_pull_request,
    get_pull_request_diff,
    get_open_issues
]
