import os
import sys
import subprocess

def main():
    """Launch Streamlit app with the correct port for Render."""
    port = os.environ.get("PORT", "5000")
    print(f"Starting Streamlit app on port {port}")
    
    # Build the command with the environment's PORT
    cmd = [
        "streamlit", "run", 
        "app_streamlit.py", 
        f"--server.port={port}", 
        "--server.address=0.0.0.0",
        "--server.headless=true"
    ]
    
    # Execute the command
    process = subprocess.run(cmd)
    return process.returncode

if __name__ == "__main__":
    sys.exit(main())