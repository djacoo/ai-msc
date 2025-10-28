# AI Master's Notes — UniVR

Notes, teaching materials, and custom tools developed during the master's program in Artificial Intelligence at the University of Verona (2025/2026). The repository organizes course notes, slides, code, and includes a local PDF viewing tool.

---
## Table of Contents
- [Repository Structure](#repository-structure)
- [Courses & Materials](#courses--materials)
- [PDF Viewer Desktop](#pdf-viewer-desktop)
- [Quick Start Guide](#quick-start-guide)
- [Contributing & License](#contributing--license)
- [Contact](#contact)

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
│   │   ├── notes/
│   │   └── slides/
│   ├── machine-learning-and-deep-learning/
│   │   ├── lab/
│   │   ├── notes/
│   │   └── slides/
│   └── natural-language-processing/
│       ├── notes/
│       └── slides/
└── pdf-viewer-desktop/
    ├── renderer/
    └── build-and-install.sh
```

---
## Courses & Materials

- **Automated Reasoning:** notes and slides on logical models, automated theorem proving, SAT, and SMT.
- **Human-Computer Interaction:** materials on usability principles, HCI concepts, and related slides.
- **Machine Learning & Deep Learning:** notes, labs, and slides on classic ML and modern neural networks.
- **Natural Language Processing:** computational linguistics, sequence models, and practical exercises.

Each subfolder includes:
- `notes/`: lecture notes in LaTeX or PDF
- `slides/`: lecture slides and summaries
- `lab/`: labs, notebooks (when available)

---
## PDF Viewer Desktop

Inside the `pdf-viewer-desktop/` folder you will find a PDF viewer app built with Node.js/Electron, designed for seamless reading of course materials. Refer to its [README](pdf-viewer-desktop/README.md) for detailed build and usage instructions.

---
## Quick Start Guide

1. **Download:**
   ```bash
   git clone https://github.com/djacoo/ai-masters-notes.git
   cd ai-masters-notes
   ```
2. **Environment Setup:**
   - LaTeX toolchain: any TeX distribution (e.g., MacTeX, TeX Live) + editor (VS Code + LaTeX Workshop recommended).
   - Node.js (required only for `pdf-viewer-desktop`).
3. **Browse/compile notes:**
   - Open PDFs found in each course’s `notes/`. To modify or if only the `.tex` file is present, compile:
   ```bash
   cd courses/natural-language-processing/notes/
   pdflatex "NLP Appunti.tex"
   ```
4. **Use PDF Viewer Desktop:**
   - Follow the instructions in `pdf-viewer-desktop/README.md`.

---
## Contributing & License

To suggest corrections or improvements, open an issue or submit a pull request.

All content (unless stated otherwise) is under the MIT License (see LICENSE file).

---
## Contact

**Jacopo Parretti**  
Master's in Artificial Intelligence — University of Verona (2025/2026)
- [GitHub](https://github.com/djacoo)
- Email: jacopo.parretti@studenti.univr.it
