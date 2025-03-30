"""Environment variable loader utility."""
import os
import re
from typing import Dict


def load_env(env_path: str = '.env') -> Dict[str, str]:
    """
    Load environment variables from a .env file if present.
    
    This function loads variables defined in a .env file into the environment
    but doesn't override existing environment variables.
    
    Args:
        env_path (str): Path to the .env file
        
    Returns:
        Dict[str, str]: Dictionary of loaded environment variables
    """
    if not os.path.exists(env_path):
        return {}
    
    loaded_vars = {}
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            # Handle variables with references to other environment variables
            if '${' in value:
                # Replace ${VAR} with the value of VAR from environment
                value = re.sub(
                    r'\${([A-Za-z0-9_]+)}',
                    lambda m: os.environ.get(m.group(1), ''),
                    value
                )
            
            # Don't override existing environment variables
            if key not in os.environ:
                os.environ[key] = value
                loaded_vars[key] = value
    
    return loaded_vars


# Load environment variables when the module is imported
loaded_env_vars = load_env()