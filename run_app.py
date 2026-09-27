import sys
import subprocess
import os
import time

def main():
    print("=" * 60)
    print(" 🛡️  RECOVERAI - AI REVENUE RECOVERY PLATFORM ")
    print(" Major League Hacking (MLH) 2026")
    print("=" * 60)
    print("\nStarting RecoverAI Streamlit Dashboard...\n")

    # Path to dashboard script
    dashboard_path = os.path.join(os.path.dirname(__file__), "app", "dashboard.py")
    
    # Launch streamlit process
    cmd = [sys.executable, "-m", "streamlit", "run", dashboard_path]
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n[RecoverAI] Shutting down gracefully. Goodbye!")

if __name__ == "__main__":
    main()
