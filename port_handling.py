import os

def get_port():
    """Get the port from the environment variable PORT or default to 5000."""
    return int(os.environ.get("PORT", 5000))