<div align="center">

<!-- Header Banner -->
<img src="https://capsule-render.vercel.app/api?type=venom&color=0:4FC3F7,100:81D4FA&height=300&section=header&text=AI%20Master's%20Degree&fontSize=50&fontColor=000&fontAlignY=35&desc=2025/2026&descAlignY=51&descAlign=50" width="100%"/>

<br/>

<!-- AI Animation -->
<img src="https://user-images.githubusercontent.com/74038190/212749447-bfb7e725-6987-49d9-ae85-2015e3e7cc41.gif" alt="AI Animation" width="400"/>

<br/>

<!-- Badges -->
<p align="center">
  <img src="https://img.shields.io/badge/University-Verona-DC143C?style=for-the-badge" alt="University"/>
  <img src="https://img.shields.io/badge/Year-2025/2026-4169E1?style=for-the-badge" alt="Year"/>
  <img src="https://img.shields.io/badge/Courses-5-00CED1?style=for-the-badge" alt="Courses"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/LaTeX-008080?style=for-the-badge&logo=latex&logoColor=white" alt="LaTeX"/>
  <img src="https://img.shields.io/badge/PDF-Ready-32CD32?style=for-the-badge&logo=adobe-acrobat-reader&logoColor=white" alt="PDF"/>
  <img src="https://img.shields.io/badge/AI_Quiz-NEW!-FF6B6B?style=for-the-badge&logo=openai&logoColor=white" alt="AI Quiz"/>
</p>

<br/>

### ⭐ **NEW: AI-Powered Quiz App** | Test Your Knowledge with Intelligent Evaluation!

###  *Made with 💜 by jaco for AI students at University of Verona*

<br/>

</div>

---

## 📂 Repository Structure

```
AI---PRIMO-SEMESTRE/
├── 📄 README.md
├── 📄 LICENSE
├── 📄 .gitignore
├── 🎓 quizzer-v2/              ⭐ NEW: AI-POWERED QUIZ APP!
│   ├── run.py                  # Main launcher with dependency checker
│   ├── start_quiz.sh           # Shell wrapper for macOS compatibility
│   ├── quiz.py                 # Core quiz logic engine
│   ├── quiz_gui.py             # Modern GUI with animations
│   └── local_ai.py             # Local AI integration (Ollama)
├── 📁 courses/
│   ├── automated-reasoning/
│   │   ├── notes/
│   │   └── slides/
│   ├── natural-language-processing/
│   │   ├── notes/
│   │   └── slides/
│   ├── planning-and-reinforcement-learning/
│   │   ├── notes/
│   │   └── slides/
│   ├── machine-learning-and-deep-learning/
│   │   ├── notes/
│   │   ├── slides/
│   │   └── lab/
│   └── human-computer-interaction/
│       ├── notes/
│       └── slides/
└── 📁 docs/
    └── CORSI 1 ANNO AI provvisorio.pdf
```

---

<div align="center">

## 🎓 **AI-POWERED QUIZ APP** ⭐ NEW!

<img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif" width="700">

