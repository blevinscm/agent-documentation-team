import os
from github import Github
from dotenv import load_dotenv
import re
import requests # Added for fetching diff from URL

# Load environment variables from .env file
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN environment variable not set.")
if not GITHUB_REPOSITORY:
    raise ValueError("GITHUB_REPOSITORY environment variable not set (e.g., 'owner/repo_name').")

try:
    g = Github(GITHUB_TOKEN)
    # Assuming the authenticated user's token has access to the repository
    # This might need adjustment if the repo owner is different from the token owner
    # and the token is not an org token or a GitHub App installation token.
    repo = g.get_repo(GITHUB_REPOSITORY)
    print(f"Successfully connected to GitHub repository: {GITHUB_REPOSITORY}")
except Exception as e:
    print(f"Error connecting to GitHub: {e}")
    repo = None # Set repo to None if connection fails

# Helper function for kebab-casing
def _to_kebab_case(text: str) -> str:
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and non-alphanumeric (excluding hyphens) with a hyphen
    text = re.sub(r'[\s_.:;,!?()\[\]{}]+', '-', text) # Added more special chars
    # Replace multiple hyphens with a single hyphen
    text = re.sub(r'-+', '-', text)
    # Remove leading or trailing hyphens
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
        if isinstance(contents, list): # get_contents can return a list if it's a directory
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
            # Try to get the file's current SHA on the target branch
            contents = repo.get_contents(file_path, ref=branch)
            if isinstance(contents, list):
                 return {"status": "error", "error_message": f"Commit target path '{file_path}' is a directory."}
            sha = contents.sha
            print(f"Found existing file '{file_path}' on branch '{branch}' with SHA {sha}.")
            # Update the file
            commit = repo.update_file(path=file_path, message=commit_message, content=content, sha=sha, branch=branch)
            print(f"Updated file '{file_path}' on branch '{branch}'.")
        except Exception as e:
            # If getting contents fails, the file might not exist on this branch.
            # Check if the branch exists first. If not, it will be created by create_file.
            try:
                repo.get_branch(branch)
                print(f"Branch '{branch}' exists, but file '{file_path}' not found. Creating file.")
            except:
                print(f"Branch '{branch}' does not exist. Creating branch and file.")

            # Create the file
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
        # Get the base branch (source for new branch)
        base_branch = repo.get_branch(base_branch_name)
        print(f"Found base branch '{base_branch_name}' with SHA: {base_branch.commit.sha}")

        # Create the new branch from the base branch's HEAD SHA
        try:
            repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base_branch.commit.sha)
            print(f"Successfully created new branch '{branch_name}' from '{base_branch_name}'.")
        except Exception as e:
            # Check if branch already exists (common cause for create_git_ref failure)
            try:
                repo.get_branch(branch_name)
                print(f"Branch '{branch_name}' already exists. Proceeding to commit.")
            except Exception as get_branch_e:
                print(f"Error creating branch '{branch_name}': {e}. Also failed to confirm if it exists: {get_branch_e}")
                return {"status": "error", "error_message": f"Error creating branch '{branch_name}': {e}"}

        # Now commit the file to the new (or existing) branch
        # Check if file exists to update, otherwise create
        sha = None
        try:
            existing_file = repo.get_contents(file_path, ref=branch_name)
            if isinstance(existing_file, list):
                 return {"status": "error", "error_message": f"Target path '{file_path}' on branch '{branch_name}' is a directory."}
            sha = existing_file.sha
            print(f"File '{file_path}' found on branch '{branch_name}'. Updating.")
            commit_details = repo.update_file(path=file_path, message=commit_message, content=content, sha=sha, branch=branch_name)
        except Exception: # GithubException (status 404) means file not found
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
        # Ensure the head branch exists before creating a PR
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
        # Check if the PR is already merged or closed
        if pr.state != 'open':
             print(f"PR #{pr_number} is not open (state: {pr.state}). Cannot approve.")
             return {"status": "success", "message": f"PR #{pr_number} is not open, skipping approval.", "pr_url": pr.html_url}

        # Check if the current user is the author of the PR (cannot approve your own PR unless configured otherwise)
        # This prototype assumes you might approve your own for testing.
        # In a real scenario, the approving identity would be different.
        # Consider adding a check here or configuring repo settings if needed.

        # Check if a review from the current user already exists and is approved
        existing_reviews = pr.get_reviews()
        for review in existing_reviews:
            # Note: PyGithub's get_reviews() might not directly expose the reviewer's login easily for the token user.
            # This check is complex without knowing the authenticated user's login within this context easily.
            # For simplicity, we'll just attempt to create a review. If one exists, the API might handle it.
            pass


        print(f"Approving pull request #{pr_number} with message: '{message}'")
        # Creating a review with event='APPROVE' is how you approve via API
        pr.create_review(event='APPROVE', body=message)
        print(f"Approval submitted for PR #{pr_number}. PR URL: {pr.html_url}")
        # Fetch PR again to get updated state
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
        
        # GitHub diff URLs usually don't require extra auth if the token has repo access,
        # but some setups might. For simplicity, we'll try a direct GET.
        # If this fails due to auth, headers might be needed: 
        # headers = {'Authorization': f'token {GITHUB_TOKEN}'}
        response = requests.get(diff_url)
        response.raise_for_status() # Raise an exception for bad status codes
        
        diff_content = response.text
        print(f"Successfully fetched diff for PR #{pr_number}.")
        return {"status": "success", "diff_content": diff_content, "pr_number": pr_number}
    except Exception as e:
        print(f"Error fetching diff for PR #{pr_number}: {e}")
        return {"status": "error", "error_message": str(e)}

# List of tools to expose to ADK agents
GITHUB_TOOLS = [
    create_github_issue,
    get_issue,
    get_file_content,
    commit_changes,
    create_branch_and_commit_file,
    create_pull_request,
    approve_pull_request,
    get_pull_request_diff
]
