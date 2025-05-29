import toml

# --- Configuration Loading ---
CONFIG_FILE_PATH = "config.toml"

def load_config() -> dict:
    """Loads the TOML configuration file."""
    try:
        with open(CONFIG_FILE_PATH, 'r') as f:
            config_data = toml.load(f)
            return config_data
    except FileNotFoundError:
        print(f"WARNING: Configuration file {CONFIG_FILE_PATH} not found. Using default fallbacks for core settings.")
        return {
            "models": {
                "doc_manager_agent": "gemini-2.5-pro-preview-05-06",
                "qa_agent": "gemini-2.5-pro-preview-05-06",
                "generation_agent": "gemini-2.5-pro-preview-05-06",
                "evaluation_agent": "gemini-2.5-pro-preview-05-06",
            },
            "general": {
                "github_base_branch": "main"
            },
        }
    except Exception as e:
        print(f"ERROR: Could not parse {CONFIG_FILE_PATH}: {e}. Using default fallbacks for core settings.")
        return {
            "models": {
                "doc_manager_agent": "gemini-2.5-pro-preview-05-06",
                "qa_agent": "gemini-2.5-pro-preview-05-06",
                "generation_agent": "gemini-2.5-pro-preview-05-06",
                "evaluation_agent": "gemini-2.5-pro-preview-05-06",
            },
            "general": {
                "github_base_branch": "main"
            }
        }

# Load configuration when the module is imported
config = load_config() 