### Test Your Knowledge with Intelligent AI Evaluation!

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![AI](https://img.shields.io/badge/AI-Powered-FF6B6B?style=for-the-badge&logo=openai&logoColor=white)](https://ollama.com)
[![Tkinter](https://img.shields.io/badge/GUI-Tkinter-4B8BBE?style=for-the-badge&logo=python&logoColor=white)](https://docs.python.org/3/library/tkinter.html)
[![Free](https://img.shields.io/badge/100%25-FREE-00D9FF?style=for-the-badge&logo=github&logoColor=white)](https://github.com)

</div>

### ✨ **Features**

<table>
<tr>
<td width="50%">

#### 🤖 **Smart AI Evaluation**
- **Local AI** powered by Ollama (FREE, no API key!)
- Intelligent grading on 5-level scale
- Context-aware evaluation (calculations, definitions, explanations)
- Contradiction detection
- Reference-based scoring

#### 🎨 **Modern Beautiful UI**
- Dark themed interface
- Smooth animations & transitions
- Staggered card slide-ins
- Bounce effects on results
- Responsive design

</td>
<td width="50%">

#### 📚 **Smart Content Extraction**
- Auto-extracts from your LaTeX notes
- Supports: definitions, theorems, propositions, lemmas
- Randomized questions (15 per session)
- Course-specific testing

#### ⚡ **Performance & UX**
- **PERFECT** score for correct answers
- Fair grading (no false negatives)
- Instant feedback
- Streak tracking
- No internet required (local AI)

</td>
</tr>
</table>

---

### 🚀 **Quick Start**

<details>
<summary><b>📦 Installation (One-Time Setup)</b></summary>

<br/>

**1. Install Dependencies:**

```bash
# Install Ollama (for local AI)
brew install ollama

# Install Python 3.11+ (if needed)
brew install python@3.11 python-tk@3.11

# Pull the AI model (one time, ~2GB)
ollama pull llama3.2:3b
```

**2. Start Ollama Service:**

```bash
brew services start ollama
```

✅ **That's it! You're ready to quiz!**

</details>

<details>
<summary><b>🎮 How to Use</b></summary>

<br/>

**Launch the Quiz App:**

```bash
cd quizzer-v2
./start_quiz.sh
```

**Or with Python directly:**

```bash
python3.11 run.py
```

**Quiz Workflow:**
1. 📚 **Choose your course** (Automated Reasoning, NLP, ML, etc.)
2. ⚡ **AI generates questions** from your notes automatically
3. ✍️ **Answer the question** in the text box
4. 🤖 **AI evaluates** your answer (PERFECT/GOOD/PARTIAL/WEAK/WRONG)
5. 📊 **Get detailed feedback** with reference material
6. 🔥 **Build your streak** and track perfect scores!

</details>

---

### 🎯 **Grading System**

The AI uses a **strict but fair** 5-level evaluation:

| Level | Grade | Description |
|-------|-------|-------------|
| ⭐⭐⭐⭐⭐ | **PERFECT** | Complete, accurate, covers all key points |
| ⭐⭐⭐⭐ | **GOOD** | Covers most concepts with minor gaps |
| ⭐⭐⭐ | **PARTIAL** | Shows genuine partial understanding |
| ⭐⭐ | **WEAK** | Major gaps or errors |
| ⭐ | **WRONG** | Incorrect, contradicts reference, or off-topic |

**Smart Evaluation:**
- ✅ Detects question types (calculation, factual, definition, explanation)
- ✅ Doesn't penalize for missing unrequested information
- ✅ Catches contradictions (marks as WRONG, not PARTIAL)
- ✅ Correct numerical answers = PERFECT (no extra explanation needed)
- ✅ Verifies against actual course reference material

---

### 🛠️ **Technical Highlights**

```python
# Intelligent Question Type Detection
✓ Calculations: Formula + Result = PERFECT
✓ Factual: Correct fact/number = PERFECT  
✓ Definitions: Key concepts from reference required
✓ Explanations: Reasoning aligned with reference needed

# Strict Contradiction Detection
✓ "without X" vs "with X" → WRONG
✓ "randomly" vs "maintains proportion" → WRONG
✓ Opposite statements caught immediately

# Fair Grading
✓ Only grades what was ACTUALLY asked
✓ Doesn't invent requirements
✓ Context-aware evaluation
```

---

### 📸 **Screenshots**

<div align="center">

**Course Selection Screen**

*Beautiful animated cards for each course*

**Quiz Interface**

*Clean, modern design with progress tracking*

**Results & Feedback**

*Detailed evaluation with reference material*

</div>

---

### 💡 **Why Use This Quiz App?**

<table>
<tr>
<td align="center" width="25%">
<img src="https://img.icons8.com/fluency/96/000000/artificial-intelligence.png" width="60"/><br/>
<b>AI-Powered</b><br/>
<sub>Smart evaluation like a real professor</sub>
</td>
<td align="center" width="25%">
<img src="https://img.icons8.com/fluency/96/000000/money-bag.png" width="60"/><br/>
<b>100% Free</b><br/>
<sub>No API keys, no subscriptions</sub>
</td>
<td align="center" width="25%">
<img src="https://img.icons8.com/fluency/96/000000/offline.png" width="60"/><br/>
<b>Works Offline</b><br/>
<sub>Local AI, no internet needed</sub>
</td>
<td align="center" width="25%">
<img src="https://img.icons8.com/fluency/96/000000/checked.png" width="60"/><br/>
<b>Fair Grading</b><br/>
<sub>No false negatives</sub>
</td>
</tr>
</table>

---

<a name="courses"></a>

<table>
<tr>
<td width="50%" valign="top">

<div align="center">

### 🤖 **Automated Reasoning**
[![Course](https://img.shields.io/badge/Slides-5-blue?style=flat-square)](courses/automated-reasoning/slides)
[![Notes](https://img.shields.io/badge/Notes-PDF-red?style=flat-square&logo=adobe-acrobat-reader)](courses/automated-reasoning/notes)

</div>

> 📄 **AR Appunti.pdf** • LaTeX source available

**🔬 Key Topics:**
```
✓ Logic & Formal Methods
✓ Theorem Proving  
✓ SAT Solving
✓ Constraint Programming
```

</td>
<td width="50%" valign="top">

<div align="center">

### 💬 **Natural Language Processing**
[![Course](https://img.shields.io/badge/Slides-16-blue?style=flat-square)](courses/natural-language-processing/slides)
[![Notes](https://img.shields.io/badge/Notes-500+_pages-red?style=flat-square&logo=adobe-acrobat-reader)](courses/natural-language-processing/notes)

</div>

> 📄 **NLP Appunti.pdf** • 500+ comprehensive pages • 3 Parts • 17 Sections

**🔬 Key Topics:**
```
✓ Minimum Edit Distance & Dynamic Programming
✓ Regular Expressions & Pattern Matching
✓ Text Normalization & Tokenization
✓ Subword Tokenization (BPE, WordPiece)
✓ Multilingual Processing (Chinese, Japanese)
✓ Word Normalization & Lemmatization
✓ Morphological Parsing & Stemming
✓ Sentence Segmentation
```

</td>
</tr>
<tr>
<td width="50%" valign="top">

<div align="center">

### 🧠 **Machine Learning & Deep Learning**
[![Course](https://img.shields.io/badge/Slides-1-blue?style=flat-square)](courses/machine-learning-and-deep-learning/slides)
[![Notes](https://img.shields.io/badge/Notes-20_pages-red?style=flat-square&logo=adobe-acrobat-reader)](courses/machine-learning-and-deep-learning/notes)
[![Lab](https://img.shields.io/badge/Lab-Available-green?style=flat-square)](courses/machine-learning-and-deep-learning/lab)

</div>

> 📄 **ML&DL Appunti.pdf** • Comprehensive foundations

**🔬 Key Topics:**
```
✓ Introduction to Machine Learning
✓ Supervised & Unsupervised Learning
✓ Model Training & Hypothesis Space
✓ Overfitting & Underfitting
✓ Regularization Techniques
✓ Polynomial Fitting & Error Functions
```

</td>
<td width="50%" valign="top">

<div align="center">

### 🎯 **Planning & Reinforcement Learning**
[![Course](https://img.shields.io/badge/Slides-6-blue?style=flat-square)](courses/planning-and-reinforcement-learning/slides)
[![Notes](https://img.shields.io/badge/Notes-23_pages-red?style=flat-square&logo=adobe-acrobat-reader)](courses/planning-and-reinforcement-learning/notes)

</div>

> 📄 **Planning appunti.pdf** • Detailed foundations

**🔬 Key Topics:**
```
✓ Classical Planning Foundations
✓ State Transition Systems
✓ Action Schemas & STRIPS
✓ SAT Encoding & DWR Domain
```

</td>
<td width="50%" valign="top">

<div align="center">

### 👁️ **Human-Computer Interaction**
[![Course](https://img.shields.io/badge/Slides-Available-blue?style=flat-square)](courses/human-computer-interaction/slides)
[![Notes](https://img.shields.io/badge/Notes-Theory_2-red?style=flat-square&logo=adobe-acrobat-reader)](courses/human-computer-interaction/notes)

</div>

> 📄 **HCI Theory 2 Appunti.pdf** • Multimodal Systems

**🔬 Key Topics:**
```
✓ Multimodal Interaction Design
✓ Visual & Camera-based Systems
✓ Affective Computing
✓ AR/VR Technologies
```

</td>
</tr>
</table>

---

<div align="center">

## 🚀 Getting Started

</div>

<div align="center">

### 📥 **Clone the Repository**

```bash
git clone https://github.com/djacoo/AI---PRIMO-SEMESTRE.git
cd AI---PRIMO-SEMESTRE
```

</div>

---

### 📖 **Access Study Materials**

<table>
<tr>
<td width="33%" align="center">

#### 📚 **Notes**
Comprehensive PDFs ready to read

```bash
open courses/<course>/notes/
```

</td>
<td width="33%" align="center">

#### 🎯 **Slides**
Lecture presentations

```bash
open courses/<course>/slides/
```

</td>
<td width="33%" align="center">

#### 📝 **LaTeX Source**
Customizable `.tex` files

```bash
cd courses/<course>/notes/
```

</td>
</tr>
</table>

---

### ⚡ **Quick Navigation Examples**

<details>
<summary><b>🔍 Click to expand examples</b></summary>

<br/>

**View NLP Notes:**
```bash
open courses/natural-language-processing/notes/"NLP Appunti.pdf"
```

**Browse Planning Slides:**
```bash
ls courses/planning-and-reinforcement-learning/slides/
```

**Compile LaTeX from Source:**
```bash
cd courses/automated-reasoning/notes/
pdflatex "AR Appunti.tex"
```

**Quick Course Overview:**
```bash
open docs/"CORSI 1 ANNO AI provvisorio.pdf"
```

</details>

---

<div align="center">

## 📏 License & Usage

**📚 Educational Use Only**

These materials are intended for **personal study and academic reference**.  
Course slides and materials are property of their respective professors and the **University of Verona**.

**Please respect intellectual property rights and academic integrity.**

</div>

---

<div align="center">

## 📊 Repository Stats

<table>
  <tr>
    <td align="center">
      <img src="https://img.shields.io/badge/Total_Courses-5-blue?style=for-the-badge&logo=bookstack" alt="Courses"/>
    </td>
    <td align="center">
      <img src="https://img.shields.io/badge/Lecture_Slides-29+-green?style=for-the-badge&logo=slideshare" alt="Slides"/>
    </td>
    <td align="center">
      <img src="https://img.shields.io/badge/Notes_Pages-500+-purple?style=for-the-badge&logo=read-the-docs" alt="Pages"/>
    </td>
    <td align="center">
      <img src="https://img.shields.io/badge/PDF_Files-Ready-red?style=for-the-badge&logo=adobe" alt="PDFs"/>
    </td>
    <td align="center">
      <img src="https://img.shields.io/badge/AI_Quiz-Powered-FF6B6B?style=for-the-badge&logo=openai" alt="Quiz"/>
    </td>
  </tr>
</table>

</div>

---

<div align="center">

## 👨‍💻 Author

<img src="https://img.shields.io/badge/Jacopo_Parretti-AI_Student-blueviolet?style=for-the-badge&logo=github" alt="Author"/>

**Master's in Artificial Intelligence**  
🏛️ University of Verona • 2025/2026

[![GitHub](https://img.shields.io/badge/GitHub-djacoo-181717?style=for-the-badge&logo=github)](https://github.com/djacoo)
[![Email](https://img.shields.io/badge/Email-Contact-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:jacopo.parretti@studenti.univr.it)

</div>

---

<div align="center">

## 💡 Contributions & Feedback

Found this helpful? ⭐ **Star this repository** to support the project!

**New:** Try the AI-Powered Quiz App! 🎓

<br/>

<sub>📅 Last updated: October 2025 | Made with ❤️ for AI students at University of Verona | Now with AI Quiz! 🤖</sub>

<br/><br/>

<!-- Footer -->
<img src="https://capsule-render.vercel.app/api?type=venom&color=0:4B0082,100:8B00FF&height=100&section=footer" width="100%"/>

</div>
