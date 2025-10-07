# 📚 Courses Directory

This directory contains all course materials for the **first semester** of the Master's program in Artificial Intelligence at the University of Verona (2025/2026).

## 📂 Available Courses

### 🤖 [Automated Reasoning](./automated-reasoning/)
- **Notes**: Comprehensive LaTeX-compiled PDF
- **Slides**: 5 lecture presentations
- **Topics**: Logic, theorem proving, SAT solving, constraint programming

### 💬 [Natural Language Processing](./natural-language-processing/)
- **Notes**: 400+ pages of detailed material
- **Slides**: 16 lecture presentations (L0-L15)
- **Topics**: Text processing, embeddings, transformers, neural NLP

### 🎯 [Planning & Reinforcement Learning](./planning-and-reinforcement-learning/)
- **Notes**: 23 pages of focused content
- **Slides**: 6 lecture presentations
- **Topics**: Classical planning, state systems, STRIPS, RL fundamentals

### 👁️ [Human-Computer Interaction](./human-computer-interaction/)
- **Notes**: Multimodal Systems (Theory 2)
- **Slides**: To be added
- **Topics**: Multimodal interaction, AR/VR, affective computing, Unity

## 📖 Structure

Each course directory follows a consistent structure:

```
<course-name>/
├── README.md          # Course-specific documentation
├── notes/            # Personal LaTeX notes
│   ├── *.tex        # LaTeX source files
│   └── *.pdf        # Compiled PDF documents
└── slides/          # Official course slides
    └── *.pdf/pptx   # Lecture presentations
```

## 🔧 Working with LaTeX

All personal notes are written in LaTeX for professional typesetting.

### Prerequisites
Install a LaTeX distribution:
- **macOS**: MacTeX
- **Windows**: MiKTeX
- **Linux**: TeX Live

### Compilation
Navigate to a course's notes directory and compile:

```bash
cd <course-name>/notes
pdflatex "<filename>.tex"
```

For courses with bibliographies or multiple references, run `pdflatex` twice.

## 📊 Quick Stats

| Course | Notes Pages | Slides | Status |
|--------|-------------|--------|--------|
| Automated Reasoning | ~50 | 5 | ✅ Complete |
| Natural Language Processing | 400+ | 16 | ✅ Complete |
| Planning & RL | 23 | 6 | ✅ Complete |
| Human-Computer Interaction | ~30 | TBA | 🔄 In Progress |

## 🎯 Learning Path

Recommended order for studying:
1. **Automated Reasoning** - Foundation in logic and formal methods
2. **Natural Language Processing** - Core AI/ML techniques
3. **Planning & RL** - Sequential decision making
4. **HCI** - Applied AI in interactive systems

## 📜 Academic Integrity

All materials in this directory are for **educational purposes only**:
- Course slides are property of the University of Verona
- Personal notes are shared under an educational license
- Do not use for academic misconduct
- Respect copyright and intellectual property

## 🤝 Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on:
- Reporting errors or typos
- Suggesting improvements
- Submitting corrections

## 📧 Contact

For questions about specific course materials, please open an issue on the main repository.

---

[← Back to Main Repository](../README.md)
