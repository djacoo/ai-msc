# 🎯 Planning & Reinforcement Learning

## 📚 Course Overview

This directory contains materials for **Planning & Reinforcement Learning**, covering classical planning, automated planning systems, and reinforcement learning fundamentals.

## 📂 Directory Structure

```
planning-and-reinforcement-learning/
├── README.md              # This file
├── notes/                # Personal course notes
│   ├── Planning appunti.tex  # LaTeX source
│   └── Planning appunti.pdf  # Compiled PDF (23 pages)
└── slides/               # Official course slides
    ├── Planning-1.pdf
    ├── Planning-2.pdf
    ├── Planning-3.pdf
    ├── Planning-4.pdf
    ├── Planning-5.pdf
    └── Planning-6.pdf
```

## 📖 Course Topics

### Classical Planning
- **State Transition Systems**: Formal models of planning problems
- **Action Schemas**: STRIPS and PDDL representations
- **Planning Domains**: DWR (Dock Worker Robot) and other benchmarks
- **Search Algorithms**: Forward and backward search strategies
- **Heuristics**: Domain-independent heuristics for planning

### Advanced Planning
- **SAT-based Planning**: Encoding planning problems as SAT
- **Constraint-based Planning**: Using CSP solvers for planning
- **Temporal Planning**: Time and resources in planning
- **Hierarchical Planning**: HTN (Hierarchical Task Network) planning

### Reinforcement Learning
- **MDP**: Markov Decision Processes
- **Value Functions**: State-value and action-value functions
- **Policy Optimization**: Policy iteration and value iteration
- **Q-Learning**: Model-free RL algorithms
- **Deep RL**: Neural network-based reinforcement learning

## 📊 Materials

### Notes
- **Planning appunti.pdf**: 23 pages of detailed course notes in Italian
  - Formal definitions and theorems
  - Algorithm descriptions
  - Examples and worked problems
  - Planning domain specifications

### Slides
- **6 lecture presentations** covering the complete planning curriculum
- Official course materials from University of Verona

## 🔧 Compiling LaTeX Notes

To recompile the notes from source:

```bash
cd notes
pdflatex "Planning appunti.tex"
```

**Requirements**: TeX Live, MiKTeX, or MacTeX

## 📝 Additional Resources

### Recommended Books
- *Automated Planning: Theory and Practice* - Ghallab, Nau & Traverso
- *Reinforcement Learning: An Introduction* - Sutton & Barto
- *Artificial Intelligence: A Modern Approach* (Planning chapters) - Russell & Norvig

### Online Resources
- [International Planning Competition](https://www.icaps-conference.org/competitions/)
- [PDDL Resources](http://planning.domains/)
- [OpenAI Spinning Up in Deep RL](https://spinningup.openai.com/)

### Tools & Planners
- **Fast Downward**: State-of-the-art classical planner
- **LAMA**: Heuristic search planner
- **Madagascar**: SAT-based planner
- **PyPDDL**: Python PDDL parser and tools

## 👨‍🏫 Course Information

**University**: University of Verona  
**Program**: Master's in Artificial Intelligence  
**Semester**: First Semester 2025/2026

## 📜 License

Course slides are property of the University of Verona and respective professors.  
Personal notes are shared for educational purposes only.

---

[← Back to Main Repository](../../README.md)
