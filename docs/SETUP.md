# 🛠️ Setup Guide

This guide will help you set up your environment to work with the repository materials, particularly for compiling LaTeX documents.

## 📋 Prerequisites

### 1. Git
Ensure Git is installed on your system:

```bash
# Check Git installation
git --version

# If not installed, download from: https://git-scm.com/
```

### 2. LaTeX Distribution

Choose and install a LaTeX distribution based on your operating system:

#### macOS
**MacTeX** (Recommended)

```bash
# Using Homebrew
brew install --cask mactex

# Or download from: https://www.tug.org/mactex/
```

**BasicTeX** (Minimal installation)

```bash
brew install --cask basictex
```

#### Windows
**MiKTeX** (Recommended)

- Download from: https://miktex.org/download
- Run the installer and choose "Complete" installation
- Enable automatic package installation

**TeX Live** (Alternative)

- Download from: https://www.tug.org/texlive/
- Follow installation instructions

#### Linux
**TeX Live**

```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get install texlive-full

# Fedora
sudo dnf install texlive-scheme-full

# Arch Linux
sudo pacman -S texlive-most
```

### 3. PDF Viewer

Choose a PDF viewer for viewing compiled documents:

- **macOS**: Preview (built-in), Skim, PDF Expert
- **Windows**: Adobe Acrobat Reader, Sumatra PDF, Foxit Reader
- **Linux**: Evince, Okular, Zathura

### 4. Text Editor (Optional)

For editing LaTeX files, consider:

- **VS Code** with LaTeX Workshop extension
- **TeXstudio** (LaTeX-specific IDE)
- **Overleaf** (online LaTeX editor)
- **Vim** or **Emacs** with LaTeX plugins

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/djacoo/AI---PRIMO-SEMESTRE.git
cd AI---PRIMO-SEMESTRE
```

### 2. Verify LaTeX Installation

```bash
# Check pdflatex
pdflatex --version

# Should output version information
```

### 3. Compile a Sample Document

Test your setup by compiling one of the notes:

```bash
# Navigate to a course
cd courses/automated-reasoning/notes

# Compile the LaTeX document
pdflatex "AR Appunti.tex"

# View the generated PDF
# macOS
open "AR Appunti.pdf"

# Linux
xdg-open "AR Appunti.pdf"

# Windows
start "AR Appunti.pdf"
```

## 🔧 Advanced Setup

### VS Code with LaTeX

1. **Install VS Code**: https://code.visualstudio.com/

2. **Install LaTeX Workshop Extension**:
   - Open VS Code
   - Go to Extensions (Cmd/Ctrl + Shift + X)
   - Search for "LaTeX Workshop"
   - Click Install

3. **Configure Settings** (Optional):
   
   Create `.vscode/settings.json` in the repository root:

   ```json
   {
     "latex-workshop.latex.autoBuild.run": "onSave",
     "latex-workshop.view.pdf.viewer": "tab",
     "latex-workshop.latex.recipes": [
       {
         "name": "pdflatex",
         "tools": ["pdflatex"]
       }
     ],
     "latex-workshop.latex.tools": [
       {
         "name": "pdflatex",
         "command": "pdflatex",
         "args": [
           "-synctex=1",
           "-interaction=nonstopmode",
           "-file-line-error",
           "%DOC%"
         ]
       }
     ]
   }
   ```

### TeXstudio Setup

1. **Install TeXstudio**: https://www.texstudio.org/

2. **Configure**:
   - Options → Configure TeXstudio
   - Build → Default Compiler: pdflatex
   - Configure PDF viewer preferences

## 🐛 Troubleshooting

### Common Issues

#### 1. "pdflatex: command not found"

**Solution**: LaTeX is not in your PATH

```bash
# macOS/Linux - Add to ~/.zshrc or ~/.bashrc
export PATH="/usr/local/texlive/2024/bin/x86_64-darwin:$PATH"

# Reload shell
source ~/.zshrc
```

#### 2. Missing LaTeX Packages

**Solution**: Install missing packages

```bash
# MiKTeX (Windows)
mpm --install=<package-name>

# TeX Live (macOS/Linux)
tlmgr install <package-name>

# Or enable automatic installation in MiKTeX settings
```

#### 3. Compilation Errors

**Solution**: Check error messages

```bash
# Run pdflatex with detailed output
pdflatex -interaction=nonstopmode "filename.tex"

# Check the .log file for details
cat "filename.log"
```

#### 4. Italian Language Support

Some notes use Italian. Ensure `babel` package with Italian support:

```bash
# TeX Live
tlmgr install babel babel-italian

# Check if needed in document preamble
\usepackage[italian]{babel}
```

### Getting Help

If you encounter issues:

1. Check the [LaTeX Stack Exchange](https://tex.stackexchange.com/)
2. Review the `.log` file generated during compilation
3. Open an issue on this repository with:
   - Error message
   - Operating system
   - LaTeX distribution and version
   - File you're trying to compile

## 📚 Learning Resources

### LaTeX Basics
- [Overleaf Documentation](https://www.overleaf.com/learn)
- [LaTeX Wikibook](https://en.wikibooks.org/wiki/LaTeX)
- [The Not So Short Introduction to LaTeX](https://tobi.oetiker.ch/lshort/lshort.pdf)

### Git Basics
- [GitHub Git Handbook](https://guides.github.com/introduction/git-handbook/)
- [Git Documentation](https://git-scm.com/doc)

## ✅ Verification Checklist

Before you start working with the materials, verify:

- [ ] Git is installed and working
- [ ] LaTeX distribution is installed
- [ ] `pdflatex` command is available in terminal
- [ ] You can successfully clone the repository
- [ ] You can compile at least one LaTeX document
- [ ] PDF viewer can open the generated files

## 🎯 Next Steps

Once setup is complete:

1. Explore the [courses/](../courses/) directory
2. Read course-specific READMEs
3. Review the [compilation guide](./COMPILATION.md)
4. Check [CONTRIBUTING.md](../CONTRIBUTING.md) to contribute

---

[← Back to Documentation](./README.md) | [← Back to Main Repository](../README.md)
