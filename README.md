<div align="center">

# 🎓 Master's Degree in Artificial Intelligence
## University of Verona - First Semester

[![University](https://img.shields.io/badge/University-Verona-gold?style=flat-square)](https://www.univr.it/)
[![Academic Year](https://img.shields.io/badge/Academic%20Year-2025%2F2026-blue?style=flat-square)](https://github.com/djacoo/AI---PRIMO-SEMESTRE)
[![License](https://img.shields.io/badge/License-Educational%20Use-green?style=flat-square)](#-license)

*A comprehensive collection of course materials, lecture notes, and resources for the Master's program in Artificial Intelligence*

</div>

---

## 📋 Table of Contents

- [About](#-about)
- [Repository Structure](#-repository-structure)
- [Courses](#-courses)
  - [Automated Reasoning (AR)](#automated-reasoning-ar)
  - [Natural Language Processing (NLP)](#natural-language-processing-nlp)
  - [Planning & Reinforcement Learning (PLANNING & RL)](#planning--reinforcement-learning-planning--rl)
  - [Human-Computer Interaction (HCI)](#human-computer-interaction-hci)
- [Getting Started](#-getting-started)
- [Technologies & Tools](#-technologies--tools)
- [Contributing](#-contributing)
- [University Information](#-university-information)
- [License](#-license)
- [Contact](#-contact)

---

## 🎯 About

This repository serves as a centralized, organized collection of all academic materials for the **Master's Degree in Artificial Intelligence** at the **University of Verona**. The repository is structured by semester and course, providing easy navigation and reference to all materials throughout the program.

### Key Features

- 📚 **Comprehensive Notes**: Detailed LaTeX-formatted course notes
- 📊 **Lecture Slides**: Complete slide decks from all lectures
- 💻 **Exercises & Solutions**: Practice problems and implementations
- 🔍 **Well-Organized**: Systematic folder structure for easy navigation
- 📖 **Multi-Language**: Materials in both Italian and English

---

## 📁 Repository Structure

```
AI---PRIMO-SEMESTRE/
│
├── README.md                           # This file
├── CORSI 1 ANNO AI provvisorio.pdf    # Course overview document
│
├── AR/                                 # Automated Reasoning
│   ├── AR Appunti.tex                 # LaTeX source for notes
│   ├── AR Appunti.pdf                 # Compiled course notes
│   ├── lectures/                      # Lecture slides
│   │   └── AutomatedReasoning-1.pdf to -5.pdf
│   └── [LaTeX auxiliary files]
│
├── NLP/                                # Natural Language Processing
│   ├── NLP Appunti.tex                # LaTeX source for notes
│   ├── NLP Appunti.pdf                # Compiled course notes (400+ pages)
│   └── Slide/                         # Lecture slides
│       ├── L0 Introduction.pptx
│       ├── L1.pptx - L15.pptx        # 16 lecture presentations
│       └── [Additional materials]
│
├── PLANNING & RL/                      # Planning & Reinforcement Learning
│   └── lectures/                      # Lecture slides
│       └── Planning-1.pdf to -6.pdf  # 6 lecture presentations
│
└── HCI/                                # Human-Computer Interaction
    └── Theory 2/                      # MultiModal Systems - Theory 2
        ├── HCI Theory 2 Appunti.tex   # LaTeX source for notes
        ├── HCI Theory 2 Appunti.pdf   # Compiled course notes
        └── [LaTeX auxiliary files]
```

---

## 🎓 Courses

### Automated Reasoning (AR)

**Course Overview**: Study of automated reasoning techniques, logic programming, and constraint solving.

**Materials Available**:
- 📄 **Comprehensive Notes**: `AR Appunti.pdf` (240+ KB, LaTeX-formatted)
- 📊 **Lecture Slides**: 5 lectures (AutomatedReasoning-1 to -5) in PDF format
- 📝 **Source Files**: Complete LaTeX source code for customization
- 🔧 **Topics Covered**: Logic, theorem proving, SAT solving, and more

**Quick Access**:
```bash
# View the notes
open AR/AR\ Appunti.pdf

# Access lecture slides
cd AR/lectures

# Compile from source
cd AR && pdflatex AR\ Appunti.tex
```

---

### Natural Language Processing (NLP)

**Course Overview**: In-depth exploration of modern NLP techniques, from traditional methods to state-of-the-art deep learning approaches.

**Materials Available**:
- 📄 **Extensive Notes**: `NLP Appunti.pdf` (400+ KB, 87K+ LaTeX source)
- 📊 **Complete Slide Deck**: 16 lectures (L0-L15) covering the entire course
- 🎯 **Topics Covered**: 
  - Introduction to NLP
  - Text preprocessing and tokenization
  - Language models and embeddings
  - Neural networks for NLP
  - Transformers and attention mechanisms
  - Advanced applications

**Quick Access**:
```bash
# View the notes
open NLP/NLP\ Appunti.pdf

# Access lecture slides
cd NLP/Slide

# Compile from source
cd NLP && pdflatex NLP\ Appunti.tex
```

**Lecture Breakdown**:
| Lecture | File | Format |
|---------|------|--------|
| L0 | Introduction | PPTX |
| L1-L9 | Core Concepts | PPTX |
| L10, L12 | Advanced Topics | PDF |
| L11, L13-L15 | Applications | PPTX |

---

### Planning & Reinforcement Learning (PLANNING & RL)

**Course Overview**: Study of automated planning techniques and reinforcement learning algorithms for intelligent decision-making systems.

**Materials Available**:
- 📊 **Complete Lecture Series**: 6 lectures (Planning-1 to -6) in PDF format
- 🎯 **Topics Covered**: 
  - Classical planning approaches
  - Search algorithms for planning
  - Reinforcement learning fundamentals
  - Advanced RL techniques
  - Applications and case studies

**Quick Access**:
```bash
# Access lecture slides
cd PLANNING\ \&\ RL/lectures

# View a specific lecture
open PLANNING\ \&\ RL/lectures/Planning-1.pdf
```

**Lecture Breakdown**:
| Lecture | File | Size |
|---------|------|------|
| Planning-1 | PDF | ~7.5 MB |
| Planning-2 | PDF | ~250 KB |
| Planning-3 | PDF | ~420 KB |
| Planning-4 | PDF | ~560 KB |
| Planning-5 | PDF | ~1.5 MB |
| Planning-6 | PDF | ~1.1 MB |

---

### Human-Computer Interaction (HCI)

**Course Overview**: Study of multimodal interaction systems, combining theoretical foundations of HCI with practical implementation of intelligent interfaces.

**Materials Available**:
- 📄 **Comprehensive Notes**: `HCI Theory 2 Appunti.pdf` (150+ KB, LaTeX-formatted)
- 📝 **Source Files**: Complete LaTeX source code for customization
- 🎯 **Topics Covered**: 
  - Foundations of multimodal interaction
  - Evolution of interaction paradigms (CLI → GUI → Pervasive)
  - Human factors in interface design
  - Visual interaction and 3D reconstruction
  - Nonverbal behavior in communication
  - Automated analysis of body language
  - Social artificial intelligence
  - Affective computing
  - Multimodal fusion techniques

**Laboratory Topics**:
- Deep image matching and feature detection
- 3D model reconstruction (Structure from Motion)
- Camera pose estimation
- Unity 3D graphics and game engine
- Model-based augmented reality
- Deep learning for computer vision

**Quick Access**:
```bash
# View the notes
open HCI/Theory\ 2/HCI\ Theory\ 2\ Appunti.pdf

# Compile from source
cd HCI/Theory\ 2 && pdflatex HCI\ Theory\ 2\ Appunti.tex
```

**Course Structure**:
| Component | Content | Format |
|-----------|---------|--------|
| Theory 2 | MultiModal Systems | LaTeX Notes |
| Focus | Intelligent Multimodal Interfaces | PDF (150KB) |
| Language | Italian | TEX Source |

---

## 🚀 Getting Started

### Prerequisites

To work with the LaTeX source files, you'll need:

- **LaTeX Distribution**: 
  - macOS: [MacTeX](https://www.tug.org/mactex/)
  - Windows: [MiKTeX](https://miktex.org/)
  - Linux: `texlive-full`

- **PDF Viewer**: Any modern PDF reader
- **Office Suite**: Microsoft Office or LibreOffice for slide presentations

### Cloning the Repository

```bash
# Clone this repository
git clone https://github.com/djacoo/AI---PRIMO-SEMESTRE.git

# Navigate to the directory
cd AI---PRIMO-SEMESTRE
```

### Compiling LaTeX Notes

```bash
# For AR notes
cd AR
pdflatex AR\ Appunti.tex
pdflatex AR\ Appunti.tex  # Run twice for TOC

# For NLP notes
cd ../NLP
pdflatex NLP\ Appunti.tex
pdflatex NLP\ Appunti.tex  # Run twice for TOC

# For HCI notes
cd ../HCI/Theory\ 2
pdflatex HCI\ Theory\ 2\ Appunti.tex
pdflatex HCI\ Theory\ 2\ Appunti.tex  # Run twice for TOC
```

---

## 🛠️ Technologies & Tools

### Documentation
- ![LaTeX](https://img.shields.io/badge/LaTeX-008080?style=flat-square&logo=latex&logoColor=white) - Professional typesetting for notes
- ![Markdown](https://img.shields.io/badge/Markdown-000000?style=flat-square&logo=markdown&logoColor=white) - Documentation

### Formats
- **PDF** - Compiled notes and some lecture slides
- **PPTX** - Lecture presentations
- **TEX** - LaTeX source files

---

## 🤝 Contributing

This is a personal academic repository, but suggestions and corrections are welcome!

### How to Contribute

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/improvement`)
3. **Commit** your changes (`git commit -m 'Add some improvement'`)
4. **Push** to the branch (`git push origin feature/improvement`)
5. **Open** a Pull Request

### Contribution Guidelines

- Maintain the existing folder structure
- Follow LaTeX best practices for note formatting
- Ensure all materials respect copyright and academic integrity
- Add clear commit messages

---

## 🏛️ University Information

| | |
|---|---|
| **Institution** | Università degli Studi di Verona |
| **Faculty** | Department of Computer Science |
| **Program** | Master's Degree in Artificial Intelligence |
| **Academic Year** | 2025/2026 |
| **Semester** | First Semester (Primo Semestre) |
| **Location** | Verona, Italy 🇮🇹 |
| **Author** | Jacopo Parretti |


---

## 📄 License

**Educational Use Only**

This repository contains academic materials for personal educational purposes. All materials are subject to the following terms:

- ✅ **Permitted**: Personal study, reference, and learning
- ❌ **Not Permitted**: Commercial use, redistribution without attribution
- ⚠️ **Copyright**: Please respect the intellectual property rights of professors and the University of Verona

**Disclaimer**: Course slides and some materials are property of their respective professors and the University of Verona. This repository is maintained for educational purposes only.

---

## 📧 Contact

**Jacopo Parretti**

- 🐙 GitHub: [@djacoo](https://github.com/djacoo)
- 📧 Email: [Contact via GitHub](https://github.com/djacoo)

### Questions or Issues?

If you find any errors in the notes or have suggestions for improvement:
1. Open an [Issue](https://github.com/djacoo/AI---PRIMO-SEMESTRE/issues)
2. Submit a [Pull Request](https://github.com/djacoo/AI---PRIMO-SEMESTRE/pulls)
3. Contact me directly via GitHub

---

<div align="center">

### ⭐ If you find this repository useful, please consider giving it a star!

**Made with ❤️ for the AI community at University of Verona**

*Last updated: October 2025 - Added HCI MultiModal Systems course materials*

</div>
