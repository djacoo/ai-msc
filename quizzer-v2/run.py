#!/usr/bin/env python3
"""
Quizzer V2 Launcher
Grounded Q&A engine with teacher-grade evaluation
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

# Silence tkinter deprecation warnings
os.environ['TK_SILENCE_DEPRECATION'] = '1'

def check_python_version():
    """Check if Python version is adequate."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor} detected")

def check_tkinter():
    """Check if tkinter is available."""
    try:
        import tkinter
        print("✅ Tkinter is available")
        return True
    except ImportError:
        print("❌ Tkinter is not available")
        print("⚠️  Please install tkinter:")
        if sys.platform == "darwin":
            print("   Run: brew install python-tk@3.11")
        else:
            print("   Run: sudo apt-get install python3-tk")
        return False

def main():
    print("🚀 Quizzer V2 Launcher - Grounded Q&A Engine")
    print("=" * 50)
    print("🎓 AI-POWERED QUIZ - Dependency Checker")
    print("=" * 60)
    print()
    
    # Check Python version
    check_python_version()
    
    # Check tkinter
    if not check_tkinter():
        sys.exit(1)
    
    print("\n📦 Checking PDF parser...")
    try:
        import PyPDF2
        print("   ✓ PyPDF2 installed")
    except ImportError:
        print("   Installing PyPDF2...")
        subprocess.run([sys.executable, "-m", "pip", "install", "PyPDF2==3.0.1"], check=True)
        print("   ✓ PyPDF2 installed")
    
    # Step 5: Launch Quizzer V2 GUI
    print("\n📱 Launching Quizzer V2 GUI...")
    try:
        from quizzer_v2_gui import QuizzerV2GUI
        from quizzer_v2_engine import QuizzerV2
        from local_ai import LocalAI
        
        # Find repo root
        repo_root = Path(__file__).parent.parent
        
        # Initialize AI
        print("   Initializing AI engine...")
        ai = LocalAI("llama3.2:3b")
        
        # Initialize Quizzer V2
        print("   Initializing Quizzer V2...")
        engine = QuizzerV2(str(repo_root), ai)
        
        # Launch GUI
        print("   ✓ Starting application...\n")
        app = QuizzerV2GUI(engine, ai)
        app.run()
    except Exception as e:
        print(f"❌ Failed to launch GUI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
