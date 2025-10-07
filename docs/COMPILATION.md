# 📝 LaTeX Compilation Guide

This guide provides detailed instructions for compiling LaTeX documents in this repository.

## 🎯 Quick Reference

| Course | File Path | Compilation Time |
|--------|-----------|------------------|
| Automated Reasoning | `courses/automated-reasoning/notes/AR Appunti.tex` | ~30 seconds |
| Natural Language Processing | `courses/natural-language-processing/notes/NLP Appunti.tex` | ~2-3 minutes |
| Planning & RL | `courses/planning-and-reinforcement-learning/notes/Planning appunti.tex` | ~15 seconds |
| Human-Computer Interaction | `courses/human-computer-interaction/notes/HCI Theory 2 Appunti.tex` | ~20 seconds |

## 🔧 Basic Compilation

### Single Document Compilation

Navigate to the notes directory and compile:

```bash
cd courses/<course-name>/notes
pdflatex "<filename>.tex"
```

### Example: Compile Automated Reasoning Notes

```bash
cd courses/automated-reasoning/notes
pdflatex "AR Appunti.tex"
```

The PDF will be generated in the same directory: `AR Appunti.pdf`

## 🚀 Advanced Compilation

### Multiple Runs for References

Some documents may require multiple compilation runs to resolve cross-references, table of contents, and bibliographies:

```bash
pdflatex "filename.tex"
pdflatex "filename.tex"  # Second run for references
```

### Full Build with Bibliography

If a document uses BibTeX:

```bash
pdflatex "filename.tex"
bibtex "filename"
pdflatex "filename.tex"
pdflatex "filename.tex"
```

### Clean Build

Remove auxiliary files before compilation:

```bash
# Remove auxiliary files
rm *.aux *.log *.out *.toc *.synctex.gz

# Then compile
pdflatex "filename.tex"
```

## 🛠️ Compilation Scripts

### Bash Script for All Courses

Create a script `compile-all.sh` in the repository root:

```bash
#!/bin/bash

echo "🚀 Compiling all course notes..."

# Automated Reasoning
echo "📚 Compiling Automated Reasoning..."
cd courses/automated-reasoning/notes
pdflatex -interaction=nonstopmode "AR Appunti.tex"
cd ../../..

# Natural Language Processing
echo "📚 Compiling Natural Language Processing..."
cd courses/natural-language-processing/notes
pdflatex -interaction=nonstopmode "NLP Appunti.tex"
cd ../../..

# Planning & RL
echo "📚 Compiling Planning & RL..."
cd courses/planning-and-reinforcement-learning/notes
pdflatex -interaction=nonstopmode "Planning appunti.tex"
cd ../../..

# Human-Computer Interaction
echo "📚 Compiling Human-Computer Interaction..."
cd courses/human-computer-interaction/notes
pdflatex -interaction=nonstopmode "HCI Theory 2 Appunti.tex"
cd ../../..

echo "✅ All compilations complete!"
```

Make it executable:

```bash
chmod +x compile-all.sh
./compile-all.sh
```

### PowerShell Script (Windows)

Create `compile-all.ps1`:

```powershell
Write-Host "🚀 Compiling all course notes..." -ForegroundColor Green

# Automated Reasoning
Write-Host "📚 Compiling Automated Reasoning..."
Set-Location "courses/automated-reasoning/notes"
pdflatex -interaction=nonstopmode "AR Appunti.tex"
Set-Location "../../.."

# Natural Language Processing
Write-Host "📚 Compiling Natural Language Processing..."
Set-Location "courses/natural-language-processing/notes"
pdflatex -interaction=nonstopmode "NLP Appunti.tex"
Set-Location "../../.."

# Planning & RL
Write-Host "📚 Compiling Planning & RL..."
Set-Location "courses/planning-and-reinforcement-learning/notes"
pdflatex -interaction=nonstopmode "Planning appunti.tex"
Set-Location "../../.."

# Human-Computer Interaction
Write-Host "📚 Compiling Human-Computer Interaction..."
Set-Location "courses/human-computer-interaction/notes"
pdflatex -interaction=nonstopmode "HCI Theory 2 Appunti.tex"
Set-Location "../../.."

Write-Host "✅ All compilations complete!" -ForegroundColor Green
```

Run with:

