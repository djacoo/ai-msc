<div align="center">

<svg width="800" height="100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .title { font: bold 36px sans-serif; fill: #2c3e50; }
      .letter { opacity: 0; animation: fadeIn 0.5s ease-in forwards; }
      @keyframes fadeIn { to { opacity: 1; } }
    </style>
  </defs>
  <text x="50%" y="50" text-anchor="middle" class="title">
    <tspan class="letter" style="animation-delay: 0s">A</tspan><tspan class="letter" style="animation-delay: 0.05s">I</tspan>
    <tspan class="letter" style="animation-delay: 0.1s"> </tspan>
    <tspan class="letter" style="animation-delay: 0.15s">M</tspan><tspan class="letter" style="animation-delay: 0.2s">a</tspan><tspan class="letter" style="animation-delay: 0.25s">s</tspan><tspan class="letter" style="animation-delay: 0.3s">t</tspan><tspan class="letter" style="animation-delay: 0.35s">e</tspan><tspan class="letter" style="animation-delay: 0.4s">r</tspan><tspan class="letter" style="animation-delay: 0.45s">'</tspan><tspan class="letter" style="animation-delay: 0.5s">s</tspan>
    <tspan class="letter" style="animation-delay: 0.55s"> </tspan>
    <tspan class="letter" style="animation-delay: 0.6s">N</tspan><tspan class="letter" style="animation-delay: 0.65s">o</tspan><tspan class="letter" style="animation-delay: 0.7s">t</tspan><tspan class="letter" style="animation-delay: 0.75s">e</tspan><tspan class="letter" style="animation-delay: 0.8s">s</tspan>
    <tspan class="letter" style="animation-delay: 0.85s"> </tspan><tspan class="letter" style="animation-delay: 0.9s">—</tspan><tspan class="letter" style="animation-delay: 0.95s"> </tspan>
    <tspan class="letter" style="animation-delay: 1s">U</tspan><tspan class="letter" style="animation-delay: 1.05s">n</tspan><tspan class="letter" style="animation-delay: 1.1s">i</tspan><tspan class="letter" style="animation-delay: 1.15s">v</tspan><tspan class="letter" style="animation-delay: 1.2s">e</tspan><tspan class="letter" style="animation-delay: 1.25s">r</tspan><tspan class="letter" style="animation-delay: 1.3s">s</tspan><tspan class="letter" style="animation-delay: 1.35s">i</tspan><tspan class="letter" style="animation-delay: 1.4s">t</tspan><tspan class="letter" style="animation-delay: 1.45s">y</tspan>
    <tspan class="letter" style="animation-delay: 1.5s"> </tspan>
    <tspan class="letter" style="animation-delay: 1.55s">o</tspan><tspan class="letter" style="animation-delay: 1.6s">f</tspan>
    <tspan class="letter" style="animation-delay: 1.65s"> </tspan>
    <tspan class="letter" style="animation-delay: 1.7s">V</tspan><tspan class="letter" style="animation-delay: 1.75s">e</tspan><tspan class="letter" style="animation-delay: 1.8s">r</tspan><tspan class="letter" style="animation-delay: 1.85s">o</tspan><tspan class="letter" style="animation-delay: 1.9s">n</tspan><tspan class="letter" style="animation-delay: 1.95s">a</tspan>
  </text>
</svg>

A comprehensive collection of notes, teaching materials, reference books, and resources for the Master's program in Artificial Intelligence at the University of Verona (Academic Year 2025/2026).

</div>

---

## Repository Structure

