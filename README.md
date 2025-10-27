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

## Getting Started

Clone the repository:

```bash
git clone https://github.com/djacoo/ai-masters-notes.git
cd ai-masters-notes
```

---

## Repo Setup

- LaTeX toolchain: any TeX distribution (e.g., MacTeX/TeX Live) + a LaTeX editor/VS Code with LaTeX Workshop.
- Optional: `make` or VS Code tasks to compile notes to PDF.
- Node.js (only if you plan to use the optional `pdf-viewer-desktop` app).

---

## Using the Repo

- Notes and slides live under `courses/<course>/`.
- PDFs: open existing PDFs in `notes/` if present; otherwise compile from the `.tex` sources.
- Compile LaTeX (example):

```bash
cd courses/natural-language-processing/notes/
pdflatex "NLP Appunti.tex"
```

- Lab materials (if any) are under `lab/` in the corresponding course.
- The `pdf-viewer-desktop/` folder contains a small viewer app; see its README for usage.

---

## Author

**Jacopo Parretti** — Master's in Artificial Intelligence, University of Verona (2025/2026)

- GitHub: https://github.com/djacoo
- Email: jacopo.parretti@studenti.univr.it
