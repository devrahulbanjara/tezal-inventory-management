#!/usr/bin/env bash

# Cross-platform runner for macOS & Linux

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    ./venv/bin/pip install --upgrade pip
    ./venv/bin/pip install -r requirements.txt
fi

echo "=========================================================="
echo "✨ Starting Tezal's Inventory Management System ✨"
echo "📍 Open your browser at: http://127.0.0.1:8000"
echo "🛑 Press Ctrl+C to stop the server"
echo "=========================================================="

./venv/bin/python3 main.py
