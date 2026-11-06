@echo off
setlocal

echo ==========================================================
echo ✨ Starting Tezal's Inventory Management System ✨
echo ==========================================================

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment for Windows...
    python -m venv venv
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

echo.
echo 📍 Server is running!
echo 👉 Open your browser at: http://127.0.0.1:8000
echo 🛑 Press Ctrl+C to stop the server
echo ==========================================================
echo.

python main.py

pause
