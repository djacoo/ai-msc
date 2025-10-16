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

def get_available_models():
    """Get list of available Ollama models."""
    try:
        result = subprocess.run(['ollama', 'list'], 
                               capture_output=True, 
                               text=True, 
                               check=True)
        
        models = []
        lines = result.stdout.strip().split('\n')[1:]  # Skip header
        for line in lines:
            if line.strip():
                parts = line.split()
                if parts:
                    model_name = parts[0]
                    # Only include llama models
                    if 'llama' in model_name.lower():
                        models.append(model_name)
        return models
    except:
        return []

def select_model():
    """Interactive model selection."""
    print("\n" + "=" * 60)
    print("🤖 AI MODEL SELECTION")
    print("=" * 60)
    
    # Check for available models
    available_models = get_available_models()
    
    # Recommended models with descriptions
    recommended_models = {
        "llama3.2:3b": {
            "name": "Llama 3.2 (3B)",
            "speed": "⚡⚡⚡ Very Fast",
            "quality": "⭐⭐ Fair",
            "size": "~2GB",
            "best_for": "Quick testing, low-resource systems",
            "pros": "Fast generation, low memory usage",
            "cons": "Less coherent questions, more retries needed",
            "recommended": False
        },
        "llama3.1:8b": {
            "name": "Llama 3.1 (8B)",
            "speed": "⚡⚡ Fast",
            "quality": "⭐⭐⭐⭐ Excellent",
            "size": "~4.7GB",
            "best_for": "Production use, best balance",
            "pros": "Great question quality, few retries, fast enough",
            "cons": "Slightly slower than 3B",
            "recommended": True
        },
        "llama3.1:70b": {
            "name": "Llama 3.1 (70B)",
            "speed": "⚡ Slower",
            "quality": "⭐⭐⭐⭐⭐ Outstanding",
            "size": "~40GB",
            "best_for": "Maximum quality, powerful machines",
            "pros": "Near-perfect questions, excellent grading",
            "cons": "Slow generation, requires lots of RAM",
            "recommended": False
        }
    }
    
    print("\nAvailable Models:")
    print("-" * 60)
    
    options = []
    idx = 1
    
    # Show recommended models first
    for model_key in ["llama3.2:3b", "llama3.1:8b", "llama3.1:70b"]:
        info = recommended_models[model_key]
        is_installed = model_key in available_models
        
        status = "✅ INSTALLED" if is_installed else "📥 NOT INSTALLED"
        badge = " 🌟 RECOMMENDED" if info["recommended"] else ""
        
        print(f"\n[{idx}] {info['name']}{badge}")
        print(f"    Status: {status}")
        print(f"    Speed:  {info['speed']}")
        print(f"    Quality: {info['quality']}")
        print(f"    Size:    {info['size']}")
        print(f"    Best for: {info['best_for']}")
        print(f"    ✓ {info['pros']}")
        print(f"    ✗ {info['cons']}")
        
        options.append((idx, model_key, is_installed))
        idx += 1
    
    print("\n" + "-" * 60)
    print("\n💡 RECOMMENDATION: Option [2] Llama 3.1 (8B) for best results!")
    print("   It offers excellent quality while staying fast enough.\n")
    
    # Get user choice
    while True:
        try:
            choice = input("Enter your choice [1-3] (or 'q' to quit): ").strip()
            
            if choice.lower() == 'q':
                print("Exiting...")
                sys.exit(0)
            
            choice_num = int(choice)
            if 1 <= choice_num <= 3:
                selected = [opt for opt in options if opt[0] == choice_num][0]
                model_name = selected[1]
                is_installed = selected[2]
                
                if not is_installed:
                    print(f"\n📥 Model {model_name} is not installed yet.")
                    confirm = input(f"   Download {model_name} now? This may take a few minutes [y/n]: ").strip().lower()
                    if confirm != 'y':
                        print("   Please select an installed model or quit.")
                        continue
                    print(f"\n   The model will be auto-downloaded when the app starts...")
                
                print(f"\n✅ Selected: {recommended_models[model_name]['name']}")
                return model_name
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
        except ValueError:
            print("Invalid input. Please enter a number or 'q' to quit.")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            sys.exit(0)

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
    
    # Model Selection
    selected_model = select_model()
    
    # Launch Quizzer V2 with Authentication
    print("\n📱 Launching Quizzer V2...")
    try:
        from src.gui.quizzer_v2_gui import QuizzerV2GUI
        from src.engines.quizzer_v2_engine import QuizzerV2
        from src.utils.local_ai import LocalAI
        from src.gui.auth_gui import AuthGUI
        
        # Find repo root
        repo_root = Path(__file__).parent.parent
        
        # Initialize AI with selected model
        print(f"   Initializing AI engine ({selected_model})...")
        ai = LocalAI(selected_model)
        
        # Initialize Quizzer V2
        print("   Initializing Quizzer V2...")
        engine = QuizzerV2(str(repo_root), ai)
        
        # Show authentication first
        print("   ✓ Starting application...\n")
        print("🔐 Authentication required...\n")
        
        def on_auth_success(user_id, username):
            """Callback when authentication succeeds."""
            print(f"✓ Logged in as: {username}\n")
            # Launch main GUI with authenticated user
            app = QuizzerV2GUI(engine, ai, username)
            app.run()
        
        # Show login/register screen
        auth = AuthGUI(engine, on_auth_success)
        auth.run()
        
    except Exception as e:
        print(f"❌ Failed to launch application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
