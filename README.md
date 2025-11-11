# AI Master's Notes — University of Verona

A comprehensive collection of notes, teaching materials, reference books, and resources for the Master's program in Artificial Intelligence at the University of Verona (Academic Year 2025/2026).

---

## Table of Contents
- [Overview](#overview)
- [Repository Structure](#repository-structure)
- [Reference Books](#reference-books)
- [Getting Started](#getting-started)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Overview

This repository contains structured materials for five core courses in the AI Master's program:
- Automated Reasoning
- Human-Computer Interaction
- Machine Learning and Deep Learning
- Natural Language Processing
- Planning and Reinforcement Learning

Additionally, a curated collection of reference books and textbooks is included to support learning and research.

---

## Repository Structure

```
ai-masters-notes/
├── README.md
├── LICENSE
├── .gitignore
├── courses/
│   ├── automated-reasoning/
│   │   ├── notes/
│   │   └── slides/
│   ├── human-computer-interaction/
│   │   ├── assignment-1/
│   │   ├── notes/
│   │   └── slides/
│   ├── machine-learning-and-deep-learning/
│   │   ├── lab/
│   │   ├── notes/
│   │   └── slides/
│   ├── natural-language-processing/
│   │   ├── notes/
│   │   └── slides/
│   └── planning-and-reinforcement-learning/
│       ├── notes/
│       └── slides/
└── books/
    ├── ML/
    │   ├── 0812_Machine-Learning-for-Absolute-Beginners.pdf
    │   ├── Bishop-Pattern-Recognition-and-Machine-Learning-2006.pdf
    │   ├── Designing Machine Learning Systems An Iterative Process.pdf
    │   ├── Hands-On_Machine_Learning_with_Scikit-Learn_Keras_and_Tensorflow_-_Aurelien_Geron.pdf
    │   ├── ML Machine Learning-A Probabilistic Perspective.pdf
    │   ├── Practical MLOps_ Operationalizing Machine Learning Models.pdf
    │   ├── Probabilistic Machine Learning Advanced Topics.pdf
    │   ├── building-machine-learning-powered-applications-going-from-idea-to-product.pdf
    │   └── machine_learning.pdf
    ├── AI Engineering.pdf
    ├── Applied-Machine-Learning-and-AI-for-Engineers.pdf
    ├── Artificial Intelligence. A modern approach (Stuart Russell  Peter Norvig).pdf
    ├── Deep Learning by Ian Goodfellow, Yoshua Bengio, Aaron Courville.pdf
    ├── Gans-in-action-deep-learning-with-generative-adversarial-networks.pdf
    ├── Generative-Deep-Learning.pdf
    ├── Hands-On Generative AI with Transformers and Diffusion Models.pdf
    ├── Hands-On Large Language Models Language Understanding and Generation.pdf
    ├── Hands-On Machine Learning with Pytorch.pdf
    ├── Hands-On Machine Learning with Scikit-Learn and PyTorch (Second Early Release).pdf
    ├── LLM Engineers Handbook.pdf
    ├── ML Math.pdf
    └── NLP with Transformer models.pdf
```

### Course Folders

Each course directory contains:
- **`notes/`** — Lecture notes in LaTeX/PDF format
- **`slides/`** — Presentation slides and summaries
- **`lab/`** — Laboratory exercises and Jupyter notebooks (where applicable)
- **`assignment-X/`** — Course assignments and projects (where applicable)

---

## Reference Books

### General AI & Engineering
- **AI Engineering** — Comprehensive guide to AI system design
- **Applied Machine Learning and AI for Engineers** — Practical applications
- **Artificial Intelligence: A Modern Approach** — Russell & Norvig

### Machine Learning
#### Core ML
- **Bishop: Pattern Recognition and Machine Learning (2006)** — Classic ML textbook
- **Machine Learning: A Probabilistic Perspective** — Advanced probabilistic methods
- **Machine Learning for Absolute Beginners** — Introductory text
- **Hands-On Machine Learning with Scikit-Learn, Keras and TensorFlow** — Practical guide
- **Hands-On Machine Learning with Scikit-Learn and PyTorch (Second Early Release)** — Updated practical guide
- **Hands-On Machine Learning with PyTorch** — PyTorch-focused implementation
- **Machine Learning** — General reference

#### MLOps & Production
- **Designing Machine Learning Systems: An Iterative Process** — System design
- **Practical MLOps: Operationalizing Machine Learning Models** — Deployment and operations
- **Building Machine Learning Powered Applications: Going from Idea to Product** — End-to-end ML product development

#### Advanced Topics
- **Probabilistic Machine Learning: Advanced Topics** — Kevin Murphy's advanced text
- **ML Math** — Mathematical foundations

### Deep Learning
- **Deep Learning** — Goodfellow, Bengio, Courville (The definitive textbook)
- **Generative Deep Learning** — Comprehensive guide to generative models
- **GANs in Action: Deep Learning with Generative Adversarial Networks** — Practical GANs

### Natural Language Processing & LLMs
- **NLP with Transformer Models** — Modern NLP architectures
- **Hands-On Large Language Models: Language Understanding and Generation** — Alammar & Grootendorst
- **Hands-On Generative AI with Transformers and Diffusion Models** — Practical generative AI
- **LLM Engineers Handbook** — Engineering with large language models

---

## Getting Started

### Prerequisites
- **Git** — For cloning the repository
- **LaTeX Distribution** — For compiling `.tex` files (e.g., MacTeX, TeX Live, MiKTeX)
- **PDF Reader** — For viewing compiled documents
- **Python 3.x** — For running lab notebooks (if applicable)
- **Jupyter Notebook/Lab** — For interactive lab sessions

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/djacoo/ai-masters-notes.git
   cd ai-masters-notes
   ```

2. **Browse course materials:**
   ```bash
   cd courses/<course-name>/notes/
   ```

3. **Compile LaTeX notes (if needed):**
   ```bash
   pdflatex <filename>.tex
   ```

4. **Access reference books:**
   ```bash
   cd books/
   ```

### Recommended Tools
- **LaTeX Editor:** VS Code with LaTeX Workshop extension, Overleaf, TeXstudio
- **PDF Viewer:** Adobe Acrobat Reader, Preview (macOS), Evince (Linux)
- **IDE:** VS Code, PyCharm, Jupyter Lab

---

## Contributing

Contributions are welcome! To suggest improvements, corrections, or additions:

1. **Fork the repository**
2. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Commit your changes:**
   ```bash
   git commit -m "Description of changes"
   ```
4. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Open a Pull Request**

For issues or suggestions, please open an issue on GitHub.

---

## License

This repository is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

**Note:** Reference books in the `books/` directory are subject to their respective publishers' copyrights and are included for educational purposes only.

---

## Contact

**Jacopo Parretti**  
Master's in Artificial Intelligence — University of Verona (2025/2026)

- **GitHub:** [@djacoo](https://github.com/djacoo)
- **Email:** jacopo.parretti@studenti.univr.it

---

*Last updated: November 2025*
