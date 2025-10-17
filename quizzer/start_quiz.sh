#!/bin/bash
# 🚀 Quizzer V3 Launcher - AI-Powered Quiz System with Animations
# Grounded Q&A engine with teacher-grade evaluation
# Use Homebrew Python 3.11 instead of system Python 3.9
PYTHON3_11="/opt/homebrew/bin/python3.11"

if [ ! -f "$PYTHON3_11" ]; then
    # Try alternate Homebrew path (Intel Macs)
    PYTHON3_11="/usr/local/bin/python3.11"
fi

if [ ! -f "$PYTHON3_11" ]; then
    echo "Error: Python 3.11 not found. Please install it:"
    echo "  brew install python@3.11 python-tk@3.11"
    exit 1
fi

# Launch with Python 3.11
exec "$PYTHON3_11" run.py
