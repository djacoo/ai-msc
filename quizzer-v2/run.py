#!/usr/bin/env python3
"""
AI Quiz Launcher
Checks dependencies and launches the quiz app
"""

import sys
import subprocess
import os
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

def check_ollama():
    """Check if Ollama is installed and running."""
    try:
        # Check if ollama command exists
        result = subprocess.run(['which', 'ollama'], 
                              capture_output=True, 
                              text=True)
        if result.returncode != 0:
            print("❌ Ollama is not installed")
            print("\n📥 Installing Ollama...")
            try:
                subprocess.run(['brew', 'install', 'ollama'], check=True)
                print("✅ Ollama installed successfully")
            except subprocess.CalledProcessError:
                print("⚠️  Please install Ollama manually:")
                print("   Visit: https://ollama.com/download")
                print("   Or run: brew install ollama")
                return False
        else:
            print("✅ Ollama is installed")
        
        # Check if ollama is running
        result = subprocess.run(['ollama', 'list'], 
                              capture_output=True, 
                              text=True,
                              timeout=5)
        if result.returncode != 0:
            print("⚠️  Ollama is not running, starting it...")
            subprocess.run(['brew', 'services', 'start', 'ollama'], 
                         capture_output=True)
            import time
            time.sleep(2)
            print("✅ Ollama service started")
        else:
            print("✅ Ollama is running")
        
        # Check if model is downloaded
        result = subprocess.run(['ollama', 'list'], 
                              capture_output=True, 
                              text=True)
        if 'llama3.2:3b' not in result.stdout and 'llama3.2' not in result.stdout:
            print("📥 Downloading AI model (Llama 3.2 - 3B, ~2GB)...")
            print("⏳ This may take a few minutes on first run...")
            subprocess.run(['ollama', 'pull', 'llama3.2:3b'], check=True)
            print("✅ Model downloaded successfully")
        else:
            print("✅ AI model is ready")
        
        return True
        
    except subprocess.TimeoutExpired:
        print("⚠️  Ollama appears to be hung, restarting...")
        subprocess.run(['brew', 'services', 'restart', 'ollama'], 
                     capture_output=True)
        return True
    except Exception as e:
        print(f"⚠️  Error checking Ollama: {e}")
        return False

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
    """Main launcher function."""
    print("=" * 60)
    print("🎓 AI-POWERED QUIZ - Dependency Checker")
    print("=" * 60)
    print()
    
    # Check Python version
    check_python_version()
    
    # Check tkinter
    if not check_tkinter():
        sys.exit(1)
    
    # Check Ollama
    if not check_ollama():
        print("\n⚠️  Ollama setup incomplete. The app may not work properly.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    print()
    print("=" * 60)
    print("✅ All dependencies are ready!")
    print("🚀 Launching AI Quiz App...")
    print("=" * 60)
    print()
    
    # Launch the GUI directly in same process (so monkey patches work)
    try:
        # Add script directory to path
        script_dir = Path(__file__).parent
        sys.path.insert(0, str(script_dir))
        
        # Now import and run the GUI
        from quiz_gui import main as gui_main
        gui_main()
        
    except KeyboardInterrupt:
        print("\n\n👋 Quiz app closed")
    except Exception as e:
        print(f"\n❌ Error launching app: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
