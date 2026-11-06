# Compatibility wrapper to run the FastAPI app
import uvicorn
from main import app

if __name__ == "__main__":
    print("=" * 65)
    print("✨ Tezal's Inventory Management System ✨")
    print("🚀 Running with FastAPI on Localhost")
    print("📍 Open your browser at: http://127.0.0.1:8000")
    print("=" * 65)
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
