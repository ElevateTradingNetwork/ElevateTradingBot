import os
import sys
import subprocess

def main():
    """Launch Streamlit app with the correct port for Render."""
    # Set environment variable to indicate a non-interactive environment
    os.environ["NON_INTERACTIVE"] = "true"
    
    # Get port from environment or use default
    port = os.environ.get("PORT", "5000")
    print(f"Starting Streamlit app on port {port}")
    
    # Build the command with the specified port
    cmd = [
        "streamlit", "run", 
        "app_streamlit.py", 
        f"--server.port={port}", 
        "--server.address=0.0.0.0"
    ]
    
    # Execute the command directly (not in background)
    process = subprocess.run(cmd)
    return process.returncode

if __name__ == "__main__":
    sys.exit(main())