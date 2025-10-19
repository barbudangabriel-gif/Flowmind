# Quick Reference - Prevent Indentation Errors

## 🚀 Pentru noi developeri

### Setup inițial (O singură dată)
```bash
./setup_dev_env.sh
```

## ✅ Reguli de aur

### 1. EDITOR SETUP
- ✅ VS Code cu `detectIndentation: false`
- ✅ Format on save activat
- ✅ Tab size = 4 spații pentru Python

### 2. ÎNAINTE DE COMMIT
```bash
# Auto-format all Python files
black backend/

# Check for issues
ruff check backend/ --fix

# Test pre-commit hooks
pre-commit run --all-files
```

### 3. NICIODATĂ
- ❌ NU dezactiva pre-commit hooks
- ❌ NU face commit cu `--no-verify`
- ❌ NU folosi tabs în Python files
- ❌ NU amesteca 2-space cu 4-space

## 🔥 Quick Fixes

### Dacă vezi IndentationError:
```bash
# Fix un singur fișier
black path/to/file.py

# Fix toate fișierele
black backend/
```

### Dacă pre-commit fails:
```bash
# Rulează din nou (va auto-fix)
pre-commit run --all-files

# Apoi add + commit din nou
git add .
git commit -m "Your message"
```

## 🔍 Quick Checks

### Check sintaxă Python:
```bash
python -m py_compile backend/**/*.py
```

### Check indentare:
```bash
find backend/ -name "*.py" -exec grep -l $'\t' {} \;
```

### Check formatting:
```bash
black --check backend/
```

## 📱 Contact

Probleme? Vezi `INDENTATION_PREVENTION_GUIDE.md` pentru detalii complete.
