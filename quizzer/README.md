# Quizzer V3 - AI-Powered Academic Quiz System

> **Academic-grade quiz generator with AI teacher evaluation + Smooth Animations**  
> Generate questions from your course PDFs, receive detailed grounded feedback, and enjoy a fluid, animated user experience.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/Version-3.0-success.svg)](https://github.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![macOS](https://img.shields.io/badge/Platform-macOS-lightgrey.svg)](https://www.apple.com/macos/)

---

## 🆕 What's New in V3

### ✨ Animations & Visual Feedback
- **Success Animations**: Beautiful checkmark animation on login/register
- **Loading Spinners**: Smooth 60px rotating arcs for all async operations
- **Typing Indicators**: Animated dots in chatbot conversations
- **Fluid Transitions**: 30-60 FPS animations throughout

### 🎨 UI/UX Improvements
- **Compact Layouts**: All content visible without scrolling
- **Foreground Launch**: App always opens above other windows
- **Optimized Scrolling**: 40% trackpad sensitivity for smooth control
- **Consistent Styling**: Uniform button design across the app

### 🔐 Enhanced Features
- **Password Management**: Change passwords directly from profile
- **Conversational Chatbot**: Handles greetings and casual conversation
- **Better Error Messages**: More helpful feedback throughout

### 📊 Refined Rating System
- **5-Tier System**: From Beginner to Master Scholar
- **Weighted Algorithm**: Smart calculation based on performance
- **AI Descriptions**: Personalized motivational messages

---

## 📋 Table of Contents

- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [How to Use](#-how-to-use)
- [AI Model Selection](#-ai-model-selection)
- [User Authentication](#-user-authentication)
- [AI Chatbot](#-ai-chatbot)
- [Question Types](#-question-types)
- [Project Structure](#-project-structure)
- [Architecture](#-architecture)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [Advanced Configuration](#-advanced-configuration)

---

## ✨ Features

### Core Capabilities
- **📚 PDF-Grounded Questions**: Generates questions directly from your course PDF notes
- **🤖 AI Teacher Grading**: Rigorous evaluation with detailed rubric-based feedback
- **📊 Multiple Question Types**: MCQ (single/multiple choice), short answer, long answer, derivations
- **🎯 Citation System**: Every answer includes citations to specific PDF pages
- **🔒 Anti-Cheating**: Validates answers to prevent empty or minimal responses
- **⚡ Fast Generation**: Optimized for speed with async processing
- **💬 AI Chatbot**: Ask questions about your course notes with grounded responses
- **👤 User System**: Authentication, registration, and personalized profiles
- **📊 Performance Tracking**: Track your progress, ratings, and quiz history
- **🏆 Rating System**: Dynamic rating based on performance (5-tier system)

### User Experience
- **🎨 Modern UI**: Clean, professional interface with dark theme
- **✨ Smooth Animations**: 
  - Login/register success animations with checkmark
  - Loading spinners for question generation and grading
  - Animated typing indicators in chatbot
  - Fluid page transitions
- **📈 Compact Layouts**: All content visible without scrolling
- **⚙️ Customizable**: Choose question types before starting quiz
- **🪟 Window Management**: App always opens in foreground
- **🔐 Secure Authentication**: Password hashing and secure user management
- **📖 User Profiles**: View statistics, change passwords, and track achievements
- **🖱️ Optimized Scrolling**: Smooth trackpad scrolling (40% sensitivity)

### Academic Rigor
- **Strict Grading**: ≥90% for correct, 40-89% partially correct, <40% incorrect
- **Rubric-Based**: Each question has detailed point breakdown
- **Concept Tracking**: Identifies and evaluates key concepts
- **False Positive Guard**: Automatically detects and fails minimal answers
- **Grounded Feedback**: All explanations reference course material

---

## 🔧 Prerequisites

### Required
- **Python 3.8+** (Python 3.11 recommended)
- **macOS** (tested on macOS, may work on Linux with modifications)
- **Ollama** with at least one Llama model installed (3.2:3b, 3.1:8b, or 3.1:70b)

### Automatic Dependencies
The following are installed automatically on first run:
- `PyPDF2==3.0.1` - PDF parsing
- `tkinter` - GUI (check installation below)

---

## 🚀 Installation

### Step 1: Install Python 3.11

```bash
# Using Homebrew (recommended for macOS)
brew install python@3.11
```

### Step 2: Install Tkinter

```bash
# macOS
brew install python-tk@3.11

# Linux (Ubuntu/Debian)
sudo apt-get install python3-tk
```

### Step 3: Install Ollama

```bash
# macOS
brew install ollama

# Start Ollama service
ollama serve

# In another terminal, pull a recommended model
# Choose one based on your system capabilities:

# Fast (3GB) - for quick testing
ollama pull llama3.2:3b

# Recommended (5GB) - best balance of speed and quality
ollama pull llama3.1:8b

# Highest quality (40GB) - requires powerful hardware
ollama pull llama3.1:70b
```

### Step 4: Clone/Download Quizzer V2

```bash
cd /path/to/ai-masters-notes/quizzer-v2
```

### Step 5: Make Launcher Executable

```bash
chmod +x start_quiz.sh
```

### Step 6: Verify Installation

```bash
./start_quiz.sh
```

If everything is installed correctly, you should see:
```
🚀 Quizzer V2 Launcher - Grounded Q&A Engine
✅ Python 3.11 detected
✅ Tkinter is available
✓ PyPDF2 installed
✓ Starting application...
```

---

## 🎯 Quick Start

### Basic Usage

```bash
cd /path/to/ai-masters-notes/quizzer-v2
./start_quiz.sh
```

### First-Time Setup

1. **Launch**: Run `./start_quiz.sh` or `python3 run.py`
2. **Select AI Model**: Choose from available Llama models
   - 🚀 Llama 3.2 (3B) - Fast, good for testing
   - ⭐ Llama 3.1 (8B) - **Recommended** (best quality/speed balance)
   - 💎 Llama 3.1 (70B) - Highest quality (requires powerful hardware)
3. **Create Account**: Register with username and password
4. **Login**: Enter your credentials
5. **Select Course**: Choose from available courses (NLP, ML, AR, etc.)
6. **Configure Quiz**: Select question types:
   - 📋 Multiple Choice Only
   - ✍️ Short Answers Only
   - 📝 Long Answers Only
   - 📊 Mixed Answers
   - 🎯 Everything Mixed (recommended)
7. **Start Quiz**: Click "Start Quiz →"
8. **Answer Questions**: Type answers or select options
9. **View Results**: Get detailed feedback with citations

---

## 📖 How to Use

### Course Selection

After launching, you'll see available courses:
- **Natural Language Processing** (NLP)
- **Machine Learning & Deep Learning** (ML-DL)
- **Automated Reasoning** (AR)
- **Planning**
- **Human-Computer Interaction** (HCI)

Each course shows the number of PDF notes available.

### Quiz Configuration

Choose your preferred question types:

| Option | Types Generated | Best For |
|--------|----------------|----------|
| **Multiple Choice Only** | MCQ (single/multi) | Quick review, concept testing |
| **Short Answers Only** | 2-4 sentence explanations | Concise understanding |
| **Long Answers Only** | Derivations, proofs | Deep comprehension |
| **Mixed Answers** | Short + Long | Open-ended practice |
| **Everything Mixed** | MCQ + Short + Long | Complete assessment |

### Answering Questions

#### Multiple Choice Questions
- Click the radio button for your answer
- Click "Submit Answer"

#### Open-Ended Questions
- Type your answer in the text box (minimum 3 words)
- Click "Submit Answer"

### Understanding Results

After submitting, you'll see:

1. **Result Title**: 
   - 🎉 **Excellent!** (≥90%)
   - 👍 **Good Effort!** (40-89%)
   - 📚 **Keep Studying!** (<40%)

2. **Score**: Points awarded / Total points

3. **Rubric Breakdown**:
   - ✅ Criteria met
   - ✗ Criteria not met
   - Evidence from reference notes

4. **Citations**: PDF file and page numbers referenced

---

## 🤖 AI Model Selection

Quizzer V2 supports multiple Llama models with different trade-offs:

### Available Models

| Model | Size | Speed | Quality | Best For | Recommendation |
|-------|------|-------|---------|----------|----------------|
| **Llama 3.2 (3B)** | ~2GB | ⚡⚡⚡ Very Fast | ⭐⭐ Fair | Quick testing, low-resource systems | Testing only |
| **Llama 3.1 (8B)** | ~5GB | ⚡⚡ Fast | ⭐⭐⭐⭐ Excellent | Production use, best balance | ✅ **Recommended** |
| **Llama 3.1 (70B)** | ~40GB | ⚡ Slower | ⭐⭐⭐⭐⭐ Outstanding | Maximum quality, powerful machines | Power users only |

### Model Selection Process

On first launch, you'll be presented with an interactive model selector:

```
🤖 AI MODEL SELECTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1] Llama 3.2 (3B)
    Status: ✅ INSTALLED
    Speed:  ⚡⚡⚡ Very Fast
    Quality: ⭐⭐ Fair
    Best for: Quick testing, low-resource systems

[2] Llama 3.1 (8B) 🌟 RECOMMENDED
    Status: ✅ INSTALLED
    Speed:  ⚡⚡ Fast
    Quality: ⭐⭐⭐⭐ Excellent
    Best for: Production use, best balance

[3] Llama 3.1 (70B)
    Status: 📥 NOT INSTALLED
    Speed:  ⚡ Slower
    Quality: ⭐⭐⭐⭐⭐ Outstanding
    Best for: Maximum quality, powerful machines

💡 RECOMMENDATION: Option [2] Llama 3.1 (8B) for best results!
```

- **Auto-Download**: If a model isn't installed, the app will offer to download it
- **Performance**: First question generation is slower (model loading), subsequent questions are faster
- **Memory**: Ensure you have enough RAM for your selected model

---

## 🔐 User Authentication

Quizzer V2 includes a complete user management system:

### Features

- **🔒 Secure Registration**: Username and password with validation
- **🔑 Password Hashing**: Passwords stored securely with SHA-256 + salt
- **👤 User Profiles**: Personalized experience for each user
- **📊 Progress Tracking**: All quiz attempts are saved per user
- **🏆 Rating System**: Dynamic rating based on performance

### Registration

1. Click **"Register"** on the login screen
2. Enter a unique username (3+ characters, alphanumeric)
3. Enter a password (8+ characters)
4. Confirm your password
5. Click **"Create Account"**

**Password Requirements**:
- Minimum 8 characters
- At least one letter
- At least one number or special character

### Login

1. Enter your username
2. Enter your password
3. Click **"Login"**

### User Profile

Access your profile from the main menu to view:

- **Username** and member since date
- **Current Rating** with AI-generated description
- **🎯 Quizzes Taken** - Total number of quizzes completed
- **❓ Questions Answered** - Total questions attempted
- **✅ Correct Answers** - Number of questions answered correctly
- **❌ Incorrect Answers** - Number of questions answered incorrectly
- **📊 Accuracy** - Overall percentage of correct answers
- **⭐ Total Stars** - Total stars earned from quizzes
- **💯 Average Score** - Average percentage score across all quizzes
- **📚 Favorite Course** - Your most-attempted course

**Available Actions**:
- 🔑 **Change Password**: Update your password securely
- 🗑️ **Delete Account**: Permanently remove your account and all data

### Rating System

Your rating evolves based on performance (calculated from accuracy, quizzes taken, and stars earned):

| Rating | Badge | Description |
|--------|-------|-------------|
| **Beginner** | 🎓 | New users starting their journey |
| **Emerging Scholar** | 🌱 | Building foundational knowledge |
| **Proficient Student** | 📚 | Demonstrating solid understanding |
| **Expert Learner** | ⭐ | Advanced mastery of concepts |
| **Master Scholar** | 🏆 | Exceptional performance and dedication |

*Ratings are calculated using a weighted score combining accuracy (50%), total stars earned (30%), and quiz completion (20%).*

---

## ✨ Animations & Visual Feedback

Quizzer V2 features smooth, fluid animations throughout the interface:

### Login/Registration
- **Success Animation**: Large green checkmark (✓) with fade-in effect
- **Auto-transition**: Smoothly transitions to main app after 800ms

### Loading States
- **Rotating Spinner**: 60px smooth arc animation for question generation
- **Animated Dots**: Text dots cycle (0-3) for loading messages
- **Non-blocking**: All animations run at 30-60 FPS without lag

### Chatbot
- **Typing Indicator**: Animated "typing..." with cycling dots
- **Smooth Scrolling**: Optimized trackpad scrolling (40% sensitivity)
- **Auto-scroll**: Messages automatically scroll into view

### UI Optimizations
- **Compact Layouts**: All pages fit in view without scrolling
- **Foreground Launch**: App always opens above other windows
- **Consistent Styling**: Light gray buttons (#e5e7eb) with black text
- **Responsive Design**: Adapts to window size changes

---

## 💬 AI Chatbot

Ask questions about your course material and get grounded, accurate answers.

### Features

- **📚 Course-Specific**: Chatbot only answers based on your selected course notes
- **🎯 Grounded Responses**: All answers include citations to PDF pages
- **🔍 Context-Aware**: Uses semantic search to find relevant content
- **💡 Conversational**: Handles both casual greetings and technical questions
- **📝 Source Attribution**: Every response shows which PDF and pages were used
- **⌨️ Typing Animation**: Smooth animated dots while AI generates response

### How to Use

1. **Start a Quiz Session**: Select a course and start a quiz
2. **Open Chatbot**: Click the **"💬 Ask AI"** button in the main window
3. **Ask Questions**: Type your question in the input box
4. **Get Answers**: Receive detailed responses with citations
5. **Continue Conversation**: Ask follow-up questions
6. **Close**: Click **"Close"** to return to the quiz

### Example Interaction

```
You: What is backpropagation?

AI Assistant:
Backpropagation is the fundamental algorithm used to train neural 
networks. It works by computing gradients of the loss function with 
respect to each weight by propagating error information backwards 
through the network, starting from the output layer.

The algorithm uses the chain rule of calculus to efficiently compute 
these gradients, allowing us to update weights using gradient descent.

📖 Sources:
• ML&DL Appunti.pdf (Pages 45-47)
```

### Best Practices

- **Be Specific**: Ask focused questions about concepts from your course
- **Use Context**: Reference topics from your notes
- **Follow Up**: Ask clarifying questions based on previous answers
- **Check Citations**: Verify answers by reviewing the cited pages

### Limitations

- Only answers questions based on loaded course PDFs
- Cannot access external information or the internet
- Quality depends on the selected AI model
- Response time: 3-10 seconds depending on model and question complexity

---

## 📝 Question Types

### 1. Multiple Choice (Single)
```
Question: What is the primary difference between Machine Learning 
          and Statistical Modelling?

Options:
○ A: Machine Learning uses statistical modelling
○ B: Machine Learning focuses on conventional programming
● C: Machine Learning is a subset of statistical modelling
○ D: Machine Learning involves data-driven decision making

Grading: Exact match only (10 points or 0 points)
```

### 2. Multiple Choice (Multiple)
```
Question: Select all correct statements about overfitting:

Options:
☑ A: Training error is low
☑ B: Testing error is high
☐ C: Model generalizes well
☐ D: More data always fixes it

Grading: Formula-based partial credit
Score = (correct_chosen / total_correct) - (incorrect_chosen / total_incorrect)
```

### 3. Short Answer
```
Question: Explain the five essential ingredients of machine learning 
          and their role in solving a problem.

Expected: 2-4 sentences covering Task, Data, Model, Objective, 
          Learning Algorithm

Grading: Rubric-based (concept coverage + completeness)
```

### 4. Long Answer / Derivation
```
Question: Derive the gradient descent update rule for linear regression.

Expected: Step-by-step mathematical derivation with explanations

Grading: Rubric-based (correct steps + reasoning)
```

---

## 🧪 Testing

### Test the Installation

```bash
# Run the launcher
./start_quiz.sh

# You should see:
# - Python version check ✅
# - Tkinter availability ✅
# - PyPDF2 installation ✅
# - GUI launch ✅
```

### Test Question Generation

1. Select a course (e.g., "Machine Learning & Deep Learning")
2. Choose "Multiple Choice Only" (fastest)
3. Wait 10-20 seconds for generation
4. Verify 5 questions are generated

### Test Grading System

#### Test 1: MCQ Grading
- Answer a multiple choice question
- Verify correct answers get 10/10 points
- Verify incorrect answers get 0/10 points

#### Test 2: Empty Answer Protection
- Try submitting an empty answer → Should show warning
- Try submitting "." → Should show "Invalid Answer" dialog
- Try submitting "ok" → Should get 0 points with "Answer too short" feedback

#### Test 3: Proper Answer Grading
- Write a detailed answer to a short answer question
- Verify you receive:
  - Points based on content
  - Rubric breakdown
  - Citations to PDF pages

### Test Animations

- **Hover Effects**: Hover over course buttons → should highlight
- **Progress Bar**: Should smoothly fill as you progress through questions
- **Score Animation**: Score should count up from 0 to final score
- **Pulse Effect**: Result header should pulse (grow/shrink)

### Expected Test Results

| Test | Expected Result | Pass/Fail |
|------|----------------|-----------|
| Installation | All checks ✅ | |
| Course Selection | Shows 5 courses | |
| Quiz Config | Shows 5 options | |
| Question Generation | 5 questions in 10-20s | |
| MCQ Correct | 10/10 points | |
| MCQ Incorrect | 0/10 points | |
| Empty Answer | Warning dialog | |
| Minimal Answer | 0 points + guard message | |
| Valid Answer | Partial/full credit | |
| Progress Bar | Smooth animation | |
| Score Count | Animates 0→final | |

---

## 📁 Project Structure

```
quizzer/
├── run.py                    # Main entry point with dependency checks
├── start_quiz.sh             # Shell launcher for macOS
├── README.md                 # This file
├── VERSION                   # Version number (3.0.0)
│
├── src/                      # Source code
│   ├── __init__.py
│   │
│   ├── engines/              # Core logic engines
│   │   ├── __init__.py
│   │   ├── quizzer_v2_engine.py    # Main quiz orchestrator
│   │   ├── question_generator.py   # AI question generation
│   │   ├── grading_engine.py       # AI answer evaluation
│   │   ├── rating_generator.py     # User rating system (5-tier)
│   │   └── chatbot_engine.py       # AI chatbot with conversational AI
│   │
│   ├── gui/                  # User interface
│   │   ├── __init__.py
│   │   ├── quizzer_v2_gui.py       # Main application window (1300+ lines)
│   │   ├── chatbot_gui.py          # Chat interface with animations
│   │   ├── auth_gui.py             # Login/registration with success animation
│   │   └── profile_gui.py          # Compact user profile page
│   │
│   └── utils/                # Utilities
│       ├── __init__.py
│       ├── local_ai.py             # Ollama AI interface
│       ├── pdf_grounding.py        # PDF parsing & semantic search
│       ├── user_manager.py         # User authentication & password management
│       └── animations.py           # Animation engine & UI components (NEW!)
│
├── user_data/                # User database (auto-created)
│   └── users.db              # SQLite database
│
└── tests/                    # Test suite
    ├── __init__.py
    └── test_chatbot.py       # Chatbot integration tests
```

### Key Components

**Engines**: Backend logic for quiz generation, grading, ratings, and chatbot  
**GUI**: Modern Tkinter interfaces with smooth animations  
**Utils**: Helper modules for AI, PDF processing, authentication, and animations  
**Database**: SQLite for user data, quiz history, and statistics

## 🏗️ Architecture

### Data Flow

```
User Launch
    ↓
start_quiz.sh → run.py
    ↓
[Check Python, Tkinter, PyPDF2]
    ↓
Initialize AI (Ollama)
    ↓
Launch GUI → Course Selection
    ↓
Quiz Configuration
    ↓
Question Generation (Background Thread)
    │
    ├→ PDF Grounding: Extract content from notes
    ├→ AI Generation: Create questions from content
    └→ Add rubrics & grounding citations
    ↓
Display Question
    ↓
User Answers
    ↓
Grading (Background Thread)
    │
    ├→ Validate answer (length, content)
    ├→ AI Grading: Evaluate against rubric
    ├→ False Positive Guard: Check minimal answers
    └→ Generate explanation + citations
    ↓
Display Result (with animations)
    ↓
Next Question or Final Results
```

### Key Algorithms

#### 1. MCQ Multi Grading Formula
```python
score_ratio = (correct_chosen / total_correct) - 
              (incorrect_chosen / total_incorrect)
score = max(0, min(1, score_ratio)) * max_points
```

#### 2. Decision Thresholds
```python
if percentage >= 0.9:
    decision = "correct"
elif percentage >= 0.4:
    decision = "partially_correct"
else:
    decision = "incorrect"
```

#### 3. False Positive Guard
```python
clean_answer = answer.strip().replace(punctuation, "")
if len(clean_answer) < 5:
    points = 0
    all_checks = False
```

---

## 🔍 Troubleshooting

### Common Issues

#### 1. "Python 3.11 not found"

**Solution**:
```bash
brew install python@3.11
# Verify
python3.11 --version
```

#### 2. "Tkinter is not available"

**Solution**:
```bash
brew install python-tk@3.11
# Test
python3.11 -c "import tkinter; print('OK')"
```

#### 3. "Ollama connection refused"

**Cause**: Ollama service not running

**Solution**:
```bash
# Start Ollama in one terminal
ollama serve

# Keep it running, then launch Quizzer in another terminal
```

#### 4. "Model not found: llama3.2:3b"

**Solution**:
```bash
ollama pull llama3.2:3b
# Wait for download to complete
```

#### 5. Questions take too long to generate

**Cause**: AI model loading or slow response

**Solutions**:
- First generation is slower (model loading)
- Subsequent generations are faster
- Reduce to 3 questions in code if needed
- Use faster model: `llama3.2:1b` (edit `run.py`)

#### 6. Grading always returns 0 points

**Possible Causes**:
- Answer too short (< 5 meaningful characters)
- False Positive Guard triggered
- AI connection issue

**Solution**:
- Write detailed answers (10+ words)
- Check terminal for error messages
- Verify Ollama is running

#### 7. GUI doesn't appear

**Solution**:
```bash
# Check if Python 3.11 has Tkinter
python3.11 -m tkinter
# Should open a small test window
```

#### 8. "Notes not found" error

**Cause**: PDF files missing or incorrect path

**Solution**:
- Verify PDFs exist in `courses/*/notes/*.pdf`
- Check file permissions
- Look at terminal output for exact error

---

## ⚙️ Advanced Configuration

### Change Number of Questions

Edit `src/gui/quizzer_v2_gui.py`:
```python
# Line ~330
"num_questions": 5,  # Change to desired number (3-10 recommended)
```

### Select Different AI Model

The AI model is selected at launch. To change the default:

Edit `run.py`:
```python
# Line ~207 - Modify the model selection or set a default
ai = LocalAI("llama3.1:8b")  # Options: llama3.2:3b, llama3.1:8b, llama3.1:70b
```

### Modify Grading Strictness

Edit `src/engines/grading_engine.py`:
```python
# Line ~260-267 - Change thresholds
if percentage >= 0.9:  # Change 0.9 to 0.85 for more lenient grading
    decision = "correct"
elif percentage >= 0.4:  # Change 0.4 to 0.3 for easier partial credit
    decision = "partially_correct"
```

### Add New Course

Edit `src/engines/quizzer_v2_engine.py`:
```python
# Line ~22-46
COURSES = {
    "your-course": {
        "name": "Your Course Name",
        "default_notes": ["courses/your-course/notes/notes.pdf"]
    },
    # ... existing courses
}
```

Then add your PDF files to the appropriate directory:
```bash
mkdir -p ../courses/your-course/notes/
cp your-notes.pdf ../courses/your-course/notes/
```

### Customize Colors

Edit `src/gui/quizzer_v2_gui.py`:
```python
# Line ~19-29
COLORS = {
    "bg": "#1a1a2e",       # Main background
    "fg": "#eee",          # Text color
    "primary": "#0f3460",  # Headers
    "accent": "#e94560",   # Buttons and accents
    "success": "#2ecc71",  # Success messages
    # Customize as needed
}
```

### Configure User Database Location

Edit `src/engines/quizzer_v2_engine.py`:
```python
# Line ~63 - Change database path
self.user_manager = UserManager("user_data/users.db")  # Modify path as needed
```

### Disable Debug Logging

Edit `src/gui/quizzer_v2_gui.py`:
```python
# Comment out or remove print statements:
# Search for "DEBUG:", "GRADING RESULT", etc.
# Line ~470-478 and similar debug output sections
```

### Adjust Question Generation Timeout

Edit `src/gui/quizzer_v2_gui.py`:
```python
# Line ~340 - Increase timeout for slower systems
timeout = 120  # Change from default 60 seconds to 120
```

---

## 📊 Performance

### Typical Performance Metrics

| Metric | Value |
|--------|-------|
| **Question Generation** | 10-20 seconds (5 questions) |
| **First Question** | ~15s (AI model loading) |
| **Subsequent Questions** | ~2-3s each |
| **Answer Grading** | 2-5 seconds |
| **Memory Usage** | ~500MB (with Ollama) |
| **Supported PDFs** | Unlimited size |

### Optimization Tips

1. **First Run**: Always slower due to model loading
2. **Keep Ollama Running**: Avoid restarting between sessions
3. **Smaller Quiz**: 3-5 questions for quick review
4. **MCQ Only**: Fastest generation and grading
5. **Warm-up**: Run a test quiz to load models

---

## 🛠️ Development

### Module Overview

The codebase is organized into three main packages:

#### **Engines** (`src/engines/`)
Core business logic for quiz generation and evaluation:
- `quizzer_v2_engine.py` - Main orchestrator, course management
- `question_generator.py` - AI-powered question generation from PDFs
- `grading_engine.py` - AI-powered answer evaluation with rubrics
- `rating_generator.py` - User rating calculation based on performance
- `chatbot_engine.py` - Context-aware Q&A chatbot

#### **GUI** (`src/gui/`)
User interface components using Tkinter:
- `quizzer_v2_gui.py` - Main quiz interface (1270 lines)
- `chatbot_gui.py` - Chat window for AI assistant
- `auth_gui.py` - Login and registration screens
- `profile_gui.py` - User profile and statistics display

#### **Utils** (`src/utils/`)
Helper modules and infrastructure:
- `local_ai.py` - Ollama API wrapper for local AI models
- `pdf_grounding.py` - PDF parsing, semantic search, citation extraction
- `user_manager.py` - SQLite-based user authentication and management

### Import Structure

The project uses **relative imports** within the `src` package:

```python
# Within engines/ modules
from ..utils.pdf_grounding import PDFGroundingEngine
from .grading_engine import GradingEngine

# Within gui/ modules  
from ..engines.quizzer_v2_engine import QuizzerV2
from ..utils.local_ai import LocalAI

# From external code (run.py, tests)
from src.gui.quizzer_v2_gui import QuizzerV2GUI
from src.engines.quizzer_v2_engine import QuizzerV2
```

### Running Tests

```bash
# Test chatbot integration
python3 tests/test_chatbot.py

# Test imports (syntax check)
python3 -m py_compile run.py
python3 -m py_compile src/engines/*.py
python3 -m py_compile src/gui/*.py
python3 -m py_compile src/utils/*.py
```

### Adding New Features

1. **New Engine**: Add to `src/engines/` and update `__init__.py`
2. **New GUI Component**: Add to `src/gui/` and import in main GUI
3. **New Utility**: Add to `src/utils/` and update `__init__.py`
4. **New Course**: Update `COURSES` dict in `quizzer_v2_engine.py`

### Code Style

- **Type Hints**: Use type hints for all function parameters and returns
- **Docstrings**: Google-style docstrings for all public methods
- **Error Handling**: Catch specific exceptions, provide helpful error messages
- **Threading**: Use threading for long-running AI operations (don't block GUI)
- **Logging**: Use print statements for debugging (can be removed for production)

### Database Schema

User data is stored in SQLite (`user_data/users.db`):

**Users Table**:
- `user_id` (INTEGER PRIMARY KEY)
- `username` (TEXT UNIQUE)
- `password_hash` (TEXT) - SHA-256 with salt
- `salt` (TEXT)
- `created_at` (TIMESTAMP)

**Quiz Attempts Table**:
- `attempt_id` (INTEGER PRIMARY KEY)
- `user_id` (INTEGER FK)
- `course` (TEXT)
- `score` (REAL) - Percentage 0-100
- `total_questions` (INTEGER)
- `attempted_at` (TIMESTAMP)

### Dependencies

**Runtime**:
- Python 3.8+ (3.11 recommended)
- `PyPDF2==3.0.1` - PDF parsing
- `tkinter` - GUI framework (built-in on most systems)
- `ollama` - Local AI inference (external service)

**Development** (optional):
- `pytest` - For unit testing
- `mypy` - Type checking
- `black` - Code formatting

---

## 📄 License

MIT License - Feel free to use for educational purposes.

---

## 🙏 Acknowledgments

- **Ollama** - Local AI inference
- **PyPDF2** - PDF parsing
- **Tkinter** - GUI framework
- Course materials from University of Verona AI Masters program

---

## 📧 Support

For issues or questions:
1. Check [Troubleshooting](#-troubleshooting)
2. Verify [Prerequisites](#-prerequisites)
3. Review terminal output for error messages
4. Check Ollama service status

---

**Built with ❤️ for AI Masters students**
