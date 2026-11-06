#!/usr/bin/env python3
"""
Universal cross-platform launcher for Windows, macOS, and Linux.
Usage: python run.py (or python3 run.py)
"""
import sys
import os
import subprocess

def main():
    print("=" * 65)
    print("✨ Tezal's Inventory Management System ✨")
    print(f"🖥️  Platform: {sys.platform.capitalize()}")
    print("=" * 65)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    # Check if packages are installed in current environment
    try:
        import fastapi
        import uvicorn
        import PIL
        import jinja2
    except ImportError:
        print("📦 Installing required dependencies from requirements.txt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    import uvicorn
    print("\n📍 Server starting...")
    print("👉 Open your browser at: http://127.0.0.1:8000")
    print("🛑 Press Ctrl+C in this terminal to stop the server\n")
    
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()
