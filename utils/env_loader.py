"""Environment variable loader utility."""
import os
import re
from typing import Dict, Optional


def load_env(env_path: str = '.env', override: bool = False) -> Dict[str, Optional[str]]:
    """
    Load environment variables from a .env file if present.
    
    This function loads variables defined in a .env file into the environment
    but doesn't override existing environment variables unless override is True.
    
    Args:
        env_path (str): Path to the .env file
        override (bool): Whether to override existing environment variables
        
    Returns:
        Dict[str, Optional[str]]: Dictionary of loaded environment variables
    """
    # Check if .env file exists
    if not os.path.exists(env_path):
        print(f"Warning: Environment file {env_path} not found.")
        return {}
    
    loaded_vars = {}
    
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                # Parse key-value pair
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    
                    # Handle variables with references to other environment variables
                    if '${' in value:
                        # Replace ${VAR} with the value of VAR from environment
                        value = re.sub(
                            r'\${([A-Za-z0-9_]+)}',
                            lambda m: os.environ.get(m.group(1), ''),
                            value
                        )
                    
                    # Set environment variable if it doesn't exist or override is True
                    if override or key not in os.environ:
                        os.environ[key] = value
                        loaded_vars[key] = value
    except Exception as e:
        print(f"Error loading environment variables: {e}")
    
    # Create a dictionary of the important loaded environment variables (for reporting)
    important_vars = {
        "BITGET_API_KEY": os.environ.get("BITGET_API_KEY"),
        "BITGET_API_SECRET": os.environ.get("BITGET_API_SECRET"),
        "BITGET_API_PASSWORD": os.environ.get("BITGET_API_PASSWORD"),
        "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY"),
        "DEBUG": os.environ.get("DEBUG")
    }
    
    # Filter out None values for reporting
    set_vars = {k: "***" for k, v in important_vars.items() if v is not None}
    if os.environ.get("DEBUG") == "true":
        print(f"Loaded environment variables: {', '.join(set_vars.keys())}")
    
    return loaded_vars


# Load environment variables when the module is imported
loaded_env_vars = load_env()