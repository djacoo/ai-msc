# Quizzer V2 - AI-Powered Academic Quiz System

> **Academic-grade quiz generator with AI teacher evaluation**  
> Generate questions from your course PDFs and receive detailed, grounded feedback from an AI teacher.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![macOS](https://img.shields.io/badge/Platform-macOS-lightgrey.svg)](https://www.apple.com/macos/)

---

## 📋 Table of Contents

- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [How to Use](#-how-to-use)
- [Question Types](#-question-types)
- [Testing](#-testing)
- [Architecture](#-architecture)
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

### User Experience
- **🎨 Modern UI**: Clean, professional interface with smooth animations
- **📈 Progress Tracking**: Visual progress bar and real-time score updates
- **💫 Fluid Animations**: Hover effects, score counting, pulse effects
- **⚙️ Customizable**: Choose question types before starting quiz
- **📱 Responsive**: Adapts to different screen sizes

### Academic Rigor
- **Strict Grading**: ≥90% for correct, 40-89% partially correct, <40% incorrect
- **Rubric-Based**: Each question has detailed point breakdown
- **Concept Tracking**: Identifies and evaluates key concepts
- **False Positive Guard**: Automatically detects and fails minimal answers
- **Grounded Feedback**: All explanations reference course material

---

## 🔧 Prerequisites

### Required
- **Python 3.11+** (Python 3.8+ may work but 3.11 recommended)
- **macOS** (tested on macOS, may work on Linux with modifications)
- **Ollama** with `llama3.2:3b` model installed

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

# In another terminal, pull the model
ollama pull llama3.2:3b
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

1. **Launch**: Run `./start_quiz.sh`
2. **Select Course**: Choose from available courses (NLP, ML, AR, etc.)
3. **Configure Quiz**: Select question types:
   - 📋 Multiple Choice Only
   - ✍️ Short Answers Only
   - 📝 Long Answers Only
   - 📊 Mixed Answers
   - 🎯 Everything Mixed (recommended)
4. **Start Quiz**: Click "Start Quiz →"
5. **Answer Questions**: Type answers or select options
6. **View Results**: Get detailed feedback with citations

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

## 🏗️ Architecture

### System Components

```
quizzer-v2/
├── start_quiz.sh          # Entry point launcher
├── run.py                 # Dependency checker & app launcher
├── quizzer_v2_gui.py      # User interface (36KB)
├── quizzer_v2_engine.py   # Core quiz logic
├── question_generator.py  # AI question generation
├── grading_engine.py      # AI answer evaluation
├── pdf_grounding.py       # PDF parsing & search
└── local_ai.py            # Ollama integration
```

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

Edit `quizzer_v2_gui.py`:
```python
# Line ~330
"num_questions": 5,  # Change to desired number (3-10 recommended)
```

### Change AI Model

Edit `run.py`:
```python
# Line ~75
ai = LocalAI("llama3.2:3b")  # Change to "llama3.2:1b" for faster (less accurate)
```

### Modify Grading Strictness

Edit `grading_engine.py`:
```python
# Line ~260-267 - Change thresholds
if percentage >= 0.9:  # Change 0.9 to 0.85 for more lenient
    decision = "correct"
```

### Add New Course

Edit `quizzer_v2_engine.py`:
```python
# Line ~19-42
COURSES = {
    "your-course": {
        "name": "Your Course Name",
        "default_notes": ["path/to/notes.pdf"]
    },
    # ... existing courses
}
```

### Customize Colors

Edit `quizzer_v2_gui.py`:
```python
# Line ~18-27
COLORS = {
    "bg": "#1a1a2e",       # Main background
    "primary": "#0f3460",  # Headers
    "accent": "#e94560",   # Accent elements
    # Customize as needed
}
```

### Disable Debug Logging

Edit `quizzer_v2_gui.py`:
```python
# Comment out or remove print statements:
# Line ~470-478 (GRADE_ANSWER RETURNED)
# Line ~493-501 (GRADING RESULT)
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