```powershell
.\compile-all.ps1
```

## 🔍 Troubleshooting

### Issue: LaTeX Error Messages

**Symptom**: Compilation stops with error messages

**Solutions**:

1. **Check for missing packages**:
   ```bash
   # View the log file
   cat filename.log | grep "not found"
   
   # Install missing package
   tlmgr install <package-name>  # TeX Live
   mpm --install=<package-name>  # MiKTeX
   ```

2. **Use non-stop mode**:
   ```bash
   pdflatex -interaction=nonstopmode "filename.tex"
   ```

3. **Check syntax errors**: Review the `.log` file for line numbers with errors

### Issue: Slow Compilation

**For large documents (like NLP notes with 400+ pages)**:

1. **Compile sections separately** (if supported by document structure)
2. **Use draft mode** for faster preview:
   ```latex
   \documentclass[draft]{article}
   ```
3. **Disable graphics** temporarily:
   ```latex
   \usepackage[draft]{graphicx}
   ```

### Issue: Out of Memory

**Symptom**: "TeX capacity exceeded"

**Solution**: Increase memory limits in `texmf.cnf` or use LuaLaTeX:

```bash
lualatex "filename.tex"
```

### Issue: Italian Characters Not Displaying

**Solution**: Ensure proper encoding in the preamble:

```latex
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[italian]{babel}
```

## 📊 Compilation Options

### Common pdflatex Options

```bash
pdflatex [options] filename.tex
```

**Useful options**:

| Option | Description |
|--------|-------------|
| `-interaction=nonstopmode` | Don't stop for errors |
| `-halt-on-error` | Stop immediately on error |
| `-output-directory=DIR` | Specify output directory |
| `-synctex=1` | Enable SyncTeX for editor integration |
| `-shell-escape` | Allow external commands (use with caution) |
| `-draftmode` | Skip PDF generation (faster) |

### Example with Multiple Options

```bash
pdflatex -synctex=1 -interaction=nonstopmode -file-line-error "filename.tex"
```

## 🧹 Cleaning Auxiliary Files

### Manual Cleanup

```bash
# In notes directory
rm *.aux *.log *.out *.toc *.synctex.gz *.fdb_latexmk *.fls
```

### Using latexmk

Install and use `latexmk` for automatic cleanup:

```bash
# Install latexmk
tlmgr install latexmk  # TeX Live

# Compile with latexmk
latexmk -pdf "filename.tex"

# Clean auxiliary files
latexmk -c

# Clean all including PDF
latexmk -C
```

## 🎨 Editor Integration

### VS Code

With LaTeX Workshop extension:

1. Open `.tex` file
2. Press `Cmd/Ctrl + Alt + B` to build
3. Press `Cmd/Ctrl + Alt + V` to view PDF

### TeXstudio

1. Open `.tex` file
2. Press `F5` to compile and view
3. Press `F6` to compile only

### Overleaf

Upload `.tex` files to Overleaf for online compilation (no local setup needed).

## 📈 Performance Tips

1. **Use SSD storage** for faster I/O
2. **Close other applications** during large compilations
3. **Compile changed sections only** when possible
4. **Use draft mode** for quick previews
5. **Keep LaTeX distribution updated**:
   ```bash
   tlmgr update --all  # TeX Live
   ```

## 🔗 Continuous Integration

The repository includes GitHub Actions for automatic compilation testing. See `.github/workflows/latex-compile-test.yml`.

### Run Tests Locally

```bash
# Simulate CI compilation
for course in courses/*/notes/*.tex; do
  echo "Testing: $course"
  pdflatex -interaction=nonstopmode -halt-on-error "$course"
done
```

## 📚 Additional Resources

- [LaTeX Compilation FAQ](https://texfaq.org/)
- [pdflatex Manual](https://www.tug.org/applications/pdftex/)
- [LaTeX Error Messages Explained](https://www.overleaf.com/learn/latex/Errors)

## ✅ Verification Checklist

After compilation, verify:

- [ ] PDF file was generated
- [ ] No error messages in output
- [ ] Table of contents is correct (if applicable)
- [ ] All cross-references are resolved
- [ ] Figures and tables appear correctly
- [ ] Bibliography is formatted properly (if applicable)

---

[← Back to Documentation](./README.md) | [← Back to Main Repository](../README.md)