<svg width="100%" height="700" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .node { font: 14px monospace; fill: #2c3e50; }
      .folder { fill: #3498db; font-weight: bold; }
      .file { fill: #95a5a6; }
      .line { stroke: #bdc3c7; stroke-width: 2; }
      .branch { opacity: 0; animation: slideIn 0.8s ease-out forwards; }
      @keyframes slideIn { 
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
      }
    </style>
  </defs>
  
  <!-- Root -->
  <text x="20" y="30" class="node folder branch" style="animation-delay: 0s">ai-masters-notes/</text>
  
  <!-- Root Files -->
  <line x1="20" y1="35" x2="20" y2="110" class="line branch" style="animation-delay: 0.1s"/>
  <text x="40" y="55" class="node file branch" style="animation-delay: 0.2s">├── README.md</text>
  <text x="40" y="75" class="node file branch" style="animation-delay: 0.25s">├── LICENSE</text>
  <text x="40" y="95" class="node file branch" style="animation-delay: 0.3s">├── .gitignore</text>
  
  <!-- Courses Folder -->
  <text x="40" y="125" class="node folder branch" style="animation-delay: 0.4s">├── courses/</text>
  <line x1="60" y1="130" x2="60" y2="400" class="line branch" style="animation-delay: 0.45s"/>
  
  <!-- Automated Reasoning -->
  <text x="80" y="150" class="node folder branch" style="animation-delay: 0.5s">│   ├── automated-reasoning/</text>
  <text x="100" y="170" class="node file branch" style="animation-delay: 0.55s">│   │   ├── notes/</text>
  <text x="100" y="185" class="node file branch" style="animation-delay: 0.6s">│   │   └── slides/</text>
  
  <!-- HCI -->
  <text x="80" y="210" class="node folder branch" style="animation-delay: 0.65s">│   ├── human-computer-interaction/</text>
  <text x="100" y="230" class="node file branch" style="animation-delay: 0.7s">│   │   ├── assignment-1/</text>
  <text x="100" y="245" class="node file branch" style="animation-delay: 0.75s">│   │   ├── notes/</text>
  <text x="100" y="260" class="node file branch" style="animation-delay: 0.8s">│   │   └── slides/</text>
  
  <!-- ML & DL -->
  <text x="80" y="285" class="node folder branch" style="animation-delay: 0.85s">│   ├── machine-learning-and-deep-learning/</text>
  <text x="100" y="305" class="node file branch" style="animation-delay: 0.9s">│   │   ├── lab/</text>
  <text x="100" y="320" class="node file branch" style="animation-delay: 0.95s">│   │   ├── notes/</text>
  <text x="100" y="335" class="node file branch" style="animation-delay: 1s">│   │   └── slides/</text>
  
  <!-- NLP -->
  <text x="80" y="360" class="node folder branch" style="animation-delay: 1.05s">│   ├── natural-language-processing/</text>
  <text x="100" y="380" class="node file branch" style="animation-delay: 1.1s">│   │   ├── notes/</text>
  <text x="100" y="395" class="node file branch" style="animation-delay: 1.15s">│   │   └── slides/</text>
  
  <!-- Planning & RL -->
  <text x="80" y="420" class="node folder branch" style="animation-delay: 1.2s">│   └── planning-and-reinforcement-learning/</text>
  <text x="100" y="440" class="node file branch" style="animation-delay: 1.25s">│       ├── notes/</text>
  <text x="100" y="455" class="node file branch" style="animation-delay: 1.3s">│       └── slides/</text>
  
  <!-- Books Folder -->
  <text x="40" y="485" class="node folder branch" style="animation-delay: 1.35s">└── books/</text>
  <line x1="60" y1="490" x2="60" y2="650" class="line branch" style="animation-delay: 1.4s"/>
  
  <!-- ML Books -->
  <text x="80" y="510" class="node folder branch" style="animation-delay: 1.45s">    ├── ML/</text>
  <text x="100" y="530" class="node file branch" style="animation-delay: 1.5s">    │   ├── Machine Learning textbooks...</text>
  <text x="100" y="545" class="node file branch" style="animation-delay: 1.55s">    │   └── (9 books)</text>
  
  <!-- General Books -->
  <text x="80" y="570" class="node file branch" style="animation-delay: 1.6s">    ├── AI Engineering.pdf</text>
  <text x="80" y="590" class="node file branch" style="animation-delay: 1.65s">    ├── Deep Learning.pdf</text>
  <text x="80" y="610" class="node file branch" style="animation-delay: 1.7s">    ├── LLM Engineers Handbook.pdf</text>
  <text x="80" y="630" class="node file branch" style="animation-delay: 1.75s">    ├── NLP with Transformers.pdf</text>
  <text x="80" y="650" class="node file branch" style="animation-delay: 1.8s">    └── (10 more books...)</text>
</svg>

### Directory Descriptions

**courses/** — Course materials for all AI Master's subjects
- **automated-reasoning/** — Logic, proof systems, and automated theorem proving
  - `notes/` — Lecture notes in LaTeX/PDF format
  - `slides/` — Presentation slides and summaries
  
- **human-computer-interaction/** — User interface design and usability
  - `assignment-1/` — Course assignments and projects
  - `notes/` — Lecture notes in LaTeX/PDF format
  - `slides/` — Presentation slides and summaries

- **machine-learning-and-deep-learning/** — Core ML and neural network concepts
  - `lab/` — Laboratory exercises and Jupyter notebooks
  - `notes/` — Lecture notes in LaTeX/PDF format
  - `slides/` — Presentation slides and summaries

- **natural-language-processing/** — Text processing and language models
  - `notes/` — Lecture notes in LaTeX/PDF format
  - `slides/` — Presentation slides and summaries

- **planning-and-reinforcement-learning/** — Decision making and sequential learning
  - `notes/` — Lecture notes in LaTeX/PDF format
  - `slides/` — Presentation slides and summaries

**books/** — Comprehensive reference library with textbooks covering Machine Learning, Deep Learning, NLP, LLMs, and AI Engineering

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
